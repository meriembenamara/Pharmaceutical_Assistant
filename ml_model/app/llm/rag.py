#rag.py : Système RAG
import chromadb
from chromadb.config import Settings
from typing import List, Dict
import logging
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class RAGSystem:
    """
    Système RAG (Retrieval-Augmented Generation)
    Pour la recherche sémantique dans la base de connaissances
    """
    
    def __init__(self, drug_database):
        self.drug_db = drug_database
        
        # Initialiser le modèle d'embeddings
        logger.info("Chargement du modèle d'embeddings...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialiser la base vectorielle
        self._init_vector_store()
    
    def _init_vector_store(self):
        """Initialise la base de données vectorielle"""
        try:
            self.chroma_client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="./chroma_db"
            ))
            
            # Créer ou récupérer la collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="pharma_documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("✅ Base vectorielle initialisée")
            
        except Exception as e:
            logger.error(f"Erreur d'initialisation vector store: {e}")
            raise
    
    async def retrieve_relevant_documents(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Recherche les documents les plus pertinents pour une requête
        """
        try:
            # Générer l'embedding de la requête
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Recherche dans la base vectorielle
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )
            
            # Formater les résultats
            documents = []
            for i in range(len(results['ids'][0])):
                doc = {
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "score": 1 - results['distances'][0][i],  # Convertir distance en score
                    "source": "vector_db"
                }
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} documents for query")
            return documents
            
        except Exception as e:
            logger.error(f"Erreur dans retrieve_relevant_documents: {e}")
            # Fallback: recherche textuelle simple
            return await self._fallback_search(query, limit)
    
    async def _fallback_search(self, query: str, limit: int) -> List[Dict]:
        """Recherche de secours si la base vectorielle échoue"""
        logger.warning("Utilisation de la recherche de secours")
        
        # Recherche simple dans la base de données
        try:
            drugs = await self.drug_db.search_drugs(query, limit)
            
            documents = []
            for drug in drugs:
                doc = {
                    "id": drug.get("id", ""),
                    "content": f"{drug.get('name', '')} - {drug.get('description', '')}",
                    "metadata": drug,
                    "score": 0.5,  # Score par défaut
                    "source": "drug_database_fallback"
                }
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Erreur recherche de secours: {e}")
            return []
    
    async def add_documents(self, documents: List[Dict]):
        """
        Ajoute des documents à la base vectorielle
        """
        try:
            ids = []
            texts = []
            metadatas = []
            embeddings = []
            
            for i, doc in enumerate(documents):
                doc_id = f"doc_{i}_{hash(doc['content'])}"
                ids.append(doc_id)
                texts.append(doc['content'])
                metadatas.append(doc.get('metadata', {}))
                
                # Générer l'embedding
                embedding = self.embedding_model.encode(doc['content']).tolist()
                embeddings.append(embedding)
            
            # Ajouter à la collection
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas,
                embeddings=embeddings
            )
            
            logger.info(f"Ajouté {len(documents)} documents à la base vectorielle")
            
        except Exception as e:
            logger.error(f"Erreur ajout documents: {e}")
            raise
    
    async def get_document_count(self) -> int:
        """Retourne le nombre de documents dans la collection"""
        try:
            return self.collection.count()
        except:
            return 0
