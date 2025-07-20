from qdrant_client import AsyncQdrantClient
from typing import Optional
from transformers import AutoModel, AutoTokenizer
from fastembed import SparseTextEmbedding
from src.tools.utils.embeddings import (
    init_dense_model,
    init_sparse_model,
)
from src.tools.web.pipeline import WebSearchPipeline


class ResourceManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dense_model = None
            cls._instance._tokenizer = None
            cls._instance._sparse_model = None
            cls._instance._qdrant_client = None
            cls._instance._web_search_pipeline = None

        return cls._instance

    def initialize_models(self, device: str = "mps"):
        """Initialize models if they haven't been initialized yet"""
        if self._dense_model is None:
            print("Initializing dense model...")
            self._dense_model, self._tokenizer = init_dense_model(device=device)

        if self._sparse_model is None:
            print("Initializing sparse model...")
            self._sparse_model = init_sparse_model()

    def initialize_client(self, url: str = "http://localhost:6333"):
        if self._qdrant_client is None:
            print("Initializing Qdrant client...")
            self._qdrant_client = AsyncQdrantClient(url)

    def initialize_web_search_pipeline(self):
        if self._web_search_pipeline is None:
            print("Initializing web search pipeline...")
            self._web_search_pipeline = WebSearchPipeline()

    @property
    def dense_model(self) -> Optional[AutoModel]:
        return self._dense_model

    @property
    def tokenizer(self) -> Optional[AutoTokenizer]:
        return self._tokenizer

    @property
    def sparse_model(self) -> Optional[SparseTextEmbedding]:
        return self._sparse_model

    @property
    def qdrant_client(self) -> Optional[AsyncQdrantClient]:
        return self._qdrant_client

    @property
    def web_search_pipeline(self) -> Optional[WebSearchPipeline]:
        return self._web_search_pipeline


# Create a global instance
resource_manager = ResourceManager()
resource_manager.initialize_models()
resource_manager.initialize_client()
resource_manager.initialize_web_search_pipeline()


def get_resource_manager() -> ResourceManager:
    """Get the singleton model manager instance"""

    return resource_manager
