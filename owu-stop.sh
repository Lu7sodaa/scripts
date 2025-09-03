#!/usr/bin/env bash
set -euo pipefail

# Tenter de quitter proprement LM Studio (app macOS)
osascript -e 'tell application "LM Studio" to quit' >/dev/null 2>&1 || true
sleep 1
# Au besoin, tuer le process
pkill -f "LM Studio" >/dev/null 2>&1 || true

for P in 8080 1234 8384 8385 8386; do
  if lsof -ti tcp:$P >/dev/null 2>&1; then
    echo "kill port $P"
    lsof -ti tcp:$P | xargs kill -9 || true
  fi
done

echo "✅ owu-stop: services arrêtés (OWU/LMStudio/TEI)."
