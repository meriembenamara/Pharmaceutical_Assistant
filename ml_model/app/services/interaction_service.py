# app/services/interaction_service.py
import logging

logger = logging.getLogger(__name__)

class InteractionService:
    """Service simplifié d'interactions"""
    
    def __init__(self):
        pass
    
    async def check_drug_interactions(self, drugs: List[str], language: str = "fr") -> Dict:
        logger.info(f"Analyse interactions: {drugs}")
        
        return {
            "drugs": drugs,
            "analysis": f"Analyse des interactions entre {len(drugs)} médicaments. Service en développement.",
            "has_interactions": False,
            "severity": "low",
            "language": language
        }

# Instance GLOBALE - IMPORTANT !
interaction_service = InteractionService()