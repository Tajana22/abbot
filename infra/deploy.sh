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

RUNNER_VERSION="2.335.1"
SERVER_TYPE="cx22"
LOCATION="hel1"
IMAGE="ubuntu-24.04"

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
  - ufw default deny incoming
  - ufw default allow outgoing
  - ufw deny 22
  - ufw --force enable

  - curl -fsSL https://tailscale.com/install.sh | sh
  - tailscale up --authkey=${TAILSCALE_AUTH_KEY}

  - mkdir -p /runner
  - cd /runner

  - curl -L -o actions-runner.tar.gz https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

  - tar xzf actions-runner.tar.gz

  - ./config.sh \
      --url https://github.com/${GITHUB_REPOSITORY} \
      --token ${RUNNER_TOKEN} \
      --ephemeral \
      --unattended \
      --replace \
      --labels ephemeral,hetzner

  - nohup ./run.sh > runner.log 2>&1 &
EOF
)

echo "Creating VPS..."
echo "Using server_type=${SERVER_TYPE}"
echo "Using location=${LOCATION}"
echo "Using image=${IMAGE}"

RESPONSE=$(curl -s -X POST \
  "https://api.hetzner.cloud/v1/servers" \
  -H "Authorization: Bearer ${HETZNER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"ephemeral-runner\",
    \"server_type\": \"${SERVER_TYPE}\",
    \"image\": \"${IMAGE}\",
    \"location\": \"${LOCATION}\",
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
