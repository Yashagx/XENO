#!/bin/bash
set -e
echo "Testing login..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@xeno.in","password":"admin123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "Token: ${TOKEN:0:30}..."

echo ""
echo "Testing XenoPilot (GROQ)..."
RESULT=$(curl -s -X POST http://localhost:8000/api/v1/xenopilot/chat \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"Who are my top 10 customers by spend?","conversation_history":[]}')

echo "$RESULT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'answer' in d:
    print('GROQ SUCCESS!')
    print('Answer preview:', d['answer'][:200])
else:
    print('ERROR:', d)
"
