---
description: Plan to convert vendored pmxt/ into a git submodule pinned to pmxt-dev/pmxt.
---

# PMXT submodule migration

## Current state (2026-06-21)

| Item | Status |
|------|--------|
| `pmxt/` in repo | **Vendored copy** (full tree in parent git; no nested `.git`) |
| `pmxt-mcp/`, `molt-pmxt/` | Proper submodules (see `.gitmodules`) |
| `pmxt/node_modules/` | **Removed from git index** — install via `npm --prefix pmxt install` |
| Upstream | [pmxt-dev/pmxt](https://github.com/pmxt-dev/pmxt) @ pmxt-core **2.17.1** |

## Why not converted yet

1. **Local patches** — pmxtrader carries small pmxt-specific changes (e.g. Polymarket US search pagination, `SETUP_POLYMARKET_US.md` wording). These must be upstreamed or maintained in a fork before submodule pin.
2. **One-shot size** — removing ~34k tracked `node_modules` files was done first; full submodule swap is a separate, reviewable step.
3. **Clone ergonomics** — submodule requires `git submodule update --init` for `pmxt/` in addition to MCP submodules.

## Target end state

```gitmodules
[submodule "pmxt"]
    path = pmxt
    url = https://github.com/pmxt-dev/pmxt.git
    branch = main
```

Pin SHA in parent repo after validating `./scripts/setup-dev.sh` and `npm run build --workspace=pmxt-core --prefix pmxt`.

## Manual conversion (maintainers)

Run from a clean working tree after upstreaming local pmxt patches:

```bash
# 1. Record vendored tree identity
git rev-parse HEAD:pmxt  # tree SHA for rollback reference

# 2. Remove vendored tree from index (keep working copy for diff)
git rm -r pmxt
rm -rf pmxt

# 3. Add submodule at desired upstream tag/SHA
git submodule add https://github.com/pmxt-dev/pmxt.git pmxt
cd pmxt && git checkout v2.17.1   # or specific commit
cd ..

# 4. Re-apply any pmxtrader-only patches (should be zero after upstream)
# 5. Install + build
npm install --prefix pmxt
npm run build --workspace=pmxt-core --prefix pmxt

# 6. Commit: gitlink + .gitmodules update
git add .gitmodules pmxt
git commit -m "Convert pmxt/ to submodule pinned at v2.17.1"
```

## Clone after submodule conversion

```bash
git clone --recurse-submodules https://github.com/AbsCodeX/pmxtrader.git
cd pmxtrader
./scripts/setup-dev.sh    # npm install --prefix pmxt + build
```

Until conversion lands, clone uses the vendored tree; run `./scripts/setup-dev.sh` to refresh platform-specific `node_modules` binaries.
