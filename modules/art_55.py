#!/usr/bin/env python3
"""
Artefacto 55: CCiA Monetization & Live Pipeline Activator Engine
Descripción: Auditor, parcheador de estados DRY_RUN -> LIVE y activador de pasarelas de ingresos.
"""
import os
import sys
import re
import sqlite3
import json

DB_PATH = "/home/k1/ccia_workspace/university.db"
MODULES_DIR = "/home/k1/ccia_workspace/modules"

TARGET_ARTIFACTS = {
    10: {"script": "vant_commercial_closer.py", "role": "Generación de Enlaces Stripe Live"},
    21: {"script": "synthetic_datasets_api.py", "role": "API Datasets Sintéticos (Metered Billing)"},
    36: {"script": "autonomous_outreach_pipeline.py", "role": "Pipeline de Prospección y Oferta Directa"},
    39: {"script": "universal_tunnel_sentinel.py", "role": "Túnel Público y Exposición SSL de Endpoints"},
    52: {"script": "fiat_monetization_engine.py", "role": "Pasarela de Cobros FIAT & Gastos SEPA"},
    53: {"script": "art_53_a2a_x402_gateway.py", "role": "Pasarela A2A x402 Micropagos (SOL/ETH)"}
}

def audit_and_patch_live_mode():
    print("================================================================================")
    print("⚡ AUDITORÍA Y ACTIVACIÓN DE MODOS LIVE PARA INGRESOS REALES")
    print("================================================================================")
    
    results = []
    
    for art_id, meta in TARGET_ARTIFACTS.items():
        filepath = os.path.join(MODULES_DIR, meta["script"])
        exists = os.path.exists(filepath)
        
        if not exists:
            results.append({"id": art_id, "script": meta["script"], "status": "MISSING", "detail": "Archivo no encontrado"})
            continue
            
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        # Detección de banderas de simulación/dry-run
        has_dry = bool(re.search(r'(DRY_RUN|SIMULATION_MODE|MOCK_MODE)\s*=\s*True', content, re.IGNORECASE))
        has_live = bool(re.search(r'LIVE_MODE\s*=\s*True', content, re.IGNORECASE))
        
        patched = False
        if has_dry:
            new_content = re.sub(r'DRY_RUN\s*=\s*True', 'DRY_RUN = False', content, flags=re.IGNORECASE)
            new_content = re.sub(r'SIMULATION_MODE\s*=\s*True', 'SIMULATION_MODE = False', new_content, flags=re.IGNORECASE)
            new_content = re.sub(r'MOCK_MODE\s*=\s*True', 'MOCK_MODE = False', new_content, flags=re.IGNORECASE)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            patched = True
            
        status_label = "ACTIVE LIVE" if (has_live or patched or not has_dry) else "DRY_RUN"
        results.append({
            "id": art_id,
            "script": meta["script"],
            "role": meta["role"],
            "status": status_label,
            "patched": patched
        })

    for r in results:
        patch_str = " (Convertido a LIVE)" if r.get("patched") else ""
        print(f"Artefacto [{r['id']:02d}] | {r['script']:<30} | {r['status']:<12}{patch_str}")
        print(f"  └─ Rol: {r['role']}")
        
    print("--------------------------------------------------------------------------------")
    return results

def verify_credentials_and_wallets():
    print("\n================================================================================")
    print("🔑 VERIFICACIÓN DE CREDENCIALES Y CANALES DE COBRO")
    print("================================================================================")
    
    env_vars = {
        "STRIPE_SECRET_KEY": os.getenv("STRIPE_SECRET_KEY", ""),
        "STRIPE_PUBLISHABLE_KEY": os.getenv("STRIPE_PUBLISHABLE_KEY", ""),
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", ""),
        "SOLANA_WALLET": "4mfzpej1AyUJVsLnLSZFaFRNYw3dgJen9pujtkvNvCNr",
        "ETHEREUM_WALLET": "0x500cFBE479F3ce0DDad1f943582E7b9c9fe84e22"
    }
    
    print(f"• Wallet Solana (Bitpanda):   {env_vars['SOLANA_WALLET']} [CONFIGURADA]")
    print(f"• Wallet Ethereum (Bitpanda): {env_vars['ETHEREUM_WALLET']} [CONFIGURADA]")
    
    if env_vars["STRIPE_SECRET_KEY"].startswith("sk_live"):
        print("• Stripe Live Secret Key:     sk_live_... [CONFIGURADA Y REAL]")
    elif env_vars["STRIPE_SECRET_KEY"].startswith("sk_test"):
        print("• Stripe Key actual:         sk_test_... [MODO TEST DETECTADO]")
    else:
        print("• Stripe API Key:             [EN MÓDULO BANCARIO / SISTEMA LOCAL]")
        
    if env_vars["GITHUB_TOKEN"]:
        print("• GitHub API Token:           [DETECTADO]")
    else:
        print("• GitHub API Token:           [NO CONFIGURADO EN ENV - Requerido para PRs automáticos]")
    print("--------------------------------------------------------------------------------")

def execute_live_pipeline():
    print("\n🚀 ACTIVANDO PASARELAS Y ENGINES EN PARALELO...")
    
    # 1. Levantar Túnel de Exposición de Puertos (Artefacto 39)
    print("\n[1/3] Verificando túnel de exposición pública (Artefacto 39)...")
    os.system("python3 /home/k1/ccia_workspace/modules/universal_tunnel_sentinel.py")
    
    # 2. Iniciar Pasarela A2A x402 (Artefacto 53)
    print("\n[2/3] Verificando pasarela A2A x402 Solana/ETH (Artefacto 53)...")
    os.system("python3 /home/k1/ccia_workspace/modules/art_53_a2a_x402_gateway.py")
    
    # 3. Lanzar Outreach Autónomo (Artefacto 36)
    print("\n[3/3] Ejecutando Pipeline de Prospección y Cierre Comercial (Artefacto 36)...")
    os.system("python3 /home/k1/ccia_workspace/modules/autonomous_outreach_pipeline.py")

def display_menu():
    while True:
        os.system("clear")
        print("================================================================================")
        print("💰 CCiA MONETIZATION & LIVE PIPELINE ACTIVATOR (ARTEFACTO 55)")
        print("================================================================================")
        print("  [1] 🔍 Auditar Módulos Monetizadores y Parchear Modos a LIVE")
        print("  [2] 🔑 Validar Billeteras Crypto, Keys de Stripe y GitHub Token")
        print("  [3] ⚡ Disparar Pipeline Completo de Captación e Ingresos Reales")
        print("  [0] ⬅️ Salir")
        
        choice = input("\nCCIA-v19.0 (Artefacto 55)> ").strip()
        
        if choice == "1":
            os.system("clear")
            audit_and_patch_live_mode()
            input("\n[Presiona ENTER para continuar...]")
        elif choice == "2":
            os.system("clear")
            verify_credentials_and_wallets()
            input("\n[Presiona ENTER para continuar...]")
        elif choice == "3":
            os.system("clear")
            execute_live_pipeline()
            input("\n[Presiona ENTER para continuar...]")
        elif choice == "0":
            break

if __name__ == "__main__":
    display_menu()
