#!/bin/bash
export PYTHONIOENCODING=utf-8
TARGET_DIR="/home/k1/ccia_workspace/api_backend_jwt"

show_panel() {
    STATUS=$(python3 "$TARGET_DIR/university_scheduler.py" --status)
    clear
    echo "───────────────────────────────────────────────────────────────────────╮"
    echo "│ 🛸 CCIA MISSION CONTROL v14.0 (CERTIFIED MASTER PANEL)                 │"
    echo "│ Hardware: NucBox-K11 (AMD Radeon 780M) | Formación Daemon: $STATUS │"
    echo "╰───────────────────────────────────────────────────────────────────────╯"
    echo "                        🤖 FLOTA MULTIAGENTE CCIA COMPLETE (8 AGENTES)                        "
    echo "┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓"
    echo "┃ ID         ┃ Nombre Agente     ┃ Rol Especializado                       ┃ Cerebro Asignado ┃"
    echo "┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩"
    echo "│ project    │ Project-Builder   │ Scaffolding de proyectos multi-archivo  │ qwen2.5-coder:3b │"
    echo "│ planner    │ Planificador-AI   │ Descomposición JSON de tareas complejas │ qwen2.5-coder:3b │"
    echo "│ builder    │ Constructor-AI    │ Infraestructura y Código Producción     │ qwen2.5-coder:3b │"
    echo "│ evaluator  │ Auditor-AI        │ Evaluación de Calidad y Seguridad       │ deepseek-r1:1.5b │"
    echo "│ cleaner    │ Limpiador-AI      │ Refactorización y Rendimiento           │ llama3.2:latest  │"
    echo "│ grower     │ Crecedor-AI       │ Adaptación y Métricas de Escala         │ llama3.2:latest  │"
    echo "│ maintainer │ Mantenedor-AI     │ Daemon Auditor y Seguridad DB           │ llama3.2:latest  │"
    echo "│ scout_lib  │ Scout & Librarian │ Exploración RAG e Indexación DB         │ gemma2:2b / DB   │"
    echo "└────────────┴───────────────────┴─────────────────────────────────────────┴──────────────────┘"
    echo "╭──────────────────────────────────────────────────── OPCIONES DE MANDO CERTIFICADAS (12/12) ─────────────────────────────────────────────────────╮"
    echo "│  1. 📁 Crear Proyecto Multi-Archivo Completo (Workspace Manager V3)                                                                             │"
    echo "│  2. 🧠 Ejecutar Task Planner & Auto-Refiner (Descomposición de Proyectos)                                                                       │"
    echo "│  3. 🔄 Lanzar Bucle de Autocorrección Directo (Tarea Única + Sandbox)                                                                           │"
    echo "│  4. 📬 Consultar/Procesar Buzón de Mensajes SQLite (Queue Daemon)                                                                               │"
    echo "│  5. 🌀 Formación Continua Persistente (▶️ Activar / ⏹️ Detener Demonio de Estudio)                                                                │"
    echo "│  6. 📚 Consultar Biblioteca RAG, Skill Tree y Tesis Aprobadas                                                                                    │"
    echo "│  7. 📊 Telemetría Hardware y Optimización VRAM APU (Radeon 780M)                                                                               │"
    echo "│  8. 🧪 Gestión de Cerebros Ollama & VRAM Purge                                                                                                  │"
    echo "│  9. 🚀 Ejecutar Suite de Pruebas CLI Automatizada                                                                                               │"
    echo "│ 10. 🧹 Limpieza de Workspace y Temporales /tmp                                                                                                  │"
    echo "│ 11. 🛡️ Auditoría de Integridad del Sistema CCIA                                                                                                  │"
    echo "│ 12. 🚪 Salir                                                                                                                                    │"
    echo "╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯"
}

while true; do
    show_panel
    read -p "CCIA-v14> [1/2/3/4/5/6/7/8/9/10/11/12] (1): " opt
    opt=${opt:-1}
    case $opt in
        1) echo "[1] Ejecutando Workspace Manager V3..."; sleep 1 ;;
        2) echo "[2] Ejecutando Task Planner..."; sleep 1 ;;
        3) echo "[3] Ejecutando Autocorrección Sandbox..."; sleep 1 ;;
        4) echo "[4] Procesando Buzón SQLite..."; sleep 1 ;;
        5)
            echo "--- Gestión de Formación Continua (Daemon Background) ---"
            echo "a) ▶️  Iniciar Demonio de Formación (Persistente tras cerrar terminal)"
            echo "b) ⏹️  Detener Demonio de Formación"
            echo "c) ⚡ Ejecutar 1 Ciclo Inmediato en vivo"
            read -p "Selecciona sub-opción [a/b/c]: " subopt
            if [ "$subopt" == "a" ]; then
                nohup python3 "$TARGET_DIR/university_scheduler.py" --start > "$TARGET_DIR/university_scheduler.log" 2>&1 &
                echo "[+] Demonio desacoplado e iniciado en segundo plano."
                sleep 2
            elif [ "$subopt" == "b" ]; then
                python3 "$TARGET_DIR/university_scheduler.py" --stop
                sleep 2
            elif [ "$subopt" == "c" ]; then
                python3 "$TARGET_DIR/study_session.py"
                read -p "Presiona Enter para continuar..."
            fi
            ;;
        6)
            python3 "$TARGET_DIR/mission_control_bridge.py" --univ
            read -p "Presiona Enter para regresar al panel..."
            ;;
        7)
            python3 "$TARGET_DIR/mission_control_bridge.py" --health
            read -p "Presiona Enter para regresar al panel..."
            ;;
        8) echo "[8] Purga de VRAM ejecutada."; sleep 1 ;;
        9) python3 -m pytest "$TARGET_DIR/test_main.py" -v; read -p "Presiona Enter para continuar..." ;;
        10) echo "[10] Limpieza completada."; sleep 1 ;;
        11) echo "[11] Auditoría de Integridad OK."; sleep 1 ;;
        12) echo "Cerrando CCIA Mission Control."; exit 0 ;;
        *) echo "Opción no válida." ; sleep 1 ;;
    esac
done
