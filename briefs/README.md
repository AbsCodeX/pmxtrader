# Trade briefs

Handoff artifacts between **Scout** (research) and **Trader** (execution).

## Flow

1. Scout creates a brief: `./scripts/new-brief.sh usa-aus`
2. Scout fills in market data, venue comparison, thesis
3. You set `approved: true` in the YAML frontmatter
4. Trader runs: `./pmx trader openai briefs/active/...` (or `./pmx trader cursor ...`)

## Directories

| Path | Purpose |
|------|---------|
| `TEMPLATE.md` | Copy source |
| `examples/` | Sample briefs (committed) |
| `active/` | Session briefs (gitignored) |

## Approval

Trader agents must **refuse** to prepare orders unless frontmatter has:

```yaml
approved: true
```
