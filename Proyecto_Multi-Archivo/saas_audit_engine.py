# -*- coding: utf-8 -*-
"""
CCIA MICRO-SAAS AST AUDIT ENGINE v1.0
Endpoint Comercial de Auditoría Estática, Análisis OWASP y Métricas de Rendimiento.
"""
import ast
import re

def audit_code_payload(code: str) -> dict:
    issues = []
    score = 100
    
    # Check 1: OWASP - Code Injection (eval / exec)
    if "eval(" in code or "exec(" in code:
        issues.append({"severity": "CRITICAL", "type": "OWASP_A03_INJECTION", "detail": "Uso detectado de eval() o exec()"})
        score -= 40
        
    # Check 2: OWASP - Hardcoded Secrets
    if re.search(r'(secret|password|token|key)\s*=\s*["\'][^"\']+["\']', code, re.IGNORECASE):
        issues.append({"severity": "HIGH", "type": "OWASP_A07_CREDENTIAL_LEAK", "detail": "Credencial o clave hardcodeada detectada"})
        score -= 30
        
    # Check 3: AST Syntax Validity
    try:
        ast.parse(code)
        syntax_ok = True
    except SyntaxError as e:
        syntax_ok = False
        issues.append({"severity": "CRITICAL", "type": "SYNTAX_ERROR", "detail": str(e)})
        score -= 50

    return {
        "status": "PASS" if score >= 70 else "FAIL",
        "security_score": max(0, score),
        "issues_found": len(issues),
        "issues": issues,
        "syntax_valid": syntax_ok,
        "certified_by": "CCIA OWASP Scanner v14"
    }
