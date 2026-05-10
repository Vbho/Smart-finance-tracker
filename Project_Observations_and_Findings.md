# Project Notes — What I Found, What I Learned, What I'd Do Differently
## Smart Personal Finance Tracker
**Vaishnavi Jitendra Bhor**  
[LinkedIn](https://www.linkedin.com/in/vaishnavi-bhor-business-analyst/) | vaishnavibhor123@gmail.com  
Dataset: [Kaggle Personal Finance Dataset](https://www.kaggle.com/datasets/ramyapintchy/personal-finance-data?select=Personal_Finance_Dataset.csv)

---

I want to write this document differently from most project writeups. Instead of just listing what I did, I want to explain the thinking behind the decisions — why I chose one approach over another, where I was surprised by what I found, and what I'd change if I did this again. That's the kind of thinking I think actually matters in an analyst role, more than whether the charts look good.

---

## The Data Problem I Found First

Before I did anything else, I ran a basic quality check on the dataset. The first thing I check on any dataset is whether the categorical labels make sense — it's the kind of thing that gets missed when people just start plotting.

I found that all 146 Salary transactions were classified as `Expense`. That's a significant mistake. Without correcting it, income would have been understated by $149,054, and the savings rate calculation would have been completely wrong for the entire 5-year period. Every percentage, every KPI, every recommendation downstream would have been built on bad foundations.

This is something I've learned from working across multiple client projects at Incentius — the data is almost never clean, and the worst errors are usually the quiet ones that don't throw an error message, they just silently corrupt your analysis. The Salary issue didn't cause Python to crash. If I hadn't checked manually, I would never have known.

I fixed it, noted it in the Excel workbook for audit purposes, and carried on. That's what you do.

The dataset also has a second limitation worth being upfront about: all the transaction descriptions are auto-generated gibberish. "Score each." "Quality throughout." These are not real merchant names. It means I couldn't do merchant-level analysis — which in a real engagement would have been valuable (knowing exactly which subscriptions to cancel, which specific retailer accounts for most of the shopping spend, etc.). I adapted the analysis to work at category level, which is sufficient for strategic recommendations but isn't as granular as I'd want in a live client project.

---

## On Feature Engineering

I added 20 new columns to the original 5. I want to explain the ones that actually mattered.

The most important was `Budget_Category` — classifying every transaction as Needs, Wants, or Savings. This one column is what made the 50/30/20 framework possible. Without it, you just have transactions. With it, you can ask whether the individual is structurally misallocating income, which turned out to be the central finding.

The second most useful was `Is_Discretionary` — a binary flag for shopping, travel, and entertainment. I used this in the regression analysis to quantify how much each dollar of discretionary spending reduces net cashflow. The correlation came out at -0.225. That's not massive, but it's consistent, and it points in the right direction. The regression confirmed what the budget analysis was already suggesting: the discretionary categories are where the financial damage is happening.

I spent some time thinking about whether to use a global Z-score or a category-level Z-score for `Amount_ZScore`. A global Z-score treats a $1,900 transaction as equally suspicious whether it's in Travel or Personal Care. That's wrong — a $1,900 travel spend is completely normal, a $1,900 personal care transaction is highly unusual. Category-level normalisation made more sense. This turned out to matter later when I ran the Isolation Forest, because the category-encoded features behave differently at category scale.

---

## On the KPI Framework

I defined the 12 KPIs before running the analysis. I want to be clear about why I think that matters.

If you define your metrics after you've seen the data, you end up selecting the ones that make the story look interesting. That's a subtle form of bias that produces findings which look impressive but aren't necessarily true. Pre-committing to the metrics means the analysis validates or challenges them, rather than the metrics being chosen to support what you already see.

The Financial Health Score (26/100) is the one number that summarises everything. I built it as a weighted composite: savings rate contributes 25 points, expense-to-income ratio 20 points, income diversification 20 points, budget adherence 20 points, and 50/30/20 compliance 15 points. The weights reflect how much each metric actually determines long-term financial outcomes.

The result — 26/100 — is bad. But the decomposition matters more than the headline. Income diversification scored 20/20. Savings velocity (how quickly things are improving) also scored well. The score is being dragged down entirely by the expense side. That's a different and more solvable problem than if income were also the issue.

---

## On the KPI Values — An Honest Note

The budget benchmarks I used (Rent $1,200, Food $800, etc.) are reasonable industry standards for a developed market. The dataset doesn't specify where this person lives. If they're in a high cost-of-living city, the Rent benchmark in particular might be unrealistic — $1,200/month for rent is very low in London or Zurich, for example.

In a real engagement I would spend time early on calibrating benchmarks to the specific person's context before running any comparison against them. For this portfolio project I used the standards as a diagnostic tool — they tell you the direction of the problem even if the exact numbers aren't perfectly calibrated.

The 807% Health & Fitness utilisation almost certainly doesn't mean someone is spending $2,420/month on gym memberships. It more likely means the $300 benchmark doesn't reflect this person's actual healthcare costs (which can be high if they're in a country without public healthcare). Context I don't have from the dataset.

---

## On the Machine Learning Choices

I want to be honest about this section because I think people sometimes add ML to a portfolio project to impress rather than because it genuinely adds something.

**Time series forecasting** was straightforward — 60 months of sequential data with a clear trend, forecasting future values is a natural use case. I went with Holt's Exponential Smoothing over ARIMA because with 60 data points ARIMA can be unstable. You need to estimate multiple parameters (p, d, q) and with a small sample those estimates have high variance. Holt's is more stable and the output is easier to explain to a non-technical audience, which matters in a consulting context. 85.1% accuracy is honest — not stellar, but not pretending to be better than it is.

**Isolation Forest** was used because the Z-score approach produced zero anomalies, which felt wrong. I want to flag that the 54 transactions it flagged are not necessarily errors — they're transactions that look statistically unusual given all their features combined. In a real project these would go to a subject matter expert for manual review. Some will turn out to be fine (annual insurance renewals, one-off purchases). Some might actually be worth investigating. The ML model surfaces them; a human judges them.

**K-Means clustering** is the one I'm most pleased with in terms of the insight it produced. K=2 was optimal by Silhouette Score. The finding that recovery months are distinguished by lower wants spending rather than higher income was not something I was looking for — it came from comparing the cluster centroids. That's the kind of result that feels genuinely discovered rather than constructed.

I did not use Random Forest or neural networks. 60 monthly rows is not enough data for supervised classification without serious overfitting risk. On a larger dataset, those techniques would be appropriate — I'm keeping them for a follow-up project with more rows.

---

## What I'd Do Differently

A few honest reflections:

**I'd use real bank data.** The lorem ipsum transaction descriptions are the biggest gap in this project. With real merchant names I could have built a subscription tracker, identified specific retailers driving the shopping overspend, and made the recommendations much more concrete. If you're reading this and building something similar, download your own bank statement CSV and use that.

**I'd add a forecasting model per category**, not just at the total level. Knowing that total expenses are projected to stabilise isn't as useful as knowing that Travel specifically is projected to increase in summer. Category-level forecasts would make the recommendations much more targeted.

**The budget benchmarks need personalisation.** I'd spend an hour at the start of a real engagement just agreeing what reasonable category budgets are for this specific person's circumstances before running any utilisation analysis.

**The clustering could be pushed further.** With more time I'd try to build a simple early-warning model — if by the 10th of the month the spending profile matches the Deficit cluster centroid, send an alert. That's genuinely usable. The clustering analysis as it stands is descriptive; it could easily become predictive with one more step.

---

## What This Project Demonstrates

Honestly, what I was trying to show with this project is not that I know how to code. It's that I know how to think about a problem before I start coding.

The MECE issue tree, the pre-defined KPIs, the hypothesis testing structure — these are habits from working in analytics where the cost of going down the wrong analytical path is real. At Incentius I saw what happens when decisions get made before the data is properly validated — the cost of correcting course mid-project is always higher than getting the foundations right at the start. Getting the structure right before you start is always the better path.

The ML models add genuine value here — the anomaly detection found something Z-score missed, the clustering produced an unexpected insight about recovery months. But they're not the point of the project. The point is the question at the top: why is this person in deficit 67% of the time, and what would actually fix it?

The answer: the income is fine, the trajectory is improving, and three targeted changes to discretionary spending would turn a -$3,250/month deficit into a +$1,200 to +$1,800/month surplus within six months. That's a usable answer. That's what the project was for.

---

*Vaishnavi Jitendra Bhor*  
*vaishnavibhor123@gmail.com*  
*[linkedin.com/in/vaishnavi-bhor-business-analyst](https://www.linkedin.com/in/vaishnavi-bhor-business-analyst/)*
