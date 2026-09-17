import sys
import json
import hashlib
import os

def verify_and_compile(script_path):
    manifest_path = script_path.replace(".py", ".manifest.json")
    if not os.path.exists(manifest_path):
        print(f"❌ [KERNEL REJECTED] Bloqueado: Falta el manifiesto Hapax (.manifest.json) para {script_path}")
        sys.exit(1)
        
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
        
    with open(script_path, "rb") as f:
        code_hash = hashlib.sha256(f.read()).hexdigest()
        
    if manifest.get("code_sha256") != code_hash:
        print("❌ [KERNEL REJECTED] Modificación no autorizada. La firma SHA-256 del código no coincide.")
        sys.exit(1)
        
    print(f"✅ [KERNEL CERTIFIED] Módulo '{manifest.get('module_name')}' verificado correctamente.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        verify_and_compile(sys.argv[1])
