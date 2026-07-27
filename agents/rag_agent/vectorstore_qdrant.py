import os
import re
import logging
import json
from uuid import uuid4
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from langchain_core.documents import Document
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, SparseVectorParams, VectorParams


class SimpleFileStore:
    """
    Minimal key-value file store for document chunks.
    Replaces langchain's LocalFileStore which moved packages.
    Stores chunks as JSON in a local directory.
    """
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)

    def mset(self, items: List[Tuple[str, bytes]]):
        for key, value in items:
            file_path = self.path / f"{key}.bin"
            file_path.write_bytes(value)

    def mget(self, keys: List[str]) -> List[Optional[bytes]]:
        results = []
        for key in keys:
            file_path = self.path / f"{key}.bin"
            if file_path.exists():
                results.append(file_path.read_bytes())
            else:
                results.append(None)
        return results


class VectorStore:
    """
    Create vector store, ingest documents, retrieve relevant documents.
    Uses Qdrant (local) with Gemini embeddings (768-dim).
    """
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.collection_name = config.rag.collection_name
        self.embedding_dim = config.rag.embedding_dim
        self.distance_metric = config.rag.distance_metric
        self.embedding_model = config.rag.embedding_model
        self.retrieval_top_k = config.rag.top_k
        self.vector_search_type = config.rag.vector_search_type
        self.vectorstore_local_path = config.rag.vector_local_path
        self.docstore_local_path = config.rag.doc_local_path

        os.makedirs(self.vectorstore_local_path, exist_ok=True)
        os.makedirs(self.docstore_local_path, exist_ok=True)

        self.client = QdrantClient(path=self.vectorstore_local_path)

    def _does_collection_exist(self) -> bool:
        try:
            collection_info = self.client.get_collections()
            collection_names = [c.name for c in collection_info.collections]
            return self.collection_name in collection_names
        except Exception as e:
            self.logger.error(f"Error checking collection: {e}")
            return False

    def _create_collection(self):
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={"dense": VectorParams(size=self.embedding_dim, distance=Distance.COSINE)},
                sparse_vectors_config={
                    "sparse": SparseVectorParams(index=models.SparseIndexParams(on_disk=False))
                },
            )
            self.logger.info(f"Created collection: {self.collection_name} (dim={self.embedding_dim})")
        except Exception as e:
            self.logger.error(f"Error creating collection: {e}")
            raise

    def load_vectorstore(self) -> Tuple[QdrantVectorStore, SimpleFileStore]:
        if not self._does_collection_exist():
            raise ValueError(
                f"Collection '{self.collection_name}' does not exist. "
                "Please run: python ingest_rag_data.py first."
            )

        sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        qdrant_vectorstore = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embedding_model,
            sparse_embedding=sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name="dense",
            sparse_vector_name="sparse",
        )
        docstore = SimpleFileStore(self.docstore_local_path)
        return qdrant_vectorstore, docstore

    def create_vectorstore(
        self,
        document_chunks: List[str],
        document_path: str,
    ) -> None:
        doc_ids = [str(uuid4()) for _ in range(len(document_chunks))]

        langchain_documents = [
            Document(
                page_content=chunk,
                metadata={
                    "source": os.path.basename(document_path),
                    "doc_id": doc_ids[idx],
                    "source_path": f"http://localhost:8000/{document_path}"
                }
            )
            for idx, chunk in enumerate(document_chunks)
        ]

        sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

        if not self._does_collection_exist():
            self._create_collection()

        qdrant_vectorstore = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embedding_model,
            sparse_embedding=sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name="dense",
            sparse_vector_name="sparse",
        )

        docstore = SimpleFileStore(self.docstore_local_path)

        qdrant_vectorstore.add_documents(documents=langchain_documents, ids=doc_ids)

        encoded_chunks = [chunk.encode('utf-8') for chunk in document_chunks]
        docstore.mset(list(zip(doc_ids, encoded_chunks)))

        self.logger.info(f"Stored {len(document_chunks)} chunks for {os.path.basename(document_path)}")

    def retrieve_relevant_chunks(
        self,
        query: str,
        vectorstore: QdrantVectorStore,
        docstore: SimpleFileStore,
    ) -> List[Dict[str, Any]]:
        results = vectorstore.similarity_search_with_score(
            query=query,
            k=self.retrieval_top_k
        )

        retrieved_docs = []
        for chunk, score in results:
            doc_id = chunk.metadata.get('doc_id')
            doc_content_bytes_list = docstore.mget([doc_id])
            doc_content_bytes = doc_content_bytes_list[0] if doc_content_bytes_list else None

            if doc_content_bytes:
                doc_content = doc_content_bytes.decode('utf-8')
            else:
                doc_content = chunk.page_content

            doc_dict = {
                "id": doc_id,
                "content": doc_content,
                "score": score,
                "source": chunk.metadata.get('source', 'unknown'),
                "source_path": chunk.metadata.get('source_path', ''),
            }
            retrieved_docs.append(doc_dict)

        return retrieved_docs