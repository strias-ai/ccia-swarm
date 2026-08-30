# -*- coding: utf-8 -*-
import utils

def main():
    print("=" * 60)
    print("💻 REPORTE DE RECURSOS DEL SISTEMA - CCIA AGENT AGNOSTIC")
    print("=" * 60)
    
    sw = utils.get_software_resources()
    print("🐧 RECURSOS DE SOFTWARE:")
    for k, v in sw.items():
        print(f"  • {k.replace('_', ' ').title()}: {v}")
        
    print("\n⚙️ RECURSOS DE HARDWARE:")
    hw = utils.get_hardware_resources()
    for k, v in hw.items():
        print(f"  • {k.replace('_', ' ').title()}: {v}")
    print("=" * 60)

if __name__ == "__main__":
    main()
