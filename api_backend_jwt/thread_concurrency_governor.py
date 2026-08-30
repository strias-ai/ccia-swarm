# -*- coding: utf-8 -*-
"""
CCIA THREAD CONCURRENCY GOVERNOR v1.0
Controla el límite dinámico de hilos para tareas en segundo plano en el Queue Daemon (Opción 4).
"""
import os
import psutil

def get_optimal_thread_limit() -> int:
    cpu_count = os.cpu_count() or 4
    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
    except Exception:
        cpu_usage = 50.0
    
    if cpu_usage > 80.0:
        return max(1, cpu_count // 4)
    elif cpu_usage > 50.0:
        return max(2, cpu_count // 2)
    return cpu_count

if __name__ == "__main__":
    limit = get_optimal_thread_limit()
    print(f"⚡ Límite óptimo de hilos de fondo: {limit}")
