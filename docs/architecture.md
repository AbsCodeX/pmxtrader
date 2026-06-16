# Architecture

## Overview

`pmxtrader` is a prediction market trading platform built around PMXT as the core integration layer. The project is designed to support both terminal-based workflows and future expansion into web interfaces and autonomous agents.

## High-Level Architecture

```
pmxtrader/
├── pmxt/                 # PMXT integration layer (source copy)
│   ├── client/           # API wrappers and client logic
│   ├── analysis/         # Market analysis and reporting
│   ├── mcp/              # MCP tools for AI agents
│   └── cli/              # Custom CLI commands
├── apps/                 # Applications
│   ├── dashboard/        # Web interface (future)
│   ├── agents/           # AI agents (future)
│   └── cli/              # Terminal tools
├── packages/             # Shared code
├── tools/                # Utilities and backtesting
└── scripts/              # Project scripts (e.g. security tools)
```

## Key Principles

- **PMXT as the core**: All market data and execution goes through the PMXT layer.
- **Security first**: Pre-commit secret scanning and strict environment handling.
- **Single source of truth**: All work lives inside `pmxtrader`.
- **Modular design**: Clear separation between integration, applications, and tools.

## Technology Stack

- **Language**: TypeScript (primary), Python (supporting)
- **Package Manager**: npm
- **Version Control**: Git + GitHub
- **CI/CD**: GitHub Actions

## Security Architecture

- Secrets are never committed to the repository
- Pre-commit hook scans for common secret patterns
- GitHub Actions runs additional secret scanning on every push
