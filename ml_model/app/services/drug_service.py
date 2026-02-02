# app/services/drug_service.py
"""
Service médicaments utilisant le RAG léger
"""
from typing import List, Dict, Optional
import logging
from app.llm.llm_engine import llm_engine
from app.llm.rag_light import light_rag  # ⬅️ CHANGÉ: rag_light au lieu de rag
from app.database.dailymed_loader import dailymed_loader
from app.config import config

logger = logging.getLogger(__name__)

class DrugService:
    """Service de gestion des médicaments avec RAG léger"""
    
    def __init__(self):
        self.llm = llm_engine
        self.rag = light_rag  # ⬅️ Utilise le RAG léger
        self.loader = dailymed_loader
    
    async def get_drug_information(self, drug_name: str, language: str = "fr") -> Dict:
        """
        Obtient des informations sur un médicament
        Utilise le RAG léger avec OpenAI embeddings
        """
        logger.info(f" Traitement: {drug_name} (langue: {language})")
        
        # 1. Obtenir le contexte via RAG léger
        context = await self.rag.get_drug_context(drug_name)
        
        # 2. Si contexte insuffisant, chercher dans DailyMed
        if "Aucune information locale" in context or not context:
            logger.info("Recherche dans DailyMed API...")
            
            # Recherche dans DailyMed
            search_results = self.loader.search_drugs(drug_name, limit=2)
            
            if search_results:
                # Préparer les données pour le RAG
                documents = []
                for result in search_results:
                    doc_text = f"""
                    Médicament: {result.get('name', '')}
                    Type: {result.get('type', '')}
                    Principe actif: {', '.join(result.get('active_ingredients', []))}
                    Voie d'administration: {result.get('route', '')}
                    """
                    
                    documents.append({
                        "text": doc_text,
                        "metadata": {
                            "source": "DailyMed",
                            "drug_name": result.get('name', ''),
                            "timestamp": "2024-01-15"
                        }
                    })
                
                # Ajouter au RAG pour les prochaines fois
                await self.rag.add_documents(documents)
                
                # Mettre à jour le contexte
                context = await self.rag.get_drug_context(drug_name)
        
        # 3. Formater avec LLM
        prompt = config.PROMPT_TEMPLATES["drug_info"].format(
            context=context,
            question=drug_name,
            language=language
        )
        
        response = await self.llm.generate_response(prompt)
        
        return {
            "drug_name": drug_name,
            "information": response,
            "context_used": bool(context and "Aucune information" not in context),
            "language": language,
            "source": "DailyMed FDA + OpenAI RAG",
            "rag_mode": "light",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    
    # ... (autres méthodes restent similaires)