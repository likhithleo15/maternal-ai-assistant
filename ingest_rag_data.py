"""
Maternal RAG Data Ingestion
Handles: .md, .txt, .pdf files
"""

import sys
import os
import json
import logging
import argparse
from pathlib import Path

import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sys.path.append(str(Path(__file__).parent))

from config import Config
from agents.rag_agent import MedicalRAG

parser = argparse.ArgumentParser(description="Ingest documents into maternal RAG system")
parser.add_argument("--file", type=str, help="Path to a single file to ingest")
parser.add_argument("--dir", type=str, help="Path to directory of files to ingest")
parser.add_argument("--reset", action="store_true", help="Reset/delete existing Qdrant collection first")
args = parser.parse_args()

config = Config()

# Reset collection if requested (needed when changing embedding dimensions)
if args.reset:
    logger.info("Resetting Qdrant collection...")
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(path=config.rag.vector_local_path)
        collections = client.get_collections()
        names = [c.name for c in collections.collections]
        if config.rag.collection_name in names:
            client.delete_collection(config.rag.collection_name)
            logger.info(f"Deleted collection: {config.rag.collection_name}")
        else:
            logger.info("No existing collection to delete")
    except Exception as e:
        logger.warning(f"Could not reset collection: {e}")

rag = MedicalRAG(config)


def ingest():
    if args.file:
        logger.info(f"Ingesting file: {args.file}")
        result = rag.ingest_file(args.file)
        print(json.dumps(result, indent=2))
        return result["success"]

    elif args.dir:
        logger.info(f"Ingesting directory: {args.dir}")
        result = rag.ingest_directory(args.dir)
        print(json.dumps(result, indent=2))
        return result["success"]

    else:
        # Default: ingest maternal docs
        default_dir = "./data/maternal_docs"
        if os.path.isdir(default_dir):
            logger.info(f"Ingesting default maternal docs from: {default_dir}")
            result = rag.ingest_directory(default_dir)
            print(json.dumps(result, indent=2))
            return result["success"]
        else:
            logger.error("No file, directory, or default docs found. Use --file or --dir")
            return False


if __name__ == "__main__":
    logger.info("Starting document ingestion...")
    success = ingest()
    if success:
        logger.info("✅ Ingestion complete!")
    else:
        logger.error("❌ Ingestion failed")
        sys.exit(1)