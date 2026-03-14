#!/usr/bin/env bash
set -euo pipefail

# Install uv if not available
if ! command -v uv &>/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

if ! command -v chromium-browser &>/dev/null && ! command -v chromium &>/dev/null; then
  sudo apt-get update && sudo apt-get install -y chromium
fi

uv pip install --system .
npm install
