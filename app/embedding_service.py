import logging
from sentence_transformers import SentenceTransformer
from typing import List
import os

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        """Initialize with smaller, faster embedding model"""
        try:
            logger.info("🔧 Initializing all-MiniLM-L6-v2 embedding service...")
            
            # Use smaller, faster model - perfect for deployment
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            
            # Load model - much smaller download (~90MB vs 400MB)
            logger.info(f"📥 Loading model: {model_name}")
            self.model = SentenceTransformer(model_name)
            
            logger.info("✅ MiniLM embedding service initialized successfully")
            logger.info(f"📊 Model dimension: {self.model.get_sentence_embedding_dimension()}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize embedding service: {str(e)}")
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            logger.debug(f"🔄 Generating embedding for text: {text[:100]}...")
            
            # Generate embedding using MiniLM model
            embedding = self.model.encode(text, normalize_embeddings=True)
            
            # Convert numpy array to list
            embedding_list = embedding.tolist()
            
            logger.debug(f"✅ Generated embedding of dimension: {len(embedding_list)}")
            return embedding_list
            
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {str(e)}")
            raise

    async def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for search query"""
        try:
            logger.debug(f"🔍 Generating query embedding for: {query}")
            
            # No special prefix needed for MiniLM - it works well as-is
            embedding = self.model.encode(query, normalize_embeddings=True)
            embedding_list = embedding.tolist()
            
            logger.debug(f"✅ Generated query embedding of dimension: {len(embedding_list)}")
            return embedding_list
            
        except Exception as e:
            logger.error(f"❌ Failed to generate query embedding: {str(e)}")
            raise

    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts at once (for faster processing)"""
        try:
            logger.info(f"🔄 Generating batch embeddings for {len(texts)} texts")
            
            # Batch encode for faster processing with progress bar
            embeddings = self.model.encode(
                texts, 
                normalize_embeddings=True, 
                batch_size=32,  # Larger batch size since model is smaller
                show_progress_bar=True,
                convert_to_tensor=False  # Return numpy arrays
            )
            
            # Convert to list of lists
            embeddings_list = [emb.tolist() for emb in embeddings]
            
            logger.info(f"✅ Generated {len(embeddings_list)} embeddings (dimension: {len(embeddings_list[0])})")
            return embeddings_list
            
        except Exception as e:
            logger.error(f"❌ Failed to generate batch embeddings: {str(e)}")
            raise