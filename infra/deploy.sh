#!/bin/bash

set -e

echo "Creating Hetzner VPS..."

curl -X POST "https://api.hetzner.cloud/v1/servers" \
  -H "Authorization: Bearer $HETZNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ephemeral-runner",
    "server_type": "cx11",
    "image": "ubuntu-22.04",
    "start_after_create": true
  }'
