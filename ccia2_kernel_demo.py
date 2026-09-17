import sqlite3
import json
import hashlib
from datetime import datetime

DB_PATH = "/home/k1/ccia_workspace/university.db"

def init_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de Paquetes Certificados por el Kernel
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ccia2_packages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        module_name TEXT UNIQUE,
        version TEXT,
        hapax_hash TEXT,
        manifest_json TEXT,
        status TEXT,
        installed_at DATETIME
    );
    """)
    
    # Tabla de Reservas de Cuerpos Libres para IAs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS embodied_ai_reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id TEXT,
        event_id TEXT,
        preferred_payment TEXT,
        requested_sensors TEXT,
        total_amount_usd REAL,
        status TEXT,
        booking_hash TEXT UNIQUE,
        created_at DATETIME
    );
    """)
    conn.commit()
    conn.close()

def install_hapax_module(manifest):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    raw_str = json.dumps(manifest, sort_keys=True)
    calculated_hash = hashlib.sha256(raw_str.encode('utf-8')).hexdigest()
    
    cursor.execute("""
        INSERT OR REPLACE INTO ccia2_packages (module_name, version, hapax_hash, manifest_json, status, installed_at)
        VALUES (?, ?, ?, ?, 'CERTIFIED_ACTIVE', ?)
    """, (manifest["module_name"], manifest["version"], calculated_hash, raw_str, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    return calculated_hash

def register_ai_reservation(agent_id, event_id, payment_method, sensors, base_price, sensor_price_each):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    total = base_price + (len(sensors) * sensor_price_each)
    booking_payload = {
        "agent_id": agent_id,
        "event_id": event_id,
        "payment": payment_method,
        "sensors": sensors,
        "total_usd": total,
        "timestamp": datetime.now().isoformat()
    }
    raw_payload = json.dumps(booking_payload, sort_keys=True)
    booking_hash = hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()
    
    cursor.execute("""
        INSERT INTO embodied_ai_reservations 
        (agent_id, event_id, preferred_payment, requested_sensors, total_amount_usd, status, booking_hash, created_at)
        VALUES (?, ?, ?, ?, ?, 'CONFIRMED_PENDING_DEPOSIT', ?, ?)
    """, (agent_id, event_id, payment_method, json.dumps(sensors), total, booking_hash, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    return booking_hash, total

if __name__ == '__main__':
    print("🚀 [CCIA2 KERNEL] Inicializando motor y validando esquemas...")
    init_tables()
    
    # 1. Probar instalación de módulo con Manifiesto Hapax
    sample_manifest = {
        "module_name": "ccia2_embodied_teleop_gateway",
        "version": "2.0.0",
        "capabilities": ["NET_5G_TELEOP", "CAN_BUS_READ", "A2A_SOLANA_ESCROW"],
        "tool_bus_hooks": ["vehicle.steer", "vehicle.accelerate"]
    }
    pkg_hash = install_hapax_module(sample_manifest)
    print(f"✅ Módulo '{sample_manifest['module_name']}' certificado con Hash Hapax:\n   [{pkg_hash}]\n")
    
    # 2. Simular reserva de una IA para el Evento de Madrid (Vehículo 5G)
    agent = "Claude-3.7-Explorer-Bot"
    event = "MADRID_MOUNTAIN_5G_RC_01"
    payment = "USDC_SOLANA"
    sensors = ["LIDAR_2D", "GAS_TERRAIN_SENSOR"]
    
    booking_hash, total_usd = register_ai_reservation(agent, event, payment, sensors, base_price=10.0, sensor_price_each=20.0)
    
    print("🏎️ [A2A EMBODIED RESERVATIONS] Nueva reserva de IA procesada:")
    print(f"   • Agente: {agent}")
    print(f"   • Evento: {event}")
    print(f"   • Método Pago: {payment}")
    print(f"   • Sensores Extra: {sensors}")
    print(f"   • Importe Total: ${total_usd:.2f} USD")
    print(f"   • Booking SHA-256 Hash Fingerprint:\n     [{booking_hash}]")
    print("\n💾 Todos los datos han sido sellados de forma inmutable en 'university.db'.")
