# pmxtrader

Prediction market trading platform with PMXT, MCP, and agentic capabilities.

## Overview

`pmxtrader` is a custom-built prediction market trading system centered around [PMXT](https://www.pmxt.dev/). The project focuses on clean market analysis, CLI tooling, and future expansion into web interfaces and autonomous agents, with strong emphasis on MCP integration and security best practices.

## Goals

- Deliver high-quality, structured market analysis in the terminal
- Build a clean, maintainable integration layer around PMXT
- Enable agentic workflows through MCP
- Maintain strong security standards (pre-commit secret scanning, etc.)
- Serve as a public portfolio project demonstrating professional engineering practices

## Project Structure

| Directory     | Purpose                                      |
|---------------|----------------------------------------------|
| `pmxt/`       | PMXT integration layer (source copy)         |
| `apps/`       | Applications (CLI, dashboard, agents)        |
| `packages/`   | Shared components and utilities              |
| `tools/`      | Paper trading, backtesting, and utilities    |
| `scripts/`    | Project scripts (including security tools)   |
| `docs/`       | Architecture decisions and documentation     |

## Current Focus

Early development. Priority is building a clean terminal-based analysis experience and establishing strong security safeguards.

## Security

This project treats security as a top priority:

- Pre-commit hook with Python secret scanner
- Strict `.gitignore` for environment and key files
- No secrets committed to the repository

## Status

**Phase:** Early Development  
**Focus:** Terminal analysis tooling + security foundation

## License

MIT
