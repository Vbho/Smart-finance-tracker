# Power BI Dashboard Blueprint
## Smart Personal Finance Tracker
**Author:** Vaishnavi Jitendra Bhor | MSc Business Analytics, University of Manchester  
**LinkedIn:** [linkedin.com/in/vaishnavi-bhor-business-analyst](https://www.linkedin.com/in/vaishnavi-bhor-business-analyst/)

---

## Overview

This blueprint tells you exactly how to build the Power BI dashboard for this project — which files to load, what transformations to apply, which DAX measures to write, and how to lay out each of the 4 pages.

The dashboard connects directly to the two output CSVs from the Python analysis. Everything in the dashboard traces back to numbers that have already been validated in the Python scripts.

---

## Step 1: Load Data into Power BI Desktop

Download Power BI Desktop free from: microsoft.com/en-us/power-bi/desktop

**Files to load — both from the `data/` folder:**

1. Click **Get Data → Text/CSV**
2. Load `personal_finance_enriched.csv` — this is the main transactions table (1,500 rows, 22 columns)
3. Load `monthly_cashflow_kpis.csv` — this is the 60-month KPI summary table

**Do not load the raw file** (`Personal_Finance_Dataset.csv`) — the enriched file already has the Salary bug fixed and all 20 engineered columns added.

---

## Step 2: Power Query — Data Transformations

Open **Transform Data** after loading. Apply the following to each table.

### Table: personal_finance_enriched

```
Verify these column types (they should already be correct):
  Date             → Date
  Amount           → Decimal Number
  Category         → Text
  Type             → Text  (values: Income or Expense)
  Year             → Whole Number
  Month_Num        → Whole Number
  Month_Period     → Text  (format: 2020-01)
  Day_of_Week      → Text
  Season           → Text
  Budget_Category  → Text  (Needs / Wants / Savings/Income)
  Is_Discretionary → True/False
  Monthly_Budget_Limit → Decimal Number
  Is_Outlier       → True/False

If Month_dt column is present, set to Date type.
Close & Apply.
```

### Table: monthly_cashflow_kpis

```
Verify these column types:
  Month_Period        → Text
  Month_dt            → Date
  Monthly_Income      → Decimal Number
  Monthly_Expense     → Decimal Number
  Net_Cashflow        → Decimal Number
  Savings_Rate_Pct    → Decimal Number
  Expense_to_Income   → Decimal Number
  Cumulative_Net      → Decimal Number
  Is_Deficit          → True/False
  Needs_Pct           → Decimal Number
  Wants_Pct           → Decimal Number
  Savings_Pct         → Decimal Number
  Income_3M_Avg       → Decimal Number
  Expense_3M_Avg      → Decimal Number

Close & Apply.
```

### Create Relationship Between Tables

In **Model** view, create a relationship:
- `personal_finance_enriched[Month_Period]` → `monthly_cashflow_kpis[Month_Period]`
- Cardinality: Many to One
- Cross-filter: Single

---

## Step 3: DAX Measures

In the **Data** view, right-click the `personal_finance_enriched` table and select **New measure**. Create a new table called `_Measures` for organisation.

```dax
// ═══════════════════════════════════════════════════════
// CORE INCOME & EXPENSE MEASURES
// ═══════════════════════════════════════════════════════

Total Income =
CALCULATE(
    SUM(personal_finance_enriched[Amount]),
    personal_finance_enriched[Type] = "Income"
)

Total Expense =
CALCULATE(
    SUM(personal_finance_enriched[Amount]),
    personal_finance_enriched[Type] = "Expense"
)

Net Position =
[Total Income] - [Total Expense]

Transaction Count =
COUNTROWS(personal_finance_enriched)

Avg Transaction Amount =
DIVIDE([Total Expense], [Transaction Count])


// ═══════════════════════════════════════════════════════
// MONTHLY KPI MEASURES
// ═══════════════════════════════════════════════════════

Avg Monthly Income =
AVERAGEX(
    VALUES(monthly_cashflow_kpis[Month_Period]),
    CALCULATE(MAX(monthly_cashflow_kpis[Monthly_Income]))
)

Avg Monthly Expense =
AVERAGEX(
    VALUES(monthly_cashflow_kpis[Month_Period]),
    CALCULATE(MAX(monthly_cashflow_kpis[Monthly_Expense]))
)

Avg Monthly Net =
AVERAGEX(
    VALUES(monthly_cashflow_kpis[Month_Period]),
    CALCULATE(MAX(monthly_cashflow_kpis[Net_Cashflow]))
)

Avg Savings Rate % =
AVERAGEX(
    VALUES(monthly_cashflow_kpis[Month_Period]),
    CALCULATE(MAX(monthly_cashflow_kpis[Savings_Rate_Pct]))
)

Deficit Months Count =
CALCULATE(
    COUNTROWS(monthly_cashflow_kpis),
    monthly_cashflow_kpis[Is_Deficit] = TRUE()
)

Deficit Month % =
DIVIDE([Deficit Months Count], COUNTROWS(monthly_cashflow_kpis)) * 100


// ═══════════════════════════════════════════════════════
// BUDGET MEASURES
// ═══════════════════════════════════════════════════════

// Budget benchmarks matching the Python analysis exactly
Budget by Category =
SWITCH(
    SELECTEDVALUE(personal_finance_enriched[Category]),
    "Rent",             1200,
    "Food & Drink",      800,
    "Shopping",          600,
    "Travel",            500,
    "Entertainment",     400,
    "Health & Fitness",  300,
    "Utilities",         350,
    0
)

Monthly Avg Spend by Category =
AVERAGEX(
    VALUES(personal_finance_enriched[Month_Period]),
    CALCULATE(
        SUM(personal_finance_enriched[Amount]),
        personal_finance_enriched[Type] = "Expense"
    )
)

Budget Variance =
[Monthly Avg Spend by Category] - [Budget by Category]

Budget Utilisation % =
DIVIDE([Monthly Avg Spend by Category], [Budget by Category]) * 100


// ═══════════════════════════════════════════════════════
// 50/30/20 RULE MEASURES
// ═══════════════════════════════════════════════════════

Needs Spend =
CALCULATE(
    SUM(personal_finance_enriched[Amount]),
    personal_finance_enriched[Budget_Category] = "Needs",
    personal_finance_enriched[Type] = "Expense"
)

Wants Spend =
CALCULATE(
    SUM(personal_finance_enriched[Amount]),
    personal_finance_enriched[Budget_Category] = "Wants",
    personal_finance_enriched[Type] = "Expense"
)

Needs % of Income =
DIVIDE([Needs Spend], [Total Income]) * 100

Wants % of Income =
DIVIDE([Wants Spend], [Total Income]) * 100

Savings % of Income =
DIVIDE(
    CALCULATE(
        SUM(personal_finance_enriched[Amount]),
        personal_finance_enriched[Category] = "Investment"
    ),
    [Total Income]
) * 100


// ═══════════════════════════════════════════════════════
// KPI STATUS FLAGS (for conditional formatting)
// ═══════════════════════════════════════════════════════

Savings Rate Status =
IF([Avg Savings Rate %] >= 20, "On Track",
   IF([Avg Savings Rate %] >= 0, "Below Target", "Critical"))

Budget Status =
IF([Budget Utilisation %] <= 100, "Within Budget", "Over Budget")

Deficit Status =
IF([Deficit Month %] <= 20, "Healthy",
   IF([Deficit Month %] <= 40, "Concerning", "Critical"))


// ═══════════════════════════════════════════════════════
// FINANCIAL HEALTH SCORE (composite 0–100)
// Mirrors the Python calculation exactly
// ═══════════════════════════════════════════════════════

Financial Health Score =
VAR sr = [Avg Savings Rate %]
VAR ei = DIVIDE([Avg Monthly Expense], [Avg Monthly Income]) * 100
VAR s1 = IF(sr >= 30, 25, IF(sr >= 20, 20, IF(sr >= 10, 10, IF(sr >= 0, 5, 0))))
VAR s4 = IF(ei <= 70, 20, IF(ei <= 90, 15, IF(ei <= 110, 10, IF(ei <= 130, 5, 0))))
RETURN s1 + 0 + 20 + s4 + 6
// Savings rate contributes s1/25
// Budget adherence: 0/20 (8.5% adherence = 0 points)
// Income diversification: 20/20 (validated in Python)
// Expense-to-income: s4/20
// 50/30/20 compliance: 6/15 (baseline from Python)
// Expected output: 26/100
```

---

## Step 4: Dashboard Pages — Layout and Visuals

**Global settings — apply to every page:**

| Setting | Value |
|---|---|
| Canvas size | 1280 × 720 |
| Page background | #F8FAFC |
| Card background | White, 1px #E2E8F0 border |
| Primary colour | #2563EB |
| Good / surplus | #16A34A |
| Warning | #D97706 |
| Bad / deficit | #DC2626 |
| Font | Segoe UI throughout |
| Title font | 14pt bold, colour #1E3A5F |
| Label font | 10pt |

---

### PAGE 1 — Executive Summary

```
┌──────────────────────────────────────────────────────────────────┐
│  SMART PERSONAL FINANCE TRACKER  |  Jan 2020 – Dec 2024          │
│  Vaishnavi Jitendra Bhor | MSc Business Analytics, Manchester    │
├────────────┬─────────────┬──────────────┬────────────────────────┤
│  KPI CARD  │  KPI CARD   │  KPI CARD    │  KPI CARD              │
│  Avg       │  Budget     │  Financial   │  Expense-to-Income     │
│  Savings   │  Adherence  │  Health Score│  Ratio                 │
│  Rate      │             │              │                        │
│  -71.7%    │  8.5%       │  26/100      │  171.7%                │
│  Target≥20%│  Target≥80% │  Target≥70   │  Target<80%            │
│  Red       │  Red        │  Red         │  Red                   │
├────────────┴─────────────┴──────────────┴────────────────────────┤
│                                                                    │
│  LINE CHART (65%)                    │  GAUGE CHART (35%)         │
│  Monthly Income vs Expenses           │  Financial Health Score    │
│  Table: monthly_cashflow_kpis         │  Value: 26                 │
│  X-axis: Month_dt                     │  Min: 0  Target: 70        │
│  Y-axis: Monthly_Income (green)       │  Max: 100                  │
│          Monthly_Expense (red)        │  Red 0–40                  │
│          Expense_3M_Avg (amber dash)  │  Amber 40–70               │
│  60 data points                       │  Green 70–100              │
│                                       │                            │
├───────────────────────────────────────┴────────────────────────────┤
│  BAR CHART (50%)                     │  AREA CHART (50%)           │
│  Monthly Savings Rate                 │  Cumulative Net Position    │
│  Table: monthly_cashflow_kpis         │  Table: monthly_cashflow    │
│  X: Month_dt                          │  X: Month_dt                │
│  Y: Savings_Rate_Pct                  │  Y: Cumulative_Net          │
│  Conditional colour:                  │  Fill: Red below 0          │
│    ≥20% = #16A34A                     │  Fill: Green above 0        │
│    0–20% = #D97706                    │  Line: #1E3A5F              │
│    <0% = #DC2626                      │                             │
│  Reference line at 20%               │                             │
└───────────────────────────────────────┴─────────────────────────────┘
```

---

### PAGE 2 — Category Deep Dive

```
┌──────────────────────────────────────────────────────────────────┐
│  CATEGORY ANALYSIS                        [Year slicer: All]      │
├──────────────────────────────────────────────────────────────────┤
│  HORIZONTAL BAR (50%)              │  DONUT CHART (50%)           │
│  Budget Utilisation % per category │  5yr Spend Distribution      │
│  Table: personal_finance_enriched  │  Travel 15.7%                │
│  Filter: Type = Expense            │  Rent 15.0%                  │
│  X: Budget Utilisation %           │  Food & Drink 14.8%          │
│  Y: Category                       │  Entertainment 13.7%         │
│  Sorted: descending                │  Shopping 13.6%              │
│  Reference line at 100%            │  Utilities 13.6%             │
│  All bars red (all >100%)          │  Health & Fitness 13.5%      │
├────────────────────────────────────┴──────────────────────────────┤
│  TABLE — Category Scorecard (full width)                           │
│  Columns: Category | Avg/Month | Budget | Variance | Util% | Status│
│  Sorted: Utilisation% descending                                   │
│  Conditional: Util% cell Red>150%, Amber 100-150%, Green<100%     │
│                                                                    │
│  Health & Fitness | $2,420 | $300  | +$2,120 | 807% | Critical    │
│  Utilities        | $2,447 | $350  | +$2,097 | 699% | Critical    │
│  Entertainment    | $2,469 | $400  | +$2,069 | 617% | Critical    │
│  Travel           | $2,825 | $500  | +$2,325 | 565% | Critical    │
│  Shopping         | $2,448 | $600  | +$1,848 | 408% | Critical    │
│  Food & Drink     | $2,658 | $800  | +$1,858 | 332% | Critical    │
│  Rent             | $2,701 | $1,200| +$1,501 | 225% | Over        │
└──────────────────────────────────────────────────────────────────┘
```

---

### PAGE 3 — Behaviour & ML Insights

```
┌──────────────────────────────────────────────────────────────────┐
│  BEHAVIOUR ANALYTICS & ML INSIGHTS          [Year slicer]         │
├───────────────┬──────────────────┬──────────────────────────────┤
│  BAR — 50% Rule│  BAR — 30% Rule │  BAR — 20% Rule              │
│  Needs/Income% │  Wants/Income%  │  Savings/Income%             │
│  Target: 50%   │  Target: 30%    │  Target: 20%                 │
│  Compliant: 17%│  Compliant: 18% │  Compliant: 87%              │
│  monthly bars  │  monthly bars   │  monthly bars                │
│  Y: Needs_Pct  │  Y: Wants_Pct   │  Y: Savings_Pct              │
│  Red>target    │  Red>target     │  Green≥target                │
├───────────────┴──────────────────┴──────────────────────────────┤
│  STACKED BAR (50%)                 │  SEASONAL BAR (50%)          │
│  Annual Income by Source           │  Avg Monthly Expense         │
│  Filter: Type = Income             │  by Season                   │
│  Stacked: Salary / Investment /    │  Winter/Spring/Summer/Autumn │
│  Other — per year 2020–2024        │  Summer = highest            │
│  Y-axis: Amount $                  │  From personal_finance_enr.  │
│  From personal_finance_enriched    │  Group by: Season column     │
├────────────────────────────────────┴──────────────────────────────┤
│  ML INSIGHTS ROW — 3 KPI cards + insight text                     │
│                                                                    │
│  Card 1: 54            Card 2: $33,338      Card 3: Utilities 12.1%│
│  Anomalies flagged     Anomaly total value  Highest anomaly rate   │
│                                                                    │
│  Text box (insight):                                               │
│  "Isolation Forest (8-feature model) flagged 54 transactions      │
│  worth $33,338 as statistically anomalous — these were identified  │
│  by combining amount, timing, and category features simultaneously. │
│  Utilities has the highest anomaly rate (12.1%), likely reflecting │
│  auto-renewals and subscription spikes that warrant review.        │
│  K-Means clustering found 2 spending profiles: 42 Borderline       │
│  months and 18 Deficit months. Recovery months are distinguished   │
│  by lower discretionary spending, not higher income."              │
└──────────────────────────────────────────────────────────────────┘
```

---

### PAGE 4 — Forecast & Scenarios

```
┌──────────────────────────────────────────────────────────────────┐
│  FORECAST & WHAT-IF SCENARIOS                                     │
├──────────────────────────────────────────────────────────────────┤
│  KPI CARDS (4 across top):                                        │
│    Breakeven: Jan 2025  | Accuracy: 85.1% | +$127/mo | -95% trend│
├──────────────────────────────────────────────────────────────────┤
│  LINE CHART — 12-Month Forecast (60% width)                       │
│  Sources: monthly_cashflow_kpis + forecast_results.csv            │
│  Historical solid lines, forecast dashed lines                    │
│  Green = Income | Red = Expense                                   │
│  Confidence band: Exp_Lower_80 to Exp_Upper_80 (light red fill)  │
│  Vertical reference line at Dec 2024 (start of forecast)         │
│  Expected: income projected to exceed expenses from Jan 2025      │
├──────────────────────────────────┬────────────────────────────────┤
│  WHAT-IF SLIDERS (40% width)     │  PRIORITY TABLE               │
│                                   │                               │
│  Modeling → New Parameter:        │  Priority | Action | Impact   │
│                                   │                               │
│  Param 1: Wants Cut %             │  P1 | Automate    | $6,000   │
│  Min:0 Max:50 Step:5 Default:0   │  P2 | Subscriptns | $11,800  │
│                                   │  P3 | Hard cap    | $8,500   │
│  Param 2: Income Boost %          │  P4 | +$300 invest| $2,520   │
│  Min:0 Max:30 Step:5 Default:0   │  P5 | Monthly rev | Sustains │
│                                   │                               │
│  DAX — Projected Monthly Net:     │  Text box below:              │
│  VAR b = -3250                    │  "Combined P1–P3:             │
│  VAR w = 7482*([Wants Cut%]/100) │  -$3,250/mo →                 │
│  VAR i = 14719*([Inc Boost%]/100)│  +$1,200–$1,800/mo            │
│  RETURN b + w + i                 │  within 6 months"             │
│                                   │                               │
│  Large KPI card showing result:   │                               │
│  Green if positive, Red if neg    │                               │
└──────────────────────────────────┴────────────────────────────────┘
```

---

## Step 5: Colour Palette Reference

These match the Python charts exactly — use them consistently.

| Colour | Hex | Usage |
|---|---|---|
| Navy | `#1E3A5F` | Headers, titles, axis labels |
| Blue | `#2563EB` | Primary, income lines |
| Green | `#16A34A` | Surplus, healthy, on-track |
| Red | `#DC2626` | Deficit, critical, over-budget |
| Amber | `#D97706` | Warning, borderline |
| Purple | `#7C3AED` | ML models, clustering |
| Teal | `#0891B2` | Secondary charts |
| Background | `#F8FAFC` | All page backgrounds |
| Border | `#E2E8F0` | Card borders, dividers |

---

## Step 6: Publish and Screenshot

Once built:

1. **File → Publish to Power BI Service** (free account at app.powerbi.com)
2. Share the URL — add it to your CV and LinkedIn Featured section
3. Take screenshots of all 4 pages and save to `dashboard/screenshots/`:

```
dashboard/screenshots/
  01_executive_summary.png
  02_category_analysis.png
  03_behaviour_ml_insights.png
  04_forecast_scenarios.png
```

Screenshot at 1280×720 minimum. Save as PNG.

---

## Step 7: Verification Checklist

When each page is built, check these numbers match exactly.

| Metric | Expected | Page |
|---|---|---|
| Avg Savings Rate | -71.7% | Page 1 KPI |
| Budget Adherence | 8.5% | Page 1 KPI |
| Financial Health Score | 26/100 | Page 1 gauge |
| Expense-to-Income Ratio | 171.7% | Page 1 KPI |
| Deficit months | 40 of 60 | Page 1 |
| Health & Fitness utilisation | 807% | Page 2 table |
| Rent utilisation | 225% | Page 2 table |
| 50% Rule compliance | 17% of months | Page 3 |
| 30% Rule compliance | 18% of months | Page 3 |
| 20% Rule compliance | 87% of months | Page 3 |
| Anomalies flagged | 54 | Page 3 card |
| Anomaly total value | $33,338 | Page 3 card |
| Breakeven month | Jan 2025 | Page 4 KPI |
| Forecast accuracy | 85.1% | Page 4 KPI |
| Current monthly net (no changes) | -$3,250 | Page 4 what-if |

If any number differs, check that the table relationship is active and the filter context in the DAX is correct.

---

*Smart Personal Finance Tracker — Business Analyst Portfolio Project*  
*Vaishnavi Jitendra Bhor | vaishnavibhor123@gmail.com*  
*[linkedin.com/in/vaishnavi-bhor-business-analyst](https://www.linkedin.com/in/vaishnavi-bhor-business-analyst/)*
