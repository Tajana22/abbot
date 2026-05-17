#!/bin/bash
set -e

response=$(curl -X POST "https://api.hetzner.cloud/v1/servers" \
-H "Authorization: Bearer $HCLOUD_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "name":"ephemeral-runner",
  "server_type":"cx22",
  "image":"ubuntu-24.04",
  "location":"fsn1"
}')

echo "$response"

if echo "$response" | jq -e '.error' > /dev/null; then
  echo "Hetzner API error"
  exit 1
fi
