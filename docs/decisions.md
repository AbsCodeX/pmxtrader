# Project Decisions

This document records important architectural and process decisions made during the development of `pmxtrader`.

## Decision Log

### 2026-06-16 – PMXT as Source Copy

**Decision:** Treat the PMXT fork as a source copy only, not as a separately maintained repository.

**Rationale:**  
- Simplifies project tracking (single repo: `pmxtrader`)
- Reduces maintenance overhead
- All work and history stays in one place

**Status:** Implemented

---

### 2026-06-16 – Pre-Commit Secret Scanner

**Decision:** Implement a Python-based pre-commit hook to scan for secrets before every commit.

**Rationale:**  
- Security is a top priority
- Prevents accidental exposure of API keys, private keys, and environment variables
- Complements GitHub’s native secret scanning

**Status:** Implemented

---

### 2026-06-16 – Documentation Approach

**Decision:** Maintain lightweight but professional documentation in the `docs/` folder.

**Rationale:**  
- Keeps the project understandable for future self or contributors
- Architecture and decisions should be recorded early
- Avoids over-documentation in early stages

**Status:** In Progress
