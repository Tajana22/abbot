#!/bin/bash

set -e

echo "Creating Hetzner VPS..."

# DEBUG SAFE
echo "TOKEN LENGTH: ${#HETZNER_TOKEN}"

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
    "ssh_keys": []
  }')

echo "Response:"
echo "$RESPONSE"

SERVER_ID=$(echo "$RESPONSE" | jq -r '.server.id')

if [ "$SERVER_ID" = "null" ] || [ -z "$SERVER_ID" ]; then
  echo "ERROR: VPS creation failed"
  exit 1
fi

echo "Server created: $SERVER_ID"
