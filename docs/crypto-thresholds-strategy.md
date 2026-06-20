# Crypto Price Thresholds – Full Strategy Playbook (Polymarket)

**Category**: 2 – Crypto Price Thresholds  
**Primary Venue**: Polymarket  
**Last Updated**: June 20, 2026

---

## 1. Overview

This playbook covers binary threshold markets on Polymarket (e.g., “Will BTC reach $110k by July 31?”).

**Core Thesis**: Exploit mispricings between market-implied probability and statistically modeled probability on high-liquidity crypto price threshold contracts.

**Why It Suits Hermes**:
- Objective, binary resolution
- High liquidity on major coins
- Easy to model using volatility and historical path data

---

## 2. Eligible Markets

**Allowed Assets** (only these):
- Bitcoin (BTC)
- Ethereum (ETH)
- Solana (SOL)

**Market Format**:
- “Will [Asset] be above $X by [Date]?”
- Minimum liquidity: ≥$300K volume

**Priority**:
1. BTC thresholds (highest liquidity)
2. ETH thresholds
3. SOL thresholds (only when volume is strong)

---

## 3. Trading Rules

### Entry Criteria
- Enter when market price differs from modeled probability by **≥8–12%**.
- Only trade thresholds with **≥30 days** remaining until resolution.
- Prefer entries when edge is stable for 24+ hours.

### Exit Rules
- **Target**: Sell at 60–75% probability or when edge shrinks to <4%.
- **Time-based**: Begin reducing position when <14 days remain.
- **Stop-loss**: Cut if price moves against position by 40% of original edge.

---

## 4. Position Sizing Calculator Template

### 4.1 Formula

```
Position Size ($) = (Edge % × Bankroll) / (Volatility Factor × Time Risk Factor)
```

**Definitions**:
- **Edge %** = |Modeled Probability – Market Price|
- **Bankroll** = Capital allocated to crypto threshold strategy
- **Volatility Factor** = 30-day historical volatility of the asset (normalized 0.8–2.0)
- **Time Risk Factor** = 1.0 (if >60 days left) → 1.3 (30–60 days) → 1.6 (<30 days)

### 4.2 Example Calculation Table

| Asset | Threshold     | Days Left | Edge % | Bankroll | Vol Factor | Time Factor | Position Size | Notes |
|-------|---------------|-----------|--------|----------|------------|-------------|---------------|-------|
| BTC   | > $110k       | 45        | 11%    | $10,000  | 1.2        | 1.3         | **$706**      | Good edge, moderate time risk |
| ETH   | > $4,000      | 60        | 9%     | $10,000  | 1.4        | 1.0         | **$643**      | Stable time window |
| SOL   | > $200        | 25        | 13%    | $10,000  | 1.8        | 1.6         | **$451**      | High volatility + time risk |
| BTC   | > $120k       | 90        | 7%     | $10,000  | 1.2        | 1.0         | **$583**      | Lower edge |

### 4.3 Hermes Position Sizing Template (Copy-Paste Ready)

**Inputs**:
- Asset + Threshold: _______________
- Edge %: ______
- Bankroll: $______
- Volatility Factor (30d): ______
- Time Risk Factor: ______

**Calculation**:
```
Position Size = (Edge % × Bankroll) / (Volatility Factor × Time Risk Factor)
```

**Output**:
- Recommended Position: $______
- Max Position (capped at 10% of crypto bankroll): $______
- Final Size to Use: $______

**Hermes Logging Format**:
```
Asset: BTC
Threshold: > $110,000 by July 31
Edge: 11%
Vol Factor: 1.2
Time Factor: 1.3
Bankroll: $10,000
Position Size: $706
Risk %: 7.06%
```

### 4.4 Risk-Adjusted Sizing Rules

- Maximum **10%** of crypto strategy bankroll per position.
- Reduce size by 30% if <30 days remain.
- Never hold more than **4** open threshold positions simultaneously.

---

## 5. Evaluation Metrics

| Metric                        | Description                                   | Target     |
|-------------------------------|-----------------------------------------------|------------|
| Edge Capture Rate             | % of modeled edge realized                    | ≥60%       |
| Win Rate                      | % of profitable threshold bets                | ≥55%       |
| Average ROI per Trade         | Mean return                                   | ≥15%       |
| Model Accuracy                | Modeled probability vs actual resolution      | ≥68%       |
| Average Hold Time             | Days position is held                         | 20–45 days |
| Max Drawdown                  | Worst losing streak                           | <30%       |

---

## 6. Risk Management Rules

- **Maximum concurrent positions**: 4
- **Maximum exposure per asset**: 15% of crypto bankroll
- **Kill switch**: Pause new entries if 3 consecutive losses on same asset
- **Blackout**: No new entries when <10 days remain unless edge >15%

---

## 7. Hermes Workflow

1. **Scan** — Identify active high-volume threshold markets.
2. **Model** — Calculate probability using historical volatility.
3. **Size** — Run position sizing calculator.
4. **Brief** — Log edge, size, and rules.
5. **Execute** — User confirms → provide exact `./pmx poly` command.
6. **Monitor** — Track price vs modeled probability weekly.
7. **Review** — Post-resolution analysis and model update.

---

*This playbook is maintained in the pmxtrader project for Hermes agentic trading.*