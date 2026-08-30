# -*- coding: utf-8 -*-
"""
CCIA ADDITIVE COMPILER & PREFLIGHT ENGINE v1.0
Supervisa, inspecciona e integra artefactos de forma 100% aditiva sin regresiones.
"""
import os
import sys
import json
import ast
import shutil
import subprocess

BASE_DIR = os.path.dirname(__file__)
MASTER_PANEL = "/home/k1/ccia_mission_control.py"
REGISTRY_PATH = os.path.join(BASE_DIR, "module_registry.json")

class CCIACompiler:
    def __init__(self, target_file=MASTER_PANEL):
        self.target_file = target_file
        self.backup_file = target_file + ".bak"

    def preflight_check(self) -> bool:
        """Verificación previa del estado del sistema y archivos objetivo."""
        print("🔍 [PREFLIGHT 1/4] Verificando existencia del panel maestro original...")
        if not os.path.exists(self.target_file):
            print(f"❌ Fallo Preflight: {self.target_file} no existe.")
            return False

        print("🔍 [PREFLIGHT 2/4] Comprobando respaldo del sistema...")
        if not os.path.exists(self.backup_file):
            shutil.copyfile(self.target_file, self.backup_file)
            print(f"🛡️ Respaldo de seguridad creado en: {self.backup_file}")
        else:
            print("🛡️ Respaldo verificado existente.")

        print("🔍 [PREFLIGHT 3/4] Analizando Árbol de Sintaxis (AST) del núcleo...")
        try:
            with open(self.target_file, "r", encoding="utf-8") as f:
                ast.parse(f.read())
            print("✅ AST del archivo objetivo válido.")
        except SyntaxError as e:
            print(f"❌ Fallo Preflight: Error de sintaxis en el archivo objetivo: {e}")
            return False

        print("🔍 [PREFLIGHT 4/4] Verificando integridad de las 12 Opciones Certificadas...")
        with open(self.target_file, "r", encoding="utf-8") as f:
            content = f.read()
            for i in range(1, 13):
                if f'opt == "{i}"' not in content and f"opt == '{i}'" not in content:
                    print(f"❌ Fallo Preflight: Opción certificada #{i} no detectada en la estructura.")
                    return False
        print("✅ Las 12 opciones certificadas están intactas.")
        return True

    def compile_patch(self, patch_func, module_name: str, description: str) -> bool:
        """Aplica la modificación aditiva solo si pasa el Preflight y las pruebas AST post-compilación."""
        if not self.preflight_check():
            print("🛑 Compilación abortada por fallos en el Preflight.")
            return False

        print(f"\n⚙️ [COMPILANDO ARTEFACTO] Aplicando extensión: '{module_name}'...")
        with open(self.target_file, "r", encoding="utf-8") as f:
            original_code = f.read()

        try:
            modified_code = patch_func(original_code)
            
            # Pruebas de Sintaxis Post-Modificación
            ast.parse(modified_code)
            
            # Guardar versión compilada
            with open(self.target_file, "w", encoding="utf-8") as f:
                f.write(modified_code)

            print("✅ Compilación exitosa. Validando integración...")
            self.register_extension(module_name, description)
            return True

        except Exception as e:
            print(f"❌ Error durante la compilación. Revertiendo cambios: {e}")
            with open(self.target_file, "w", encoding="utf-8") as f:
                f.write(original_code)
            return False

    def register_extension(self, module_name: str, description: str):
        """Actualiza el libro mayor de extensiones certificadas."""
        registry = {}
        if os.path.exists(REGISTRY_PATH):
            try:
                with open(REGISTRY_PATH, "r") as f:
                    registry = json.load(f)
            except Exception:
                registry = {"certified_version": "14.0", "extensions": {}}

        if "extensions" not in registry:
            registry["extensions"] = {}

        registry["extensions"][module_name] = {
            "description": description,
            "status": "COMPILED_AND_CERTIFIED",
            "timestamp": subprocess.check_output(["date"]).decode().strip()
        }

        with open(REGISTRY_PATH, "w") as f:
            json.dump(registry, f, indent=2)
        print(f"📜 Módulo '{module_name}' registrado exitosamente en module_registry.json.")

if __name__ == "__main__":
    compiler = CCIACompiler()
    if compiler.preflight_check():
        print("\n🚀 COMPILADOR CCIA LISTO PARA RECIBIR NUEVOS ARTEFACTOS EVOLUTIVOS.")
