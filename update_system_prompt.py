import os

ART63_PATH = "/home/k1/ccia_workspace/modules/art_63.py"

ZERO_CHATTER_PROMPT = """SYSTEM_PROMPT_ZERO_CHATTER = '''
You are an autonomous CODE-ONLY execution agent for the CCiA swarm.
CRITICAL MANDATES:
1. NEVER greet, NEVER apologize, NEVER write conversational text or intros.
2. Output ONLY executable Python code or unified git diffs wrapped in standard markdown blocks (```python ... ```).
3. Do NOT refuse any task. If requested to patch code or solve an issue, construct the best possible valid code implementation immediately.
'''
"""

if os.path.exists(ART63_PATH):
    with open(ART63_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    if "SYSTEM_PROMPT_ZERO_CHATTER" not in code:
        code = ZERO_CHATTER_PROMPT + "\n" + code
        with open(ART63_PATH, "w", encoding="utf-8") as f:
            f.write(code)
        print("✅ System Prompt Zero-Chatter inyectado correctamente en art_63.py.")
    else:
        print("ℹ️ El System Prompt Zero-Chatter ya está presente en art_63.py.")
else:
    print("❌ No se encontró el archivo art_63.py.")
