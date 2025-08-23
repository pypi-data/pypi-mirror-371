"""
Faiss vector store implementation
"""

import numpy as np
import pickle
import os
from typing import List, Tuple

from .base import BaseVectorStore


class FaissVectorStore(BaseVectorStore):
    def __init__(self, dimension: int = 384):
        """Initialize Faiss vector store"""
        super().__init__(dimension)
        
        try:
            import faiss
            self.faiss = faiss
        except ImportError:
            raise ImportError("faiss-cpu required. Install with: pip install faiss-cpu")
        
        self.index = self.faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
    
    def add_vectors(self, embeddings: List[List[float]], texts: List[str]):
        """Add vectors and corresponding texts to the store"""
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Normalize for cosine similarity
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        embeddings_array = embeddings_array / (norms + 1e-8)  # Add small epsilon to avoid division by zero
        
        self.index.add(embeddings_array)
        self.texts.extend(texts)
        self.embeddings.extend(embeddings)
    
    def search(self, query_embedding: List[float], k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar vectors"""
        if self.index.ntotal == 0:
            return []
        
        query_array = np.array([query_embedding], dtype=np.float32)
        
        # Normalize query
        norm = np.linalg.norm(query_array)
        if norm > 0:
            query_array = query_array / norm
        
        scores, indices = self.index.search(query_array, min(k, self.index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:  # Valid index
                results.append((self.texts[idx], float(score)))
        
        return results
    
    def save(self, filepath: str):
        """Save the vector store to disk"""
        data = {
            'texts': self.texts,
            'embeddings': self.embeddings,
            'dimension': self.dimension
        }
        
        # Save index
        self.faiss.write_index(self.index, f"{filepath}.index")
        
        # Save metadata
        with open(f"{filepath}.pkl", 'wb') as f:
            pickle.dump(data, f)
    
    def load(self, filepath: str):
        """Load the vector store from disk"""
        # Load index
        if os.path.exists(f"{filepath}.index"):
            self.index = self.faiss.read_index(f"{filepath}.index")
        
        # Load metadata
        if os.path.exists(f"{filepath}.pkl"):
            with open(f"{filepath}.pkl", 'rb') as f:
                data = pickle.load(f)
                self.texts = data['texts']
                self.embeddings = data['embeddings']
                self.dimension = data['dimension']
    
    def clear(self):
        """Clear all stored vectors and texts"""
        super().clear()
        self.index = self.faiss.IndexFlatIP(self.dimension)