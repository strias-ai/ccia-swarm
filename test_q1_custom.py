import sys
from modules.art_63 import TriSwarmOrchestrator

orch = TriSwarmOrchestrator()
q1_obj = orch.queen_brains[0]

prompt = (
    "Title: Consulta de Diagnostico de Infraestructura CCiA\n"
    "Body: El enjambre reina y los otros enjambres esta usando todo el potencial del CCIA?\n"
    "Cuentan con 16 cores CPU, 15.45 GB RAM, sin GPU NVIDIA, pero con Firecracker, Podman, "
    "ChromaDB, Qdrant, FAISS, sqlite_vec, gh, glab y tea instalados.\n\n"
    "INSTRUCCIÓN OBLIGATORIA: Responde ÚNICAMENTE un JSON estricto con el formato:\n"
    '{"valid": true, "reason": "explicacion"}\n'
    "Marca valid: false solo si detectas spam, texto troll, números repetitivos o solicitudes absurdas."
)

print("📡 Enviando consulta a Reina Q1...")
out = orch.execute_brain_turn(q1_obj, "Prueba Final Potencial CCiA", prompt, stream_live=True)
is_valid, reason = orch.parse_antispam_decision(out)

print("\n" + "="*80)
print(f"📊 Decisión Parseada : VÁLIDO = {is_valid}")
print(f"📊 Razón Registrada : {reason}")
print("="*80)
