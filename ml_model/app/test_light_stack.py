# test_light_stack.py
print("Test de la stack légère...")

# Test 1: Imports
try:
    from app.llm.embeddings_openai import embeddings_service
    print("Embeddings OpenAI importés")
except Exception as e:
    print(f" Embeddings: {e}")

# Test 2: RAG Léger
try:
    from app.llm.rag_light import light_rag
    print("RAG Léger importé")
    print(f"   Mode: OpenAI Embeddings")
except Exception as e:
    print(f" RAG Léger: {e}")

# Test 3: FastEmbed (alternative)
try:
    from fastembed import TextEmbedding
    embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    print("FastEmbed disponible")
except ImportError:
    print("FastEmbed non installé (optionnel)")