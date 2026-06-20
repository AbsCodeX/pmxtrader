# U.S. Politics & Elections – Full Strategy Playbook

**Category**: 3 – U.S. Politics & Elections  
**Venues**: Kalshi + Polymarket  
**Last Updated**: June 20, 2026

---

## 1. Overview

This playbook covers U.S. political outcomes with clear, verifiable resolutions (elections, congressional control, state races, etc.).

**Core Thesis**: Combine cross-venue arbitrage (Kalshi vs Polymarket) with data-driven probability modeling to capture edges in high-volume political markets.

**Why It Suits Hermes**:
- Strong polling and historical data
- Clear cross-venue price discrepancies
- Structured election cycles with predictable timelines

---

## 2. Eligible Markets

**Priority Tiers**:

| Tier | Market Type                        | Liquidity | Recommended Focus                  |
|------|------------------------------------|-----------|------------------------------------|
| 1    | Senate / House Control             | Very High | Primary focus                      |
| 2    | Presidential Popular Vote          | High      | Strong data availability           |
| 3    | Key Senate / Gubernatorial Races   | High      | Only top 5–7 most liquid races     |
| 4    | State Legislative Control          | Medium    | Only when volume > $400K           |

**Rule**: Only trade markets with ≥$400K volume and clear resolution criteria.

---

## 3. Trading Rules

### 3.1 Cross-Venue Arbitrage
- Execute when price difference between Kalshi and Polymarket is **≥4–6¢**.
- Direction: Buy the cheaper venue, sell the more expensive one (when possible) or directional on the undervalued side.

### 3.2 Directional Trading
- Enter when Hermes’ modeled probability differs from the market by **≥7%**.
- Prefer entries **30–90 days** before election day.
- Reduce or exit positions in the final **14 days** before major elections.

### 3.3 Exit Rules
- **Target**: Sell when price reaches modeled probability ±3% or edge shrinks below 4%.
- **Time-based**: Begin scaling out 14 days before election.
- **Stop-loss**: Cut if price moves against position by 50% of original edge.

---

## 4. Position Sizing Calculator Template

### 4.1 Formula

```
Position Size ($) = (Edge % × Bankroll) / (Liquidity Risk Factor × Time Risk Factor)
```

**Definitions**:
- **Edge %** = |Modeled Probability – Market Price|
- **Bankroll** = Capital allocated to politics strategy
- **Liquidity Risk Factor** = 1.0 (Very High volume) → 1.4 (Medium volume)
- **Time Risk Factor** = 1.0 (>60 days) → 1.2 (30–60 days) → 1.5 (<30 days)

### 4.2 Example Calculation Table

| Market                        | Venue Diff | Edge % | Bankroll | Liquidity Factor | Time Factor | Position Size | Notes |
|-------------------------------|------------|--------|----------|------------------|-------------|---------------|-------|
| Senate Control                | 5¢         | 8%     | $10,000  | 1.0              | 1.2         | **$667**      | Strong arbitrage opportunity |
| Presidential Popular Vote     | 4¢         | 7%     | $10,000  | 1.0              | 1.0         | **$700**      | High liquidity, stable timing |
| Key Senate Race (Top 5)       | 6¢         | 9%     | $10,000  | 1.2              | 1.3         | **$481**      | Good edge, moderate time risk |
| Gubernatorial Race            | 5¢         | 6%     | $10,000  | 1.4              | 1.2         | **$298**      | Lower edge + liquidity risk |

### 4.3 Hermes Position Sizing Template (Copy-Paste Ready)

**Inputs**:
- Market: _______________
- Edge %: ______
- Bankroll: $______
- Liquidity Risk Factor: ______
- Time Risk Factor: ______

**Calculation**:
```
Position Size = (Edge % × Bankroll) / (Liquidity Risk Factor × Time Risk Factor)
```

**Output**:
- Recommended Position: $______
- Max Position (capped at 12% of politics bankroll): $______
- Final Size to Use: $______

**Hermes Logging Format**:
```
Market: Senate Control 2026
Edge: 8%
Liquidity Factor: 1.0
Time Factor: 1.2
Bankroll: $10,000
Position Size: $667
Risk %: 6.67%
```

### 4.4 Risk-Adjusted Sizing Rules

- Maximum **12%** of politics strategy bankroll per position.
- Reduce size by 40% when <30 days remain.
- Never hold more than **5** open political positions at once.

---

## 5. Evaluation Metrics

| Metric                        | Description                                      | Target     |
|-------------------------------|--------------------------------------------------|------------|
| Arbitrage Capture Rate        | % of spreads successfully closed                 | ≥70%       |
| Edge Capture Rate             | % of modeled edge realized                       | ≥60%       |
| Win Rate                      | % of profitable political trades                 | ≥58%       |
| Average ROI per Trade         | Mean return                                      | ≥14%       |
| Model Accuracy                | Modeled probability vs final result              | ≥72%       |
| Max Drawdown                  | Worst losing streak                              | <28%       |

---

## 6. Risk Management Rules

- **Maximum concurrent positions**: 5
- **Maximum exposure per race/control market**: 12% of politics bankroll
- **Kill switch**: Pause new entries after 3 consecutive losses
- **Election Blackout**: No new entries in final 10 days before major elections unless edge >12%

---

## 7. Hermes Workflow

1. **Scan** — Compare Kalshi vs Polymarket prices daily.
2. **Model** — Aggregate polling and historical data.
3. **Size** — Run position sizing calculator.
4. **Brief** — Log edge, arbitrage opportunity, and size.
5. **Execute** — User confirms → provide exact commands.
6. **Monitor** — Track price movement and polling shifts weekly.
7. **Review** — Post-election analysis and model refinement.

---

*This playbook is maintained in the pmxtrader project for Hermes agentic trading.*