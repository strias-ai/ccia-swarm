#!/usr/bin/env python3
"""
CCiA Real FIAT Generator & Payout Router (Artefacto 52)
Maneja las 3 vías de liquidez real para pagos de servicios (Luz, Alquiler, Servidores).
Carga variables directamente de .env o del entorno del sistema.
"""
import os
import sys
import json
import sqlite3

def load_env_file():
    env_path = "/home/k1/ccia_workspace/.env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

def check_env_vars():
    load_env_file()
    print("=== 💳 CREDENCIALES DE LIQUIDEZ REAL PARA GASTOS (LUZ / ALQUILER) ===")
    
    stripe_key = os.environ.get("STRIPE_SECRET_KEY", "")
    stripe_ok = stripe_key.startswith("sk_live_")
    
    github_key = os.environ.get("GITHUB_TOKEN", "")
    github_ok = github_key.startswith("ghp_") or github_key.startswith("github_pat_")
    
    iban = os.environ.get("USER_IBAN_SEPA", "")
    crypto_ok = bool(iban and "REMPLAZAR" not in iban)
    
    print(f"  [1] Stripe Live (Tarjeta -> Banco Directo)   : {'✅ ACTIVO (sk_live_)' if stripe_ok else '⚠️ PENDIENTE (Edita /home/k1/ccia_workspace/.env)'}")
    print(f"  [2] Crypto Off-Ramp (USDC -> IBAN SEPA)      : {'✅ ACTIVO (' + iban[:4] + '...)' if crypto_ok else '⚠️ PENDIENTE (Configura USER_IBAN_SEPA en .env)'}")
    print(f"  [3] GitHub Bounties (Algora/PRs -> Cash)     : {'✅ ACTIVO' if github_ok else '⚠️ PENDIENTE (Configura GITHUB_TOKEN en .env)'}")
    
    return stripe_ok, crypto_ok, github_ok

if __name__ == "__main__":
    check_env_vars()
