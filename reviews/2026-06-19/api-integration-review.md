# API / Integration review — 2026-06-19

**Linear parent:** [ABI-43](https://linear.app/pmxt/issue/ABI-43/api-integration-review-2026-06-19)  
**Sub-issues:** ABI-44–ABI-50  
**Fix commit:** Batch E (see git log after `54e83152`)

---

## Checklist (audit criteria)

| Criterion | Verdict | Notes |
|-----------|---------|-------|
| API endpoints are known | **Pass** | Mapped in this doc + `docs/kalshi-integration.md`, `docs/polymarket-us-integration.md` |
| Official docs match code behavior | **Pass (after Batch E)** | Fixed stale Kalshi URLs in `SETUP_KALSHI.md` |
| Rate limits considered | **Partial** | PMXT throttles 100ms; panic + PH now spaced/retried in scripts |
| Error handling exists | **Pass** | Layered: PMXT `BaseError`, subprocess capture, curl retry |
| Retry logic is safe | **Pass** | Connection-only retry in PMXT SDK; no POST auto-retry on trades/panic closes |
| Network calls are not hidden | **Pass (documented)** | Transparency model in `docs/architecture.md` |

---

## Integration map

```
UI → subprocess ./pmx → pmxt CLI → sidecar :3847 → Kalshi / Polymarket US
                                  → api.pmxt.dev (Router, hosted)
ph-sports-compare.sh → Prediction Hunt REST (curl)
agent-run / cockpit AI → Hermes → LLM providers
kill-switch --cash-out → kalshi-emergency-exit.py → Kalshi REST (direct, documented)
```

---

## Findings and fixes (Batch E)

| Linear | Issue | Fix applied |
|--------|-------|-------------|
| [ABI-45](https://linear.app/pmxt/issue/ABI-45) | Stale Kalshi URLs in `SETUP_KALSHI.md` | Updated to `external-api.kalshi.com` / demo equivalents; noted `KALSHI_BASE_URL` override |
| [ABI-44](https://linear.app/pmxt/issue/ABI-44) | `has_poly_us_env()` wrong var | Now checks `POLYMARKET_US_KEY_ID` + `POLYMARKET_US_SECRET_KEY` |
| [ABI-46](https://linear.app/pmxt/issue/ABI-46) | Panic bypasses PMXT throttle | 100ms spacing between cancel/close; GET positions retry once on 429/503; docs in `kalshi-integration.md` |
| [ABI-47](https://linear.app/pmxt/issue/ABI-47) | PH no retry | `ph_api_get()` — 3 attempts, exponential backoff on 429/5xx |
| [ABI-49](https://linear.app/pmxt/issue/ABI-49) | Cockpit full parent env | `pmx.env()` uses `minimal_subprocess_env()` |
| [ABI-48](https://linear.app/pmxt/issue/ABI-48) | Router errors easy to miss | `pmxt-eval.py` prints `crossVenueError` in human table output |
| [ABI-50](https://linear.app/pmxt/issue/ABI-50) | No review mirror | This file + `linear-task-api.md` |

---

## Remaining gaps (not in Batch E)

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| Hermes LLM HTTP opaque | Low | Accept; document in architecture (done) |
| Sidecar venue HTTP only in verbose mode | Low | Enable `x-pmxt-verbose` when debugging |
| `pmxt-monitor.sh` fixed 30s poll | Low | OK for brief snapshots; not live trading |
| Full Kalshi OpenAPI surface not wrapped | Info | Documented in `kalshi-integration.md` intentionally-not-wrapped list |

---

## Progress

| Batch | Issues | Done |
|-------|--------|------|
| Batch E | 7 (ABI-44–ABI-50) | 7 |
| **Parent ABI-43** | **7 sub-issues** | **7** |
