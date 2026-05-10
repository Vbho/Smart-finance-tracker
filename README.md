# Smart Personal Finance Tracker
**Author:** Vaishnavi Jitendra Bhor  
**LinkedIn:** [linkedin.com/in/vaishnavi-bhor-business-analyst](https://www.linkedin.com/in/vaishnavi-bhor-business-analyst/)  
**Email:** vaishnavibhor123@gmail.com

---

## Why I Built This

I kept seeing the same problem in my analytics work — people (and businesses) have the data, but they don't know what it's telling them. This project started from a simple question most people can relate to: why does someone who earns a decent income still end up spending more than they earn month after month?

I found a personal finance dataset on Kaggle and decided to treat it the way I would treat a real client problem at Incentius — not just "explore the data and make some charts," but actually structure the problem, define what good looks like, build metrics around it, test hypotheses, and come out the other end with something you could genuinely act on.

The dataset is from Kaggle: [Personal Finance Dataset](https://www.kaggle.com/datasets/ramyapintchy/personal-finance-data?select=Personal_Finance_Dataset.csv) — 1,500 transactions across 5 years. Before I ran a single line of analysis, I found a data quality bug: every Salary transaction was miscategorised as an Expense. That kind of thing matters — it would have completely broken the income calculations. Catching this kind of thing before any analysis runs is a habit I built from working on multiple client datasets at Incentius — the quiet errors that don't crash your code are the ones that do the most damage.

This is not a showcase of charts. It's a structured diagnostic with a specific answer at the end.

---

## The Central Question

> *Why does this individual end up in financial deficit 67% of the time despite earning $883,000 over 5 years — and what would actually fix it?*

The answer turned out to be simpler than I expected. The income is fine. The trajectory is improving. The problem is that discretionary spending (shopping, travel, entertainment) accounts for 52.6% of income — nearly double the 30% that the 50/30/20 rule recommends. Once I saw that number, everything else made sense.

---

## Repository Structure

```
smart-finance-tracker/
│
├── README.md
├── Project_Observations_and_Findings.md  ← Analytical decisions, what I learned,
│                                            what I'd do differently
│
├── data/
│   ├── Personal_Finance_Dataset.csv      ← Raw Kaggle data, untouched
│   ├── personal_finance_enriched.csv     ← 20 new engineered columns added
│   ├── monthly_cashflow_kpis.csv         ← 60-month KPI table
│   ├── forecast_results.csv             ← ML1 forecast output
│   ├── anomaly_flagged_transactions.csv  ← ML2 flagged transactions
│   └── cluster_assignments.csv          ← ML3 cluster labels per month
│
├── analysis/
│   └── mbb_finance_analysis.py          ← Main EDA script, 6 phases
│
├── ml_models/
│   ├── ml1_timeseries.py                ← Holt smoothing + bootstrap CI
│   ├── ml2_anomaly.py                   ← Isolation Forest
│   └── ml3_clustering.py               ← K-Means clustering
│
├── excel/
│   └── Smart_Finance_Tracker_Complete.xlsx  ← 10-sheet workbook
│
├── dashboard/
│   ├── Smart_Finance_Tracker_Dashboard.html ← Interactive dashboard (open in browser)
│   └── POWER_BI_BLUEPRINT.md            ← Step-by-step Power BI build guide with DAX
│
└── charts/
    ├── A1_executive_dashboard.png
    ├── A2_503020_compliance.png
    ├── A3_budget_utilisation.png
    ├── A4_yoy_matrix.png
    ├── A5_anomaly_analysis.png
    ├── A6_correlation_drivers.png
    ├── A7_temporal_heatmap.png
    ├── A8_income_analysis.png
    ├── A9_forecast_scenarios.png
    ├── A10_priority_matrix.png
    ├── ML1_timeseries_forecast.png
    ├── ML2_anomaly_detection.png
    └── ML3_clustering.png
```

---

## How I Structured the Analysis

I used a MECE issue tree to make sure I wasn't just poking around the data looking for something interesting. The structure forces you to be exhaustive and non-overlapping — every possible explanation gets tested, and you close each one before moving on.

```
Is the person in deficit because of an income problem?
├── Is income too low?              → No. $14,719/month is enough for 20% savings.
├── Is income growing slowly?       → No. Income grew faster than expenses in 3 of 4 years.
└── Is income too concentrated?     → Moderate. HHI = 0.374. Salary is only 17%.

Is it an expense problem?
├── Which categories breach budget? → All 7. Every single one.
├── Fixed vs variable split?        → 29% fixed — healthy. Variable is the issue.
├── Anomalous transactions?         → 54 flagged by Isolation Forest ($33,338).
└── Is discretionary spend driving it? → Yes. Correlation r = -0.225 with net cashflow.

Is it a behaviour problem?
├── Temporal patterns?              → Summer peaks, Friday is highest spend day.
├── Is spending accelerating?       → No. Declining year-on-year since 2020.
└── 50/30/20 compliance?            → 17% needs compliance, 18% wants compliance.

Is it structural?
├── Overall health score?           → 26/100. Critical.
├── Savings trajectory?             → Improving — +63 percentage points over 5 years.
└── Forward outlook?                → Breakeven projected January 2025.
```

---

## Dataset

| Property | Detail |
|---|---|
| Source | [Kaggle — Personal Finance Dataset](https://www.kaggle.com/datasets/ramyapintchy/personal-finance-data?select=Personal_Finance_Dataset.csv) |
| Rows | 1,500 transactions |
| Period | January 2020 – December 2024 |
| Categories | 10 (Salary, Investment, Other, Rent, Food & Drink, Shopping, Travel, Entertainment, Health & Fitness, Utilities) |
| Bug fixed | Salary was labelled as Expense. Corrected before any calculations. |

### Feature Engineering — 20 columns added

The original dataset had 5 columns. I engineered 20 more. A few I want to specifically call out:

- `Budget_Category` (Needs/Wants/Savings) — this one column is what enabled the entire 50/30/20 framework. Without classifying transactions this way, you just have a pile of numbers.
- `Is_Discretionary` — binary flag for shopping, travel, entertainment. Used in the regression analysis to isolate discretionary spend as a deficit driver.
- `Amount_ZScore` — calculated at category level, not globally. A $1,900 travel transaction is normal. A $1,900 personal care transaction is not. Global Z-scores miss this distinction.
- `Season` — Winter/Spring/Summer/Autumn. Summer ended up being the highest-spend season, which feeds directly into the forecast's seasonal adjustment.

---

## KPI Framework — 12 metrics

I defined these before running the analysis, not after. Defining KPIs upfront stops you from cherry-picking metrics that make the data look more interesting than it is.

| # | KPI | Value | Target | Status |
|---|---|---|---|---|
| 1 | Monthly Savings Rate | -71.7% | ≥ 20% | Critical |
| 2 | Budget Adherence Rate | 8.5% | ≥ 80% | Critical |
| 3 | Income Diversification (HHI) | 0.374 | < 0.25 | Moderate |
| 4 | Expense-to-Income Ratio | 171.7% | < 80% | Critical |
| 5 | Discretionary Spend Ratio | 52.6% | ≤ 30% | Excessive |
| 6 | 50% Rule Compliance | 17% of months | ≥ 70% | Failing |
| 7 | 30% Rule Compliance | 18% of months | ≥ 70% | Failing |
| 8 | Deficit Month Rate | 67% | < 20% | Critical |
| 9 | Fixed:Variable Cost Ratio | 29% fixed | < 50% | Healthy |
| 10 | Savings Velocity | +63pp | > 0 | Improving |
| 11 | Anomaly Rate (ML) | 5.0% | < 5% | At threshold |
| 12 | Financial Health Score | 26/100 | ≥ 70 | Critical |

The composite Financial Health Score (26/100) is built from these 12 metrics weighted by their importance. Income diversification scored 20/20 — that's a genuine strength in this dataset. Savings rate and expense-to-income ratio scored zero. That's where all the work needs to go.

---

## Machine Learning Models

I want to be upfront about why I chose these three techniques and not others.

### ML1 — Time Series Forecasting (Holt Exponential Smoothing)

I considered ARIMA but 60 monthly data points is on the low end for it. ARIMA needs stationarity testing and iterative order selection — with this sample size, you risk overfitting the parameters to noise. Holt's handles trend and seasonality cleanly with fewer parameters. I added a seasonal multiplier on top to capture the summer spending spikes, and used bootstrap resampling for the confidence intervals rather than analytical standard errors, since bootstrapping makes fewer distributional assumptions.

Model accuracy: 85.1% (MAPE = 14.9%). Breakeven projected January 2025 at current trajectory.

### ML2 — Anomaly Detection (Isolation Forest)

The standard approach here would be Z-score. I ran Z-score first and it found zero outliers, which felt wrong. The reason: Z-score is univariate — it only looks at amount within a category. Isolation Forest uses 8 features simultaneously: amount, log-amount, month number, day of week, category encoding, deviation from category average, category percentile rank, and day of month. A transaction can have a totally normal amount but be anomalous in its timing or context. That's exactly what Isolation Forest catches.

Result: 54 transactions flagged, $33,338 total. Utilities had 19 of them, which points to auto-renewals or subscription spikes worth reviewing.

### ML3 — K-Means Clustering

I used Silhouette Score to find optimal K rather than just eyeballing an elbow plot — K=2 came out cleanest. The two clusters separated into what I called "Borderline" months (42 of 60) and "Deficit" months (18 of 60). The interesting thing from the transition analysis is that recovery months are distinguished by lower wants spending, not higher income. Which again points to discretionary control as the primary lever.

I deliberately did not use Random Forest or neural networks. With 60 monthly rows, any supervised model would overfit badly. The three techniques I used are appropriate for this data size and each answers a distinct question.

---

## Key Findings

1. Income is not the problem. $14,719/month is enough. The issue is that 52.6% of it goes on discretionary spending.
2. All 7 expense categories exceed their budgets. This is systemic, not a one-category issue.
3. The financial trajectory is genuinely improving — annual deficit dropped from -$102K in 2020 to -$5K in 2024.
4. 54 transactions worth $33,338 are statistically anomalous and should be reviewed individually.
5. 42 of 60 months are "Borderline" — one category cut away from being positive.

---

## Recommendations

| Priority | Action | Why | Annual Impact |
|---|---|---|---|
| 1 | Automate $500/month savings transfer on payday | Removes discretionary access before spending begins | $6,000 |
| 2 | Subscription and utilities audit | 19 anomalous Utilities transactions flagged | $11,800 |
| 3 | Hard monthly cap on Travel, Health, Entertainment | Running at 500–800% of benchmark budgets | $8,500 |
| 4 | Increase investment contributions by $300/month | Investment income already 41% of total — build on this strength | $2,520/yr return |
| 5 | 30-minute monthly review against these KPIs | Sustains all other changes | — |

Combined projected impact: from -$3,250/month to +$1,200–$1,800/month within 6 months.

---

## How to Run

```bash
pip install pandas numpy matplotlib seaborn scikit-learn openpyxl scipy

# Run in this order
python analysis/mbb_finance_analysis.py
python ml_models/ml1_timeseries.py
python ml_models/ml2_anomaly.py
python ml_models/ml3_clustering.py
```

The HTML dashboard (`dashboard/Smart_Finance_Tracker_Dashboard.html`) opens directly in any browser — no Python or Power BI needed.

---

## Tools

Python (pandas, numpy, matplotlib, seaborn, scikit-learn) · openpyxl · Chart.js · Power BI · Excel

---

*Vaishnavi Jitendra Bhor — vaishnavibhor123@gmail.com*  
*[LinkedIn](https://www.linkedin.com/in/vaishnavi-bhor-business-analyst/) | MSc Business Analytics, University of Manchester*  
*Open to Business Analyst, Data Analyst, and consulting roles in UK and Europe*
