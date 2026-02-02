import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
import logging
from app.config import config

logger = logging.getLogger(__name__)

class RAGSystem:
    """Système RAG (Retrieval Augmented Generation) pour DailyMed"""
    
    def __init__(self):
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self._initialize()
    
    def _initialize(self):
        """Initialise le système RAG"""
        try:
            # Initialiser ChromaDB
            self.chroma_client = chromadb.Client(Settings(
                persist_directory=config.CHROMA_PERSIST_DIR,
                chroma_db_impl="duckdb+parquet"
            ))
            
            # Charger ou créer la collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="dailymed_drugs",
                metadata={"description": "Base de données des médicaments DailyMed"}
            )
            
            logger.info(f"✅ RAG System initialisé - {self.collection.count()} documents")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation RAG: {str(e)}")
            self.collection = None
    
    def add_documents(self, documents: List[Dict]):
        """
        Ajoute des documents à la base vectorielle
        
        Args:
            documents: Liste de documents avec 'id', 'text', 'metadata'
        """
        if not self.collection:
            logger.error("Collection ChromaDB non initialisée")
            return
        
        try:
            ids = [doc["id"] for doc in documents]
            texts = [doc["text"] for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]
            
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"📚 {len(documents)} documents ajoutés à la base vectorielle")
            
        except Exception as e:
            logger.error(f"❌ Erreur ajout documents: {str(e)}")
    
    def search_similar(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Recherche des documents similaires
        
        Args:
            query: Requête de recherche
            n_results: Nombre de résultats
        """
        if not self.collection or self.collection.count() == 0:
            logger.warning("Base vectorielle vide ou non initialisée")
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Formater les résultats
            formatted_results = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "text": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche: {str(e)}")
            return []
    
    def get_drug_context(self, drug_name: str, max_context: int = 3) -> str:
        """
        Obtient le contexte pour un médicament
        
        Args:
            drug_name: Nom du médicament
            max_context: Nombre maximum de contextes
        """
        # Recherche simple par nom
        results = self.search_similar(drug_name, n_results=max_context)
        
        # Concaténer les résultats
        context_parts = []
        for result in results:
            if result["distance"] < 1.0 - config.SIMILARITY_THRESHOLD:
                context_parts.append(result["text"])
        
        return "\n\n---\n\n".join(context_parts) if context_parts else "Aucune information trouvée dans la base de données."
    
    def is_ready(self) -> bool:
        """Vérifie si le système RAG est prêt"""
        return self.collection is not None and self.collection.count() > 0

# Instance globale
rag_system = RAGSystem()