import re
import os

mando_path = "/home/k1/ccia_workspace/ccia_mando_63.py"

if os.path.exists(mando_path):
    with open(mando_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Inyección de función limpiadora de etiquetas <think> de DeepSeek-R1
    cleaner_func = """
def clean_r1_output(text: str) -> str:
    \"\"\"Elimina el bloque de pensamiento de DeepSeek-R1 y deja solo la respuesta de gobernanza.\"\"\"
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned.strip()
"""

    if "def clean_r1_output" not in content:
        content = cleaner_func + "\n" + content
        # Remplazar salidas de la Reina para que usen la limpieza
        content = content.replace("print(q1_response)", "print(clean_r1_output(q1_response))")
        
        with open(mando_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Parche de extracción limpia de DeepSeek-R1 inyectado en ccia_mando_63.py")
    else:
        print("ℹ️ El limpiador de traza R1 ya existe en el archivo.")
