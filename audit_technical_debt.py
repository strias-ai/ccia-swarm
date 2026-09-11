import os
import sys
import glob
import sqlite3
import py_compile

DB_PATH = "/home/k1/ccia_workspace/university.db"
WORKSPACE_DIR = "/home/k1/ccia_workspace"
MODULES_DIR = "/home/k1/ccia_workspace/modules"

print("=" * 80)
print("🧹 INFORME Y DIAGNÓSTICO DE DEUDA TÉCNICA - CCiA SYSTEM")
print("=" * 80)

debt_issues = []

# 1. Auditoría Base de Datos vs. Sistema de Archivos
print("\n1. 🗄️ Verificación DB Manifest vs. Archivos Físicos:")
registered_artifacts = {}
if os.path.exists(DB_PATH):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT artifact_id, name, path, status FROM ccia_artifact_manifests ORDER BY artifact_id ASC")
        rows = cursor.fetchall()
        for art_id, name, path, status in rows:
            registered_artifacts[str(art_id)] = {"name": name, "path": path, "status": status}
            if path and not os.path.exists(path):
                debt_issues.append(f"[HIGH] Artefacto [{art_id}] '{name}' apunta a ruta inexistente: {path}")
                print(f"  ❌ Artefacto [{art_id:2}] '{name}' -> ARCHIVO INEXISTENTE ({path})")
            else:
                print(f"  ✅ Artefacto [{art_id:2}] '{name}' -> Registrado y Presente")
        conn.close()
    except Exception as e:
        print(f"  ❌ Error leyendo DB: {e}")
else:
    print("  ❌ DB university.db no encontrada.")

# 2. Detección de Scripts Huérfanos / No Registrados
print("\n2. 📁 Scripts Huérfanos en Sistema (No registrados en DB):")
py_files = sorted(list(set(glob.glob(f"{WORKSPACE_DIR}/*.py") + glob.glob(f"{MODULES_DIR}/*.py"))))
db_paths = [v['path'] for v in registered_artifacts.values() if v['path']]

orphan_count = 0
for pf in py_files:
    fname = os.path.basename(pf)
    # Excluir scripts temporales o de utilidad interna conocidos
    if pf not in db_paths and not any(fname.startswith(prefix) for prefix in ['test_', 'deploy_', 'audit_', 'force_', 'fix_', 'restore_', 'upgrade_', 'diagnose_', 'inspect_', 'debug_']):
        orphan_count += 1
        debt_issues.append(f"[MEDIUM] Script huérfano no registrado en DB: {pf}")
        print(f"  ⚠️ Huérfano detectado: {pf}")

if orphan_count == 0:
    print("  ✅ No se encontraron scripts huérfanos sin registrar.")

# 3. Control de Calidad de Sintaxis Python (py_compile)
print("\n3. 🐍 Verificación de Sintaxis Python (py_compile):")
syntax_errors = 0
for pf in py_files:
    try:
        py_compile.compile(pf, doraise=True)
    except Exception as e:
        syntax_errors += 1
        debt_issues.append(f"[CRITICAL] Error de sintaxis en {pf}: {e}")
        print(f"  ❌ Error de sintaxis en {os.path.basename(pf)}: {e}")

if syntax_errors == 0:
    print(f"  ✅ 100% de los scripts ({len(py_files)} archivos) sintácticamente válidos.")

# 4. Estado de Adopción del Puente Artefacto 65 (art_65_bridge.py)
print("\n4. 🔗 Cobertura de Integración con Artefacto 65 (Gateway Bus):")
core_modules = [f for f in py_files if "art_" in os.path.basename(f) and not "art_65" in os.path.basename(f)]
integrated = []
pending = []

for cm in core_modules:
    try:
        with open(cm, "r", encoding="utf-8") as f:
            content = f.read()
            if "art_65_bridge" in content or "CCiAGatewayBridge" in content:
                integrated.append(os.path.basename(cm))
            else:
                pending.append(os.path.basename(cm))
    except Exception:
        pass

print(f"  • Módulos con puente Art 65 activo ({len(integrated)}): {integrated}")
print(f"  • Módulos sin conexión al Bus aún ({len(pending)}): {pending}")
if pending:
    debt_issues.append(f"[INFO] Hay {len(pending)} módulos listos para importar art_65_bridge cuando sea necesario.")

# 5. Resumen Ejecutivo de Deuda Técnica
print("\n" + "=" * 80)
print(f"📊 RESUMEN EJECUTIVO: {len(debt_issues)} PUNTOS DE DEUDA TÉCNICA DETECTADOS")
print("=" * 80)
if not debt_issues:
    print("🎉 ¡SISTEMA IMPECABLE! No se detectó deuda técnica ni archivos corruptos.")
else:
    for idx, issue in enumerate(debt_issues, 1):
        print(f"  {idx}. {issue}")

print("\n" + "=" * 80)
print("💡 COPIA Y PEGA LA SALIDA COMPLETA EN EL CHAT PARA RESOLVER LOS PUNTOS PENDIENTES.")
print("=" * 80)
