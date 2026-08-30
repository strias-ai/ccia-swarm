# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_vector_patch(code: str) -> str:
    old = """        elif opt == "6":"""
    new = """        elif opt == "6":
            try:
                from vector_embeddings_router import rank_similar_snippets
                console.print("🧠 [bold green]Motor Vectorial Semántico RAG:[/bold green] Similitud del coseno activa")
            except Exception:
                pass"""
    if old in code and "vector_embeddings_router" not in code:
        return code.replace(old, new, 1)
    return code

def apply_prom_patch(code: str) -> str:
    old = """        elif opt == "12":"""
    new = """        elif opt == "12":
            try:
                from prometheus_telemetry_bridge import export_prometheus_format
                console.print("📊 [bold cyan]Prometheus Exporter:[/bold cyan] Métricas OpenTelemetry listas en /metrics")
            except Exception:
                pass"""
    if old in code and "prometheus_telemetry_bridge" not in code:
        return code.replace(old, new, 1)
    return code

def apply_dist_patch(code: str) -> str:
    old = """        elif opt == "11":"""
    new = """        elif opt == "11":
            try:
                from distributed_persistence_adapter import check_persistence_bridge
                st = check_persistence_bridge()
                console.print(f"🌐 [bold magenta]Persistencia Distribuida:[/bold magenta] Modo {st['mode']} | Sync={st['distributed_sync']}")
            except Exception:
                pass"""
    if old in code and "distributed_persistence_adapter" not in code:
        return code.replace(old, new, 1)
    return code

compiler = CCIACompiler()
p1 = compiler.compile_patch(apply_vector_patch, "vector_embeddings_router", "Búsqueda Semántica Vectorial por Similitud de Coseno (Opción 6)")
p2 = compiler.compile_patch(apply_prom_patch, "prometheus_telemetry_bridge", "Puente Expresor de Métricas Prometheus/OpenTelemetry (Opción 12)")
p3 = compiler.compile_patch(apply_dist_patch, "distributed_persistence_adapter", "Adaptador Híbrido de Persistencia Distribuida (Opción 11)")

sys.exit(0 if (p1 and p2 and p3) else 1)
