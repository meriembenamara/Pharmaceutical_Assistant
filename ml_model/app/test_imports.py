# app/test_imports.py
"""
Script de test pour vérifier que tous les imports fonctionnent
Exécutez: python app/test_imports.py
"""

import sys
import os

print("🔍 TEST DES IMPORTS - Pharma Assistant")
print("=" * 50)

# Ajouter le dossier courant au chemin Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

tests_passed = 0
tests_failed = 0

def test_import(module_name, import_statement):
    """Teste un import et affiche le résultat"""
    global tests_passed, tests_failed
    
    try:
        # Exécute l'import dynamiquement
        exec(import_statement)
        print(f"{module_name}")
        tests_passed += 1
        return True
    except ImportError as e:
        print(f"{module_name} - ImportError: {e}")
        tests_failed += 1
        return False
    except Exception as e:
        print(f"{module_name} - Erreur: {type(e).__name__}: {e}")
        tests_failed += 1
        return False

# Liste des imports à tester
imports_to_test = [
    # Modules de base
    ("FastAPI", "from fastapi import FastAPI"),
    ("Uvicorn", "import uvicorn"),
    ("OpenAI", "import openai"),
    
    # Notre application
    ("Configuration", "from app.config import config"),
    
    # Services (ces tests peuvent échouer si fichiers non créés)
    ("LLM Engine", "from app.llm.llm_engine import llm_engine"),
    ("Drug Service", "from app.services.drug_service import DrugService"),
    ("DailyMed Loader", "from app.database.dailymed_loader import dailymed_loader"),
    
    # Utilitaires
    ("Dotenv", "from dotenv import load_dotenv"),
    ("ChromaDB", "import chromadb"),
    ("Sentence Transformers", "from sentence_transformers import SentenceTransformer"),
]

print("\n Test des imports...\n")

# Exécuter tous les tests
for module_name, import_stmt in imports_to_test:
    test_import(module_name, import_stmt)

print(f"\n{'='*50}")
print(f"RÉSULTATS : {tests_passed}/{len(imports_to_test)} tests réussis")

if tests_failed > 0:
    print(f"\n {tests_failed} import(s) ont échoué.")
    print("\n Vérifiez que ces fichiers existent :")
    
    # Liste des fichiers potentiellement manquants
    expected_files = [
        "app/config.py",
        "app/llm/llm_engine.py",
        "app/services/drug_service.py", 
        "app/database/dailymed_loader.py",
        "app/llm/rag.py",
        "app/models/medicine.py",
        "app/services/interaction_service.py"
    ]
    
    print("\nFichiers requis dans app/ :")
    for file in expected_files:
        if os.path.exists(file):
            print(f" {file}")
        else:
            print(f" {file} - MANQUANT")
    
    print(f"\n💡 Solution : Créez les fichiers manquants ou utilisez la version simplifiée.")
else:
    print("🎉 Tous les imports fonctionnent !")
    print("\n Vous pouvez lancer l'application avec :")
    print("   python -m app.main")
    print("   ou")
    print("   uvicorn app.main:app --reload")

print(f"\n{'='*50}")

# Vérifier aussi la structure des dossiers
print("\n Structure des dossiers :")
required_dirs = ["app/llm", "app/database", "app/models", "app/services", "data/dailymed", "data/chroma_db"]
for dir_path in required_dirs:
    if os.path.exists(dir_path):
        print(f" {dir_path}/")
    else:
        print(f"   {dir_path}/ - MANQUANT")

# Test supplémentaire : vérifier .env
print(f"\n Fichier .env :")
if os.path.exists(".env"):
    print("  .env trouvé")
    # Vérifier OpenAI key
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"  OPENAI_API_KEY configurée ({api_key[:15]}...)")
    else:
        print(" OPENAI_API_KEY non trouvée dans .env")
else:
    print(" .env non trouvé")