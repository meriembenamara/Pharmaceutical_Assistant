#main.py - API FastAPI principale
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Optional

from app.config import settings
from app.llm.llm_engine import LLMEngine
from app.llm.rag import RAGSystem
from app.database.dailymed_loader import DrugDatabase

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variables globales pour les ressources partagées
llm_engine = None
rag_system = None
drug_db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion du cycle de vie de l'application
    Initialise les ressources au démarrage, les nettoie à l'arrêt
    """
    global llm_engine, rag_system, drug_db
    
    # Initialisation au démarrage
    logger.info("Initialisation des services AI...")
    
    try:
        # Initialiser la base de données des médicaments
        drug_db = DrugDatabase()
        await drug_db.initialize()
        
        # Initialiser le système RAG
        rag_system = RAGSystem(drug_db)
        
        # Initialiser le moteur LLM
        llm_engine = LLMEngine(rag_system)
        
        logger.info("✅ Services AI initialisés avec succès")
        
    except Exception as e:
        logger.error(f"❌ Erreur d'initialisation: {e}")
        raise
    
    yield  # L'application fonctionne
    
    # Nettoyage à l'arrêt
    logger.info("Arrêt des services AI...")
    if drug_db:
        await drug_db.close()

# Création de l'application FastAPI
app = FastAPI(
    title="Pharma AI Assistant API",
    description="Microservice d'IA pour l'assistant pharmaceutique",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dépendance pour vérifier l'API key
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key or x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Clé API invalide")
    return x_api_key

@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé du service"""
    return {
        "status": "healthy",
        "service": "pharma-ai-service",
        "version": "1.0.0",
        "llm_ready": llm_engine is not None
    }

@app.post("/api/llm/ask", dependencies=[Depends(verify_api_key)])
async def ask_llm(query: dict):
    """
    Endpoint principal pour les questions médicales
    """
    try:
        question = query.get("query", "")
        context = query.get("context", {})
        
        if not question:
            raise HTTPException(status_code=400, detail="Question requise")
        
        # Traiter la requête via le moteur LLM
        response = await llm_engine.process_query(
            question=question,
            context=context
        )
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement LLM: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/drugs/search", dependencies=[Depends(verify_api_key)])
async def search_drugs(q: str, limit: int = 10):
    """
    Recherche sémantique de médicaments
    """
    try:
        results = await drug_db.search_drugs(q, limit)
        return {"results": results}
    except Exception as e:
        logger.error(f"Erreur recherche médicaments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/drugs/interactions", dependencies=[Depends(verify_api_key)])
async def check_interactions(data: dict):
    """
    Vérifie les interactions médicamenteuses
    """
    try:
        drugs = data.get("drugs", [])
        patient_info = data.get("patient_info", {})
        
        if len(drugs) < 2:
            raise HTTPException(status_code=400, detail="Au moins 2 médicaments requis")
        
        interactions = await drug_db.check_interactions(drugs, patient_info)
        return {"interactions": interactions}
        
    except Exception as e:
        logger.error(f"Erreur vérification interactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Handler d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erreur non gérée: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur"}
    )