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

**Status**: Mitigated  
**Workaround**: `./pmx scan poly-global QUERY` for broad discovery (Gamma/CLOB); `./pmx scan poly-us QUERY` for US retail (paginated search in pmxt); `./pmx poly link/quote` with known slugs for execution.

**Resolution (2026-06):** Added `apps/bridge/poly_scanner.py` + `./pmx scan`; fixed `polymarket_us` query to paginate events/markets instead of filtering one page.

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