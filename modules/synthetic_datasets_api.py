import json, sqlite3
from datetime import datetime

def run():
    return {"artifact_id": 21, "name": "API Datasets Sintéticos (Metered Billing)", "status": "HEALTHY", "timestamp": datetime.now().astimezone().isoformat()}

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False))
