#!/usr/bin/env bash
# Load Prediction Hunt settings from pmxt/.env

load_prediction_hunt_env() {
  local env_file="${PMXT_DIR:?PMXT_DIR not set}/.env"

  export PREDICTION_HUNT_API_URL="${PREDICTION_HUNT_API_URL:-https://www.predictionhunt.com/api/v2}"

  if [[ ! -f "$env_file" ]]; then
    export PREDICTION_HUNT_API_KEY="${PREDICTION_HUNT_API_KEY:-}"
    return 0
  fi

  if [[ -z "${PREDICTION_HUNT_API_KEY:-}" ]]; then
    PREDICTION_HUNT_API_KEY="$(
      grep -E '^PREDICTION_HUNT_API_KEY=' "$env_file" 2>/dev/null \
        | head -1 \
        | sed 's/^PREDICTION_HUNT_API_KEY=//' \
        | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' \
        | sed 's/^"//;s/"$//'
    )"
    export PREDICTION_HUNT_API_KEY
  fi

  local url_from_env
  url_from_env="$(
    grep -E '^PREDICTION_HUNT_API_URL=' "$env_file" 2>/dev/null \
      | head -1 \
      | sed 's/^PREDICTION_HUNT_API_URL=//' \
      | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' \
      | sed 's/^"//;s/"$//'
  )"
  if [[ -n "$url_from_env" ]]; then
    export PREDICTION_HUNT_API_URL="$url_from_env"
  fi
}

require_prediction_hunt_key() {
  load_prediction_hunt_env
  if [[ -z "${PREDICTION_HUNT_API_KEY:-}" ]]; then
    echo "Missing PREDICTION_HUNT_API_KEY in pmxt/.env"
    echo "Free key: https://www.predictionhunt.com/api/docs"
    exit 1
  fi
}

ph_api_get() {
  local endpoint="$1"
  shift
  curl -sS \
    -H "X-API-Key: ${PREDICTION_HUNT_API_KEY}" \
    "${PREDICTION_HUNT_API_URL%/}/${endpoint}" \
    "$@"
}

ph_pretty_json() {
  python3 -m json.tool 2>/dev/null || cat
}
