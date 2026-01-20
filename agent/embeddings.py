from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings using sentence-transformers"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        """
        Initialize embedding model
        
        Args:
            model_name: HuggingFace model name (384-dim output)
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = 384
        logger.info(f"✅ Model loaded. Embedding dimension: {self.dimension}")
    
    def encode(self, texts: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for text(s)
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for processing
            
        Returns:
            Numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 100,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def encode_query(self, query: str) -> List[float]:
        """
        Encode a single query text
        
        Args:
            query: Query text
            
        Returns:
            Embedding as list of floats
        """
        embedding = self.model.encode([query], convert_to_numpy=True)[0]
        return embedding.tolist()
    
    def encode_documents(self, documents: List[str]) -> List[List[float]]:
        """
        Encode multiple documents
        
        Args:
            documents: List of document texts
            
        Returns:
            List of embeddings
        """
        embeddings = self.model.encode(
            documents,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings.tolist()