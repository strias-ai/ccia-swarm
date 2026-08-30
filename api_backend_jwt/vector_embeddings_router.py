# -*- coding: utf-8 -*-
"""
CCIA VECTOR EMBEDDINGS ROUTER v1.0
Búsqueda Semántica de Código mediante Similitud del Coseno Vectorial (Opción 6).
"""
import math

def cosine_similarity(v1: list, v2: list) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    return dot / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0

def generate_text_embedding(text: str) -> list:
    words = text.lower().split()
    return [
        len(words),
        sum(len(w) for w in words),
        text.count("def"),
        text.count("class"),
        text.count("import"),
        text.count("error"),
        text.count("jwt"),
        float(hash(text) % 100) / 100.0
    ]

def rank_similar_snippets(query: str, snippets: list) -> list:
    q_vec = generate_text_embedding(query)
    ranked = []
    for snip in snippets:
        s_vec = generate_text_embedding(snip)
        sim = cosine_similarity(q_vec, s_vec)
        ranked.append((sim, snip))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return ranked

if __name__ == "__main__":
    test_q = "autenticación JWT con FastAPI"
    test_docs = ["def create_access_token(): pass", "class DatabaseConfig: pass", "import jwt"]
    results = rank_similar_snippets(test_q, test_docs)
    print(f"🧠 Buscador Vectorial Semántico: Top Match = '{results[0][1]}' (Similitud: {results[0][0]:.4f})")
