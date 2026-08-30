import urllib.request
import json
from verify_subscription import check_user_subscription

TEST_USER = "lifecycle_user@ccia.edu"
ENDPOINT = "http://localhost:8080/v1/stripe/webhook"

def send_event(event_id, event_type, metadata):
    payload = json.dumps({
        "id": event_id,
        "type": event_type,
        "data": {"object": {"amount": 4900, "customer": "cus_test", "metadata": metadata}}
    }).encode('utf-8')
    req = urllib.request.Request(ENDPOINT, data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

print("--------------------------------------------------------")
print("1. Estado inicial del usuario:")
print(f"   Acceso: {check_user_subscription(TEST_USER)}")

print("\n2. Simulando Pago Exitoso (payment_intent.succeeded)...")
send_event("evt_live_1", "payment_intent.succeeded", {"user_email": TEST_USER})
print(f"   Acceso prémium tras pago: {check_user_subscription(TEST_USER)}")

print("\n3. Simulando Cancelación de Suscripción (customer.subscription.deleted)...")
send_event("evt_live_2", "customer.subscription.deleted", {"user_email": TEST_USER})
print(f"   Acceso prémium tras cancelación: {check_user_subscription(TEST_USER)}")
print("--------------------------------------------------------")
