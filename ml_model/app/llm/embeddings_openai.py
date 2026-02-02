# app/llm/embeddings_openai.py
"""
Embeddings via OpenAI API - Léger, rapide, pas de PyTorch
"""
import openai
import numpy as np
from typing import List, Optional
import logging
from app.config import config
import asyncio

logger = logging.getLogger(__name__)

class OpenAIEmbeddings:
    """
    Service d'embeddings utilisant l'API OpenAI
    Plus léger que sentence-transformers, meilleure qualité
    """
    
    def __init__(self):
        openai.api_key = config.OPENAI_API_KEY
        self.model = "text-embedding-3-small"  # Léger et rapide
        # Alternative: "text-embedding-ada-002"
    
    async def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Génère un embedding pour un texte
        
        Args:
            text: Texte à encoder
            
        Returns:
            Liste de floats (embedding) ou None en cas d'erreur
        """
        try:
            if not text or not text.strip():
                return None
                
            response = await openai.Embedding.acreate(
                model=self.model,
                input=text,
                encoding_format="float"
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Erreur embedding OpenAI: {str(e)}")
            return None
    
    async def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Génère des embeddings pour plusieurs textes
        
        Args:
            texts: Liste de textes
            
        Returns:
            Liste d'embeddings
        """
        if not texts:
            return []
        
        # OpenAI limite à ~2048 tokens par requête, donc on batch
        batch_size = 16  # Conservatif
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = await openai.Embedding.acreate(
                    model=self.model,
                    input=batch,
                    encoding_format="float"
                )
                
                for item in response.data:
                    results.append(item.embedding)
                    
            except Exception as e:
                logger.error(f"Erreur batch embedding: {str(e)}")
                # Ajouter None pour les textes échoués
                results.extend([None] * len(batch))
                
            # Petite pause pour éviter rate limiting
            await asyncio.sleep(0.1)
        
        return results
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calcule la similarité cosinus entre deux vecteurs
        """
        if not vec1 or not vec2:
            return 0.0
        
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)

# Instance globale
embeddings_service = OpenAIEmbeddings()