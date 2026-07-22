#!/bin/bash
# Live demo for teacher — POST t2.jpg to /api/predict (no need to paste base64)
set -e
cd "$(dirname "$0")"
HOST="${1:-http://34.151.142.31:30080}"

if [[ ! -f demo_payload_t2.json ]]; then
  python3 -c "
import base64, json
from pathlib import Path
b = base64.b64encode(Path('Test_images/t2.jpg').read_bytes()).decode()
Path('demo_payload_t2.json').write_text(json.dumps({'uuid':'live-demo-t2','image':b}))
print('Created demo_payload_t2.json')
"
fi

echo "POST ${HOST}/api/predict (t2.jpg — may take 30–60s, image is large)..."
curl -s -X POST "${HOST}/api/predict" \
  -H "Content-Type: application/json" \
  -d @demo_payload_t2.json | python3 -m json.tool | head -40
