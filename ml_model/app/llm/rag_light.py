# app/llm/rag_light.py - NOUVELLE VERSION
"""
Système RAG avec nouvelle API ChromaDB (v0.4+)
"""
import chromadb
from typing import List, Dict, Optional
import logging
from app.config import config

logger = logging.getLogger(__name__)

class LightRAGSystem:
    """
    Système RAG compatible avec ChromaDB v0.4+
    """
    
    def __init__(self):
        self.client = None
        self.collection = None
        self._init_rag()
    
    def _init_rag(self):
        """Initialise avec la NOUVELLE API ChromaDB"""
        try:
            # NOUVELLE SYNTAXE - PersistentClient au lieu de Client
            self.client = chromadb.PersistentClient(
                path=config.CHROMA_PERSIST_DIR
            )
            
            # Créer ou récupérer la collection
            self.collection = self.client.get_or_create_collection(
                name="pharma_drugs_v2",
                metadata={
                    "description": "Base médicaments Pharma Assistant",
                    "version": "2.0",
                    "rag_mode": "light"
                }
            )
            
            logger.info(f"✅ RAG v2 initialisé - Documents: {self.collection.count()}")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation RAG: {str(e)}")
            # Mode dégradé
            self.collection = None
    
    async def add_documents(self, documents: List[Dict]):
        """
        Ajoute des documents (version simplifiée)
        """
        if not self.collection:
            logger.warning("RAG non initialisé - skip add_documents")
            return
        
        if not documents:
            return
        
        try:
            # Préparer les données
            ids = []
            texts = []
            metadatas = []
            
            for i, doc in enumerate(documents):
                doc_id = f"doc_{i}_{hash(doc.get('text', '')) % 10000}"
                ids.append(doc_id)
                texts.append(doc.get("text", ""))
                metadatas.append(doc.get("metadata", {}))
            
            # Ajouter avec embeddings par défaut de ChromaDB
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"📚 {len(documents)} documents ajoutés")
            
        except Exception as e:
            logger.error(f"❌ Erreur ajout: {str(e)}")
    
    async def search_similar(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Recherche simplifiée
        """
        if not self.collection or self.collection.count() == 0:
            return []
        
        try:
            # ChromaDB utilise ses embeddings par défaut
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            formatted = []
            if results and results.get("documents"):
                for i in range(len(results["documents"][0])):
                    formatted.append({
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "distance": results["distances"][0][i] if results.get("distances") else 0,
                        "relevance": 1.0 - (results["distances"][0][i] / 2.0 if results.get("distances") else 0)
                    })
            
            return formatted
            
        except Exception as e:
            logger.error(f"❌ Recherche échouée: {str(e)}")
            return []
    
    async def get_drug_context(self, drug_name: str, max_context: int = 3) -> str:
        """
        Récupère le contexte pour un médicament
        """
        results = await self.search_similar(drug_name, n_results=max_context)
        
        if not results:
            return f"Aucune information locale pour: {drug_name}"
        
        # Filtrer par pertinence
        good_results = [r for r in results if r.get("relevance", 0) > 0.3]
        
        if not good_results:
            return f"Informations locales peu pertinentes pour: {drug_name}"
        
        # Construire le contexte
        context_parts = []
        for i, result in enumerate(good_results[:max_context]):
            context_parts.append(
                f"[Source {i+1}]\n{result['text'][:500]}..."
            )
        
        return "\n\n---\n\n".join(context_parts)
    
    def is_ready(self) -> bool:
        """Vérifie si le RAG est prêt"""
        return self.collection is not None

# Instance globale
light_rag = LightRAGSystem()