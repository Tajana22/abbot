#!/bin/bash

set -euo pipefail

echo "Starting Hetzner ephemeral runner deployment..."

required_vars=(
  HETZNER_TOKEN
  TAILSCALE_AUTH_KEY
  RUNNER_TOKEN
  GITHUB_REPOSITORY
)

for var in "${required_vars[@]}"; do
  if [ -z "${!var:-}" ]; then
    echo "Missing required variable: $var"
    exit 1
  fi
done

USER_DATA=$(cat <<EOF
#cloud-config

package_update: true
package_upgrade: true

packages:
  - curl
  - git
  - jq
  - python3
  - python3-pip
  - ufw

runcmd:
  # Firewall
  - ufw default deny incoming
  - ufw default allow outgoing
  - ufw deny 22
  - ufw --force enable

  # Install Tailscale
  - curl -fsSL https://tailscale.com/install.sh | sh
  - tailscale up --authkey=${TAILSCALE_AUTH_KEY}

  # Create runner directory
  - mkdir -p /runner
  - cd /runner

  # Download ARM64 GitHub runner
  - curl -L -o actions-runner.tar.gz https://github.com/actions/runner/releases/latest/download/actions-runner-linux-arm64-2.334.0.tar.gz

  - tar xzf actions-runner.tar.gz

  # Configure ephemeral runner
  - ./config.sh \
      --url https://github.com/${GITHUB_REPOSITORY} \
      --token ${RUNNER_TOKEN} \
      --ephemeral \
      --unattended \
      --replace \
      --labels ephemeral,hetzner

  # Start runner
  - nohup ./run.sh > runner.log 2>&1 &
EOF
)

echo "Creating VPS..."

RESPONSE=$(curl -s -X POST \
  "https://api.hetzner.cloud/v1/servers" \
  -H "Authorization: Bearer ${HETZNER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"ephemeral-runner\",
    \"server_type\": \"cax11\",
    \"image\": \"ubuntu-22.04\",
    \"location\": \"fsn1\",
    \"user_data\": $(jq -Rs . <<< "$USER_DATA")
  }")

SERVER_ID=$(echo "$RESPONSE" | jq -r '.server.id')

if [[ -z "$SERVER_ID" || "$SERVER_ID" == "null" ]]; then
  echo "Failed to create server"
  echo "$RESPONSE"
  exit 1
fi

echo "Server created successfully"
echo "Server ID: $SERVER_ID"

echo "server_id=$SERVER_ID" >> "$GITHUB_OUTPUT"
