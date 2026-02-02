# app/llm/llm_engine.py - VERSION CORRIGÉE
import openai
from typing import List, Dict, Optional
import logging
from app.config import config

logger = logging.getLogger(__name__)

class LLMEngine:
    """Moteur LLM pour interagir avec OpenAI"""
    
    def __init__(self):
        # NOUVELLE SYNTAXE OpenAI v1.0+
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
        
    async def generate_response(
        self, 
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> str:
        """
        Génère une réponse à partir d'un prompt
        """
        try:
            if not config.OPENAI_API_KEY:
                return "Service LLM non configuré. Vérifiez la clé API."
            
            # NOUVELLE SYNTAXE OpenAI v1.0+
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Tu es un assistant pharmaceutique expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except openai.AuthenticationError:  # ⬅️ SANS .error !
            logger.error("❌ Erreur d'authentification OpenAI")
            return "Erreur d'authentification. Vérifiez la clé API OpenAI."
            
        except openai.RateLimitError:  # ⬅️ SANS .error !
            logger.error("⚠️  Limite de taux OpenAI atteinte")
            return "Limite de requêtes atteinte. Réessayez plus tard."
            
        except openai.APIError:  # ⬅️ SANS .error !
            logger.error("❌ Erreur API OpenAI")
            return "Erreur temporaire du service d'intelligence artificielle."
            
        except Exception as e:
            logger.error(f"❌ Erreur OpenAI: {str(e)}")
            return f"Erreur lors de la génération de la réponse: {str(e)}"
    
    async def format_drug_info(
        self, 
        context: str, 
        drug_name: str, 
        language: str = "fr"
    ) -> Dict:
        """
        Formate les informations sur un médicament
        """
        prompt = config.PROMPT_TEMPLATES["drug_info"].format(
            context=context,
            question=drug_name,
            language=language
        )
        
        response = await self.generate_response(prompt)
        
        return {
            "drug_name": drug_name,
            "information": response,
            "context_used": bool(context.strip()),
            "language": language,
            "source": "DailyMed FDA + LLM Analysis"
        }
    
    async def analyze_interactions(
        self,
        context: str,
        drugs: List[str],
        language: str = "fr"
    ) -> Dict:
        """
        Analyse les interactions médicamenteuses
        """
        prompt = config.PROMPT_TEMPLATES["interaction_check"].format(
            context=context,
            drugs=", ".join(drugs),
            language=language
        )
        
        response = await self.generate_response(prompt)
        
        return {
            "drugs": drugs,
            "analysis": response,
            "has_interactions": "interaction" in response.lower() or "risque" in response.lower(),
            "language": language,
            "disclaimer": "Cette analyse est générée par IA. Consultez un pharmacien pour confirmation."
        }

# Instance globale
llm_engine = LLMEngine()