# -*- coding: utf-8 -*-
import os, sys, platform, subprocess

def get_software_resources():
    return {
        "os": f"{platform.system()} {platform.release()}",
        "python_version": platform.python_version(),
        "architecture": platform.machine(),
        "hostname": platform.node()
    }

def get_hardware_resources():
    hardware_info = {
        "cpu_count": os.cpu_count(),
        "ram_total_gb": "N/A",
        "gpu_apu": "AMD Radeon 780M (APU)"
    }
    
    # Lectura de RAM desde /proc/meminfo
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if "MemTotal" in line:
                    kb = int(line.split()[1])
                    hardware_info["ram_total_gb"] = f"{kb / (1024**2):.2f} GB"
                    break
    except Exception:
        pass
        
    return hardware_info
