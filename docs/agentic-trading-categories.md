# Hermes Agentic Trading Categories & Frameworks

**Project**: pmxtrader  
**Purpose**: Structured trading and evaluation frameworks optimized for Hermes’ strengths (research, data analysis, calculations, rule-based execution, and cross-venue comparison).  
**Last Updated**: June 20, 2026

---

## Overview

This document defines five specialized market categories where Hermes performs best. Each category includes tailored trading strategies, evaluation metrics, and risk rules designed around Hermes’ capabilities and limitations.

---

## 1. Economic Data Releases (Kalshi Primary)

**Focus**: Scheduled macroeconomic data prints and policy decisions.

**Why It Suits Hermes**:
- Fixed release dates
- Objective, data-driven resolution
- Strong historical datasets available
- Low subjectivity

**Example Markets**:
- CPI / Core CPI
- Unemployment Rate
- Fed Rate Decisions
- PCE, GDP, Retail Sales

**Trading Strategy**:
- Enter 24–72 hours before release when price deviates from modeled probability.
- Use historical reaction data + consensus deviation for edge calculation.
- Exit 30–60 minutes after release or at target probability.

**Evaluation Metrics**:
- Edge per trade (modeled vs market probability)
- Win rate on directional bets
- Average return per data release
- Maximum drawdown during high-impact weeks

**Risk Rules**:
- No trading on unscheduled announcements.
- Hard stop after 3 consecutive losses on the same data type.

---

## 2. Crypto Price Thresholds (Polymarket Primary)

**Focus**: Will a crypto asset reach a specific price level by a defined date?

**Why It Suits Hermes**:
- Purely objective resolution
- High liquidity on major coins
- Easy to model with volatility and historical path data

**Example Markets**:
- BTC > $110,000 by July 31?
- ETH > $4,000 by August 15?
- SOL > $200 before Q4?

**Trading Strategy**:
- Buy when market price is ≥8–12% away from modeled probability.
- Scale in over 2–3 days.
- Target 60–75% probability for partial exits.

**Evaluation Metrics**:
- Probability model accuracy vs actual resolution
- ROI on threshold markets
- Average hold time
- Liquidity-adjusted performance

**Risk Rules**:
- Maximum 3 open threshold positions at once.
- Only trade high-liquidity major coins.

---

## 3. U.S. Politics & Elections

**Focus**: Political outcomes with clear, verifiable results.

**Why It Suits Hermes**:
- High volume of polling and historical data
- Strong cross-venue arbitrage opportunities (Kalshi vs Polymarket)
- Structured election cycles

**Example Markets**:
- Senate / House Control
- Key State Races
- Popular Vote Winner
- Specific Candidate to Win State

**Trading Strategy**:
- Execute arbitrage when price difference ≥4–6¢ between venues.
- Build directional positions when model probability differs significantly from market.
- Reduce exposure 7–14 days before major elections.

**Evaluation Metrics**:
- Arbitrage capture rate
- Model accuracy vs final results
- Cross-venue ROI
- Time-weighted exposure

**Risk Rules**:
- No positions in low-liquidity local races.
- Strict position limits near election day.

---

## 4. Weather & Climate Events (Kalshi Primary)

**Focus**: Measurable weather and climate outcomes.

**Why It Suits Hermes**:
- Objective resolution (temperature, landfall, records)
- Strong historical and seasonal data
- Predictable seasonal patterns

**Example Markets**:
- Hurricane landfall location/strength
- Record high/low temperatures
- Named storm counts
- Snowfall totals

**Trading Strategy**:
- Enter when market price deviates from long-term historical frequency.
- Adjust for current seasonal factors (El Niño/La Niña).
- Exit or hedge on significant model updates.

**Evaluation Metrics**:
- Model accuracy vs climatology
- ROI per season
- Hit rate on binary contracts
- Drawdown during active seasons

**Risk Rules**:
- No long-range uncertain forecasts.
- Seasonal exposure caps during peak periods.

---

## 5. Simple Binary Sports Props

**Focus**: Clear Yes/No sports outcomes with strong historical data.

**Why It Suits Hermes**:
- Objective resolution
- Statistical modeling possible
- Avoids complex live in-game decisions

**Example Markets**:
- Player to score 1+ goal/assist
- Total points/goals over/under
- Team to win by X+ goals
- Clean sheet / shutout

**Trading Strategy**:
- Enter when modeled probability differs from market by ≥10%.
- Prefer over/unders and simple player props.
- Exit before game starts or hold to resolution.

**Evaluation Metrics**:
- Model accuracy rate
- ROI on prop bets
- Average edge captured
- Performance by sport/league

**Risk Rules**:
- No live trading.
- Maximum 4 open positions.
- Avoid leagues with poor data quality.

---

## Category Comparison

| Category                    | Best Venue     | Resolution Style     | Data Richness | Agent Fit     | Complexity | Primary Strategy          |
|-----------------------------|----------------|----------------------|---------------|---------------|------------|---------------------------|
| Economic Data Releases      | Kalshi        | Binary / Range       | Very High     | Excellent     | Low        | Calendar + Stats          |
| Crypto Price Thresholds     | Polymarket    | Binary               | High          | Excellent     | Low        | Probability Modeling      |
| U.S. Politics & Elections   | Both          | Binary / Multi       | Very High     | Very Good     | Medium     | Cross-Venue Arbitrage     |
| Weather & Climate Events    | Kalshi        | Binary / Range       | High          | Very Good     | Low        | Seasonal + Climatology    |
| Simple Binary Sports Props  | Polymarket    | Binary               | Medium-High   | Good          | Medium     | Statistical Prop Edge     |

---

## Next Steps

This document serves as the foundation for building detailed playbooks, position sizing formulas, monitoring checklists, and performance dashboards for each category.

**Recommended Future Files**:
- `docs/economic-data-strategy.md`
- `docs/crypto-thresholds-strategy.md`
- `docs/politics-arbitrage-strategy.md`
- `docs/weather-climate-strategy.md`
- `docs/sports-props-strategy.md`

---

*Document created and maintained for pmxtrader project.*