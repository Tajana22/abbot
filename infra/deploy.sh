#!/bin/bash

SERVER_NAME="github-runner"

curl -X POST \
  -H "Authorization: Bearer $HETZNER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"$SERVER_NAME\",
    \"server_type\": \"cx22\",
    \"image\": \"ubuntu-22.04\",
    \"location\": \"nbg1\"
  }" \
  https://api.hetzner.cloud/v1/servers
