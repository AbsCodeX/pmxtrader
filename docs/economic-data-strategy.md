# Economic Data Releases – Full Strategy Playbook (Kalshi)

**Category**: 1 – Economic Data Releases  
**Primary Venue**: Kalshi  
**Last Updated**: June 20, 2026

---

## 1. Overview

This playbook covers trading scheduled macroeconomic and policy events on Kalshi. It is optimized for Hermes’ strengths in data analysis, probability modeling, and rule-based execution.

**Core Thesis**: Systematically exploit deviations between market-implied probability and statistically modeled probability around major data releases.

---

## 2. Eligible Markets (Priority Order)

| Priority | Event                        | Impact     | Resolution     | Frequency   |
|----------|------------------------------|------------|----------------|-------------|
| 1        | CPI / Core CPI               | Very High  | Binary/Range   | Monthly     |
| 2        | Fed Rate Decision (FOMC)     | Very High  | Binary         | 8×/year     |
| 3        | Unemployment Rate            | High       | Binary/Range   | Monthly     |
| 4        | PCE Inflation                | High       | Binary/Range   | Monthly     |
| 5        | GDP (Advance/Final)          | Medium-High| Binary/Range   | Quarterly   |
| 6        | Retail Sales                 | Medium     | Binary/Range   | Monthly     |

**Rule**: Only trade events with ≥$500K historical volume and clear resolution language.

---

## 3. Trading Rules

### Entry Criteria
- Enter **24–72 hours** before release.
- Market price must differ from modeled probability by **≥6–8%**.
- Historical reaction data must support the direction.

### Exit Rules
- **Target**: Sell when price reaches modeled probability ±2% (or 60–75% probability).
- **Time-based**: Exit 30–60 minutes after release.
- **Stop-loss**: Cut if price moves against position by 50% of original edge.

---

## 4. Position Sizing Calculator Template

### 4.1 Formula

```
Position Size ($) = (Edge % × Bankroll) / Volatility Factor
```

**Where**:
- **Edge %** = |Modeled Probability – Market Price|
- **Bankroll** = Total capital allocated to this strategy
- **Volatility Factor** = Average absolute price movement after the last 6 releases of this event type (normalized to 0–2 range)

### 4.2 Example Calculation Table

| Event              | Edge % | Bankroll | Volatility Factor | Position Size | Notes |
|--------------------|--------|----------|-------------------|---------------|-------|
| CPI                | 9%     | $10,000  | 1.4               | **$643**      | Strong historical reaction |
| Fed Rate Decision  | 7%     | $10,000  | 1.8               | **$389**      | Lower edge, higher volatility |
| Unemployment Rate  | 11%    | $10,000  | 1.2               | **$917**      | High edge, stable volatility |
| PCE                | 6%     | $10,000  | 1.5               | **$400**      | Borderline edge |

### 4.3 Hermes Position Sizing Template (Copy-Paste Ready)

**Inputs** (to be filled before each trade):
- Event: _______________
- Edge %: ______
- Bankroll: $______
- Volatility Factor (last 6 releases): ______

**Calculation**:
```
Position Size = (Edge % × Bankroll) / Volatility Factor
```

**Output**:
- Recommended Position: $______
- Max Position (capped at 8% of strategy bankroll): $______
- Final Size to Use: $______

**Hermes Logging Format**:
```
Event: CPI (June 2026)
Edge: 9%
Vol Factor: 1.4
Bankroll: $10,000
Position Size: $643
Risk %: 6.43%
```

### 4.4 Risk-Adjusted Sizing Rules

- Never exceed **8%** of total strategy bankroll on a single event.
- Reduce position size by 50% if fewer than 6 historical data points are available.
- Apply a **0.5x multiplier** during high-impact weeks (e.g., FOMC + CPI in same week).

---

## 5. Evaluation Metrics

| Metric                        | Description                                      | Target     |
|-------------------------------|--------------------------------------------------|------------|
| Edge Capture Rate             | % of modeled edge realized                       | ≥65%       |
| Win Rate                      | % of profitable trades                           | ≥58%       |
| Average ROI per Trade         | Mean return                                      | ≥12%       |
| Max Drawdown (per event)      | Worst streak on one data series                  | <25%       |
| Model Accuracy                | Modeled probability closer to reality than market| ≥70%       |
| Calendar Adherence            | Trades executed in defined windows               | 100%       |

---

## 6. Risk Management Rules

- **Maximum concurrent positions**: 3
- **Maximum exposure per event type**: 8% of strategy bankroll
- **Kill switch**: Pause after 3 consecutive losses on same event type
- **Blackout**: No new entries in final 4 hours before release unless edge >12%

---

## 7. Hermes Workflow

1. **Research** — Pull historical data + consensus estimates.
2. **Model** — Calculate probability and compare to Kalshi price.
3. **Size** — Run position sizing calculator.
4. **Brief** — Log edge, size, and rules.
5. **Execute** — User confirms → provide exact command.
6. **Review** — Post-release analysis and model update.

---

*This playbook is maintained in the pmxtrader project for Hermes agentic trading.*