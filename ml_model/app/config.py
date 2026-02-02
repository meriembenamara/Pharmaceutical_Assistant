import os
from dotenv import load_dotenv
from typing import Dict, List

# Charger les variables d'environnement
load_dotenv()

class Config:
    """Configuration de l'application"""
    
    # Application
    APP_PORT = int(os.getenv("APP_PORT", 8000))
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    
    # DailyMed
    DAILYMED_API_URL = os.getenv("DAILYMED_API_URL", "https://dailymed.nlm.nih.gov/dailymed/services/v2")
    DAILYMED_CACHE_DIR = os.getenv("DAILYMED_CACHE_DIR", "./data/dailymed")
    
    # Vector DB
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.7))
    
    # Langues
    SUPPORTED_LANGUAGES = os.getenv("SUPPORTED_LANGUAGES", "fr,en").split(",")
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "fr")
    
    # Prompt templates
    PROMPT_TEMPLATES = {
        "drug_info": """
        Tu es un assistant pharmaceutique expert. Fournis des informations claires et précises sur le médicament.
        
        Informations disponibles:
        {context}
        
        Question: {question}
        
        Réponds en {language} avec:
        1. Nom commercial et générique
        2. Posologie standard (adultes/enfants)
        3. Précautions générales
        4. Effets secondaires communs
        5. Mode de conservation
        
        IMPORTANT: Mentionne toujours "Consultez un professionnel de santé" à la fin.
        """,
        
        "interaction_check": """
        Tu es un expert en interactions médicamenteuses. Analyse ces médicaments:
        
        Médicaments: {drugs}
        
        Informations disponibles:
        {context}
        
        Langue: {language}
        
        Fournis une analyse avec:
        1. Niveau de risque (Faible/Moyen/Élevé)
        2. Interactions détectées
        3. Recommandations
        4. Alternatives possibles
        
        Si pas d'infos, dis-le clairement.
        """,
        
        "general_question": """
        Réponds à la question pharmaceutique suivante en {language}:
        
        Contexte: {context}
        Question: {question}
        
        Réponse concise et professionnelle.
        """
    }
    
    @classmethod
    def validate_config(cls):
        """Valide la configuration"""
        if not cls.OPENAI_API_KEY:
            print(" Avertissement: OPENAI_API_KEY non configurée")
        
        # Créer les dossiers nécessaires
        os.makedirs(cls.DAILYMED_CACHE_DIR, exist_ok=True)
        os.makedirs(cls.CHROMA_PERSIST_DIR, exist_ok=True)
        
        print(f"Configuration chargée - Environnement: {cls.APP_ENV}")

config = Config()
config.validate_config()