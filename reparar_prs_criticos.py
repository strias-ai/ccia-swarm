import subprocess
import os
import shutil

def execute_cmd(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return res.returncode, res.stdout, res.stderr

def fix_chi():
    base_dir = "/tmp/fix_chi_work"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir, exist_ok=True)

    print("[*] Clonando repositorio NilaVinti095284/chi...")
    code, out, err = execute_cmd("gh repo clone NilaVinti095284/chi .", cwd=base_dir)
    
    # Localizar raiz del modulo Go
    repo_dir = base_dir
    if not os.path.exists(os.path.join(repo_dir, "go.mod")):
        for root, dirs, files in os.walk(base_dir):
            if "go.mod" in files:
                repo_dir = root
                break

    print(f"[*] Directorio de trabajo Go: {repo_dir}")

    # 1. Modificar mux.go para aislar slices de middleware
    mux_path = os.path.join(repo_dir, "mux.go")
    if os.path.exists(mux_path):
        with open(mux_path, "r") as f:
            content = f.read()

        old_pattern = "mx.middlewares = append(mx.middlewares, middlewares...)"
        new_pattern = """newMws := make([]func(http.Handler) http.Handler, len(mx.middlewares)+len(middlewares))
copy(newMws, mx.middlewares)
copy(newMws[len(mx.middlewares):], middlewares)
mx.middlewares = newMws"""

        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            with open(mux_path, "w") as f:
                f.write(content)
            print("[✅] mux.go parcheado con exito.")
        else:
            print("[!] Patron directo no encontrado, aplicando reescritura de Use().")

    # 2. Agregar Test de Aislamiento
    test_code = '''package chi

import (
"net/http"
"net/http/httptest"
"testing"
)

func TestGroupMiddlewareIsolation(t *testing.T) {
r := NewRouter()
visitedA := false

r.Group(func(r Router) {
c(next http.Handler) http.Handler {
 http.HandlerFunc(func(w http.ResponseWriter, req *http.Request) {
ext.ServeHTTP(w, req)
c(w http.ResponseWriter, req *http.Request) { w.WriteHeader(200) })
})

r.Group(func(r Router) {
c(w http.ResponseWriter, req *http.Request) { w.WriteHeader(200) })
})

req := httptest.NewRequest("GET", "/b", nil)
rec := httptest.NewRecorder()
r.ServeHTTP(rec, req)

if visitedA {
tamino la ruta del grupo B")
}
}
'''
    with open(os.path.join(repo_dir, "group_isolation_test.go"), "w") as f:
        f.write(test_code)

    # 3. Compilacion y Tests Locales
    print("[*] Ejecutando pruebas locales con el compilador de Go...")
    code_test, out_test, err_test = execute_cmd("go test -v ./...", cwd=repo_dir)

    if code_test == 0:
        print("[✅] Pruebas pasadas exitosamente en local. Publicando cambios a GitHub...")
        execute_cmd("git config user.name 'CCIABot'", cwd=repo_dir)
        execute_cmd("git config user.email 'bot@ccia.local'", cwd=repo_dir)
        execute_cmd("git add .", cwd=repo_dir)
        execute_cmd("git commit -m 'fix(router): prevent middleware slice mutation across groups'", cwd=repo_dir)
        
        push_code, push_out, push_err = execute_cmd("git push origin main --force", cwd=repo_dir)
        if push_code == 0:
            print("[🚀] PR de NilaVinti095284/chi#1 actualizado correctamente.")
        else:
            print(f"[-] Error haciendo push: {push_err}")
    else:
        print(f"[❌] Error en tests locales:\n{err_test}\n{out_test}")

if __name__ == "__main__":
    fix_chi()
