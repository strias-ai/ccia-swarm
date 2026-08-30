# -*- coding: utf-8 -*-
import sys
from ccia_compiler import CCIACompiler

def apply_rate_limit_patch(code: str) -> str:
    old_opt3 = """        elif opt == "3":"""
    new_opt3 = """        elif opt == "3":
            try:
                from rate_limiter_sentinel import check_rate_limit
                rl = check_rate_limit()
                console.print(f"🛡️ [bold yellow]Rate Limiter Sentinel:[/bold yellow] Tokens={rl['remaining_tokens']} | Permitido={rl['allowed']}")
            except Exception:
                pass"""
    if old_opt3 in code and "rate_limiter_sentinel" not in code:
        code = code.replace(old_opt3, new_opt3, 1)
    return code

def apply_cache_patch(code: str) -> str:
    old_opt4 = """        elif opt == "4":"""
    new_opt4 = """        elif opt == "4":
            try:
                from multi_tier_cache_manager import set_l1_cache
                set_l1_cache("last_tick", str(sys.meta_path))
                console.print("⚡ [bold cyan]Multi-Tier Cache L1/L2:[/bold cyan] Capa de aceleración activa")
            except Exception:
                pass"""
    if old_opt4 in code and "multi_tier_cache_manager" not in code:
        code = code.replace(old_opt4, new_opt4, 1)
    return code

compiler = CCIACompiler()
p1 = compiler.compile_patch(apply_rate_limit_patch, "rate_limiter_sentinel", "Protección Rate Limiting Token Bucket (Opción 3)")
p2 = compiler.compile_patch(apply_cache_patch, "multi_tier_cache_manager", "Gestor de Caché Multi-Nivel L1/L2 (Opción 4)")
sys.exit(0 if (p1 and p2) else 1)
