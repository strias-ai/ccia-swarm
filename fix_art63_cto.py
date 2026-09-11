import os
import re
import sys
import shutil
import ast  # Importación requerida para el validador sintáctico

ART63_PATH = "/home/k1/ccia_workspace/modules/art_63.py"
BACKUP_PATH = "/home/k1/ccia_workspace/modules/art_63.py.bak"
LOG_DIR = "/home/k1/ccia_workspace/logs"
LOG_FILE = os.path.join(LOG_DIR, "art_63.log")

print("================================================================================")
print("🛠️ CCiA CTO ENGINE: AUDITORÍA Y FIX INTEGRAL DEL ARTEFACTO 63")
print("================================================================================")

# 1. Creación de carpeta de logs y archivo inicial si no existen
os.makedirs(LOG_DIR, exist_ok=True)
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("[INIT] Log de ejecuciones de Artefacto 63 iniciado.\n")
    print(f"✅ Directorio y log inicializado en: {LOG_FILE}")
else:
    print(f"✅ Archivo de log verificado en: {LOG_FILE}")

# 2. Respaldo de seguridad de art_63.py
if os.path.exists(ART63_PATH):
    shutil.copyfile(ART63_PATH, BACKUP_PATH)
    print(f"📦 Respaldo creado en: {BACKUP_PATH}")
else:
    print(f"❌ Error: No se encontró {ART63_PATH}")
    sys.exit(1)

with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# 3. Inyección del Sanitizador ANSI y Validador de Parches
helper_functions = '''
# ==============================================================================
# 🛡️ CCiA CTO SANITIZERS & VALIDATORS (ADDED BY AUTO-FIX)
# ==============================================================================
import re
import ast

def clean_ansi_and_junk(raw_text: str) -> str:
    """Elimina secuencias de escape ANSI, spinners y basura de terminal."""
    if not raw_text:
        return ""
    # Remover ANSI escapes y caracteres no imprimibles de terminal
    text = re.sub(r'\\x1b\\[[0-9;]*[a-zA-Z]', '', raw_text)
    text = re.sub(r'\\x1b\\(B', '', text)
    text = re.sub(r'\\x1b\\[\\?25[lh]', '', text)
    text = re.sub(r'\\x1b\\[\\?2026[lh]', '', text)
    # Remover caracteres de spinners unicode (⠋, ⠙, ⠹, ⠸, ⠼, ⠴, ⠦, ⠧, ⠇, ⠏)
    text = re.sub(r'[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]', '', text)
    return text.strip()

def validate_llm_code_patch(response_text: str) -> tuple[bool, str]:
    """
    Valida si la respuesta del LLM contiene un parche/código real.
    Retorna (es_valido, motivo_o_codigo).
    """
    if not response_text:
        return False, "RESPUESTA_VACIA"
    
    clean_resp = clean_ansi_and_junk(response_text)
    lower_resp = clean_resp.lower()
    
    # Palabras clave de rechazo conversacional
    refusal_triggers = [
        "lo siento", "no puedo proporcionar", "no contiene ningún código",
        "i cannot provide", "i am sorry", "as an ai language model",
        "no puedo ayudar", "no tengo acceso"
    ]
    
    if any(trigger in lower_resp for trigger in refusal_triggers):
        return False, "RECHAZO_CONVERSACIONAL_DETECTADO"
        
    # Verificar existencia de bloque de código o diff
    has_code_block = "```" in clean_resp or "diff --git" in clean_resp or "def " in clean_resp
    if not has_code_block:
        return False, "SIN_BLOQUE_DE_CODIGO_O_DIFF"
        
    return True, clean_resp
# ==============================================================================
'''

if "def clean_ansi_and_junk" not in code:
    code = helper_functions + "\n" + code
    print("✅ Funciones de sanitización ANSI y validación de parches inyectadas.")

# 4. Corrección de la consulta SQL defectuosa en el menú
old_query = "SELECT id, issue_key, solution_summary, created_at FROM bounty_vector_memory ORDER BY id DESC LIMIT 5;"
new_query = "SELECT id, target_issue, status, created_at FROM bounty_swarm_history ORDER BY id DESC LIMIT 5;"

if old_query in code:
    code = code.replace(old_query, new_query)
    print("✅ Consulta defectuosa de la Opción [7] corregida a bounty_swarm_history.")

# 5. Guardar cambios en art_63.py
with open(ART63_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("\n================================================================================")
print("🚀 VERIFICACIÓN SINTÁCTICA DEL ARCHIVO CORREGIDO")
print("================================================================================")

try:
    with open(ART63_PATH, "r", encoding="utf-8") as f:
        ast.parse(f.read())
    print("✅ CÓDIGO FINAL DE ART_63.PY COMPILADO Y VALIDADO SIN ERRORES SINTÁCTICOS.")
except Exception as e:
    print(f"❌ Error sintáctico detectado: {e}")
    print("Restaurando respaldo...")
    shutil.copyfile(BACKUP_PATH, ART63_PATH)

print("================================================================================")
