import logging
from typing import List

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# We use a relatively small, fast model for development
# all-MiniLM-L6-v2 creates 384-dimensional embeddings
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

_model = None

def get_model() -> SentenceTransformer:
    """Lazy load the sentence transformer model."""
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate vector embeddings for a list of text chunks.
    
    Args:
        texts: A list of text strings to embed.
        
    Returns:
        A list of embedding vectors (each vector is a list of floats).
    """
    if not texts:
        return []
    
    model = get_model()
    # encode returns a numpy array, we convert to list for easier handling
    # normalising the embeddings is good practice for cosine similarity (which FAISS inner product matches if normalized)
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()

def generate_embedding(text: str) -> List[float]:
    """Generate a vector embedding for a single text string."""
    return generate_embeddings([text])[0]
