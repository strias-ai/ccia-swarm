import os
import sys
import json
import sqlite3
import shutil
from datetime import datetime

WORKSPACE = "/home/k1/ccia_workspace"
DB_PATH = os.path.join(WORKSPACE, "art_66_registry.db")
BACKUP_DIR = os.path.join(WORKSPACE, "backups_art66")

class CCiAManualRegistry:
    def __init__(self):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS artifact_specs (
                id INTEGER PRIMARY KEY,
                number INTEGER UNIQUE,
                name TEXT,
                category TEXT,
                center_control TEXT,
                ollama_models TEXT,
                uses_sandbox BOOLEAN,
                uses_memory BOOLEAN,
                connected_artifacts TEXT,
                current_strategy TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS strategy_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artifact_number INTEGER,
                version TEXT,
                strategy_text TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS script_backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artifact_number INTEGER,
                script_path TEXT,
                backup_path TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def get_artifact_files(self, art_num):
        matches = []
        padded = f"{art_num:02d}"
        keywords = [f"art_{art_num}", f"art_{padded}", f"art{art_num}", f"art{padded}"]
        for root, _, files in os.walk(WORKSPACE):
            if "backups" in root or ".git" in root or "__pycache__" in root:
                continue
            for f in files:
                if any(kw in f.lower() for kw in keywords) and f.endswith(('.py', '.sh', '.json', '.conf')):
                    matches.append(os.path.join(root, f))
        return sorted(list(set(matches)))

    def display_cascade_spec(self, art_num):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT name, category, center_control, ollama_models, uses_sandbox, uses_memory, connected_artifacts, current_strategy FROM artifact_specs WHERE number=?", (art_num,))
        row = cur.fetchone()
        conn.close()

        files = self.get_artifact_files(art_num)
        
        spec = {
            "artefacto_num": art_num,
            "nombre": row[0] if row else f"Artefacto {art_num}",
            "categoria": row[1] if row else "Desconocido / General",
            "centro_de_mando": row[2] if row else f"/home/k1/ccia_workspace/modules/art_{art_num}.py",
            "modelos_ollama": json.loads(row[3]) if row and row[3] else ["ccia-coder-xl-14b:latest"],
            "usa_sandbox_vant": bool(row[4]) if row else True,
            "usa_memoria_persistente": bool(row[5]) if row else True,
            "artefactos_conectados": json.loads(row[6]) if row and row[6] else ["Art 11 (Event Bus)", "Art 45 (AST)"],
            "archivos_detectados": [os.path.relpath(f, WORKSPACE) for f in files],
            "estrategia_actual": row[7] if row else "Estrategia base de ejecución autónoma dentro de la red CCIA."
        }

        print("\n" + "="*80)
        print(f"📋 FICHA TÉCNICA CANÓNICA - ARTEFACTO {art_num}")
        print("="*80)
        print(json.dumps(spec, indent=2, ensure_ascii=False))
        print("="*80 + "\n")

    def backup_script(self, art_num):
        files = self.get_artifact_files(art_num)
        if not files:
            print(f"⚠️ No se detectaron scripts automáticos asociados al Artefacto {art_num}.")
            return

        print(f"\n📦 Selecciona el script para crear copia de seguridad (Art {art_num}):")
        print("  [A] RESPALDAR TODOS LOS SCRIPTS A LA VEZ")
        for idx, f in enumerate(files, 1):
            print(f"  [{idx}] {os.path.relpath(f, WORKSPACE)}")
        
        choice = input("\nNúmero de script o 'A' para respaldar todos: ").strip().lower()
        
        targets = []
        if choice == 'a':
            targets = files
        elif choice.isdigit() and 1 <= int(choice) <= len(files):
            targets = [files[int(choice) - 1]]
        else:
            print("⚠️ Opción cancelada o no válida.")
            return

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        art_backup_dir = os.path.join(BACKUP_DIR, f"art_{art_num:02d}")
        os.makedirs(art_backup_dir, exist_ok=True)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        count = 0
        for target_file in targets:
            fname = os.path.basename(target_file)
            dest = os.path.join(art_backup_dir, f"{ts}_{fname}")
            shutil.copy2(target_file, dest)
            cur.execute("INSERT INTO script_backups (artifact_number, script_path, backup_path) VALUES (?, ?, ?)",
                        (art_num, target_file, dest))
            count += 1

        conn.commit()
        conn.close()
        print(f"\n✅ ¡Copia masiva completada! {count} script(s) guardado(s) en:\n   {os.path.relpath(art_backup_dir, WORKSPACE)}")

    def view_backup_history(self, art_num):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, script_path, backup_path, timestamp FROM script_backups WHERE artifact_number=? ORDER BY timestamp ASC", (art_num,))
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print(f"⚠️ No existen respaldos registrados para el Artefacto {art_num}.")
            return

        print(f"\n📜 HISTORIAL DE COPIAS DE SEGURIDAD (Art {art_num}) - [Más Viejo -> Más Nuevo]:")
        for idx, r in enumerate(rows, 1):
            fname = os.path.basename(r[2])
            print(f"  [{idx}] {r[3]} | {fname}")

        choice = input("\nSelecciona número de copia para desplegar en cascada (o ENTER para salir): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(rows):
            target_backup = rows[int(choice) - 1][2]
            print("\n" + "="*80)
            print(f"📄 CONTENIDO DE RESPALDO: {target_backup}")
            print("="*80)
            try:
                with open(target_backup, "r", encoding="utf-8", errors="ignore") as f:
                    print(f.read())
            except Exception as e:
                print(f"❌ Error leyendo respaldo: {e}")
            print("="*80 + "\n")

    def manage_strategy_evolution(self, art_num):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT version, strategy_text, timestamp FROM strategy_history WHERE artifact_number=? ORDER BY timestamp ASC", (art_num,))
        rows = cur.fetchall()
        conn.close()

        print(f"\n🧠 CATÁLOGO DE EVOLUCIÓN DE ESTRATEGIAS (Art {art_num}):")
        if not rows:
            print("  ℹ️ Sin historial evolutivo previo. Mostrando versión inicial v1.0 por defecto.")
        else:
            for r in rows:
                print(f"  • [{r[2]}] Versión {r[0]}:\n    {r[1]}\n")

        opt = input("\n¿Deseas agregar una NUEVA actualización de estrategia? (s/N): ").strip().lower()
        if opt == 's':
            ver = input("Número de versión (ej. v1.1, v2.0): ").strip() or "v1.1"
            strat = input("Describe la nueva estrategia / cambios aprendidos: ").strip()
            if strat:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("INSERT INTO strategy_history (artifact_number, version, strategy_text) VALUES (?, ?, ?)",
                            (art_num, ver, strat))
                cur.execute("INSERT INTO artifact_specs (number, current_strategy) VALUES (?, ?) ON CONFLICT(number) DO UPDATE SET current_strategy=excluded.current_strategy",
                            (art_num, strat))
                conn.commit()
                conn.close()
                print(f"✅ Evolución {ver} registrada con éxito para el Artefacto {art_num}.")

    def run_menu(self):
        while True:
            print("\n" + "═"*60)
            print(" 🏛️  CCIA ARTEFACTO 66: MANUAL & REGISTRO EVOLUTIVO DE ARQUITECTURA")
            print("═"*60)
            art_input = input("Introduce número de Artefacto [1-66] (o 'Q' para salir): ").strip()
            
            if art_input.lower() == 'q':
                break
            if not art_input.isdigit():
                continue

            art_num = int(art_input)
            
            while True:
                print(f"\n--- SUBMENÚ ARTEFACTO [{art_num:02d}] ---")
                print("  [1] Ver Ficha Técnica Completa (JSON Cascada para Chat)")
                print("  [2] Realizar Copia de Seguridad de Script (Individual o Masiva [A])")
                print("  [3] Historial Cronológico de Copias de Seguridad")
                print("  [4] Catálogo y Registro de Evolución de Estrategias")
                print("  [0] Volver al Menú Principal")
                
                sub_opt = input("\nOpción: ").strip()
                if sub_opt == '1':
                    self.display_cascade_spec(art_num)
                elif sub_opt == '2':
                    self.backup_script(art_num)
                elif sub_opt == '3':
                    self.view_backup_history(art_num)
                elif sub_opt == '4':
                    self.manage_strategy_evolution(art_num)
                elif sub_opt == '0':
                    break

if __name__ == "__main__":
    app = CCiAManualRegistry()
    app.run_menu()
