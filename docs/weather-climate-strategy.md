# Weather & Climate Events – Full Strategy Playbook (Kalshi)

**Category**: 4 – Weather & Climate Events  
**Primary Venue**: Kalshi  
**Last Updated**: June 20, 2026

---

## 1. Overview

This playbook covers measurable weather and climate outcomes with objective resolution.

**Core Thesis**: Use historical climatology and seasonal patterns to identify when market prices deviate from statistically expected probabilities.

**Why It Suits Hermes**:
- Objective, data-rich resolution
- Strong historical and seasonal datasets
- Predictable seasonal patterns that can be modeled

---

## 2. Eligible Markets

**Priority Tiers**:

| Tier | Market Type                          | Liquidity | Focus Areas                          |
|------|--------------------------------------|-----------|--------------------------------------|
| 1    | Hurricane Landfall / Strength        | High      | Atlantic & Gulf seasons              |
| 2    | Record High / Low Temperatures       | Medium-High | Major U.S. cities                    |
| 3    | Named Storm Counts (Season)          | Medium    | Full hurricane season                |
| 4    | Snowfall Totals                      | Medium    | High-volume regional markets         |

**Rule**: Only trade markets with ≥$250K volume and clear, measurable resolution criteria.

---

## 3. Trading Rules

### Entry Criteria
- Enter when market price deviates from long-term historical frequency by **≥8%**.
- Adjust for current seasonal factors (El Niño / La Niña / neutral).
- Prefer entries **2–6 weeks** before the peak of the relevant season.

### Exit Rules
- **Target**: Sell when price aligns with updated meteorological probability (±3%).
- **Time-based**: Begin reducing positions as the event window approaches.
- **Stop-loss**: Cut if new official forecasts significantly contradict the position.

---

## 4. Position Sizing Calculator Template

### 4.1 Formula

```
Position Size ($) = (Edge % × Bankroll) / (Seasonal Risk Factor × Event Uncertainty Factor)
```

**Definitions**:
- **Edge %** = |Modeled Probability – Market Price|
- **Bankroll** = Capital allocated to weather strategy
- **Seasonal Risk Factor** = 1.0 (Off-season) → 1.3 (Shoulder) → 1.6 (Peak season)
- **Event Uncertainty Factor** = 1.0 (High model confidence) → 1.4 (Medium) → 1.8 (Low)

### 4.2 Example Calculation Table

| Event                          | Edge % | Bankroll | Seasonal Factor | Uncertainty Factor | Position Size | Notes |
|--------------------------------|--------|----------|-----------------|--------------------|---------------|-------|
| Hurricane Landfall (Major)     | 10%    | $10,000  | 1.6             | 1.4                | **$446**      | Peak season, moderate uncertainty |
| Record High Temp (City)        | 9%     | $10,000  | 1.3             | 1.2                | **$577**      | Good edge, stable conditions |
| Named Storms (Season Total)    | 8%     | $10,000  | 1.4             | 1.5                | **$381**      | Higher uncertainty |
| Snowfall Total (Regional)      | 11%    | $10,000  | 1.2             | 1.3                | **$641**      | Strong edge, lower seasonal risk |

### 4.3 Hermes Position Sizing Template (Copy-Paste Ready)

**Inputs**:
- Event: _______________
- Edge %: ______
- Bankroll: $______
- Seasonal Risk Factor: ______
- Event Uncertainty Factor: ______

**Calculation**:
```
Position Size = (Edge % × Bankroll) / (Seasonal Risk Factor × Event Uncertainty Factor)
```

**Output**:
- Recommended Position: $______
- Max Position (capped at 10% of weather bankroll): $______
- Final Size to Use: $______

**Hermes Logging Format**:
```
Event: Hurricane Landfall Probability
Edge: 10%
Seasonal Factor: 1.6
Uncertainty Factor: 1.4
Bankroll: $10,000
Position Size: $446
Risk %: 4.46%
```

### 4.4 Risk-Adjusted Sizing Rules

- Maximum **10%** of weather strategy bankroll per position.
- Reduce size by 40% during peak hurricane season if uncertainty is high.
- Never hold more than **4** open weather positions at once.

---

## 5. Evaluation Metrics

| Metric                        | Description                                      | Target     |
|-------------------------------|--------------------------------------------------|------------|
| Edge Capture Rate             | % of modeled edge realized                       | ≥62%       |
| Win Rate                      | % of profitable weather trades                   | ≥56%       |
| Average ROI per Trade         | Mean return                                      | ≥13%       |
| Model Accuracy                | Climatology + seasonal model vs reality          | ≥70%       |
| Seasonal ROI                  | Performance per hurricane / winter season        | Track      |
| Max Drawdown                  | Worst losing streak                              | <30%       |

---

## 6. Risk Management Rules

- **Maximum concurrent positions**: 4
- **Maximum exposure per event type**: 10% of weather bankroll
- **Kill switch**: Pause after 3 consecutive losses on the same event type
- **Seasonal Cap**: Reduce overall exposure by 50% during peak hurricane months if model confidence is low

---

## 7. Hermes Workflow

1. **Research** — Pull historical climatology and current seasonal indicators.
2. **Model** — Adjust baseline probabilities for current conditions.
3. **Size** — Run position sizing calculator.
4. **Brief** — Log edge, seasonal factors, and size.
5. **Execute** — User confirms → provide exact command.
6. **Monitor** — Track official forecasts and model updates.
7. **Review** — Post-event analysis and seasonal model refinement.

---

*This playbook is maintained in the pmxtrader project for Hermes agentic trading.*