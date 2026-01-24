#llm_engine.py : Moteur LLM
import openai
from typing import Dict, List, Optional
import json
from app.config import settings
from app.llm.rag import RAGSystem
import logging

logger = logging.getLogger(__name__)

class LLMEngine:
    """
    Classe principale pour interagir avec l'API OpenAI
    Gère la logique de prompt engineering et de réponse
    """
    
    def __init__(self, rag_system: RAGSystem):
        self.rag_system = rag_system
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL  # "gpt-4-turbo-preview" ou "gpt-3.5-turbo"
        
        # Templates de prompts pour différents types de questions
        self.prompt_templates = {
            "general_medical": """
            Tu es un assistant pharmaceutique expert. 
            Réponds à la question de l'utilisateur en te basant sur les informations fournies.
            
            INFORMATIONS CONTEXTUELLES:
            {context}
            
            QUESTION:
            {question}
            
            DIRECTIVES:
            1. Sois précis et factuel
            2. Mentionne tes sources quand c'est pertinent
            3. Si tu n'es pas sûr, dis-le clairement
            4. Formate ta réponse de manière lisible
            5. Ne propose jamais de diagnostic médical
            
            RÉPONSE:
            """,
            
            "drug_info": """
            Tu es un pharmacien expert. Fournis des informations sur le(s) médicament(s).
            
            DONNÉES DU MÉDICAMENT:
            {drug_data}
            
            QUESTION:
            {question}
            
            Inclus dans ta réponse:
            1. Nom commercial et générique
            2. Indications principales
            3. Posologie typique
            4. Contre-indications importantes
            5. Effets secondaires courants
            6. Interactions notables
            
            RÉPONSE:
            """
        }
    
    async def process_query(self, question: str, context: Dict) -> Dict:
        """
        Traite une question médicale en utilisant RAG + LLM
        """
        logger.info(f"Traitement question: {question[:100]}...")
        
        try:
            # 1. Recherche de documents pertinents via RAG
            relevant_docs = await self.rag_system.retrieve_relevant_documents(question)
            
            # 2. Déterminer le type de question
            query_type = self._classify_query(question)
            
            # 3. Construire le prompt contextuel
            prompt = self._build_prompt(question, relevant_docs, query_type)
            
            # 4. Appeler l'API OpenAI
            response = await self._call_llm(prompt, context)
            
            # 5. Structurer et valider la réponse
            structured_response = self._structure_response(
                question, response, relevant_docs, query_type
            )
            
            return structured_response
            
        except Exception as e:
            logger.error(f"Erreur dans process_query: {e}")
            raise
    
    async def _call_llm(self, prompt: str, context: Dict) -> str:
        """
        Appelle l'API OpenAI avec gestion d'erreurs
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Tu es un assistant pharmaceutique expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Bas pour plus de consistance
                max_tokens=1500,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            return response.choices[0].message.content
            
        except openai.APIError as e:
            logger.error(f"Erreur API OpenAI: {e}")
            raise Exception(f"Erreur de service LLM: {e}")
    
    def _classify_query(self, question: str) -> str:
        """
        Classifie le type de question pour utiliser le bon template
        """
        question_lower = question.lower()
        
        # Mots-clés pour la classification
        drug_keywords = ["médicament", "pilule", "comprimé", "posologie", "dose", "interaction"]
        side_effect_keywords = ["effet secondaire", "effet indésirable", "danger", "risque"]
        
        if any(keyword in question_lower for keyword in drug_keywords):
            return "drug_info"
        elif any(keyword in question_lower for keyword in side_effect_keywords):
            return "side_effects"
        else:
            return "general_medical"
    
    def _build_prompt(self, question: str, documents: List, query_type: str) -> str:
        """
        Construit le prompt contextuel pour le LLM
        """
        template = self.prompt_templates.get(query_type, self.prompt_templates["general_medical"])
        
        # Formater les documents pour le contexte
        context_text = "\n\n".join([
            f"Document {i+1}:\n{doc['content'][:500]}..."
            for i, doc in enumerate(documents[:5])  # Limiter à 5 documents
        ])
        
        return template.format(
            question=question,
            context=context_text,
            drug_data=json.dumps(documents[0], indent=2) if documents else "Aucune donnée spécifique"
        )
    
    def _structure_response(self, question: str, raw_response: str, 
                           sources: List, query_type: str) -> Dict:
        """
        Structure la réponse du LLM dans un format standard
        """
        return {
            "answer": raw_response,
            "sources": [
                {
                    "title": doc.get("title", "Document"),
                    "relevance_score": doc.get("score", 0.0),
                    "snippet": doc.get("content", "")[:200]
                }
                for doc in sources[:3]  # Limiter à 3 sources principales
            ],
            "confidence": self._calculate_confidence(raw_response, sources),
            "query_type": query_type,
            "suggestions": self._generate_suggestions(question, query_type)
        }
    
    def _calculate_confidence(self, response: str, sources: List) -> float:
        """
        Calcule un score de confiance basé sur la réponse et les sources
        """
        # Logique simplifiée - à améliorer
        base_score = 0.7
        
        # Augmenter si des sources sont présentes
        if sources:
            base_score += min(0.2, len(sources) * 0.05)
        
        # Réduire si la réponse contient des phrases d'incertitude
        uncertainty_phrases = ["je ne suis pas sûr", "je ne sais pas", "je ne peux pas"]
        if any(phrase in response.lower() for phrase in uncertainty_phrases):
            base_score -= 0.2
        
        return max(0.1, min(1.0, base_score))
    
    def _generate_suggestions(self, question: str, query_type: str) -> List[str]:
        """
        Génère des suggestions de questions suivantes
        """
        suggestions = []
        
        if query_type == "drug_info":
            suggestions = [
                "Quels sont les effets secondaires courants?",
                "Y a-t-il des interactions alimentaires?",
                "Quelle est la posologie pour les enfants?",
                "Existe-t-il des alternatives génériques?"
            ]
        elif query_type == "side_effects":
            suggestions = [
                "Comment gérer cet effet secondaire?",
                "Quand consulter un médecin?",
                "Existe-t-il des traitements pour ces effets?"
            ]
        else:
            suggestions = [
                "Pouvez-vous me donner plus de détails?",
                "Quels sont les traitements alternatifs?",
                "Quand faut-il consulter un professionnel?"
            ]
        
        return suggestions[:3]  # Limiter à 3 suggestions