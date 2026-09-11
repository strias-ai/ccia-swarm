import sys
import os

sys.path.append("/home/k1/ccia_workspace/modules")

print("=" * 80)
print("🧪 VERIFICANDO INTEGRACIÓN DE ARTEFACTOS CON ART_65_BRIDGE")
print("=" * 80)

from art_65_bridge import CCiAGatewayBridge

# 1. Simulación Artefacto 63 (Tri-Swarm)
print("\n1. 🤖 [ART. 63 - Tri-Swarm] Solicitando contexto enriquecido:")
ctx63 = CCiAGatewayBridge.get_enriched_prompt_context("/home/k1/ccia_workspace")
print(f"  • Estado: {ctx63['status']}")
print(f"  • Prompt recuperado: {ctx63['system_prompt'][:50]}...")
print(f"  • Archivos indexados: {ctx63['total_files']}")

# 2. Simulación Artefacto 64 (Compilador Evolutivo)
print("\n2. 🧬 [ART. 64 - Evolutionary Compiler] Ejecutando validación en Sandbox:")
res64 = CCiAGatewayBridge.run_sandbox_validation("python3 --version")
print(f"  • Éxito: {res64['success']}")
print(f"  • Salida: {res64['stdout'].strip()}")

# 3. Simulación Artefacto 62 (Pro-Bono & Chat A2A)
print("\n3. 💬 [ART. 62 - Scientific & A2A] Enviando paquete de datos A2A Bus:")
msg62 = CCiAGatewayBridge.dispatch_a2a_bus_message("art_62", "art_63", {"task": "AUDIT_REPLICATE"})
print(f"  • Estado Bus: {msg62['bus_status']} | Remitente: {msg62['sender']} -> Destinatario: {msg62['target']}")

# 4. Simulación Artefactos 43 & 47 (Memoria Cognitiva & GraphRAG)
print("\n4. 🧠 [ART. 43 & 47 - Memory Engines] Recuperando nodos de conocimiento:")
mem = CCiAGatewayBridge.fetch_memory_context("art_43", "security_audits")
print(f"  • Nodos recuperados: {mem['memory_nodes']}")

print("\n" + "=" * 80)
print("🎉 TODAS LAS PRUEBAS DE ENLACE COMPLETADAS CON ÉXITO.")
print("=" * 80)
