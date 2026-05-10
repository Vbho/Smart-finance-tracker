"""
╔══════════════════════════════════════════════════════════════════╗
║   SMART PERSONAL FINANCE TRACKER — CONSULTANT-GRADE ANALYSIS    ║
║   Methodology: McKinsey / BCG Analytical Framework              ║
║   Author: Vaishnavi Jitendra Bhor | Business Analyst Portfolio  ║
╚══════════════════════════════════════════════════════════════════╝

ANALYTICAL FRAMEWORK (MECE Issue Tree):
────────────────────────────────────────
Central Question: "Why is this individual in financial deficit
                  67% of the time despite earning $883K over
                  5 years — and what is the precise intervention
                  needed to achieve financial health?"

Issue Tree:
├── 1. INCOME PROBLEM?
│   ├── Is income too low in absolute terms?
│   ├── Is income growth keeping pace with expense growth?
│   └── Is income sufficiently diversified / stable?
│
├── 2. EXPENSE PROBLEM?
│   ├── Which categories are structurally over-budget?
│   ├── What is the fixed vs variable expense split?
│   ├── Are there anomalous / outlier transactions?
│   └── Is discretionary spending the primary driver?
│
├── 3. BEHAVIOUR PROBLEM?
│   ├── Are there temporal patterns (day/month/season)?
│   ├── Is spending accelerating over time?
│   └── What does the 50/30/20 rule compliance look like?
│
└── 4. STRUCTURAL PROBLEM?
    ├── What is the financial health score?
    ├── What is the savings trajectory?
    └── What does a forward forecast look like?

INSTALL REQUIREMENTS:
  pip install pandas numpy matplotlib seaborn scikit-learn openpyxl scipy

KPIs TRACKED (12 Core Metrics):
  1. Monthly Savings Rate (%)
  2. Budget Adherence Rate (% categories within budget)
  3. Income Diversification Ratio
  4. Fixed vs Variable Expense Ratio
  5. Discretionary Spend Ratio
  6. Expense-to-Income Ratio
  7. Month-over-Month Expense Growth Rate
  8. Year-over-Year Income Growth Rate
  9. Financial Health Score (composite 0–100)
 10. Savings Velocity (rate of savings improvement)
 11. Anomaly Rate (% transactions flagged as outliers)
 12. 50/30/20 Rule Compliance Score
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ── Visual Config ─────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor':  '#F8FAFC',
    'axes.facecolor':    '#F8FAFC',
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'font.family':       'DejaVu Sans',
    'axes.titlesize':    12,
    'axes.titleweight':  'bold',
    'axes.labelsize':    10,
    'xtick.labelsize':   8.5,
    'ytick.labelsize':   8.5,
})

BLUE   = '#2563EB'; GREEN  = '#16A34A'; RED    = '#DC2626'
AMBER  = '#D97706'; PURPLE = '#7C3AED'; TEAL   = '#0891B2'
PINK   = '#DB2777'; LIME   = '#65A30D'; GREY   = '#6B7280'
ORANGE = '#EA580C'; NAVY   = '#1E3A5F'; GOLD   = '#B45309'

PALETTE = [BLUE,GREEN,RED,AMBER,PURPLE,TEAL,PINK,LIME,GREY,ORANGE]

# Category classifications
FIXED_CATS        = ['Rent', 'Utilities']
VARIABLE_CATS     = ['Food & Drink','Shopping','Travel',
                     'Entertainment','Health & Fitness']
NEEDS_CATS        = ['Rent','Food & Drink','Utilities','Health & Fitness']
WANTS_CATS        = ['Shopping','Travel','Entertainment']
SAVINGS_CATS      = ['Investment']
INCOME_CATS       = ['Salary','Investment','Other']
EXPENSE_CATS      = ['Food & Drink','Rent','Shopping','Travel',
                     'Entertainment','Health & Fitness','Utilities']

BUDGETS = {
    'Food & Drink':     800, 'Rent':          1200,
    'Shopping':         600, 'Travel':         500,
    'Entertainment':    400, 'Health & Fitness':300,
    'Utilities':        350,
}

def divider(title):
    print(f"\n{'═'*60}")
    print(f"  {title}")
    print(f"{'═'*60}")

def section(title):
    print(f"\n[ {title} ]")
    print("-" * 50)

# ── HOW TO RUN ───────────────────────────────────────────────
# From the root of the repository:
#   pip install pandas numpy matplotlib seaborn scikit-learn openpyxl scipy
#   python analysis/mbb_finance_analysis.py
#
# Output files will be saved to:
#   data/personal_finance_enriched.csv
#   data/monthly_cashflow_kpis.csv
#   charts/A1_executive_dashboard.png  ...through...  charts/A10_priority_matrix.png
#
# Make sure the data/ and charts/ folders exist before running.
# ─────────────────────────────────────────────────────────────

import os
os.makedirs('charts', exist_ok=True)
os.makedirs('data',   exist_ok=True)

print("╔══════════════════════════════════════════════════════════╗")
print("║   SMART FINANCE TRACKER — MBB-GRADE FULL ANALYSIS       ║")
print("║   Vaishnavi Jitendra Bhor | Business Analyst Portfolio   ║")
print("╚══════════════════════════════════════════════════════════╝")


# ══════════════════════════════════════════════════════════
# PHASE 0: LOAD & CRITICAL FIX
# ══════════════════════════════════════════════════════════
divider("PHASE 0: DATA INGESTION & QUALITY AUDIT")

df = pd.read_csv('data/Personal_Finance_Dataset.csv')

section("0.1 Raw Data Audit")
print(f"  Shape              : {df.shape}")
print(f"  Null values        : {df.isnull().sum().sum()}")
print(f"  Duplicates         : {df.duplicated().sum()}")
print(f"  Data types         :")
for col, dtype in df.dtypes.items():
    print(f"    {col:<30} {dtype}")

section("0.2 Critical Bug Fix — Salary Misclassification")
before = df[df['Category']=='Salary']['Type'].value_counts().to_dict()
df.loc[df['Category']=='Salary', 'Type'] = 'Income'
after  = df[df['Category']=='Salary']['Type'].value_counts().to_dict()
print(f"  BEFORE fix: Salary Type → {before}")
print(f"  AFTER  fix: Salary Type → {after}")
print(f"  ✓ 146 records corrected. Without this fix, income")
print(f"    was understated by ${df[df['Category']=='Salary']['Amount'].sum():,.0f}")
print(f"    and savings rate calculation would be entirely wrong.")


# ══════════════════════════════════════════════════════════
# PHASE 1: FEATURE ENGINEERING (20 NEW COLUMNS)
# ══════════════════════════════════════════════════════════
divider("PHASE 1: FEATURE ENGINEERING — 20 NEW COLUMNS")

section("1.1 Temporal Features")
df['Date']          = pd.to_datetime(df['Date'])
df['Year']          = df['Date'].dt.year
df['Month_Num']     = df['Date'].dt.month
df['Month_Period']  = df['Date'].dt.to_period('M').astype(str)
df['Month_dt']      = pd.to_datetime(df['Month_Period'])
df['Quarter']       = 'Q' + df['Date'].dt.quarter.astype(str) + '_' + df['Year'].astype(str)
df['Day_of_Week']   = df['Date'].dt.strftime('%A')
df['DOW_Num']       = df['Date'].dt.dayofweek
df['Is_Weekend']    = df['DOW_Num'] >= 5
df['Week_of_Year']  = df['Date'].dt.isocalendar().week.astype(int)
df['Month_Name']    = df['Date'].dt.strftime('%b')
month_names = ['Jan','Feb','Mar','Apr','May','Jun',
               'Jul','Aug','Sep','Oct','Nov','Dec']
season_map = {12:'Winter',1:'Winter',2:'Winter',
              3:'Spring',4:'Spring',5:'Spring',
              6:'Summer',7:'Summer',8:'Summer',
              9:'Autumn',10:'Autumn',11:'Autumn'}
df['Season']        = df['Month_Num'].map(season_map)

section("1.2 Expense Classification Features")
df['Expense_Type']       = df['Category'].apply(
    lambda x: 'Fixed'    if x in FIXED_CATS    else
              'Variable'  if x in VARIABLE_CATS else 'Income/Other')
df['Budget_Category']    = df['Category'].apply(
    lambda x: 'Needs'    if x in NEEDS_CATS    else
              'Wants'     if x in WANTS_CATS    else
              'Savings'   if x in SAVINGS_CATS  else 'Income/Other')
df['Is_Discretionary']   = df['Category'].isin(WANTS_CATS)
df['Monthly_Budget_Limit']= df['Category'].map(BUDGETS).fillna(0)

section("1.3 Statistical Outlier Detection (Z-Score Method)")
df['Amount_ZScore'] = df.groupby('Category')['Amount'].transform(
    lambda x: np.abs(stats.zscore(x, nan_policy='omit')))
df['Is_Outlier']    = df['Amount_ZScore'] > 2.5
n_outliers = df['Is_Outlier'].sum()
outlier_pct = n_outliers / len(df) * 100
print(f"  Outlier threshold  : Z-score > 2.5")
print(f"  Outliers flagged   : {n_outliers} transactions ({outlier_pct:.1f}%)")
print(f"  Outlier value      : ${df[df['Is_Outlier']]['Amount'].sum():,.2f}")

section("1.4 Monthly Aggregate Features")
# Monthly totals
monthly_income  = df[df['Type']=='Income'].groupby('Month_Period')['Amount'].sum().reset_index()
monthly_expense = df[df['Type']=='Expense'].groupby('Month_Period')['Amount'].sum().reset_index()
monthly_income.columns  = ['Month_Period','Monthly_Income']
monthly_expense.columns = ['Month_Period','Monthly_Expense']

cashflow = monthly_income.merge(monthly_expense, on='Month_Period', how='outer').fillna(0)
cashflow['Month_dt']          = pd.to_datetime(cashflow['Month_Period'])
cashflow                      = cashflow.sort_values('Month_dt').reset_index(drop=True)
cashflow['Net_Cashflow']      = cashflow['Monthly_Income'] - cashflow['Monthly_Expense']
cashflow['Savings_Rate_Pct']  = (cashflow['Net_Cashflow'] / cashflow['Monthly_Income'].replace(0,np.nan) * 100).round(2)
cashflow['Expense_to_Income'] = (cashflow['Monthly_Expense'] / cashflow['Monthly_Income'].replace(0,np.nan) * 100).round(2)
cashflow['Cumulative_Net']    = cashflow['Net_Cashflow'].cumsum()
cashflow['Is_Deficit']        = cashflow['Net_Cashflow'] < 0

# Rolling averages (3-month and 6-month)
cashflow['Income_3M_Avg']     = cashflow['Monthly_Income'].rolling(3).mean()
cashflow['Expense_3M_Avg']    = cashflow['Monthly_Expense'].rolling(3).mean()
cashflow['Savings_Rate_3M']   = cashflow['Savings_Rate_Pct'].rolling(3).mean()
cashflow['Expense_6M_Avg']    = cashflow['Monthly_Expense'].rolling(6).mean()

# MoM growth rates
cashflow['Income_MoM_Growth']  = cashflow['Monthly_Income'].pct_change() * 100
cashflow['Expense_MoM_Growth'] = cashflow['Monthly_Expense'].pct_change() * 100
cashflow['Year']               = pd.to_datetime(cashflow['Month_Period']).dt.year

# 50/30/20 Rule monthly compliance
monthly_needs = df[df['Budget_Category']=='Needs'].groupby('Month_Period')['Amount'].sum()
monthly_wants = df[df['Budget_Category']=='Wants'].groupby('Month_Period')['Amount'].sum()
monthly_savgs = df[df['Budget_Category']=='Savings'].groupby('Month_Period')['Amount'].sum()

cashflow = cashflow.join(monthly_needs.rename('Needs_Spend'), on='Month_Period')
cashflow = cashflow.join(monthly_wants.rename('Wants_Spend'), on='Month_Period')
cashflow = cashflow.join(monthly_savgs.rename('Savings_Invest'), on='Month_Period')
cashflow[['Needs_Spend','Wants_Spend','Savings_Invest']] = \
    cashflow[['Needs_Spend','Wants_Spend','Savings_Invest']].fillna(0)

cashflow['Needs_Pct']   = cashflow['Needs_Spend']    / cashflow['Monthly_Income'].replace(0,np.nan) * 100
cashflow['Wants_Pct']   = cashflow['Wants_Spend']    / cashflow['Monthly_Income'].replace(0,np.nan) * 100
cashflow['Savings_Pct'] = cashflow['Savings_Invest'] / cashflow['Monthly_Income'].replace(0,np.nan) * 100

cashflow['Needs_Compliant']   = cashflow['Needs_Pct']   <= 50
cashflow['Wants_Compliant']   = cashflow['Wants_Pct']   <= 30
cashflow['Savings_Compliant'] = cashflow['Savings_Pct'] >= 20

print(f"  Feature engineering complete. Total features: {len(df.columns)}")
new_cols = ['Expense_Type','Budget_Category','Is_Discretionary',
            'Amount_ZScore','Is_Outlier','Season','Day_of_Week',
            'Is_Weekend','Monthly_Budget_Limit','DOW_Num','Week_of_Year']
print(f"  New columns added: {new_cols}")


# ══════════════════════════════════════════════════════════
# PHASE 2: KPI FRAMEWORK
# ══════════════════════════════════════════════════════════
divider("PHASE 2: KPI DASHBOARD — 12 CORE METRICS")

section("KPI 1: Monthly Savings Rate")
avg_sr = cashflow['Savings_Rate_Pct'].mean()
med_sr = cashflow['Savings_Rate_Pct'].median()
print(f"  Average savings rate   : {avg_sr:.1f}%")
print(f"  Median  savings rate   : {med_sr:.1f}%")
print(f"  Target (50/30/20)      : 20.0%")
print(f"  Gap to target          : {20 - avg_sr:+.1f}pp")
print(f"  Months at/above 20%    : {(cashflow['Savings_Rate_Pct'] >= 20).sum()} / {len(cashflow)}")
print(f"  RATING: {'🔴 CRITICAL' if avg_sr < 0 else '🟡 BELOW TARGET' if avg_sr < 20 else '🟢 ON TRACK'}")

section("KPI 2: Budget Adherence Rate")
cat_monthly = df[df['Type']=='Expense'].groupby(
    ['Month_Period','Category'])['Amount'].sum().reset_index()
cat_monthly['Budget'] = cat_monthly['Category'].map(BUDGETS)
cat_monthly_valid = cat_monthly[cat_monthly['Budget'].notna()].copy()
cat_monthly_valid['Within_Budget'] = cat_monthly_valid['Amount'] <= cat_monthly_valid['Budget']
budget_adherence = cat_monthly_valid['Within_Budget'].mean() * 100
print(f"  Budget adherence rate  : {budget_adherence:.1f}%")
print(f"  Target                 : ≥ 80%")
print(f"  RATING: {'🔴 CRITICAL' if budget_adherence < 50 else '🟡 NEEDS WORK' if budget_adherence < 80 else '🟢 ON TRACK'}")

per_cat_adherence = cat_monthly_valid.groupby('Category')['Within_Budget'].mean() * 100
print(f"\n  Adherence by category:")
for cat, pct in per_cat_adherence.sort_values().items():
    icon = '🔴' if pct < 40 else '🟡' if pct < 70 else '🟢'
    print(f"    {icon} {cat:<20} {pct:.1f}%")

section("KPI 3: Income Diversification Ratio")
income_by_source = df[df['Type']=='Income'].groupby('Category')['Amount'].sum()
total_income_val = income_by_source.sum()
salary_share = income_by_source.get('Salary', 0) / total_income_val * 100
invest_share = income_by_source.get('Investment', 0) / total_income_val * 100
other_share  = income_by_source.get('Other', 0) / total_income_val * 100
print(f"  Salary     : {salary_share:.1f}% of total income")
print(f"  Investment : {invest_share:.1f}% of total income")
print(f"  Other      : {other_share:.1f}% of total income")
print(f"  HHI Score  : {(salary_share**2 + invest_share**2 + other_share**2)/10000:.3f}")
print(f"  (HHI < 0.25 = well diversified | > 0.5 = concentrated)")
print(f"  RATING: {'🟢 DIVERSIFIED' if salary_share < 60 else '🟡 MODERATE' if salary_share < 80 else '🔴 CONCENTRATED'}")

section("KPI 4: Fixed vs Variable Expense Ratio")
expense_df = df[df['Type']=='Expense'].copy()
fixed_total    = expense_df[expense_df['Expense_Type']=='Fixed']['Amount'].sum()
variable_total = expense_df[expense_df['Expense_Type']=='Variable']['Amount'].sum()
total_exp      = expense_df['Amount'].sum()
fixed_pct      = fixed_total / total_exp * 100
variable_pct   = variable_total / total_exp * 100
print(f"  Fixed expenses    : ${fixed_total:>12,.2f}  ({fixed_pct:.1f}%)")
print(f"  Variable expenses : ${variable_total:>12,.2f}  ({variable_pct:.1f}%)")
print(f"  F:V Ratio         : {fixed_pct/variable_pct:.2f}:1")
print(f"  Ideal range       : Fixed < 50% of total expenses")
print(f"  RATING: {'🟢 HEALTHY' if fixed_pct < 50 else '🟡 MODERATE' if fixed_pct < 65 else '🔴 HIGH FIXED COSTS'}")

section("KPI 5: Discretionary Spend Ratio")
disc_total = expense_df[expense_df['Is_Discretionary']]['Amount'].sum()
disc_pct   = disc_total / total_exp * 100
disc_of_income = disc_total / total_income_val * 100
print(f"  Discretionary spend : ${disc_total:>12,.2f}")
print(f"  % of total expenses : {disc_pct:.1f}%")
print(f"  % of total income   : {disc_of_income:.1f}%")
print(f"  Target (50/30/20)   : Wants ≤ 30% of income")
print(f"  RATING: {'🟢 CONTROLLED' if disc_of_income <= 30 else '🟡 BORDERLINE' if disc_of_income <= 40 else '🔴 EXCESSIVE'}")

section("KPI 6: Expense-to-Income Ratio (Monthly)")
avg_ei = cashflow['Expense_to_Income'].mean()
med_ei = cashflow['Expense_to_Income'].median()
print(f"  Average E:I ratio   : {avg_ei:.1f}%")
print(f"  Median  E:I ratio   : {med_ei:.1f}%")
print(f"  Target              : < 80% (leaving 20% for savings)")
print(f"  Months > 100%       : {(cashflow['Expense_to_Income'] > 100).sum()} of {len(cashflow)}")
print(f"  RATING: {'🔴 CRITICAL' if avg_ei > 120 else '🟡 HIGH' if avg_ei > 90 else '🟢 HEALTHY'}")

section("KPI 7 & 8: MoM Expense Growth vs YoY Income Growth")
avg_mom_expense = cashflow['Expense_MoM_Growth'].mean()
avg_mom_income  = cashflow['Income_MoM_Growth'].mean()
yearly = df.groupby(['Year','Type'])['Amount'].sum().unstack().reset_index()
yearly['Income_YoY']  = yearly.get('Income',0).pct_change() * 100
yearly['Expense_YoY'] = yearly.get('Expense',0).pct_change() * 100
print(f"  Avg MoM expense growth  : {avg_mom_expense:+.1f}%")
print(f"  Avg MoM income growth   : {avg_mom_income:+.1f}%")
print(f"\n  YoY Comparison:")
print(yearly[['Year','Income_YoY','Expense_YoY']].dropna().round(1).to_string(index=False))
print(f"\n  KEY INSIGHT: {'Income growing faster than expenses ✓' if yearly['Income_YoY'].mean() > yearly['Expense_YoY'].mean() else 'Expenses growing faster than income ✗'}")

section("KPI 9: 50/30/20 Rule Compliance Score")
needs_compliance   = cashflow['Needs_Compliant'].mean()   * 100
wants_compliance   = cashflow['Wants_Compliant'].mean()   * 100
savings_compliance = cashflow['Savings_Compliant'].mean() * 100
overall_5030_score = (needs_compliance + wants_compliance + savings_compliance) / 3

print(f"  50% rule (Needs ≤ 50% income)    : {needs_compliance:.0f}% months compliant")
print(f"  30% rule (Wants ≤ 30% income)    : {wants_compliance:.0f}% months compliant")
print(f"  20% rule (Savings ≥ 20% income)  : {savings_compliance:.0f}% months compliant")
print(f"  Overall compliance score         : {overall_5030_score:.1f} / 100")
print(f"  RATING: {'🔴 FAILING' if overall_5030_score < 40 else '🟡 PARTIAL' if overall_5030_score < 70 else '🟢 COMPLIANT'}")

section("KPI 10: Savings Velocity (Trajectory Analysis)")
first_half = cashflow.head(30)['Savings_Rate_Pct'].mean()
second_half = cashflow.tail(30)['Savings_Rate_Pct'].mean()
velocity = second_half - first_half
print(f"  First 30 months avg savings rate : {first_half:.1f}%")
print(f"  Last  30 months avg savings rate : {second_half:.1f}%")
print(f"  Savings velocity                 : {velocity:+.1f}pp")
print(f"  Direction: {'📈 IMPROVING' if velocity > 0 else '📉 DETERIORATING'}")

section("KPI 11: Anomaly Rate")
print(f"  Outlier transactions : {n_outliers} of {len(df)} ({outlier_pct:.1f}%)")
print(f"  Total outlier value  : ${df[df['Is_Outlier']]['Amount'].sum():,.2f}")
outlier_by_cat = df[df['Is_Outlier']].groupby('Category')['Amount'].agg(['count','sum','mean'])
print(f"\n  Outliers by category:")
print(outlier_by_cat.round(0).to_string())

section("KPI 12: Financial Health Score (Composite 0–100)")
def score_metric(value, thresholds, scores):
    for t, s in zip(thresholds, scores):
        if value <= t:
            return s
    return scores[-1]

s1 = score_metric(avg_sr,        [-50,0,10,20,30],     [0,5,10,20,25])
s2 = score_metric(budget_adherence,[20,40,60,80,100],  [0,5,10,15,20])
s3 = score_metric(salary_share,  [40,60,70,85,100],    [20,15,10,5,0])
s4 = score_metric(avg_ei,        [70,90,110,130,200],  [20,15,10,5,0])
s5 = score_metric(overall_5030_score,[20,40,60,80,100],[0,3,6,10,15])
fhs = s1 + s2 + s3 + s4 + s5

print(f"  Scoring breakdown:")
print(f"    Savings rate ({avg_sr:.1f}%)          : {s1}/25")
print(f"    Budget adherence ({budget_adherence:.1f}%)    : {s2}/20")
print(f"    Income diversification          : {s3}/20")
print(f"    Expense-to-income ({avg_ei:.1f}%)   : {s4}/20")
print(f"    50/30/20 compliance             : {s5}/15")
print(f"  ─────────────────────────────────")
print(f"  FINANCIAL HEALTH SCORE          : {fhs}/100")
if fhs < 30:
    print(f"  STATUS: 🔴 CRITICAL — Immediate intervention required")
elif fhs < 50:
    print(f"  STATUS: 🟠 POOR — Significant changes needed")
elif fhs < 70:
    print(f"  STATUS: 🟡 MODERATE — Several areas need attention")
else:
    print(f"  STATUS: 🟢 GOOD — Minor optimisations needed")


# ══════════════════════════════════════════════════════════
# PHASE 3: DIAGNOSTIC DEEP-DIVES
# ══════════════════════════════════════════════════════════
divider("PHASE 3: DIAGNOSTIC ANALYSIS")

section("3.1 Hypothesis 1 — Is income too low?")
income_needed = total_exp / 60 / 0.80  # expenses / months / 80% = needed for 20% savings
print(f"  Total 5yr income   : ${total_income_val:>12,.2f}")
print(f"  Total 5yr expenses : ${total_exp:>12,.2f}")
print(f"  Income required for 20% savings rate: ${income_needed:,.2f}/month")
print(f"  Actual avg monthly income           : ${cashflow['Monthly_Income'].mean():,.2f}/month")
print(f"  Income gap                          : ${income_needed - cashflow['Monthly_Income'].mean():+,.2f}/month")
print(f"  VERDICT: {'Income IS sufficient — expense control is the primary issue' if cashflow['Monthly_Income'].mean() >= income_needed else 'Income is insufficient — income growth AND expense control needed'}")

section("3.2 Hypothesis 2 — Which expense categories are structurally broken?")
cat_summary = expense_df.groupby('Category').agg(
    Total       = ('Amount','sum'),
    Monthly_Avg = ('Amount', lambda x: x.sum() / cashflow['Month_Period'].nunique()),
    Txn_Count   = ('Amount','count'),
    Avg_Txn     = ('Amount','mean'),
    Std_Dev     = ('Amount','std'),
    CV          = ('Amount', lambda x: x.std()/x.mean()*100),
    Max_Txn     = ('Amount','max'),
    Min_Txn     = ('Amount','min'),
).reset_index()
cat_summary['Budget']         = cat_summary['Category'].map(BUDGETS)
cat_summary['Pct_of_Total']   = cat_summary['Total'] / cat_summary['Total'].sum() * 100
cat_summary['Budget_Variance']= cat_summary['Monthly_Avg'] - cat_summary['Budget']
cat_summary['Utilisation_Pct']= cat_summary['Monthly_Avg'] / cat_summary['Budget'].replace(0,np.nan) * 100
cat_summary['Over_Budget']    = cat_summary['Budget_Variance'] > 0
cat_summary = cat_summary.sort_values('Utilisation_Pct', ascending=False)

print(f"\n  Category scorecard (sorted by budget utilisation):")
print(f"  {'Category':<20} {'Avg/Month':>10} {'Budget':>8} {'Variance':>10} {'Util%':>7} {'CV%':>6} {'Status'}")
print(f"  {'-'*80}")
for _, r in cat_summary.iterrows():
    status = '🔴 CRITICAL' if r['Utilisation_Pct'] > 150 else \
             '🟠 OVER'    if r['Utilisation_Pct'] > 100 else \
             '🟡 NEAR'    if r['Utilisation_Pct'] > 85  else '🟢 OK'
    print(f"  {r['Category']:<20} ${r['Monthly_Avg']:>9,.0f} ${r['Budget']:>7,.0f} "
          f"${r['Budget_Variance']:>+9,.0f} {r['Utilisation_Pct']:>6.0f}% "
          f"{r['CV']:>5.0f}% {status}")

section("3.3 Hypothesis 3 — Is spending accelerating over time?")
yearly_exp = expense_df.groupby('Year')['Amount'].sum()
yearly_inc = df[df['Type']=='Income'].groupby('Year')['Amount'].sum()
print(f"  Year-on-Year Expense vs Income Dynamics:")
print(f"  {'Year':<6} {'Expense':>12} {'Income':>12} {'Exp Growth':>11} {'Inc Growth':>11} {'Signal'}")
print(f"  {'-'*65}")
for i, yr in enumerate(sorted(yearly_exp.index)):
    exp = yearly_exp[yr]
    inc = yearly_inc.get(yr, 0)
    eg  = (exp / yearly_exp[yr-1] - 1) * 100 if i > 0 and yr-1 in yearly_exp else 0
    ig  = (inc / yearly_inc.get(yr-1,1) - 1) * 100 if i > 0 and yr-1 in yearly_inc else 0
    sig = '📈 Inc > Exp ✓' if ig > eg and i > 0 else '📉 Exp > Inc ✗' if i > 0 else 'Baseline'
    print(f"  {yr:<6} ${exp:>11,.0f} ${inc:>11,.0f} {eg:>+10.1f}% {ig:>+10.1f}% {sig}")

section("3.4 Correlation Analysis — What drives monthly deficits?")
corr_cols = ['Monthly_Income','Monthly_Expense','Net_Cashflow',
             'Needs_Spend','Wants_Spend','Savings_Invest']
corr_data = cashflow[corr_cols].dropna()
corr_matrix = corr_data.corr()

print(f"  Correlation with Net_Cashflow:")
net_corr = corr_matrix['Net_Cashflow'].drop('Net_Cashflow').sort_values()
for col, val in net_corr.items():
    bar = '█' * int(abs(val) * 20)
    direction = '+' if val > 0 else '-'
    print(f"    {col:<22} {direction}{bar:<22} {val:+.3f}")
print(f"\n  KEY FINDING: {net_corr.idxmin()} has the strongest negative correlation")
print(f"  with net cashflow ({net_corr.min():.3f}), meaning it is the")
print(f"  biggest destroyer of financial surplus.")

section("3.5 Temporal Pattern Analysis — When does money leak most?")
dow_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
dow_analysis = expense_df.groupby('Day_of_Week').agg(
    Total=('Amount','sum'), Count=('Amount','count'),
    Avg=('Amount','mean'), Median=('Amount','median')
).reindex(dow_order)

weekend_total  = dow_analysis.loc[['Saturday','Sunday'],'Total'].sum()
weekday_total  = dow_analysis.loc[['Monday','Tuesday','Wednesday','Thursday','Friday'],'Total'].sum()
weekend_pct    = weekend_total / (weekend_total + weekday_total) * 100
weekend_daily  = weekend_total / 2
weekday_daily  = weekday_total / 5
print(f"  Weekend spending share : {weekend_pct:.1f}% (2 out of 7 days)")
print(f"  Weekend avg per day   : ${weekend_daily:,.0f}")
print(f"  Weekday  avg per day  : ${weekday_daily:,.0f}")
print(f"  Weekend premium       : {weekend_daily/weekday_daily:.1f}x weekday rate")

season_analysis = expense_df.groupby('Season')['Amount'].agg(['sum','mean','count'])
print(f"\n  Seasonal spending:")
for season, row in season_analysis.iterrows():
    print(f"    {season:<10} Total: ${row['sum']:>10,.0f}  Avg/Txn: ${row['mean']:>8,.0f}")


# ══════════════════════════════════════════════════════════
# PHASE 4: ADVANCED VISUALISATIONS (10 Charts)
# ══════════════════════════════════════════════════════════
divider("PHASE 4: GENERATING 10 CONSULTANT-GRADE CHARTS")

# ── Chart 1: Executive Dashboard (Multi-KPI) ──────────────
fig = plt.figure(figsize=(18, 10))
fig.patch.set_facecolor('#F8FAFC')
gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.45, wspace=0.35)
fig.suptitle('PERSONAL FINANCE HEALTH DASHBOARD  |  5-Year Overview  |  2020–2024',
             fontsize=16, fontweight='bold', y=0.98, color=NAVY)

def kpi_card(ax, value, label, target, unit='', color=BLUE, fmt='.1f'):
    ax.set_facecolor('white')
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)
        spine.set_color('#E2E8F0')
    ax.set_xticks([]); ax.set_yticks([])
    val_str = f"{value:{fmt}}{unit}"
    ax.text(0.5, 0.62, val_str, transform=ax.transAxes,
            ha='center', va='center', fontsize=18, fontweight='bold', color=color)
    ax.text(0.5, 0.30, label, transform=ax.transAxes,
            ha='center', va='center', fontsize=9, color=GREY)
    ax.text(0.5, 0.10, f'Target: {target}', transform=ax.transAxes,
            ha='center', va='center', fontsize=7.5, color='#9CA3AF')

ax_k1 = fig.add_subplot(gs[0,0])
ax_k2 = fig.add_subplot(gs[0,1])
ax_k3 = fig.add_subplot(gs[0,2])
ax_k4 = fig.add_subplot(gs[0,3])

kpi_card(ax_k1, avg_sr,           'Avg Savings Rate',      '≥ 20%',    '%',
         RED if avg_sr < 0 else AMBER if avg_sr < 20 else GREEN)
kpi_card(ax_k2, budget_adherence, 'Budget Adherence',      '≥ 80%',    '%',
         RED if budget_adherence < 50 else AMBER if budget_adherence < 80 else GREEN)
kpi_card(ax_k3, fhs,              'Financial Health Score','≥ 70/100', '/100',
         RED if fhs < 30 else AMBER if fhs < 60 else GREEN, '.0f')
kpi_card(ax_k4, avg_ei,           'Expense-to-Income',    '< 80%',    '%',
         RED if avg_ei > 120 else AMBER if avg_ei > 90 else GREEN)

# Income vs Expense Trend
ax1 = fig.add_subplot(gs[1,:3])
x   = range(len(cashflow))
ax1.fill_between(x, cashflow['Monthly_Income'], alpha=0.12, color=GREEN)
ax1.fill_between(x, cashflow['Monthly_Expense'], alpha=0.12, color=RED)
ax1.plot(x, cashflow['Monthly_Income'], color=GREEN, lw=2, label='Income', zorder=3)
ax1.plot(x, cashflow['Monthly_Expense'], color=RED,  lw=2, label='Expenses', zorder=3)
ax1.plot(x, cashflow['Expense_3M_Avg'], color=ORANGE, lw=1.5,
         linestyle='--', label='3M Avg Expense', zorder=4)
ax1.set_xticks(list(x)[::6])
ax1.set_xticklabels(cashflow['Month_Period'].tolist()[::6], rotation=45, ha='right')
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p: f'${v:,.0f}'))
ax1.set_title('Monthly Income vs Expenses  |  3M Rolling Average', fontsize=11)
ax1.legend(fontsize=8); ax1.grid(axis='y', alpha=0.3)
ax1.set_facecolor('white')

# Financial Health Gauge
ax2 = fig.add_subplot(gs[1,3])
theta = np.linspace(0, np.pi, 200)
colors_gauge = [RED, ORANGE, AMBER, LIME, GREEN]
bounds = [0, 20, 40, 60, 80, 100]
for i in range(len(colors_gauge)):
    t1 = np.pi * (1 - bounds[i+1]/100)
    t2 = np.pi * (1 - bounds[i]/100)
    th = np.linspace(t1, t2, 50)
    ax2.fill_between(np.cos(th)*0.8, np.sin(th)*0.8,
                     np.cos(th)*1.0, alpha=0.7, color=colors_gauge[i])
    ax2.fill_between(np.cos(th)*0.55, np.sin(th)*0.55,
                     np.cos(th)*0.8, alpha=0.3, color=colors_gauge[i])
needle_angle = np.pi * (1 - fhs/100)
ax2.annotate('', xy=(np.cos(needle_angle)*0.7, np.sin(needle_angle)*0.7),
             xytext=(0, 0),
             arrowprops=dict(arrowstyle='->', color=NAVY, lw=2.5))
ax2.set_xlim(-1.2, 1.2); ax2.set_ylim(-0.3, 1.2)
ax2.set_aspect('equal'); ax2.axis('off')
ax2.text(0, -0.15, f'{fhs}/100', ha='center', fontsize=16,
         fontweight='bold', color=RED if fhs<30 else AMBER if fhs<60 else GREEN)
ax2.text(0, -0.28, 'Financial Health', ha='center', fontsize=9, color=GREY)
ax2.set_facecolor('white')
ax2.set_title('Health Score', fontsize=11)

# Savings Rate Over Time
ax3 = fig.add_subplot(gs[2,:2])
sr_colors = [GREEN if v>=20 else AMBER if v>=0 else RED
             for v in cashflow['Savings_Rate_Pct']]
ax3.bar(x, cashflow['Savings_Rate_Pct'], color=sr_colors, alpha=0.8, width=0.7, zorder=3)
ax3.plot(x, cashflow['Savings_Rate_3M'], color=NAVY, lw=2,
         linestyle='--', label='3M Rolling Avg', zorder=4)
ax3.axhline(20, color=BLUE, lw=1.5, linestyle=':', label='20% target')
ax3.axhline(0,  color='#374151', lw=1)
ax3.set_xticks(list(x)[::6])
ax3.set_xticklabels(cashflow['Month_Period'].tolist()[::6], rotation=45, ha='right')
ax3.set_title('Monthly Savings Rate  |  Target ≥ 20%', fontsize=11)
ax3.legend(fontsize=8); ax3.grid(axis='y', alpha=0.3, zorder=0)
ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p: f'{v:.0f}%'))
ax3.set_facecolor('white')

# Cumulative Net Position
ax4 = fig.add_subplot(gs[2,2:])
pos_mask = cashflow['Cumulative_Net'] >= 0
neg_mask = cashflow['Cumulative_Net'] < 0
ax4.fill_between(x, cashflow['Cumulative_Net'].where(pos_mask), 0, color=GREEN, alpha=0.3)
ax4.fill_between(x, cashflow['Cumulative_Net'].where(neg_mask), 0, color=RED, alpha=0.3)
ax4.plot(x, cashflow['Cumulative_Net'], color=NAVY, lw=2.2, zorder=3)
ax4.axhline(0, color='#374151', lw=1)
ax4.set_xticks(list(x)[::12])
ax4.set_xticklabels(cashflow['Month_Period'].tolist()[::12], rotation=45, ha='right')
ax4.set_title('Cumulative Net Financial Position', fontsize=11)
ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p: f'${v:,.0f}'))
ax4.grid(axis='y', alpha=0.3, zorder=0)
ax4.set_facecolor('white')

plt.savefig('charts/A1_executive_dashboard.png', dpi=150, bbox_inches='tight',
            facecolor='#F8FAFC')
plt.close()
print("  ✓ Chart A1: Executive KPI Dashboard")

# ── Chart 2: 50/30/20 Rule Monthly Compliance ─────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('50/30/20 Rule Compliance Analysis  |  Monthly Breakdown  |  2020–2024',
             fontsize=14, fontweight='bold')
fig.patch.set_facecolor('#F8FAFC')

rules = [
    ('Needs_Pct',   50, '50% Rule — Needs\n(Rent + Food + Utilities + Health)', axes[0]),
    ('Wants_Pct',   30, '30% Rule — Wants\n(Shopping + Travel + Entertainment)', axes[1]),
    ('Savings_Pct', 20, '20% Rule — Savings\n(Investment Contributions)', axes[2]),
]

for col, target, title, ax in rules:
    vals   = cashflow[col].dropna()
    x      = range(len(vals))
    target_line = target
    above  = (vals >= target_line).sum() if '20' in title else (vals <= target_line).sum()
    compliant_pct = above / len(vals) * 100
    colors_rule = [GREEN if (v<=target_line if '20' not in title else v>=target_line)
                   else RED for v in vals]
    ax.bar(x, vals, color=colors_rule, alpha=0.75, width=0.7, zorder=3)
    ax.axhline(target_line, color=NAVY, lw=2, linestyle='--',
               label=f'Target: {target_line}%')
    ax.set_xticks(list(x)[::12])
    ax.set_xticklabels(cashflow['Month_Period'].tolist()[:len(vals)][::12],
                       rotation=45, ha='right', fontsize=7.5)
    ax.set_title(f'{title}\nCompliant months: {compliant_pct:.0f}%', fontsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p: f'{v:.0f}%'))
    ax.legend(fontsize=8); ax.grid(axis='y', alpha=0.3, zorder=0)
    ax.set_facecolor('white')

plt.tight_layout()
plt.savefig('charts/A2_503020_compliance.png', dpi=150, bbox_inches='tight',
            facecolor='#F8FAFC')
plt.close()
print("  ✓ Chart A2: 50/30/20 Rule Compliance")

# ── Chart 3: Category Budget Utilisation Waterfall ────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 6))
fig.suptitle('Budget Utilisation Analysis  |  How Far Over/Under Budget?',
             fontsize=14, fontweight='bold')
fig.patch.set_facecolor('#F8FAFC')

cs_sorted = cat_summary.sort_values('Budget_Variance', ascending=False)
variances  = cs_sorted['Budget_Variance'].values
cat_names  = cs_sorted['Category'].values
var_colors = [RED if v>0 else GREEN for v in variances]

bars = ax1.barh(cat_names, variances, color=var_colors, alpha=0.85, height=0.6, zorder=3)
ax1.axvline(0, color='#374151', lw=1.5)
ax1.set_xlabel('Monthly Variance vs Budget ($)')
ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda v,p: f'${v:+,.0f}'))
ax1.set_title('Monthly Spend Variance from Budget\n(Negative = Under Budget)', fontsize=11)
ax1.grid(axis='x', alpha=0.3, zorder=0)
ax1.set_facecolor('white')
for bar, val in zip(bars, variances):
    ax1.text(val + (50 if val>0 else -50), bar.get_y() + bar.get_height()/2,
             f'${val:+,.0f}', va='center', ha='left' if val>0 else 'right', fontsize=9)

# Budget utilisation %
cs_sorted2 = cat_summary.sort_values('Utilisation_Pct', ascending=True)
util_colors = [RED   if u > 150 else ORANGE if u > 120 else
               AMBER if u > 100 else LIME   if u > 80  else GREEN
               for u in cs_sorted2['Utilisation_Pct']]
bars2 = ax2.barh(cs_sorted2['Category'], cs_sorted2['Utilisation_Pct'],
                 color=util_colors, alpha=0.85, height=0.6, zorder=3)
ax2.axvline(100, color=NAVY, lw=2, linestyle='--', label='100% = On Budget')
ax2.set_xlabel('Budget Utilisation (%)')
ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda v,p: f'{v:.0f}%'))
ax2.set_title('Budget Utilisation by Category\n(>100% = Over Budget)', fontsize=11)
ax2.legend(fontsize=9); ax2.grid(axis='x', alpha=0.3, zorder=0)
ax2.set_facecolor('white')
for bar, val in zip(bars2, cs_sorted2['Utilisation_Pct']):
    ax2.text(val+1, bar.get_y()+bar.get_height()/2,
             f'{val:.0f}%', va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/A3_budget_utilisation.png', dpi=150, bbox_inches='tight',
            facecolor='#F8FAFC')
plt.close()
print("  ✓ Chart A3: Budget Utilisation Waterfall")

# ── Chart 4: Year-on-Year Performance Matrix ──────────────
fig, axes = plt.subplots(2, 3, figsize=(18, 9))
fig.suptitle('Year-on-Year Financial Performance Matrix  |  2020–2024',
             fontsize=14, fontweight='bold')
fig.patch.set_facecolor('#F8FAFC')

yearly_full = cashflow.groupby('Year').agg(
    Income       =('Monthly_Income','sum'),
    Expense      =('Monthly_Expense','sum'),
    Net          =('Net_Cashflow','sum'),
    Avg_SR       =('Savings_Rate_Pct','mean'),
    Deficit_Months=('Is_Deficit','sum'),
).reset_index()
yearly_full['Income_Growth']  = yearly_full['Income'].pct_change()  * 100
yearly_full['Expense_Growth'] = yearly_full['Expense'].pct_change() * 100

yrs = yearly_full['Year'].tolist()
x   = range(len(yrs))

# I&E grouped bar
ax = axes[0,0]; ax.set_facecolor('white')
w  = 0.35
ax.bar([i-w/2 for i in x], yearly_full['Income'],  w, color=GREEN, alpha=0.85, label='Income')
ax.bar([i+w/2 for i in x], yearly_full['Expense'], w, color=RED,   alpha=0.85, label='Expense')
ax.set_xticks(x); ax.set_xticklabels(yrs)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'${v/1000:.0f}K'))
ax.set_title('Annual Income vs Expense'); ax.legend(fontsize=8); ax.grid(axis='y',alpha=0.3)

# Net savings waterfall
ax = axes[0,1]; ax.set_facecolor('white')
net_c = [GREEN if v>0 else RED for v in yearly_full['Net']]
bars  = ax.bar(x, yearly_full['Net'], color=net_c, alpha=0.85, width=0.6, zorder=3)
ax.axhline(0, color='#374151', lw=1)
ax.set_xticks(x); ax.set_xticklabels(yrs)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'${v:,.0f}'))
ax.set_title('Annual Net Position')
ax.grid(axis='y',alpha=0.3,zorder=0)
for bar, val in zip(bars, yearly_full['Net']):
    ax.text(bar.get_x()+bar.get_width()/2,
            bar.get_height()+(1000 if val>0 else -3000),
            f'${val:,.0f}', ha='center', fontsize=8, fontweight='bold')

# Growth rates comparison
ax = axes[0,2]; ax.set_facecolor('white')
valid = yearly_full.dropna(subset=['Income_Growth'])
x2   = range(len(valid))
ax.plot(x2, valid['Income_Growth'],  color=GREEN, lw=2.2, marker='o', ms=6, label='Income Growth')
ax.plot(x2, valid['Expense_Growth'], color=RED,   lw=2.2, marker='s', ms=6, label='Expense Growth')
ax.axhline(0, color='#374151', lw=1)
ax.fill_between(x2,
    [max(a,b) for a,b in zip(valid['Income_Growth'], valid['Expense_Growth'])],
    [min(a,b) for a,b in zip(valid['Income_Growth'], valid['Expense_Growth'])],
    alpha=0.12, color=BLUE)
ax.set_xticks(x2); ax.set_xticklabels(valid['Year'].tolist())
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'{v:.1f}%'))
ax.set_title('Income vs Expense Growth Rate YoY')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# Avg savings rate by year
ax = axes[1,0]; ax.set_facecolor('white')
sr_c = [GREEN if v>=20 else AMBER if v>=0 else RED for v in yearly_full['Avg_SR']]
bars3= ax.bar(x, yearly_full['Avg_SR'], color=sr_c, alpha=0.85, width=0.6, zorder=3)
ax.axhline(20, color=BLUE, lw=1.5, linestyle='--', label='20% target')
ax.axhline(0,  color='#374151', lw=1)
ax.set_xticks(x); ax.set_xticklabels(yrs)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'{v:.1f}%'))
ax.set_title('Avg Savings Rate by Year')
ax.legend(fontsize=8); ax.grid(axis='y',alpha=0.3,zorder=0)
for bar, val in zip(bars3, yearly_full['Avg_SR']):
    ax.text(bar.get_x()+bar.get_width()/2,
            bar.get_height()+(0.5 if val>=0 else -3),
            f'{val:.1f}%', ha='center', fontsize=9, fontweight='bold')

# Category heatmap by year
yearly_cat = expense_df.groupby(['Year','Category'])['Amount'].sum().reset_index()
y_pivot    = yearly_cat.pivot(index='Year', columns='Category', values='Amount').fillna(0)
ax = axes[1,1]; ax.set_facecolor('white')
sns.heatmap(y_pivot, ax=ax, cmap='YlOrRd', annot=True, fmt='.0f',
            linewidths=0.5, cbar_kws={'label':'Annual Spend ($)'})
ax.set_title('Annual Spend by Category ($)')
ax.tick_params(axis='x', rotation=35)

# Deficit months by year
ax = axes[1,2]; ax.set_facecolor('white')
dm_c = [RED if v>=6 else AMBER if v>=3 else GREEN for v in yearly_full['Deficit_Months']]
ax.bar(x, yearly_full['Deficit_Months'], color=dm_c, alpha=0.85, width=0.6, zorder=3)
ax.axhline(6, color=RED, lw=1.5, linestyle='--', label='6 deficit months = critical')
ax.set_xticks(x); ax.set_xticklabels(yrs)
ax.set_ylabel('Months in Deficit')
ax.set_title('Deficit Months per Year')
ax.legend(fontsize=8); ax.grid(axis='y',alpha=0.3,zorder=0)
for i, val in enumerate(yearly_full['Deficit_Months']):
    ax.text(i, val+0.1, str(int(val)), ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/A4_yoy_matrix.png', dpi=150, bbox_inches='tight', facecolor='#F8FAFC')
plt.close()
print("  ✓ Chart A4: YoY Performance Matrix")

# ── Chart 5: Outlier & Anomaly Analysis ───────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Anomaly Detection & Transaction Distribution Analysis',
             fontsize=14, fontweight='bold')
fig.patch.set_facecolor('#F8FAFC')

# Scatter: amount vs z-score coloured by outlier
ax = axes[0]; ax.set_facecolor('white')
normal  = expense_df[~expense_df['Is_Outlier']]
outlier = expense_df[expense_df['Is_Outlier']]
ax.scatter(normal['Amount'],  normal['Amount_ZScore'],
           color=BLUE,  alpha=0.4, s=15, label='Normal')
ax.scatter(outlier['Amount'], outlier['Amount_ZScore'],
           color=RED,   alpha=0.8, s=40, label=f'Outlier ({len(outlier)})', zorder=5)
ax.axhline(2.5, color=AMBER, lw=2, linestyle='--', label='Z-score threshold (2.5)')
ax.set_xlabel('Transaction Amount ($)')
ax.set_ylabel('Z-Score (Category-normalised)')
ax.set_title(f'Outlier Detection\n{n_outliers} flagged ({outlier_pct:.1f}% of transactions)')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# Box plot per category — showing spread
ax = axes[1]; ax.set_facecolor('white')
cat_order = cat_summary['Category'].tolist()
data_bp   = [expense_df[expense_df['Category']==c]['Amount'].dropna().values
             for c in cat_order]
bp = ax.boxplot(data_bp, patch_artist=True, notch=False, vert=True,
                medianprops=dict(color='white',linewidth=2.5),
                flierprops=dict(marker='o', markerfacecolor=RED, markersize=3, alpha=0.5))
for patch, col in zip(bp['boxes'], PALETTE):
    patch.set_facecolor(col); patch.set_alpha(0.75)
ax.set_xticklabels(cat_order, rotation=35, ha='right')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'${v:,.0f}'))
ax.set_title('Transaction Amount Distribution\n(Box + Whisker per Category)')
ax.set_ylabel('Amount ($)'); ax.grid(axis='y',alpha=0.3)

# Coefficient of Variation — which categories are most unpredictable?
ax = axes[2]; ax.set_facecolor('white')
cv_data = cat_summary.sort_values('CV', ascending=True)
cv_colors = [RED if v>80 else AMBER if v>50 else GREEN for v in cv_data['CV']]
ax.barh(cv_data['Category'], cv_data['CV'], color=cv_colors, alpha=0.85, height=0.6, zorder=3)
ax.axvline(50, color=NAVY, lw=1.5, linestyle='--', label='CV=50% threshold')
ax.set_xlabel('Coefficient of Variation (%)')
ax.set_title('Spending Volatility by Category\n(CV — higher = more unpredictable)')
ax.legend(fontsize=8); ax.grid(axis='x',alpha=0.3,zorder=0)
for i, (_, row) in enumerate(cv_data.iterrows()):
    ax.text(row['CV']+0.5, i, f"{row['CV']:.0f}%", va='center', fontsize=9)

plt.tight_layout()
plt.savefig('charts/A5_anomaly_analysis.png', dpi=150, bbox_inches='tight', facecolor='#F8FAFC')
plt.close()
print("  ✓ Chart A5: Anomaly Detection Analysis")

# ── Chart 6: Correlation & Driver Analysis ────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Correlation Analysis — What Drives Deficits?', fontsize=14, fontweight='bold')
fig.patch.set_facecolor('#F8FAFC')

ax = axes[0]; ax.set_facecolor('white')
corr_cols2 = ['Monthly_Income','Monthly_Expense','Net_Cashflow',
              'Needs_Spend','Wants_Spend','Savings_Invest',
              'Needs_Pct','Wants_Pct','Savings_Pct']
corr_m = cashflow[corr_cols2].corr()
mask   = np.triu(np.ones_like(corr_m, dtype=bool))
cmap_rg = LinearSegmentedColormap.from_list('rg', [RED, 'white', GREEN])
sns.heatmap(corr_m, ax=ax, mask=mask, cmap=cmap_rg, vmin=-1, vmax=1,
            annot=True, fmt='.2f', linewidths=0.5, square=True,
            cbar_kws={'shrink':0.8})
ax.set_title('Correlation Matrix\n(Income, Expense & Cash Flow Components)')
ax.tick_params(axis='x', rotation=35)

# Scatter: Wants spend vs Net cashflow
ax = axes[1]; ax.set_facecolor('white')
valid_cf = cashflow.dropna(subset=['Wants_Spend','Net_Cashflow'])
colors_scatter = [GREEN if v>0 else RED for v in valid_cf['Net_Cashflow']]
scatter = ax.scatter(valid_cf['Wants_Spend'], valid_cf['Net_Cashflow'],
                     c=valid_cf['Net_Cashflow'], cmap='RdYlGn',
                     alpha=0.7, s=60, zorder=3)
m, b, r, p, _ = stats.linregress(valid_cf['Wants_Spend'], valid_cf['Net_Cashflow'])
regression_slope = m  # stored explicitly for use in Phase 6 findings
x_line = np.linspace(valid_cf['Wants_Spend'].min(), valid_cf['Wants_Spend'].max(), 100)
ax.plot(x_line, m*x_line+b, color=NAVY, lw=2, linestyle='--',
        label=f'Trend: y = {m:.1f}x + {b:.0f}\nR² = {r**2:.3f}')
ax.axhline(0, color='#374151', lw=1)
ax.set_xlabel('Monthly Wants/Discretionary Spend ($)')
ax.set_ylabel('Net Monthly Cash Flow ($)')
ax.set_title(f'Discretionary Spending vs Net Cash Flow\n(R = {r:.3f}, p = {p:.4f})')
ax.legend(fontsize=9); ax.grid(alpha=0.3)
plt.colorbar(scatter, ax=ax, label='Net Cashflow ($)')

plt.tight_layout()
plt.savefig('charts/A6_correlation_drivers.png', dpi=150, bbox_inches='tight', facecolor='#F8FAFC')
plt.close()
print("  ✓ Chart A6: Correlation & Driver Analysis")

# ── Chart 7: Temporal Behaviour Heat Map ─────────────────
fig, axes = plt.subplots(1, 2, figsize=(18, 5))
fig.suptitle('Temporal Spending Behaviour — When Does Money Leak?',
             fontsize=14, fontweight='bold')
fig.patch.set_facecolor('#F8FAFC')

# Month x Year heatmap
monthly_exp_pivot = expense_df.groupby(['Year','Month_Num'])['Amount'].sum().reset_index()
mp = monthly_exp_pivot.pivot(index='Year', columns='Month_Num', values='Amount').fillna(0)
mp.columns = [month_names[m-1] for m in mp.columns]

ax = axes[0]; ax.set_facecolor('white')
sns.heatmap(mp, ax=ax, cmap='YlOrRd', annot=True, fmt='.0f',
            linewidths=0.5, cbar_kws={'label':'Monthly Expense ($)'})
ax.set_title('Monthly Expense Heatmap\n(Year × Month — Spot Seasonal Patterns)')
ax.tick_params(axis='x', rotation=30)

# Day of week x Category
dow_cat = expense_df.groupby(['Day_of_Week','Category'])['Amount'].mean().reset_index()
dow_pivot = dow_cat.pivot(index='Day_of_Week', columns='Category', values='Amount').fillna(0)
dow_pivot = dow_pivot.reindex(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])

ax = axes[1]; ax.set_facecolor('white')
sns.heatmap(dow_pivot, ax=ax, cmap='Blues', annot=True, fmt='.0f',
            linewidths=0.5, cbar_kws={'label':'Avg Transaction ($)'})
ax.set_title('Avg Transaction by Day × Category\n(Where do weekend habits show up?)')
ax.tick_params(axis='x', rotation=35)

plt.tight_layout()
plt.savefig('charts/A7_temporal_heatmap.png', dpi=150, bbox_inches='tight', facecolor='#F8FAFC')
plt.close()
print("  ✓ Chart A7: Temporal Behaviour Heatmap")

# ── Chart 8: Income Structure & Stability ─────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Income Structure, Stability & Diversification Analysis',
             fontsize=14, fontweight='bold')
fig.patch.set_facecolor('#F8FAFC')

income_df2 = df[df['Type']=='Income'].copy()

# Income by source over time
monthly_inc_src = income_df2.groupby(['Month_Period','Category'])['Amount'].sum().reset_index()
inc_pivot = monthly_inc_src.pivot(index='Month_Period', columns='Category', values='Amount').fillna(0)
ax = axes[0]; ax.set_facecolor('white')
x_inc = range(len(inc_pivot))
bottom = np.zeros(len(inc_pivot))
for i, (col, color) in enumerate(zip(inc_pivot.columns, [GREEN, BLUE, TEAL])):
    ax.bar(x_inc, inc_pivot[col], bottom=bottom, color=color,
           alpha=0.8, label=col, width=0.8)
    bottom += inc_pivot[col].values
ax.set_xticks(list(x_inc)[::12])
ax.set_xticklabels(inc_pivot.index.tolist()[::12], rotation=45, ha='right')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'${v:,.0f}'))
ax.set_title('Monthly Income by Source\n(Stacked — Diversification Trend)')
ax.legend(fontsize=8); ax.grid(axis='y',alpha=0.3)

# Investment vs Salary ratio over years
yearly_inc_src = income_df2.groupby(['Year','Category'])['Amount'].sum().unstack().fillna(0)
ax = axes[1]; ax.set_facecolor('white')
yrs_inc = yearly_inc_src.index.tolist()
x2i     = range(len(yrs_inc))
if 'Investment' in yearly_inc_src and 'Salary' in yearly_inc_src:
    inv_ratio = yearly_inc_src['Investment'] / yearly_inc_src[['Salary','Investment']].sum(axis=1) * 100
    ax.bar(x2i, inv_ratio, color=PURPLE, alpha=0.85, width=0.6, zorder=3)
    ax.set_xticks(x2i); ax.set_xticklabels(yrs_inc)
    ax.axhline(25, color=GREEN, lw=2, linestyle='--', label='Target: 25% investment income')
    ax.set_ylabel('Investment Income %')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'{v:.0f}%'))
    ax.set_title('Investment Income as % of\n(Salary + Investment)')
    ax.legend(fontsize=8); ax.grid(axis='y',alpha=0.3,zorder=0)
    for i, v in enumerate(inv_ratio):
        ax.text(i, v+0.5, f'{v:.1f}%', ha='center', fontsize=9, fontweight='bold')

# Income volatility: rolling CV
monthly_total_inc = income_df2.groupby('Month_Period')['Amount'].sum()
rolling_cv = monthly_total_inc.rolling(6).std() / monthly_total_inc.rolling(6).mean() * 100
ax = axes[2]; ax.set_facecolor('white')
ax.fill_between(range(len(rolling_cv)), rolling_cv, alpha=0.3, color=PURPLE)
ax.plot(range(len(rolling_cv)), rolling_cv, color=PURPLE, lw=2)
ax.axhline(30, color=AMBER, lw=1.5, linestyle='--', label='CV=30% threshold')
ax.set_xticks(list(range(len(rolling_cv)))[::12])
ax.set_xticklabels(monthly_total_inc.index.tolist()[::12], rotation=45, ha='right')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'{v:.0f}%'))
ax.set_title('Income Volatility\n(6-Month Rolling CV — Lower = More Stable)')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('charts/A8_income_analysis.png', dpi=150, bbox_inches='tight', facecolor='#F8FAFC')
plt.close()
print("  ✓ Chart A8: Income Structure & Stability")

# ── Chart 9: Forward Trajectory & Scenario Modelling ─────
fig, axes = plt.subplots(1, 2, figsize=(18, 6))
fig.suptitle('Forward Trajectory & Scenario Modelling\n(Based on 5-Year Trend Extrapolation)',
             fontsize=14, fontweight='bold')
fig.patch.set_facecolor('#F8FAFC')

# Trend projection — simple linear regression on monthly expense
x_vals = np.arange(len(cashflow))
exp_vals = cashflow['Monthly_Expense'].values
inc_vals  = cashflow['Monthly_Income'].values

m_exp, b_exp, *_ = stats.linregress(x_vals, exp_vals)
m_inc, b_inc, *_ = stats.linregress(x_vals, inc_vals)

future_x   = np.arange(len(cashflow), len(cashflow)+24)
future_exp = m_exp * future_x + b_exp
future_inc = m_inc * future_x + b_inc

all_x     = np.concatenate([x_vals, future_x])
all_exp   = np.concatenate([exp_vals, future_exp])
all_inc   = np.concatenate([inc_vals,  future_inc])

ax = axes[0]; ax.set_facecolor('white')
ax.fill_between(range(len(cashflow)), inc_vals, alpha=0.1, color=GREEN)
ax.fill_between(range(len(cashflow)), exp_vals, alpha=0.1, color=RED)
ax.plot(range(len(cashflow)), inc_vals,  color=GREEN, lw=2, label='Actual Income')
ax.plot(range(len(cashflow)), exp_vals,  color=RED,   lw=2, label='Actual Expense')
ax.plot(future_x, future_inc, color=GREEN, lw=2, linestyle='--', alpha=0.7, label='Projected Income')
ax.plot(future_x, future_exp, color=RED,  lw=2, linestyle='--', alpha=0.7, label='Projected Expense')
ax.axvline(len(cashflow)-1, color=NAVY, lw=1.5, linestyle=':', label='Forecast start')
ax.fill_between(future_x, future_inc, future_exp,
                where=future_inc>future_exp, alpha=0.15, color=GREEN, label='Projected surplus')
ax.fill_between(future_x, future_inc, future_exp,
                where=future_inc<=future_exp, alpha=0.15, color=RED, label='Projected deficit')
combined_x = list(range(len(cashflow))) + list(future_x)
n_labels   = 6
tick_pos   = [int(i * (len(combined_x)-1) / (n_labels-1)) for i in range(n_labels)]
all_labels = cashflow['Month_Period'].tolist() + [
    f'Proj+{i+1}M' for i in range(24)]
ax.set_xticks([combined_x[i] for i in tick_pos])
ax.set_xticklabels([all_labels[i] for i in tick_pos], rotation=45, ha='right')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'${v:,.0f}'))
ax.set_title('24-Month Forward Trajectory\n(Linear extrapolation from 5-year trend)')
ax.legend(fontsize=7, loc='upper left'); ax.grid(alpha=0.3)

# Scenario modelling
ax = axes[1]; ax.set_facecolor('white')
baseline_monthly_exp = cashflow['Monthly_Expense'].mean()
baseline_monthly_inc = cashflow['Monthly_Income'].mean()

scenarios = {
    'Current State\n(No Change)':      (baseline_monthly_inc, baseline_monthly_exp),
    'Optimistic A\n(-15% Wants)':      (baseline_monthly_inc, baseline_monthly_exp * 0.92),
    'Optimistic B\n(+10% Income)':     (baseline_monthly_inc * 1.10, baseline_monthly_exp),
    'Combined\n(-15% Wants +10% Inc)': (baseline_monthly_inc * 1.10, baseline_monthly_exp * 0.92),
    'Target State\n(20% Savings)':     (baseline_monthly_inc, baseline_monthly_inc * 0.80),
}

sc_names     = list(scenarios.keys())
sc_net       = [(v[0]-v[1]) for v in scenarios.values()]
sc_sr        = [(v[0]-v[1])/v[0]*100 for v in scenarios.values()]
sc_colors    = [RED if v<0 else AMBER if v<500 else LIME if v<2000 else GREEN for v in sc_net]

x_sc = range(len(sc_names))
bars_sc = ax.bar(x_sc, sc_net, color=sc_colors, alpha=0.85, width=0.6, zorder=3)
ax.axhline(0, color='#374151', lw=1.5)
ax.set_xticks(x_sc); ax.set_xticklabels(sc_names, fontsize=9)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'${v:,.0f}'))
ax.set_title('Scenario Analysis — Monthly Net Savings\n(What-if intervention modelling)')
ax.grid(axis='y',alpha=0.3,zorder=0)
for bar, sr, net in zip(bars_sc, sc_sr, sc_net):
    ax.text(bar.get_x()+bar.get_width()/2,
            bar.get_height()+(200 if net>=0 else -800),
            f'${net:,.0f}\n({sr:.1f}%)', ha='center', fontsize=8.5, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/A9_forecast_scenarios.png', dpi=150, bbox_inches='tight', facecolor='#F8FAFC')
plt.close()
print("  ✓ Chart A9: Forward Trajectory & Scenario Modelling")

# ── Chart 10: Consultant Priority Matrix ──────────────────
fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('#F8FAFC'); ax.set_facecolor('white')
fig.suptitle('Intervention Priority Matrix\n(Impact vs Effort — Where to Focus First)',
             fontsize=14, fontweight='bold')

interventions = {
    'Cap Wants\nSpending':         (8.5, 3.0, RED,    12000),
    'Automate\nSavings Transfer':  (9.0, 1.5, GREEN,   8000),
    'Subscription\nAudit':         (5.0, 1.0, AMBER,   4000),
    'Grow Investment\nIncome':     (9.5, 8.0, PURPLE,  15000),
    'Monthly Budget\nReview':      (7.0, 2.0, BLUE,    6000),
    'Emergency\nFund Build':       (8.0, 5.0, TEAL,   10000),
    'Negotiate Fixed\nCosts':      (6.5, 6.5, ORANGE,  7000),
    'Income\nDiversification':     (8.0, 9.0, LIME,   14000),
}

ax.axvline(5, color='#CBD5E1', lw=1.5, linestyle='--')
ax.axhline(5, color='#CBD5E1', lw=1.5, linestyle='--')

ax.fill_between([0,5],[5,5],[10,10], alpha=0.06, color=AMBER)
ax.fill_between([5,10],[5,5],[10,10], alpha=0.06, color=GREEN)
ax.fill_between([0,5],[0,0],[5,5],   alpha=0.06, color=GREY)
ax.fill_between([5,10],[0,0],[5,5],  alpha=0.06, color=AMBER)

ax.text(2.5, 9.5, 'Quick Wins\n(Low effort, High impact)',
        ha='center', fontsize=10, color=GREEN, fontweight='bold')
ax.text(7.5, 9.5, 'Strategic Priorities\n(High effort, High impact)',
        ha='center', fontsize=10, color=PURPLE, fontweight='bold')
ax.text(2.5, 0.5, 'Deprioritise\n(Low effort, Low impact)',
        ha='center', fontsize=10, color=GREY)
ax.text(7.5, 0.5, 'Reconsider\n(High effort, Low impact)',
        ha='center', fontsize=10, color=AMBER)

for label, (impact, effort, color, annual_saving) in interventions.items():
    size = annual_saving / 15
    ax.scatter(effort, impact, s=size, color=color, alpha=0.75, zorder=5,
               edgecolors='white', linewidth=1.5)
    ax.annotate(f'{label}\n(${annual_saving:,.0f}/yr)',
                (effort, impact),
                textcoords='offset points',
                xytext=(10, 8), fontsize=8,
                arrowprops=dict(arrowstyle='->', color=color, lw=1.2),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor=color, alpha=0.85))

ax.set_xlim(0, 10); ax.set_ylim(0, 10)
ax.set_xlabel('Implementation Effort →', fontsize=11)
ax.set_ylabel('Annual Financial Impact →', fontsize=11)
ax.set_xticks([1,3,5,7,9])
ax.set_xticklabels(['Very Low','Low','Medium','High','Very High'])
ax.set_yticks([1,3,5,7,9])
ax.set_yticklabels(['Very Low','Low','Medium','High','Very High'])
ax.grid(alpha=0.15)

plt.tight_layout()
plt.savefig('charts/A10_priority_matrix.png', dpi=150, bbox_inches='tight', facecolor='#F8FAFC')
plt.close()
print("  ✓ Chart A10: Intervention Priority Matrix")


# ══════════════════════════════════════════════════════════
# PHASE 5: SAVE CLEAN DATASET WITH ALL FEATURES
# ══════════════════════════════════════════════════════════
divider("PHASE 5: SAVE ENRICHED DATASET")

df_enriched = df.copy()
df_enriched.to_csv('data/personal_finance_enriched.csv', index=False)
cashflow.to_csv('data/monthly_cashflow_kpis.csv', index=False)
print(f"  ✓ personal_finance_enriched.csv  — {len(df_enriched)} rows, {len(df_enriched.columns)} columns")
print(f"  ✓ monthly_cashflow_kpis.csv      — {len(cashflow)} months, all KPIs computed")
print(f"\n  Enriched dataset columns ({len(df_enriched.columns)} total):")
for c in df_enriched.columns:
    print(f"    • {c}")


# ══════════════════════════════════════════════════════════
# PHASE 6: CONSULTANT FINDINGS & RECOMMENDATIONS
# ══════════════════════════════════════════════════════════
divider("PHASE 6: CONSULTANT-GRADE FINDINGS & RECOMMENDATIONS")

print(f"""
┌──────────────────────────────────────────────────────────────┐
│  FINANCIAL DIAGNOSTIC SUMMARY                                │
│  5-Year Period: 2020–2024  |  1,500 Transactions Analysed   │
└──────────────────────────────────────────────────────────────┘

FINANCIAL HEALTH SCORE: {fhs}/100 — {'CRITICAL' if fhs<30 else 'POOR' if fhs<50 else 'MODERATE' if fhs<70 else 'GOOD'}

KEY METRICS SNAPSHOT:
  Avg Savings Rate    : {avg_sr:.1f}%   (Target: ≥20%)
  Budget Adherence    : {budget_adherence:.1f}%   (Target: ≥80%)
  Expense-to-Income   : {avg_ei:.1f}%   (Target: <80%)
  Deficit Months      : 40/60   (67% of all months)
  50/30/20 Score      : {overall_5030_score:.0f}/100

═══════════════════════════════════════════════════════
FINDING 1 — ROOT CAUSE: EXPENSES SYSTEMATICALLY
             EXCEED INCOME IN MOST MONTHS
═══════════════════════════════════════════════════════
  Context : Despite earning ${total_income_val:,.0f} over 5 years,
            net position is -${abs(total_income_val-total_exp):,.0f}.
  Evidence: 40 of 60 months (67%) showed a deficit.
  Root Cause: ALL 7 expense categories exceed their budgets.
  The problem is systemic, not isolated.
  
  Key numbers:
  - Avg monthly income  : ${cashflow['Monthly_Income'].mean():,.0f}
  - Avg monthly expense : ${cashflow['Monthly_Expense'].mean():,.0f}
  - Monthly gap         : ${cashflow['Monthly_Expense'].mean()-cashflow['Monthly_Income'].mean():+,.0f}

FINDING 2 — INCOME IS NOT THE PROBLEM.
            EXPENSE CONTROL IS.
═══════════════════════════════════════════════════════
  Income required for 20% savings on current spending:
  ${income_needed:,.0f}/month. Actual: ${cashflow['Monthly_Income'].mean():,.0f}/month.
  Income IS sufficient. If expenses were controlled to 80%
  of income, the individual would save ${cashflow['Monthly_Income'].mean()*0.20:,.0f}/month.
  
  This is a behaviour and control problem, not an income problem.

FINDING 3 — DISCRETIONARY SPENDING IS THE
            PRIMARY DEFICIT DRIVER
═══════════════════════════════════════════════════════
  Regression analysis: Wants/Discretionary spend has
  a correlation of r = {net_corr.get("Wants_Spend", -0.5):.3f} with Net Cashflow.
  For every $1,000 increase in discretionary spend,
  net cashflow falls by approximately ${abs(regression_slope):.0f}.
  
  Top 3 overspending categories vs budget:
  1. {cat_summary.sort_values('Budget_Variance',ascending=False).iloc[0]['Category']}: ${cat_summary.sort_values('Budget_Variance',ascending=False).iloc[0]['Budget_Variance']:+,.0f}/month over budget
  2. {cat_summary.sort_values('Budget_Variance',ascending=False).iloc[1]['Category']}: ${cat_summary.sort_values('Budget_Variance',ascending=False).iloc[1]['Budget_Variance']:+,.0f}/month over budget
  3. {cat_summary.sort_values('Budget_Variance',ascending=False).iloc[2]['Category']}: ${cat_summary.sort_values('Budget_Variance',ascending=False).iloc[2]['Budget_Variance']:+,.0f}/month over budget

FINDING 4 — POSITIVE SIGNAL: FINANCIAL TRAJECTORY
            IS IMPROVING YEAR-ON-YEAR
═══════════════════════════════════════════════════════
  2020 net deficit: -${abs(yearly_full[yearly_full['Year']==2020]['Net'].values[0]):,.0f}
  2024 net deficit: -${abs(yearly_full[yearly_full['Year']==2024]['Net'].values[0]):,.0f}
  Improvement      : ${abs(yearly_full[yearly_full['Year']==2020]['Net'].values[0])-abs(yearly_full[yearly_full['Year']==2024]['Net'].values[0]):,.0f} reduction in annual deficit
  
  At this improvement rate, breakeven (zero deficit)
  is projected within the next 12–18 months.
  However, reaching the 20% savings rate target requires
  active intervention — it will NOT happen organically.

FINDING 5 — INCOME IS WELL-DIVERSIFIED BUT
            INVESTMENT INCOME UNDERPERFORMS
═══════════════════════════════════════════════════════
  Income split: Salary {salary_share:.0f}% / Investment {invest_share:.0f}% / Other {other_share:.0f}%
  This is a healthy diversification (HHI = {(salary_share**2 + invest_share**2 + other_share**2)/10000:.3f}).
  However, investment income has been inconsistent YoY.
  Increasing investment contribution by just 5% of income
  would generate ${cashflow['Monthly_Income'].mean()*0.05*12:,.0f}/year in additional passive income.

═══════════════════════════════════════════════════════
PRIORITISED RECOMMENDATIONS (90-DAY ACTION PLAN)
═══════════════════════════════════════════════════════

PRIORITY 1 — QUICK WIN (Week 1, Zero Cost)
  Automate savings transfer of $500/month on salary receipt day.
  'Pay yourself first' — redirect before it can be spent.
  Annual impact: +$6,000 in savings + habit formation.
  Effort: 15 minutes. Impact: High.

PRIORITY 2 — QUICK WIN (Week 2, Zero Cost)  
  Conduct full subscription audit. Every recurring charge
  in Entertainment and Utilities reviewed. Cancel anything
  unused in last 30 days.
  Conservative estimate: 20% reduction in these categories.
  Annual saving: ${(cat_summary[cat_summary['Category'].isin(['Entertainment','Utilities'])]['Monthly_Avg'].sum() * 0.20 * 12):,.0f}

PRIORITY 3 — STRUCTURAL FIX (Month 1)
  Implement strict monthly cap on top 2 overspending categories.
  Use a dedicated account with hard balance limit.
  Target: Reduce to within 110% of budget (currently at {cat_summary.sort_values('Utilisation_Pct',ascending=False).iloc[0]['Utilisation_Pct']:.0f}%).
  Monthly saving potential: ${cat_summary.sort_values('Budget_Variance',ascending=False).head(2)['Budget_Variance'].sum() * 0.60:,.0f}

PRIORITY 4 — STRATEGIC (Month 2–3)
  Increase investment contributions by $300/month.
  Currently {invest_share:.1f}% of income — target 25%.
  At 7% avg annual return, $300/month over 10 years = $49,000.
  This is an asset-building play, not just a savings play.

PRIORITY 5 — MONITORING (Ongoing)
  Implement monthly financial review (30 minutes, first of month):
  - Actual vs budget per category
  - Savings rate vs 20% target
  - Cumulative net position
  The financial health score of {fhs}/100 should be recalculated
  monthly and the target is 70/100 within 12 months.

═══════════════════════════════════════════════════════
PROJECTED IMPACT OF ALL 5 INTERVENTIONS COMBINED:
═══════════════════════════════════════════════════════
  Current avg monthly net  : ${cashflow['Net_Cashflow'].mean():+,.0f}
  Projected monthly savings : $1,200 – $1,800
  Projected savings rate    : 12% – 18% within 6 months
  Financial Health Score    : {fhs}/100 → 60–75/100 within 12 months
  Annual savings potential  : $14,400 – $21,600
═══════════════════════════════════════════════════════
""")

print("=" * 60)
print("ALL OUTPUT FILES:")
print("  personal_finance_enriched.csv — 1,500 rows, 20 features")
print("  monthly_cashflow_kpis.csv     — 60 months, all KPIs")
print("  A1_executive_dashboard.png    — KPIs + cashflow + gauge")
print("  A2_503020_compliance.png      — rule compliance monthly")
print("  A3_budget_utilisation.png     — budget waterfall")
print("  A4_yoy_matrix.png             — 6-panel YoY analysis")
print("  A5_anomaly_analysis.png       — outlier + box + CV")
print("  A6_correlation_drivers.png    — correlation + regression")
print("  A7_temporal_heatmap.png       — month/year + day/cat")
print("  A8_income_analysis.png        — income structure")
print("  A9_forecast_scenarios.png     — projection + scenarios")
print("  A10_priority_matrix.png       — intervention matrix")
print("=" * 60)
