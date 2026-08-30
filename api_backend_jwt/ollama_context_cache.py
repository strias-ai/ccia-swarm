# -*- coding: utf-8 -*-
"""
CCIA OLLAMA CONTEXT CACHE v1.0
Reutiliza contextos de prompts del sistema previa evaluación de hash MD5
para acelerar la velocidad de tokenización de los modelos locales.
"""
import hashlib

_CACHE = {}

def get_prompt_hash(prompt: str) -> str:
    return hashlib.md5(prompt.encode('utf-8')).hexdigest()

def get_cached_context(prompt: str):
    p_hash = get_prompt_hash(prompt)
    return _CACHE.get(p_hash, None)

def store_context(prompt: str, context: list):
    p_hash = get_prompt_hash(prompt)
    _CACHE[p_hash] = context

if __name__ == "__main__":
    h = get_prompt_hash("system_prompt_test")
    print(f"⚡ Context Cache inicializado (Hash Engine: {h[:8]})")
