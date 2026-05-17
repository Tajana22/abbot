#!/bin/bash

set -e

echo "Creating Hetzner VPS..."

# DEBUG (тимчасово)
echo "TOKEN LENGTH: ${#HETZNER_TOKEN}"
echo "TOKEN PREFIX: ${HETZNER_TOKEN:0:4}"

if [ -z "$HETZNER_TOKEN" ]; then
  echo "ERROR: HETZNER_TOKEN is empty"
  exit 1
fi

RESPONSE=$(curl -s -X POST "https://api.hetzner.cloud/v1/servers" \
  -H "Authorization: Bearer $HETZNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ephemeral-runner",
    "server_type": "cx11",
    "image": "ubuntu-22.04",
    "start_after_create": true
  }')

echo "Response:"
echo "$RESPONSE"
