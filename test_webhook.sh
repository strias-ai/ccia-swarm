#!/bin/bash
ENDPOINT="http://localhost:8080/v1/stripe/webhook"
DB="/home/k1/ccia_workspace/university.db"
EVENT_ID="evt_test_$(date +%s)"

echo "--------------------------------------------------------"
echo "🧪 [PRUEBA 1]: Envío de evento nuevo ($EVENT_ID)..."
RESP1=$(curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d "{\"id\": \"$EVENT_ID\", \"type\": \"payment_intent.succeeded\", \"data\": {\"object\": {\"amount\": 4900}}}")
echo "Respuesta: $RESP1"

echo -e "\n🧪 [PRUEBA 2]: Envío de evento DUPLICADO (Verificación de Idempotencia)..."
RESP2=$(curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d "{\"id\": \"$EVENT_ID\", \"type\": \"payment_intent.succeeded\", \"data\": {\"object\": {\"amount\": 4900}}}")
echo "Respuesta: $RESP2"

echo -e "\n📊 [VERIFICACIÓN DB]: Registros en processed_stripe_events..."
sqlite3 "$DB" "SELECT event_id, event_type, amount, processed_at FROM processed_stripe_events WHERE event_id='$EVENT_ID';"
echo "--------------------------------------------------------"
