# -*- coding: utf-8 -*-
"""
CCIA FULL ECOSYSTEM AUDITOR v1.0
Valida la carga, existencia e integridad de todos los módulos registrados en module_registry.json.
"""
import os
import json
import importlib

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "module_registry.json")

def audit_full_system() -> dict:
    if not os.path.exists(REGISTRY_PATH):
        return {"status": "FAIL", "reason": "No se encontró module_registry.json"}

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    extensions = registry.get("extensions", {})
    results = {}
    passed = 0

    for name, details in extensions.items():
        file_path = os.path.join(os.path.dirname(__file__), f"{name}.py")
        exists = os.path.exists(file_path)
        importable = False
        
        if exists:
            try:
                importlib.import_module(name)
                importable = True
                passed += 1
            except Exception:
                pass

        results[name] = {
            "file_exists": exists,
            "importable": importable,
            "description": details.get("description", "Sin descripción")
        }

    return {
        "status": "PASS" if passed == len(extensions) else "DEGRADED",
        "total_modules": len(extensions),
        "verified_modules": passed,
        "details": results
    }

if __name__ == "__main__":
    report = audit_full_system()
    print(f"\n==================================================")
    print(f"🛡️ AUDITORÍA GLOBAL DEL ECOSISTEMA CCIA")
    print(f"==================================================")
    print(f"Estado General : {report['status']}")
    print(f"Módulos Activos: {report['verified_modules']}/{report['total_modules']}\n")
    
    for mod, data in report.get("details", {}).items():
        status_icon = "✅" if data["file_exists"] and data["importable"] else "❌"
        print(f"{status_icon} [{mod}] -> {data['description']}")
    print(f"==================================================\n")
