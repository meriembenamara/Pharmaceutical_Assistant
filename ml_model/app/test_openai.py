# test_openai.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# Charger les variables d'environnement
load_dotenv()

# Afficher (partiellement) la clé pour vérification
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"Clé API chargée: {api_key[:15]}...")
else:
    print("Clé API non trouvée")
    exit(1)

# Tester la connexion
client = OpenAI(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Tu es un assistant pharmaceutique."},
            {"role": "user", "content": "Dis-moi simplement 'Bonjour, je fonctionne !' en français."}
        ],
        max_tokens=50
    )
    
    print("Test réussi !")
    print(f"Réponse: {response.choices[0].message.content}")
    
except Exception as e:
    print(f" Erreur: {e}")