#dailymed_loader.py : Chargement données FDA
import aiohttp
import asyncio
import json
import logging
from typing import List, Dict, Optional
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)

class DrugDatabase:
    """
    Gère la base de données des médicaments FDA DailyMed
    """
    
    def __init__(self):
        self.db_path = "./data/drugs.db"
        self.dailymed_base_url = "https://dailymed.nlm.nih.gov/dailymed/services/v2"
        self.session = None
        self.conn = None
    
    async def initialize(self):
        """Initialise la base de données et télécharge les données si besoin"""
        logger.info("Initialisation de la base de données médicaments...")
        
        try:
            # Créer le répertoire data si inexistant
            import os
            os.makedirs("./data", exist_ok=True)
            
            # Initialiser la connexion SQLite
            self.conn = sqlite3.connect(self.db_path)
            self._create_tables()
            
            # Vérifier si la base est vide
            if self._is_database_empty():
                logger.info("Base vide, téléchargement des données...")
                await self._download_dailymed_data()
            else:
                logger.info("✅ Base de données déjà peuplée")
            
            # Initialiser session HTTP
            self.session = aiohttp.ClientSession()
            
        except Exception as e:
            logger.error(f"Erreur initialisation base: {e}")
            raise
    
    def _create_tables(self):
        """Crée les tables de la base de données"""
        cursor = self.conn.cursor()
        
        # Table médicaments
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS drugs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            generic_name TEXT,
            brand_name TEXT,
            description TEXT,
            indications TEXT,
            dosage TEXT,
            contraindications TEXT,
            side_effects TEXT,
            interactions TEXT,
            fda_id TEXT,
            last_updated TIMESTAMP
        )
        ''')
        
        # Table interactions
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS drug_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug1_id TEXT,
            drug2_id TEXT,
            interaction_type TEXT,
            severity TEXT,
            description TEXT,
            mechanism TEXT,
            recommendations TEXT,
            FOREIGN KEY (drug1_id) REFERENCES drugs (id),
            FOREIGN KEY (drug2_id) REFERENCES drugs (id)
        )
        ''')
        
        self.conn.commit()
        logger.info("Tables créées avec succès")
    
    def _is_database_empty(self) -> bool:
        """Vérifie si la base de données est vide"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM drugs")
        count = cursor.fetchone()[0]
        return count == 0
    
    async def _download_dailymed_data(self, limit: int = 1000):
        """
        Télécharge les données de DailyMed API
        Note: L'API réelle nécessite une pagination et un traitement complexe
        """
        logger.info(f"Téléchargement de {limit} médicaments...")
        
        try:
            # URL d'exemple - À ADAPTER selon la vraie API
            url = f"{self.dailymed_base_url}/drugs?limit={limit}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self._process_dailymed_response(data)
                    else:
                        logger.error(f"Erreur API DailyMed: {response.status}")
                        # Charger des données de test
                        await self._load_sample_data()
            
        except Exception as e:
            logger.error(f"Erreur téléchargement: {e}")
            # Charger des données de test en cas d'erreur
            await self._load_sample_data()
    
    async def _process_dailymed_response(self, data: Dict):
        """Traite la réponse de l'API DailyMed"""
        # NOTE: À implémenter selon le format réel de l'API
        # Ceci est un exemple simplifié
        
        drugs = data.get("data", [])
        logger.info(f"Traitement de {len(drugs)} médicaments...")
        
        cursor = self.conn.cursor()
        
        for drug in drugs[:100]:  # Limiter pour l'exemple
            drug_id = drug.get("spl_id")
            
            # Extraire les informations
            drug_data = {
                "id": drug_id,
                "name": drug.get("title", ""),
                "generic_name": self._extract_generic_name(drug),
                "brand_name": drug.get("brand_name", ""),
                "description": drug.get("description", ""),
                "indications": self._extract_indications(drug),
                "dosage": self._extract_dosage(drug),
                "contraindications": self._extract_contraindications(drug),
                "side_effects": self._extract_side_effects(drug),
                "interactions": self._extract_interactions(drug),
                "fda_id": drug_id,
                "last_updated": datetime.now().isoformat()
            }
            
            # Insérer dans la base
            cursor.execute('''
            INSERT OR REPLACE INTO drugs VALUES (
                :id, :name, :generic_name, :brand_name, :description,
                :indications, :dosage, :contraindications, :side_effects,
                :interactions, :fda_id, :last_updated
            )
            ''', drug_data)
        
        self.conn.commit()
        logger.info(f"✅ {len(drugs)} médicaments ajoutés")
    
    async def _load_sample_data(self):
        """Charge des données d'exemple si l'API échoue"""
        logger.info("Chargement de données d'exemple...")
        
        sample_drugs = [
            {
                "id": "paracetamol_001",
                "name": "Paracétamol",
                "generic_name": "Acetaminophen",
                "brand_name": "Doliprane",
                "description": "Antidouleur et antipyrétique",
                "indications": "Douleurs légères à modérées, fièvre",
                "dosage": "500-1000mg toutes les 4-6 heures, max 4000mg/jour",
                "contraindications": "Insuffisance hépatique sévère",
                "side_effects": "Rare: réactions cutanées, hépatotoxicité à fortes doses",
                "interactions": "Ant