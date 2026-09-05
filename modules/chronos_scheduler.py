#!/usr/bin/env python3
"""
CCiA Master Orchestrator: Chronos Scheduler v19.0 (61 Artefactos)
Orquestador principal del enjambre autónomo: DevSecOps, FinOps, Sentinel, Tesorería,
Gateway A2A, Ciencia, PQC, GraphRAG, Mesh, Ollama Scheduler, Email Dispatcher & Dual-Brain CRM.
"""

import time
import subprocess
import os
import sys

def log(msg):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {msg}")

def run_module(path):
    if os.path.exists(path):
        try:
            res = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=120)
            if res.stdout:
                for line in res.stdout.strip().split("\n"):
                    print(line)
            if res.stderr and res.returncode != 0:
                print(f"  ⚠️ Warning/Error en {os.path.basename(path)}: {res.stderr.strip()}")
        except Exception as e:
            print(f"  ❌ Fallo al ejecutar {path}: {e}")
    else:
        print(f"  ⚠️ Módulo no encontrado: {path}")

def main():
    print("⏰ Chronos Scheduler v19.0 iniciado (61 Artefactos activos)...")
    
    # 1. Sincronización Real con Stripe & FinOps (Artefactos 33 y 34)
    run_module("/home/k1/ccia_workspace/modules/stripe_live_sync.py")
    
    # 2. Pipeline de Outreach Autónomo (Artefacto 36)
    run_module("/home/k1/ccia_workspace/modules/autonomous_outreach_pipeline.py")
    
    # 3. Motor SLA & Procesamiento de Entregables (Artefacto 37)
    run_module("/home/k1/ccia_workspace/modules/sla_fulfillment_engine.py")
    
    # 4. Distribución Real de Tesorería por Bóvedas (Artefacto 38)
    run_module("/home/k1/ccia_workspace/modules/treasury_vault_distributor.py")
    
    # 5. Auditoría Sentinel & Túneles (Artefacto 39)
    run_module("/home/k1/ccia_workspace/modules/sentinel_tunnel_guard.py")
    
    # 6. Gateway de Protocolo A2A & Catálogo Monetizable (Artefacto 40)
    run_module("/home/k1/ccia_workspace/modules/a2a_market_gateway.py")

    # 7. Asignador de Turnos Ollama & Auditor de Conectividad (Artefacto 61)
    run_module("/home/k1/ccia_workspace/modules/art_61.py")

    # 8. Servidor de Email Autónomo & Ollama Task Dispatcher (Artefacto 59)
    run_module("/home/k1/ccia_workspace/modules/art_59.py")

    # 9. CRM Master Email, Dual-Brain Debate & Gateway I2I (Artefacto 60)
    run_module("/home/k1/ccia_workspace/modules/art_60.py")

if __name__ == "__main__":
    main()

# --- Módulos Ciencia, PQC, GraphRAG y Mesh P2P (Artefactos 41-44) ---
try:
    from ccia_science_discovery import run_science_engine
    from ccia_quantum_sentinel import run_quantum_guard
    from ccia_cognition_graph import run_cognition_graph
    from ccia_mesh_orchestrator import run_mesh_subcontractor

    run_science_engine()
    run_quantum_guard()
    run_cognition_graph()
    run_mesh_subcontractor()
except Exception as e:
    print(f"  ⚠️ Notificación de submódulos P2P/Science/PQC: {e}")
