#!/usr/bin/env bash
# Load Prediction Hunt settings from pmxt/.env

if [[ "${BASH_SOURCE[0]:-}" == "${0:-}" ]]; then
  echo "Source this file: source scripts/ph-env.sh" >&2
  exit 1
fi

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
  local url="${PREDICTION_HUNT_API_URL%/}/${endpoint}"
  local attempt=1
  local max_attempts=3
  local delay=1
  local tmp code

  while [[ "$attempt" -le "$max_attempts" ]]; do
    tmp="$(mktemp "${TMPDIR:-/tmp}/pmxt-ph.XXXXXX")"
    code="$(
      curl -sS -w "%{http_code}" -o "$tmp" \
        -H "X-API-Key: ${PREDICTION_HUNT_API_KEY}" \
        "$url" \
        "$@" || echo "000"
    )"
    if [[ "$code" =~ ^2 ]]; then
      cat "$tmp"
      rm -f "$tmp"
      return 0
    fi
    rm -f "$tmp"
    if [[ "$code" == "429" || "$code" =~ ^5 ]]; then
      if [[ "$attempt" -lt "$max_attempts" ]]; then
        echo "Prediction Hunt HTTP $code — retry in ${delay}s (attempt ${attempt}/${max_attempts})" >&2
        sleep "$delay"
        delay=$((delay * 2))
        attempt=$((attempt + 1))
        continue
      fi
    fi
    echo "Prediction Hunt API error HTTP ${code} for ${endpoint}" >&2
    return 1
  done
  return 1
}

ph_pretty_json() {
  python3 -m json.tool 2>/dev/null || cat
}
