from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List, Dict, Optional
import logging

from app.config import config
from app.services.drug_service import DrugService
from app.services.interaction_service import InteractionService

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de l'application
app = FastAPI(
    title="Pharma Assistant API",
    description="API intelligente d'assistance pharmaceutique avec DailyMed",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation des services
drug_service = DrugService()
interaction_service = InteractionService()

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    logger.info(" Démarrage du Pharma Assistant API")
    logger.info(f"Modèle LLM: {config.OPENAI_MODEL}")
    logger.info(f" Langues supportées: {config.SUPPORTED_LANGUAGES}")

@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "service": "Pharma Assistant API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": [
            "/api/drug-info",
            "/api/check-interactions",
            "/api/search-drugs",
            "/api/ask-question"
        ]
    }

@app.get("/api/health")
async def health_check():
    """Vérification de santé"""
    return {
        "status": "healthy",
        "model": config.OPENAI_MODEL,
        "environment": config.APP_ENV
    }

@app.post("/api/drug-info")
async def get_drug_info(
    drug_name: str,
    language: str = config.DEFAULT_LANGUAGE
):
    """
    Obtient des informations sur un médicament
    
    Args:
        drug_name: Nom du médicament
        language: Langue de réponse (fr/en)
    """
    try:
        if language not in config.SUPPORTED_LANGUAGES:
            language = config.DEFAULT_LANGUAGE
            
        logger.info(f"Recherche info médicament: {drug_name} ({language})")
        
        result = await drug_service.get_drug_information(
            drug_name=drug_name,
            language=language
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"❌ Erreur: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des informations: {str(e)}"
        )

@app.post("/api/check-interactions")
async def check_interactions(
    drugs: List[str],
    language: str = config.DEFAULT_LANGUAGE
):
    """
    Vérifie les interactions entre plusieurs médicaments
    
    Args:
        drugs: Liste des noms de médicaments
        language: Langue de réponse
    """
    try:
        if len(drugs) < 2:
            raise HTTPException(
                status_code=400,
                detail="Au moins 2 médicaments sont requis pour vérifier les interactions"
            )
        
        if language not in config.SUPPORTED_LANGUAGES:
            language = config.DEFAULT_LANGUAGE
            
        logger.info(f"⚗️  Vérification interactions: {drugs} ({language})")
        
        result = await interaction_service.check_drug_interactions(
            drugs=drugs,
            language=language
        )
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la vérification des interactions: {str(e)}"
        )

@app.get("/api/search-drugs")
async def search_drugs(
    query: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    language: str = config.DEFAULT_LANGUAGE
):
    """
    Recherche de médicaments par nom
    
    Args:
        query: Terme de recherche
        limit: Nombre maximum de résultats
        language: Langue de réponse
    """
    try:
        logger.info(f"🔎 Recherche médicaments: '{query}'")
        
        results = await drug_service.search_drugs(
            query=query,
            limit=limit,
            language=language
        )
        
        return {
            "query": query,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la recherche: {str(e)}"
        )

@app.post("/api/ask-question")
async def ask_question(
    question: str,
    context: Optional[Dict] = None,
    language: str = config.DEFAULT_LANGUAGE
):
    """
    Pose une question générale sur les médicaments
    
    Args:
        question: Question à poser
        context: Contexte supplémentaire
        language: Langue de réponse
    """
    try:
        if not question or len(question.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="La question doit contenir au moins 3 caractères"
            )
            
        logger.info(f"❓ Question: '{question[:50]}...' ({language})")
        
        result = await drug_service.answer_question(
            question=question,
            context=context or {},
            language=language
        )
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement de la question: {str(e)}"
        )

@app.get("/api/status")
async def get_status():
    """Statut du système"""
    return {
        "service": "Pharma Assistant ML API",
        "llm_model": config.OPENAI_MODEL,
        "environment": config.APP_ENV,
        "dailymed_connected": drug_service.is_dailymed_available(),
        "vector_db_ready": drug_service.is_vector_db_ready(),
        "supported_languages": config.SUPPORTED_LANGUAGES
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=config.DEBUG
    )