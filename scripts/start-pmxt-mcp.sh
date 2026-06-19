#!/bin/bash
# Start PMXT MCP server using the API key from CLI auth

AUTH_FILE="$HOME/.pmxt/cli-auth.json"

if [ ! -f "$AUTH_FILE" ]; then
    echo "Error: PMXT CLI auth file not found at $AUTH_FILE"
    echo "Please run: pmxt auth login"
    exit 1
fi

API_KEY=$(cat "$AUTH_FILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('pmxtApiKey') or d.get('apiKey') or '')")

if [ -z "$API_KEY" ]; then
    echo "Error: Could not read API key from $AUTH_FILE"
    exit 1
fi

echo "Starting PMXT MCP server..."
cd "$(dirname "$0")/../pmxt-mcp"
PMXT_API_KEY="$API_KEY" node dist/index.js
