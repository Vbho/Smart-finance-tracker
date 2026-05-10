"""
╔══════════════════════════════════════════════════════════════════╗
║  ML MODEL 2: ANOMALY DETECTION — ISOLATION FOREST              ║
║  Business Question: Which transactions are genuinely unusual    ║
║  given their amount, timing, and category simultaneously?       ║
║  Author: Vaishnavi Jitendra Bhor | Business Analyst Portfolio   ║
╚══════════════════════════════════════════════════════════════════╝
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')
import os
os.makedirs('charts', exist_ok=True)
os.makedirs('data',   exist_ok=True)

plt.rcParams.update({
    'figure.facecolor':'#F8FAFC','axes.facecolor':'#F8FAFC',
    'axes.spines.top':False,'axes.spines.right':False,
    'font.family':'DejaVu Sans','axes.titlesize':12,'axes.titleweight':'bold'
})
BLUE='#2563EB';GREEN='#16A34A';RED='#DC2626';AMBER='#D97706';NAVY='#1E3A5F'

print("="*60)
print("ML MODEL 2: ISOLATION FOREST ANOMALY DETECTION")
print("Vaishnavi Jitendra Bhor | Business Analyst Portfolio")
print("="*60)

# ── Load data ───────────────────────────────────────────────
df = pd.read_csv('data/Personal_Finance_Dataset.csv')
df.loc[df['Category']=='Salary','Type'] = 'Income'
df['Date']       = pd.to_datetime(df['Date'])
df['Month_Num']  = df['Date'].dt.month
df['DOW_Num']    = df['Date'].dt.dayofweek
df['Year']       = df['Date'].dt.year
df['Week']       = df['Date'].dt.isocalendar().week.astype(int)
df['Day']        = df['Date'].dt.day
expense_df       = df[df['Type']=='Expense'].copy().reset_index(drop=True)

# ── Step 1: Feature Engineering for ML ─────────────────────
print("\n[ STEP 1 ] Feature Engineering for Anomaly Detection")
print("-"*50)

le_cat = LabelEncoder()
expense_df['Cat_Encoded'] = le_cat.fit_transform(expense_df['Category'])

# Monthly avg per category (expected baseline)
cat_monthly_avg = expense_df.groupby('Category')['Amount'].mean()
expense_df['Cat_Avg']      = expense_df['Category'].map(cat_monthly_avg)
expense_df['Deviation_Pct']= (expense_df['Amount'] - expense_df['Cat_Avg']) / expense_df['Cat_Avg'] * 100
expense_df['Amount_Log']   = np.log1p(expense_df['Amount'])

# Category percentile rank
expense_df['Cat_Percentile'] = expense_df.groupby('Category')['Amount'].rank(pct=True) * 100

features = ['Amount', 'Amount_Log', 'Month_Num', 'DOW_Num',
            'Cat_Encoded', 'Deviation_Pct', 'Cat_Percentile', 'Day']

X = expense_df[features].copy()
scaler  = StandardScaler()
X_scaled= scaler.fit_transform(X)

print(f"  Features used         : {features}")
print(f"  Total expense records : {len(expense_df)}")
print(f"  Feature matrix shape  : {X_scaled.shape}")

# ── Step 2: Fit Isolation Forest ────────────────────────────
print("\n[ STEP 2 ] Fitting Isolation Forest")
print("-"*50)

# Test multiple contamination rates
contamination_rates = [0.03, 0.05, 0.08, 0.10]
results = {}
for rate in contamination_rates:
    iso = IsolationForest(
        n_estimators=200,
        contamination=rate,
        max_samples='auto',
        random_state=42
    )
    preds = iso.fit_predict(X_scaled)
    scores= iso.score_samples(X_scaled)
    n_anom = (preds == -1).sum()
    results[rate] = {'preds':preds,'scores':scores,'n_anom':n_anom}
    print(f"  Contamination {rate:.0%}: {n_anom} anomalies flagged ({rate*100:.0f}%)")

# Use 5% contamination as primary model
primary_rate = 0.05
iso_final = IsolationForest(
    n_estimators=200,
    contamination=primary_rate,
    max_samples='auto',
    random_state=42
)
expense_df['Anomaly_Label'] = iso_final.fit_predict(X_scaled)
expense_df['Anomaly_Score'] = iso_final.score_samples(X_scaled)
expense_df['Is_Anomaly']    = expense_df['Anomaly_Label'] == -1
# Severity using percentile-based thresholds on actual score distribution
# (Fixed bins [-0.15, -0.10, -0.05] don't match actual score range — use percentiles instead)
_anom_scores = expense_df.loc[expense_df['Anomaly_Label']==-1, 'Anomaly_Score']
_p15 = _anom_scores.quantile(0.15)
_p40 = _anom_scores.quantile(0.40)
expense_df['Anomaly_Severity'] = expense_df['Anomaly_Score'].apply(
    lambda x: 'Critical' if x <= _p15 else 'High' if x <= _p40 else 'Medium'
    if x <= 0 else 'Normal'
)

n_anomalies = expense_df['Is_Anomaly'].sum()
anomaly_value = expense_df[expense_df['Is_Anomaly']]['Amount'].sum()
print(f"\n  PRIMARY MODEL (5% contamination):")
print(f"  Anomalies detected    : {n_anomalies} of {len(expense_df)} ({n_anomalies/len(expense_df)*100:.1f}%)")
print(f"  Total anomaly value   : ${anomaly_value:,.2f}")
print(f"  Avg anomaly amount    : ${expense_df[expense_df['Is_Anomaly']]['Amount'].mean():,.2f}")
print(f"  Avg normal amount     : ${expense_df[~expense_df['Is_Anomaly']]['Amount'].mean():,.2f}")

# ── Step 3: Anomaly Analysis ────────────────────────────────
print("\n[ STEP 3 ] Anomaly Analysis by Category & Severity")
print("-"*50)

print(f"\n  Anomalies by Category:")
anom_cat = expense_df[expense_df['Is_Anomaly']].groupby('Category').agg(
    Count=('Amount','count'),
    Total=('Amount','sum'),
    Avg=('Amount','mean'),
    Max=('Amount','max'),
    Min_Score=('Anomaly_Score','min')
).sort_values('Count', ascending=False)
print(anom_cat.round(2).to_string())

print(f"\n  Anomalies by Severity:")
sev = expense_df[expense_df['Is_Anomaly']]['Anomaly_Severity'].value_counts()
for level, count in sev.items():
    print(f"    {level:<12}: {count} transactions")

print(f"\n  Top 10 Most Anomalous Transactions:")
top_anomalies = expense_df[expense_df['Is_Anomaly']].nsmallest(10,'Anomaly_Score')
print(f"  {'Date':<12} {'Category':<20} {'Amount':>10} {'Score':>8} {'Severity'}")
print(f"  {'-'*65}")
for _, row in top_anomalies.iterrows():
    print(f"  {str(row['Date'].date()):<12} {row['Category']:<20} "
          f"${row['Amount']:>9,.2f} {row['Anomaly_Score']:>8.3f} {row['Anomaly_Severity']}")

print(f"\n  Monthly anomaly pattern:")
anom_monthly = expense_df[expense_df['Is_Anomaly']].groupby(
    expense_df['Date'].dt.to_period('M').astype(str))['Amount'].sum()
print(f"  Months with highest anomalous spend:")
for month, val in anom_monthly.nlargest(5).items():
    print(f"    {month}: ${val:,.2f}")

# ── Step 4: PCA for Visualisation ──────────────────────────
print("\n[ STEP 4 ] PCA Dimensionality Reduction for Visualisation")
print("-"*50)

pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_scaled)
print(f"  Variance explained by PC1: {pca.explained_variance_ratio_[0]*100:.1f}%")
print(f"  Variance explained by PC2: {pca.explained_variance_ratio_[1]*100:.1f}%")
print(f"  Total variance explained : {sum(pca.explained_variance_ratio_)*100:.1f}%")

# ── Step 5: Charts ──────────────────────────────────────────
print("\n[ STEP 5 ] Generating Anomaly Detection Charts")
print("-"*50)

fig, axes = plt.subplots(2, 2, figsize=(18, 11))
fig.suptitle('Isolation Forest Anomaly Detection\n'
             'Multi-dimensional Analysis: Amount × Timing × Category',
             fontsize=14, fontweight='bold')
fig.patch.set_facecolor('#F8FAFC')

# Chart 1: PCA scatter - anomalies highlighted
ax = axes[0,0]; ax.set_facecolor('white')
normal  = expense_df[~expense_df['Is_Anomaly']]
anomaly = expense_df[expense_df['Is_Anomaly']]
ax.scatter(X_pca[~expense_df['Is_Anomaly'],0],
           X_pca[~expense_df['Is_Anomaly'],1],
           c=BLUE, alpha=0.35, s=18, label=f'Normal ({len(normal)})', zorder=2)
scatter = ax.scatter(X_pca[expense_df['Is_Anomaly'],0],
           X_pca[expense_df['Is_Anomaly'],1],
           c=expense_df[expense_df['Is_Anomaly']]['Anomaly_Score'],
           cmap='RdYlGn_r', alpha=0.85, s=60, zorder=5,
           edgecolors='white', linewidth=0.8,
           label=f'Anomaly ({len(anomaly)})')
plt.colorbar(scatter, ax=ax, label='Anomaly Score\n(Lower = More Anomalous)')
ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.0f}% variance)')
ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.0f}% variance)')
ax.set_title('PCA Visualisation: Normal vs Anomalous Transactions\n'
             '(2D projection of 8-dimensional feature space)')
ax.legend(fontsize=9); ax.grid(alpha=0.2)

# Chart 2: Anomaly score distribution
ax = axes[0,1]; ax.set_facecolor('white')
normal_scores  = expense_df[~expense_df['Is_Anomaly']]['Anomaly_Score']
anomaly_scores = expense_df[expense_df['Is_Anomaly']]['Anomaly_Score']
ax.hist(normal_scores,  bins=40, color=BLUE,  alpha=0.6,
        label='Normal transactions', density=True)
ax.hist(anomaly_scores, bins=20, color=RED,   alpha=0.7,
        label='Anomalous transactions', density=True)
ax.axvline(iso_final.offset_, color=NAVY, lw=2, linestyle='--',
           label=f'Decision threshold ({iso_final.offset_:.3f})')
ax.set_xlabel('Anomaly Score')
ax.set_ylabel('Density')
ax.set_title('Anomaly Score Distribution\n'
             '(Separation between normal and anomalous transactions)')
ax.legend(fontsize=9); ax.grid(alpha=0.3)

# Chart 3: Anomalies by category
ax = axes[1,0]; ax.set_facecolor('white')
cat_anom_rate = expense_df.groupby('Category').apply(
    lambda x: (x['Is_Anomaly'].sum() / len(x) * 100)).sort_values(ascending=True)
colors_car = [RED if v>10 else AMBER if v>5 else GREEN for v in cat_anom_rate]
ax.barh(cat_anom_rate.index, cat_anom_rate.values,
        color=colors_car, alpha=0.85, height=0.6, zorder=3)
ax.axvline(primary_rate*100, color=NAVY, lw=2, linestyle='--',
           label=f'Expected rate ({primary_rate*100:.0f}%)')
ax.set_xlabel('Anomaly Rate (%)')
ax.set_title('Anomaly Rate by Category\n'
             '(Which categories have most unusual transactions?)')
ax.legend(fontsize=9); ax.grid(axis='x', alpha=0.3, zorder=0)
for i, (cat, val) in enumerate(cat_anom_rate.items()):
    ax.text(val+0.1, i, f'{val:.1f}%', va='center', fontsize=9)

# Chart 4: Anomaly timeline
ax = axes[1,1]; ax.set_facecolor('white')
monthly_anom = expense_df.groupby(expense_df['Date'].dt.to_period('M').astype(str)).agg(
    Total=('Amount','sum'),
    Anomaly_Total=('Amount', lambda x: x[expense_df.loc[x.index,'Is_Anomaly']].sum()),
    Anomaly_Count=('Is_Anomaly','sum')
).reset_index()
monthly_anom.columns = ['Month','Total','Anomaly_Total','Anomaly_Count']
monthly_anom['Anomaly_Pct'] = monthly_anom['Anomaly_Total'] / monthly_anom['Total'] * 100

x = range(len(monthly_anom))
ax.bar(x, monthly_anom['Total'], color=BLUE, alpha=0.3,
       width=0.8, label='Total monthly expense')
ax.bar(x, monthly_anom['Anomaly_Total'], color=RED, alpha=0.7,
       width=0.8, label='Anomalous spend')

ax2_twin = ax.twinx()
ax2_twin.plot(x, monthly_anom['Anomaly_Count'], color=AMBER,
              lw=2, marker='o', ms=4, label='Anomaly count (right)')
ax2_twin.set_ylabel('Number of Anomalies', color=AMBER)
ax2_twin.spines['top'].set_visible(False)

ax.set_xticks(list(x)[::6])
ax.set_xticklabels(monthly_anom['Month'].tolist()[::6], rotation=45, ha='right')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'${v:,.0f}'))
ax.set_title('Monthly Anomaly Timeline\n'
             '(When do unusual transactions cluster?)')
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2_twin.get_legend_handles_labels()
ax.legend(lines1+lines2, labels1+labels2, fontsize=8, loc='upper left')
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('charts/ML2_anomaly_detection.png', dpi=150,
            bbox_inches='tight', facecolor='#F8FAFC')
plt.close()
print("  ✓ ML2_anomaly_detection.png saved")

# Save flagged transactions
anomaly_df = expense_df[expense_df['Is_Anomaly']][
    ['Date','Category','Amount','Anomaly_Score','Anomaly_Severity']
].sort_values('Anomaly_Score')
anomaly_df.to_csv('data/anomaly_flagged_transactions.csv', index=False)
print(f"  ✓ anomaly_flagged_transactions.csv saved ({len(anomaly_df)} rows)")

print(f"\n  BUSINESS INSIGHT:")
print(f"  {n_anomalies} transactions ({n_anomalies/len(expense_df)*100:.1f}%) are statistically")
print(f"  anomalous. These represent ${anomaly_value:,.0f} in spending")
print(f"  that warrants individual review. The most anomalous")
print(f"  category is {anom_cat.index[0]} with {anom_cat['Count'].iloc[0]} flagged transactions.")
