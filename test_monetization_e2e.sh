#!/bin/bash
export LANG=C.UTF-8
ENDPOINT_WEBHOOK="http://localhost:8080/v1/stripe/webhook"
ENDPOINT_API="http://localhost:8000/v1/premium/courses"
TEST_USER="vip_github_client@devsecops.io"
EVENT_ID="evt_live_e2e_$(date +%s)"

echo "⚡ ================================================================= ⚡"
echo "👑 CCIA MONETIZATION E2E VALIDATION SUITE"
echo "⚡ ================================================================= ⚡"

echo -e "\n1. INTENTO DE ACCESO PREVIO AL PAGO (Debe retornar 403 Forbidden):"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$ENDPOINT_API" -H "X-User-Email: $TEST_USER")
echo "   Respuesta HTTP API (:8000) -> Code: $HTTP_CODE"

echo -e "\n2. SIMULACIÓN DE EVENTO WEBHOOK STRIPE POST-PAGO (Puerto :8080):"
PAYLOAD=$(cat <<JSON
{
  "id": "$EVENT_ID",
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "amount": 49900,
      "customer": "cus_VIP_PRO_99",
      "metadata": {
        "user_email": "$TEST_USER",
        "source": "github_outbound_issue_v2"
      }
    }
  }
}
JSON
)

RESP_WEBHOOK=$(curl -s -X POST "$ENDPOINT_WEBHOOK" -H "Content-Type: application/json" -d "$PAYLOAD")
echo "   Respuesta Webhook Listener -> $RESP_WEBHOOK"

echo -e "\n3. VERIFICACIÓN DE ESTADO EN BASE DE DATOS (university.db):"
sqlite3 /home/k1/ccia_workspace/university.db -header -column \
  "SELECT user_email, status, updated_at FROM user_subscriptions WHERE user_email='$TEST_USER';"

echo -e "\n4. RE-INTENTO DE ACCESO POST-PAGO A RECURSOS PRÉMIUM (Debe retornar 200 OK):"
API_RESPONSE=$(curl -s -w "\n   [HTTP Code: %{http_code}]\n" "$ENDPOINT_API" -H "X-User-Email: $TEST_USER")
echo "   Respuesta API Core:"
echo "$API_RESPONSE"

echo -e "\n5. PRUEBA DE RESILIENCIA / IDEMPOTENCIA (Re-envío del mismo Event ID):"
RESP_DUPLICATE=$(curl -s -X POST "$ENDPOINT_WEBHOOK" -H "Content-Type: application/json" -d "$PAYLOAD")
echo "   Respuesta Webhook Duplicado -> $RESP_DUPLICATE"
echo "⚡ ================================================================= ⚡"
