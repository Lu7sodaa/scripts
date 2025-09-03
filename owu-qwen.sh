#!/usr/bin/env bash
set -euo pipefail

QWEN_PORT=8385
QWEN_MODEL="Qwen/Qwen3-Embedding-8B"

log(){ printf "[%s] %s\n" "$(date '+%H:%M:%S')" "$*"; }
is_up(){ curl -fsS "$1" >/dev/null 2>&1; }
kill_port(){ local p="$1"; if lsof -ti tcp:$p >/dev/null 2>&1; then lsof -ti tcp:$p | xargs kill -9 || true; fi; }

case "${1:-start}" in
  start)
    kill_port "$QWEN_PORT"
    nohup text-embeddings-router \
      --model-id "$QWEN_MODEL" \
      --port "$QWEN_PORT" \
      > "$HOME/logs/tei-qwen.log" 2>&1 &
    log "Qwen lancé (port $QWEN_PORT, log: ~/logs/tei-qwen.log)"
    for i in {1..90}; do
      if is_up "http://127.0.0.1:$QWEN_PORT/embed"; then log "OK: TEI Qwen prêt"; exit 0; fi
      sleep 1
    done
    log "WARN: Qwen ne répond pas encore (boot lourd).";;
  stop)
    kill_port "$QWEN_PORT"
    log "Qwen arrêté (port $QWEN_PORT libéré).";;
  *)
    echo "Usage: owu-qwen [start|stop]"; exit 1;;
esac
