from fastapi.testclient import TestClient
from main_api import app

client = TestClient(app)

print("--------------------------------------------------------")
print("1. Acceso a Endpoint Público:")
r1 = client.get("/v1/public/status")
print(f"   HTTP {r1.status_code}: {r1.json()}")

print("\n2. Acceso Prémium con usuario ACTIVO (student@ccia.edu):")
r2 = client.get("/v1/premium/courses", headers={"X-User-Email": "student@ccia.edu"})
print(f"   HTTP {r2.status_code}: {r2.json()}")

print("\n3. Acceso Prémium con usuario CANCELADO (lifecycle_user@ccia.edu):")
r3 = client.get("/v1/premium/courses", headers={"X-User-Email": "lifecycle_user@ccia.edu"})
print(f"   HTTP {r3.status_code}: {r3.json()}")

print("\n4. Acceso Prémium con usuario INEXISTENTE (ghost@ccia.edu):")
r4 = client.get("/v1/premium/courses", headers={"X-User-Email": "ghost@ccia.edu"})
print(f"   HTTP {r4.status_code}: {r4.json()}")
print("--------------------------------------------------------")
