# pmxtrader Issue Log

**Purpose**: Track issues, limitations, observations, and improvements related to trading, tooling, and the multi-agent system.

---

## 2026-06-20 – Polymarket US Market Discovery Limitation

**Issue**: `./pmx poly markets [query]` consistently returns empty results (`[]`).

**Details**:
- Tested multiple queries: `fed`, `bitcoin`, `senate`, `valorant`, `esports`, `politics`
- Even with `--query`, `--sort volume`, `--limit`, and positional arguments, results are empty.
- Other commands (`poly quote`, `poly link`) work normally.
- Status shows Polymarket US balance is available (~$278).

**Impact**:
- Automated broad market scanning via `poly markets` is currently not functional.
- Workaround needed: Use known slugs, `poly watch book`, or manual watch lists.

**Status**: Open  
**Workaround**: Maintain a curated watch list of high-priority markets and scan them individually using `poly quote` or `poly watch book`.

**Logged by**: Hermes (Scout)

---

## Template for Future Entries

**Date** – Short Title

**Issue**:  
**Details**:  
**Impact**:  
**Status**: Open / In Progress / Resolved  
**Workaround**:  
**Resolution**:  
**Logged by**: