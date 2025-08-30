"""
Free Local Embedding Service for NewsNeuron
Uses sentence-transformers for lightweight, offline embeddings
"""
import logging
from typing import List, Optional, Dict, Any
from sentence_transformers import SentenceTransformer
import torch

from app.config import settings

logger = logging.getLogger(__name__)


class FreeEmbeddingService:
    """
    Free local embedding service using sentence-transformers
    Provides lightweight, CPU-only embeddings without API costs
    """
    
    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self.model_name = settings.embedding_model
        self.embedding_dimension = settings.embedding_dimension
        self._initialized = False  # Lazy initialization flag
    
    def _ensure_initialized(self):
        """Ensure the model is initialized (lazy loading)"""
        if not self._initialized:
            self._initialize_model()
            self._initialized = True

    def _initialize_model(self):
        """Initialize the sentence transformer model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")

            # Force CPU-only usage to keep it lightweight
            device = "cpu"

            self.model = SentenceTransformer(
                self.model_name,
                device=device,
                trust_remote_code=False  # Security best practice
            )

            # Warm up model with a short list to pre-load kernels
            test_embedding = self.model.encode(["warmup"], convert_to_tensor=False)
            if isinstance(test_embedding, list) and len(test_embedding) > 0 and hasattr(test_embedding[0], '__len__'):
                test_embedding = test_embedding[0]
            actual_dimension = len(test_embedding)

            if actual_dimension != self.embedding_dimension:
                logger.warning(
                    f"Model dimension mismatch: expected {self.embedding_dimension}, "
                    f"got {actual_dimension}. Updating config."
                )
                self.embedding_dimension = actual_dimension

            logger.info(
                f"Embedding model loaded successfully: {self.model_name} "
                f"({actual_dimension} dimensions, CPU-only)"
            )

        except Exception as e:
            logger.error(f"Failed to load embedding model {self.model_name}: {str(e)}")
            self.model = None
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text using local model

        Args:
            text: Input text to embed

        Returns:
            List of embedding values or None if model not available
        """
        # Lazy initialization
        self._ensure_initialized()

        if not self.model:
            logger.warning("Embedding model not available")
            return None

        try:
            # Clean and truncate text to reasonable length
            clean_text = self._preprocess_text(text)

            # Generate embedding (CPU-only)
            embedding = self.model.encode(
                clean_text,
                convert_to_tensor=False,  # Return as numpy array
                normalize_embeddings=True,  # Normalize for better similarity search
                show_progress_bar=False  # Suppress progress bar for API usage
            )

            # Convert to list for JSON serialization
            embedding_list = embedding.tolist()

            logger.debug(f"Generated embedding with {len(embedding_list)} dimensions")
            return embedding_list

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None

    async def generate_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Batch generate embeddings for a list of texts

        Args:
            texts: List of strings to embed

        Returns:
            List of embeddings (or None where generation failed)
        """
        # Lazy initialization
        self._ensure_initialized()

        if not self.model:
            logger.warning("Embedding model not available for batch generation")
            return [None] * len(texts)
        try:
            cleaned = [self._preprocess_text(t) for t in texts]
            vectors = self.model.encode(
                cleaned,
                batch_size=32,
                convert_to_tensor=False,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            # vectors can be numpy array; ensure list of lists
            if hasattr(vectors, 'tolist'):
                vectors = vectors.tolist()
            return vectors
        except Exception as e:
            logger.error(f"Error in batch embedding generation: {str(e)}")
            return [None] * len(texts)
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for embedding generation
        
        Args:
            text: Raw text
        
        Returns:
            Cleaned and truncated text
        """
        if not text:
            return ""
        
        # Basic cleaning
        text = text.strip()
        
        # Truncate to reasonable length (most models have token limits)
        max_chars = 8000  # Conservative limit for most models
        if len(text) > max_chars:
            text = text[:max_chars]
            logger.debug(f"Truncated text to {max_chars} characters")
        
        return text
    
    def get_backend_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding backend

        Returns:
            Dictionary with backend information
        """
        # Lazy initialization
        self._ensure_initialized()

        return {
            "backend": "sentence-transformers",
            "model": self.model_name,
            "dimension": self.embedding_dimension,
            "device": "CPU",
            "cost": "Free",
            "available": self.model is not None,
            "library": "sentence-transformers"
        }
    
    def is_available(self) -> bool:
        """Check if the embedding service is available"""
        # Lazy initialization check
        self._ensure_initialized()
        return self.model is not None


# Global embedding service instance
_embedding_service: Optional[FreeEmbeddingService] = None


def get_embedding_service() -> FreeEmbeddingService:
    """Get singleton embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = FreeEmbeddingService()
    return _embedding_service


def initialize_embedding_service() -> bool:
    """
    Initialize the embedding service (lazy initialization - just create the service instance)

    Returns:
        True if successful, False otherwise
    """
    try:
        service = get_embedding_service()
        # Don't trigger full initialization here - just check if service can be created
        return service is not None
    except Exception as e:
        logger.error(f"Failed to create embedding service: {str(e)}")
        return False
