import logging
import os
from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np

from app.core.config import settings
from app.services.embeddings import EMBEDDING_DIMENSION

logger = logging.getLogger(__name__)

# Ensure the vector store directory exists
os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)
FAISS_INDEX_PATH = Path(settings.VECTOR_STORE_DIR) / "index.faiss"
# We also need to map FAISS integer IDs back to our DocumentChunk UUIDs
# FAISS only natively stores integer IDs.
ID_MAP_PATH = Path(settings.VECTOR_STORE_DIR) / "id_map.json"

_index = None
_id_mapping = {}  # Maps FAISS int ID to DocumentChunk UUID str
_next_faiss_id = 0

def _load_index():
    """Load the FAISS index and ID mapping from disk, or create a new one."""
    global _index, _id_mapping, _next_faiss_id
    
    if _index is not None:
        return
        
    if FAISS_INDEX_PATH.exists():
        logger.info(f"Loading FAISS index from {FAISS_INDEX_PATH}")
        _index = faiss.read_index(str(FAISS_INDEX_PATH))
        
        # Load ID mapping
        import json
        if ID_MAP_PATH.exists():
            with open(ID_MAP_PATH, "r") as f:
                loaded_map = json.load(f)
                # JSON keys are always strings, convert back to int
                _id_mapping = {int(k): v for k, v in loaded_map.items()}
                _next_faiss_id = max(_id_mapping.keys()) + 1 if _id_mapping else 0
    else:
        logger.info(f"Creating new FAISS index with dimension {EMBEDDING_DIMENSION}")
        # IndexFlatIP uses Inner Product, which is equivalent to Cosine Similarity 
        # when vectors are normalized (which we do in embeddings.py)
        # We use IndexIDMap to allow us to specify custom integer IDs
        base_index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)
        _index = faiss.IndexIDMap(base_index)
        _id_mapping = {}
        _next_faiss_id = 0

def _save_index():
    """Save the FAISS index and ID mapping to disk."""
    global _index, _id_mapping
    if _index is not None:
        faiss.write_index(_index, str(FAISS_INDEX_PATH))
        
        import json
        with open(ID_MAP_PATH, "w") as f:
            json.dump(_id_mapping, f)

def add_vectors(vectors: List[List[float]], chunk_ids: List[str]) -> None:
    """Add embedding vectors to the FAISS index.
    
    Args:
        vectors: A list of embedding vectors.
        chunk_ids: A list of corresponding DocumentChunk UUIDs (as strings).
    """
    if not vectors or not chunk_ids or len(vectors) != len(chunk_ids):
        raise ValueError("vectors and chunk_ids must be non-empty and of the same length")
        
    _load_index()
    global _index, _id_mapping, _next_faiss_id
    
    # Assign new integer IDs for FAISS
    faiss_ids = []
    for chunk_id in chunk_ids:
        _id_mapping[_next_faiss_id] = str(chunk_id)
        faiss_ids.append(_next_faiss_id)
        _next_faiss_id += 1
        
    # Convert to numpy arrays
    np_vectors = np.array(vectors).astype('float32')
    np_ids = np.array(faiss_ids).astype('int64')
    
    _index.add_with_ids(np_vectors, np_ids)
    _save_index()
    
    logger.info(f"Added {len(vectors)} vectors to FAISS index. Total vectors: {_index.ntotal}")

def search_vectors(query_vector: List[float], k: int = 5) -> List[Tuple[str, float]]:
    """Search for the most similar vectors in the FAISS index.
    
    Args:
        query_vector: The embedded query vector.
        k: The number of results to return.
        
    Returns:
        A list of tuples: (chunk_id_str, similarity_score)
    """
    _load_index()
    global _index, _id_mapping
    
    if _index is None or _index.ntotal == 0:
        return []
        
    # Reshape query to 2D array for FAISS
    np_query = np.array([query_vector]).astype('float32')
    
    # Search
    distances, indices = _index.search(np_query, k)
    
    results = []
    for i in range(len(indices[0])):
        faiss_id = int(indices[0][i])
        score = float(distances[0][i])
        
        # FAISS returns -1 for empty/missing results
        if faiss_id != -1 and faiss_id in _id_mapping:
            chunk_id = _id_mapping[faiss_id]
            results.append((chunk_id, score))
            
    return results

def delete_vectors(chunk_ids: List[str]) -> None:
    """Delete vectors from the FAISS index by their chunk UUIDs."""
    _load_index()
    global _index, _id_mapping
    
    if _index is None or _index.ntotal == 0 or not chunk_ids:
        return
        
    # Find the corresponding FAISS integer IDs
    chunk_ids_set = set(str(cid) for cid in chunk_ids)
    faiss_ids_to_remove = []
    
    for faiss_id, chunk_id in list(_id_mapping.items()):
        if chunk_id in chunk_ids_set:
            faiss_ids_to_remove.append(faiss_id)
            del _id_mapping[faiss_id]
            
    if faiss_ids_to_remove:
        np_ids = np.array(faiss_ids_to_remove).astype('int64')
        _index.remove_ids(np_ids)
        _save_index()
        logger.info(f"Removed {len(faiss_ids_to_remove)} vectors from FAISS index. Total remaining: {_index.ntotal}")
