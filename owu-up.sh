#!/usr/bin/env bash
set -euo pipefail

# --- chemins / réglages ---
VENV="$HOME/.venvs/openwebui"
OWU_PORT=8080

# TEI models + ports
E5_PORT=8384
E5_MODEL="intfloat/multilingual-e5-large-instruct"

CAME_PORT=8386
CAME_MODEL="Lajavaness/sentence-camembert-large"

# LM Studio
LM_PORT=1234

log(){ printf "[%s] %s\n" "$(date '+%H:%M:%S')" "$*"; }
is_up(){ curl -fsS "$1" >/dev/null 2>&1; }
kill_port(){ local p="$1"; if lsof -ti tcp:$p >/dev/null 2>&1; then lsof -ti tcp:$p | xargs kill -9 || true; fi; }
wait_up(){
  local url="$1" name="$2" tries="${3:-45}"
  for i in $(seq 1 $tries); do
    if is_up "$url"; then log "OK: $name prêt sur $url"; return 0; fi
    sleep 1
  done
  log "WARN: $name ne répond pas encore sur $url"; return 1
}

# 1) TEI e5
kill_port "$E5_PORT"
nohup text-embeddings-router \
  --model-id "$E5_MODEL" \
  --port "$E5_PORT" \
  > "$HOME/logs/tei-e5.log" 2>&1 &
log "TEI e5 lancé (port $E5_PORT, log: ~/logs/tei-e5.log)"
wait_up "http://127.0.0.1:$E5_PORT/embed" "TEI e5" 30

# 2) TEI CamemBERT
kill_port "$CAME_PORT"
nohup text-embeddings-router \
  --model-id "$CAME_MODEL" \
  --port "$CAME_PORT" \
  > "$HOME/logs/tei-camembert.log" 2>&1 &
log "TEI CamemBERT lancé (port $CAME_PORT, log: ~/logs/tei-camembert.log)"
wait_up "http://127.0.0.1:$CAME_PORT/embed" "TEI CamemBERT" 30

# 3) LM Studio (ouvre l’app; le Local Server doit être activé dans LM Studio)
open -ga "LM Studio" || true
log "LM Studio lancé (UI). J’attends l’API locale sur http://127.0.0.1:$LM_PORT/v1/models ..."
wait_up "http://127.0.0.1:$LM_PORT/v1/models" "LM Studio API" 60 || \
  log "Note: si l’API ne répond pas, active 'Developer → Local Server' dans LM Studio."

# 4) OpenWebUI
kill_port "$OWU_PORT"
source "$VENV/bin/activate"
nohup open-webui serve --port "$OWU_PORT" \
  > "$HOME/logs/openwebui.log" 2>&1 &
log "OpenWebUI lancé (http://localhost:$OWU_PORT, log: ~/logs/openwebui.log)"
wait_up "http://127.0.0.1:$OWU_PORT" "OpenWebUI" 30

log "✅ owu-up terminé."
log "Rappel: dans OWU → Réglages → Documents → Embedding Engine = TEI, URL selon le modèle :"
log " - e5:       http://localhost:$E5_PORT"
log " - CamemBERT: http://localhost:$CAME_PORT"
