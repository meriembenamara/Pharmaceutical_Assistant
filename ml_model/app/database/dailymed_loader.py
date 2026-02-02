import requests
import json
import os
import time
from typing import List, Dict, Optional
import logging
from app.config import config

logger = logging.getLogger(__name__)

class DailyMedLoader:
    """Chargeur de données DailyMed FDA"""
    
    def __init__(self):
        self.api_url = config.DAILYMED_API_URL
        self.cache_dir = config.DAILYMED_CACHE_DIR
    
    def search_drugs(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Recherche des médicaments dans DailyMed
        
        Args:
            query: Terme de recherche
            limit: Nombre maximum de résultats
        """
        try:
            endpoint = f"{self.api_url}/drugnames.json"
            params = {
                "drug_name": query,
                "pagesize": limit
            }
            
            logger.info(f"🔍 Recherche DailyMed: {query}")
            response = requests.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                drugs = data.get("data", [])
                
                formatted_drugs = []
                for drug in drugs[:limit]:
                    formatted_drugs.append({
                        "name": drug.get("drug_name", ""),
                        "type": drug.get("drug_type", ""),
                        "active_ingredients": drug.get("active_ingredients", []),
                        "route": drug.get("route", ""),
                        "strength": drug.get("strength", ""),
                        "source": "DailyMed FDA"
                    })
                
                return formatted_drugs
            else:
                logger.error(f"❌ Erreur API DailyMed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erreur recherche DailyMed: {str(e)}")
            return []
    
    def get_drug_spl(self, spl_id: str) -> Optional[Dict]:
        """
        Obtient le SPL (Structured Product Labeling) d'un médicament
        
        Args:
            spl_id: ID du SPL
        """
        cache_file = os.path.join(self.cache_dir, f"{spl_id}.json")
        
        # Vérifier le cache
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        try:
            endpoint = f"{self.api_url}/spls/{spl_id}.json"
            response = requests.get(endpoint, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Sauvegarder en cache
                os.makedirs(os.path.dirname(cache_file), exist_ok=True)
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                return data
            else:
                logger.error(f"❌ Erreur récupération SPL {spl_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur récupération SPL: {str(e)}")
            return None
    
    def extract_drug_info(self, spl_data: Dict) -> Dict:
        """
        Extrait les informations importantes d'un SPL
        
        Args:
            spl_data: Données SPL brutes
        """
        if not spl_data:
            return {}
        
        try:
            # Extraire les sections importantes
            sections = spl_data.get("spl_product_data_elements", {}).get("product_data_elements", [])
            
            info = {
                "name": spl_data.get("title", ""),
                "active_ingredients": [],
                "indications": "",
                "dosage": "",
                "contraindications": "",
                "warnings": "",
                "side_effects": "",
                "storage": ""
            }
            
            # Parcourir les sections pour extraire l'information
            for section in sections:
                title = section.get("title", "").lower()
                content = section.get("text", "")
                
                if "ingredient" in title:
                    info["active_ingredients"].append(content)
                elif "indication" in title:
                    info["indications"] = content
                elif "dosage" in title or "administration" in title:
                    info["dosage"] = content
                elif "contraindication" in title:
                    info["contraindications"] = content
                elif "warning" in title or "precaution" in title:
                    info["warnings"] = content
                elif "reaction" in title or "side effect" in title:
                    info["side_effects"] = content
                elif "storage" in title:
                    info["storage"] = content
            
            return info
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction info médicament: {str(e)}")
            return {}
    
    def prepare_for_vector_db(self, drug_info: Dict) -> Dict:
        """
        Prépare les données pour la base vectorielle
        
        Args:
            drug_info: Informations sur le médicament
        """
        # Créer un texte structuré pour l'embedding
        text_parts = []
        
        if drug_info.get("name"):
            text_parts.append(f"Médicament: {drug_info['name']}")
        
        if drug_info.get("active_ingredients"):
            ingredients = ", ".join(drug_info["active_ingredients"])
            text_parts.append(f"Principes actifs: {ingredients}")
        
        if drug_info.get("indications"):
            text_parts.append(f"Indications: {drug_info['indications'][:500]}...")
        
        if drug_info.get("dosage"):
            text_parts.append(f"Posologie: {drug_info['dosage'][:500]}...")
        
        if drug_info.get("warnings"):
            text_parts.append(f"Précautions: {drug_info['warnings'][:500]}...")
        
        text = "\n".join(text_parts)
        
        return {
            "id": f"drug_{hash(drug_info.get('name', ''))}",
            "text": text,
            "metadata": {
                "name": drug_info.get("name", ""),
                "source": "DailyMed",
                "timestamp": time.time()
            }
        }
    
    def is_available(self) -> bool:
        """Vérifie si DailyMed est accessible"""
        try:
            response = requests.get(f"{self.api_url}/drugnames.json", params={"drug_name": "aspirin"}, timeout=5)
            return response.status_code == 200
        except:
            return False

# Instance globale
dailymed_loader = DailyMedLoader()