# -*- coding: utf-8 -*-
"""
CCIA APU THERMAL GOVERNOR v1.0
Supervisa sensores térmicos de la NucBox-K11 para prevenir estrangulamiento térmico.
"""
import os
import time

def get_cpu_temperature() -> float:
    thermal_path = "/sys/class/thermal/thermal_zone0/temp"
    if os.path.exists(thermal_path):
        try:
            with open(thermal_path, "r") as f:
                return float(f.read().strip()) / 1000.0
        except Exception:
            return 45.0
    return 45.0

def audit_and_cool_down():
    temp = get_cpu_temperature()
    if temp > 82.0:
        print(f"🔥 [ALERTA TÉRMICA] APU a {temp:.1f}°C. Aplicando pausa de enfriamiento (5s)...")
        time.sleep(5)
        return False, temp
    return True, temp

if __name__ == "__main__":
    ok, t = audit_and_cool_down()
    print(f"🌡️ Estado Térmico APU: {t:.1f}°C | Estado: {'Óptimo' if ok else 'En Friamiento'}")
