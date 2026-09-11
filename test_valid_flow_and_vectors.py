import sqlite3
import json
from modules.art_63 import TriSwarmOrchestrator

orch = TriSwarmOrchestrator()

print("================================================================================")
print("🧪 1. BÚSQUEDA SEMÁNTICA EN MEMORIA VECTORIAL (bounty_vector_memory)")
print("================================================================================")
conn = sqlite3.connect("/home/k1/ccia_workspace/university.db")
cursor = conn.cursor()
cursor.execute("SELECT artifact_id, text_content FROM bounty_vector_memory LIMIT 3")
rows = cursor.fetchall()
for art_id, content in rows:
    print(f"  • [{art_id}]: {content[:90]}...")
conn.close()

print("\n================================================================================")
print("🧪 2. PRUEBA DE FLUJO VÁLIDO EN REINA Q1 (STREAMING EN VIVO)")
print("================================================================================")
q1_obj = orch.queen_brains[0]
valid_prompt = (
    "Title: Fix memory leak in buffer allocation\n"
    "Body: Need to patch a memory leak in C++ buffer allocation within the network module."
)

# Se activa stream_live=True para evitar el bloqueo aparente de consola
out = orch.execute_brain_turn(q1_obj, "Valid Issue Test", valid_prompt, stream_live=True)
is_valid, reason = orch.parse_antispam_decision(out)

print("\n--------------------------------------------------------------------------------")
print(f"  • Clasificación : {'✅ VÁLIDO' if is_valid else '❌ SPAM'}")
print(f"  • Justificación : {reason}")
print("================================================================================")
