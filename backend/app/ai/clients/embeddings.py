from typing import List, Optional
from fastembed import TextEmbedding
from backend.app.core.config import settings
from backend.app.core.logging import logger


class LocalEmbeddingClient:
    """Lightweight local text embedding client using FastEmbed (ONNX Runtime)."""

    _instance: Optional["LocalEmbeddingClient"] = None
    _model: Optional[TextEmbedding] = None

    def __new__(cls) -> "LocalEmbeddingClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_model(self) -> TextEmbedding:
        if self._model is None:
            logger.info(f"Loading FastEmbed model '{settings.EMBEDDING_MODEL}' into memory...")
            self._model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
            logger.info(f"FastEmbed model '{settings.EMBEDDING_MODEL}' ready.")
        return self._model

    def embed_text(self, text: str) -> List[float]:
        """Generate a 384-dimensional vector embedding for a single text."""
        model = self._get_model()
        embeddings = list(model.embed([text]))
        return embeddings[0].tolist()

    def embed_query(self, text: str) -> List[float]:
        """Generate a 384-dimensional vector embedding for a query text."""
        return self.embed_text(text)


    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of text chunks in batch."""
        if not texts:
            return []
        model = self._get_model()
        embeddings = list(model.embed(texts))
        return [e.tolist() for e in embeddings]


# Global client instance
embedding_client = LocalEmbeddingClient()
