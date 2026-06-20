# Role-Based Multi-Agent System for pmxtrader + Hermes

**Project**: pmxtrader  
**Date**: June 20, 2026  
**Purpose**: Define a scalable, role-based multi-agent architecture optimized for Hermes’ strengths and weaknesses.

---

## 1. Core Philosophy

Instead of creating one Hermes agent that tries to do everything, or five fully specialized agents per category, we use a **role-based system**.

This approach:
- Plays to Hermes’ strengths (research, modeling, structured output, rule-based execution)
- Minimizes its weaknesses (real-time monitoring, subjective judgment, live execution)
- Allows specialization where it delivers the highest value

---

## 2. Agent Roles

| Role              | Primary Responsibility                          | Hermes Strengths Used                  | Weaknesses Avoided                     | Category Scope          |
|-------------------|--------------------------------------------------|----------------------------------------|----------------------------------------|-------------------------|
| **Scout**         | Market scanning, data gathering, opportunity identification | Research, cross-venue comparison       | Real-time execution                    | All 5 categories        |
| **Modeler**       | Probability modeling, edge calculation, volatility/seasonal adjustments | Data analysis, calculations            | Subjective/narrative markets           | Specialized per category |
| **Brief Writer**  | Creating standardized trade briefs               | Documentation, rule-based output       | Fast decision making                   | All categories          |
| **Trader**        | Converting approved briefs into executable commands | Rule-based execution                   | Cannot execute without human approval  | All categories          |
| **Reviewer**      | Post-event analysis, model improvement, performance tracking | Structured review, data analysis       | Live monitoring                        | All categories          |

---

## 3. Role Specialization by Category

| Category                        | Dedicated Modeler? | Reason |
|---------------------------------|--------------------|--------|
| **Economic Data Releases**      | Yes                | Highest value + data-heavy             |
| **Crypto Price Thresholds**     | Yes                | Volatility modeling is category-specific |
| **U.S. Politics & Elections**   | Yes                | Polling aggregation + cross-venue logic |
| **Weather & Climate Events**    | Optional           | Can share with Economic or standalone  |
| **Simple Binary Sports Props**  | No                 | Lowest agent compatibility             |

**Recommendation**: Start with three dedicated Modelers (Economic, Crypto, Politics) and keep Weather + Sports under the general Modeler role.

---

## 4. Handoff Process

**Standard Flow**:

1. **Scout** → Identifies market opportunity and gathers raw data.
2. **Modeler** → Calculates probability, edge, and recommended position size.
3. **Brief Writer** → Produces a standardized brief using category templates.
4. **Trader** → Converts the brief into exact `./pmx` or `./pmx poly` commands.
5. **Human** → Reviews and approves execution.
6. **Reviewer** → Analyzes outcome, updates models, and logs performance.

**File Handoff Locations** (proposed structure):

```
pmxtrader/
├── briefs/
│   ├── economic/
│   ├── crypto/
│   ├── politics/
│   ├── weather/
│   └── sports/
├── models/
│   ├── economic-model.md
│   ├── crypto-model.md
│   └── politics-model.md
├── agents/
│   ├── scout/
│   ├── modeler/
│   ├── brief-writer/
│   ├── trader/
│   └── reviewer/
└── docs/
    └── role-based-multi-agent-system.md
```

---

## 5. Agent Prompts & Responsibilities (High Level)

### Scout
- Scan active markets across all categories daily
- Flag opportunities where price deviates from baseline
- Output raw data + preliminary notes

### Modeler (Category-Specific)
- Run probability models using historical data
- Apply category-specific factors (volatility, seasonal, polling, etc.)
- Calculate edge and recommended position size using the templates

### Brief Writer
- Use standardized brief templates per category
- Include edge, sizing, risk rules, and execution commands
- Maintain consistent formatting

### Trader
- Convert approved briefs into exact terminal commands
- Never execute without explicit human confirmation
- Log all proposed commands

### Reviewer
- Analyze resolved trades
- Track metrics (edge capture, win rate, ROI)
- Update models and recommend improvements

---

## 6. Strengths & Weaknesses Alignment

| Hermes Strength                     | Best Role(s)          |
|-------------------------------------|-----------------------|
| Structured research & data gathering | Scout                 |
| Probability modeling & calculations  | Modeler               |
| Rule-based documentation             | Brief Writer          |
| Precise command generation           | Trader                |
| Post-event analysis & improvement    | Reviewer              |

| Hermes Weakness                     | Roles That Avoid It   |
|-------------------------------------|-----------------------|
| Real-time / live monitoring         | All roles             |
| Subjective or narrative markets     | Modeler (by design)   |
| Autonomous execution                | Trader (human gate)   |

---

## 7. Implementation Recommendations

1. **Start Small**: Begin with Scout + Modeler + Brief Writer roles.
2. **Specialize Gradually**: Add dedicated Modelers for Economic, Crypto, and Politics first.
3. **Standardize Briefs**: Use the category playbooks we created as templates.
4. **Human-in-the-Loop**: Keep the Trader role strictly under human approval.
5. **Review Cadence**: Run Reviewer analysis after every major event or monthly.

---

## 8. Next Steps

- Create detailed prompt templates for each role
- Define exact brief templates per category
- Set up the recommended folder structure in `~/pmxtrader`
- Build initial Modeler agents for the top 3 categories

---

*This document defines the official multi-agent architecture for the pmxtrader project.*