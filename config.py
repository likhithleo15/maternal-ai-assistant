"""
Configuration for Maternal AI Assistant
Powered by Gemini (free tier) — no Azure, no OpenAI, no ElevenLabs
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

class AgentDecisionConfig:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.1,
            google_api_key=GOOGLE_API_KEY,
        )

class ConversationConfig:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            google_api_key=GOOGLE_API_KEY,
        )

class RAGConfig:
    def __init__(self):
        self.vector_db_type = "qdrant"
        self.embedding_dim = 768          # text-embedding-004 = 768-dim
        self.distance_metric = "Cosine"
        self.use_local = True
        self.vector_local_path = "./data/qdrant_db"
        self.doc_local_path = "./data/docs_db"
        self.parsed_content_dir = "./data/parsed_docs"
        self.url = os.getenv("QDRANT_URL", None)
        self.api_key = os.getenv("QDRANT_API_KEY", None)
        self.collection_name = "maternal_rag"
        self.chunk_size = 512
        self.chunk_overlap = 50

        # Gemini Embeddings (768-dim, free)
        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=GOOGLE_API_KEY
        )

        # Gemini Flash for RAG processing
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            google_api_key=GOOGLE_API_KEY
        )
        self.summarizer_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.5,
            google_api_key=GOOGLE_API_KEY
        )
        self.chunker_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.0,
            google_api_key=GOOGLE_API_KEY
        )
        self.response_generator_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            google_api_key=GOOGLE_API_KEY
        )

        self.top_k = 5
        self.vector_search_type = "similarity"
        self.reranker_model = "cross-encoder/ms-marco-TinyBERT-L-6"
        self.reranker_top_k = 3
        self.max_context_length = 8192
        self.include_sources = True
        self.min_retrieval_confidence = 0.35   # lower threshold for better recall
        self.context_limit = 20
        self.huggingface_token = os.getenv("HUGGINGFACE_TOKEN", None)

class APIConfig:
    def __init__(self):
        self.host = os.getenv("API_HOST", "0.0.0.0")
        self.port = int(os.getenv("API_PORT", 8000))
        self.debug = True
        self.rate_limit = 10

class ValidationConfig:
    def __init__(self):
        self.require_validation = {
            "CONVERSATION_AGENT": False,
            "RAG_AGENT": False,
        }
        self.validation_timeout = 300
        self.default_action = "reject"

class SensorConfig:
    def __init__(self):
        self.sqlite_path = os.getenv("SENSOR_DB_PATH", "./data/sensor_data.db")
        self.trend_days = 7

class Config:
    def __init__(self):
        self.agent_decision = AgentDecisionConfig()
        self.conversation = ConversationConfig()
        self.rag = RAGConfig()
        self.api = APIConfig()
        self.validation = ValidationConfig()
        self.sensor = SensorConfig()
        self.max_conversation_history = 20