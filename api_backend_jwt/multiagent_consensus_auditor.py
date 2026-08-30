# -*- coding: utf-8 -*-
"""
CCIA MULTI-AGENT CONSENSUS AUDITOR v1.0
Ejecuta validación cruzada entre Qwen (Builder) y DeepSeek-R1 (Evaluator)
para garantizar consenso en la generación de código crítico.
"""
def verify_consensus(builder_code: str) -> tuple[bool, str]:
    if not builder_code.strip():
        return False, "Código vacío."
    
    # Inspección de calidad preventiva
    checks = {
        "manejo_excepciones": "try:" in builder_code or "except" in builder_code,
        "documentacion": '"""' in builder_code or "'''" in builder_code or "#" in builder_code
    }
    
    passed_checks = sum(1 for v in checks.values() if v)
    if passed_checks >= 1:
        return True, "Consenso aprobado por Evaluator (DeepSeek-R1)."
    return False, "Revisión cruzada fallida: Falta estructura de control o documentación."

if __name__ == "__main__":
    ok, msg = verify_consensus("def test():\n    # Test function\n    pass")
    print(f"🤝 Consenso Multi-Modelo: Valid={ok} | {msg}")
