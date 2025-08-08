import numpy as np
import logging
from typing import List, Dict, Any
from .models import DocumentChunk

logger = logging.getLogger(__name__)

class InMemoryVectorStore:
    def __init__(self):
        self.documents: List[DocumentChunk] = []
        
    def add_documents(self, chunks: List[DocumentChunk]):
        """Store chunks in memory"""
        logger.info(f"💾 Adding {len(chunks)} chunks to in-memory store")
        self.documents = chunks  # Replace for single-request processing
        logger.info(f"✅ Stored {len(self.documents)} chunks in memory")
        
    def search_similar(self, query_embedding: List[float], top_k: int = 15) -> List[Dict]:
        """Search for similar documents using cosine similarity"""
        if not self.documents:
            logger.warning("⚠️ No documents in memory store")
            return []
        
        logger.debug(f"🔍 Searching for {top_k} similar documents from {len(self.documents)} chunks")
        
        query_vector = np.array(query_embedding)
        similarities = []
        
        for i, doc in enumerate(self.documents):
            if not doc.embedding:
                continue
                
            doc_vector = np.array(doc.embedding)
            
            # Compute cosine similarity
            dot_product = np.dot(query_vector, doc_vector)
            norms = np.linalg.norm(query_vector) * np.linalg.norm(doc_vector)
            
            if norms > 0:
                similarity = dot_product / norms
            else:
                similarity = 0.0
            
            similarities.append({
                'text': doc.text,
                'metadata': doc.metadata,
                'similarity': float(similarity),
                'index': i
            })
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Return top_k results
        results = similarities[:top_k]
        
        logger.debug(f"✅ Found {len(results)} similar documents, top similarity: {results[0]['similarity']:.3f}")
        
        return results
    
    def clear(self):
        """Clear all documents from memory"""
        self.documents.clear()
        logger.info("🗑️ Cleared all documents from memory")
    
    def get_document_count(self) -> int:
        """Get number of documents in store"""
        return len(self.documents)