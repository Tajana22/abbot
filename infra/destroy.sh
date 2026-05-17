#!/bin/bash

SERVER_ID=$(curl \
  -H "Authorization: Bearer $HETZNER_API_TOKEN" \
  https://api.hetzner.cloud/v1/servers | jq '.servers[0].id')

curl -X DELETE \
  -H "Authorization: Bearer $HETZNER_API_TOKEN" \
  https://api.hetzner.cloud/v1/servers/$SERVER_ID
