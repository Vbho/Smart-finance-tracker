"""
╔══════════════════════════════════════════════════════════════════╗
║  ML MODEL 3: K-MEANS CLUSTERING — SPENDING PROFILE ANALYSIS    ║
║  Business Question: Are there distinct types of months in       ║
║  terms of financial behaviour? What characterises each type     ║
║  and how often does each occur?                                 ║
║  Author: Vaishnavi Jitendra Bhor | Business Analyst Portfolio   ║
╚══════════════════════════════════════════════════════════════════╝
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score
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
BLUE='#2563EB';GREEN='#16A34A';RED='#DC2626';AMBER='#D97706'
PURPLE='#7C3AED';NAVY='#1E3A5F';TEAL='#0891B2'

print("="*60)
print("ML MODEL 3: K-MEANS SPENDING PROFILE CLUSTERING")
print("Vaishnavi Jitendra Bhor | Business Analyst Portfolio")
print("="*60)

# ── Load & Prepare Monthly Features ────────────────────────
df = pd.read_csv('data/Personal_Finance_Dataset.csv')
df.loc[df['Category']=='Salary','Type'] = 'Income'
df['Date']       = pd.to_datetime(df['Date'])
df['Month']      = df['Date'].dt.to_period('M').astype(str)

NEEDS = ['Rent','Food & Drink','Utilities','Health & Fitness']
WANTS = ['Shopping','Travel','Entertainment']

monthly_inc = df[df['Type']=='Income'].groupby('Month')['Amount'].sum()
monthly_exp = df[df['Type']=='Expense'].groupby('Month')['Amount'].sum()
monthly_needs = df[df['Category'].isin(NEEDS)].groupby('Month')['Amount'].sum()
monthly_wants = df[df['Category'].isin(WANTS)].groupby('Month')['Amount'].sum()

cat_pivot = df[df['Type']=='Expense'].pivot_table(
    index='Month', columns='Category', values='Amount',
    aggfunc='sum').fillna(0)

monthly_df = pd.DataFrame({
    'Income':  monthly_inc,
    'Expense': monthly_exp,
    'Needs':   monthly_needs,
    'Wants':   monthly_wants,
}).fillna(0)
monthly_df = monthly_df.join(cat_pivot)
monthly_df['Net']         = monthly_df['Income'] - monthly_df['Expense']
monthly_df['Savings_Rate']= monthly_df['Net'] / monthly_df['Income'].replace(0,np.nan) * 100
monthly_df['Needs_Pct']   = monthly_df['Needs']  / monthly_df['Income'].replace(0,np.nan) * 100
monthly_df['Wants_Pct']   = monthly_df['Wants']  / monthly_df['Income'].replace(0,np.nan) * 100
monthly_df['EI_Ratio']    = monthly_df['Expense'] / monthly_df['Income'].replace(0,np.nan) * 100
monthly_df['Month_Dt']    = pd.to_datetime(monthly_df.index)
monthly_df['Month_Num']   = monthly_df['Month_Dt'].dt.month
monthly_df['Year']        = monthly_df['Month_Dt'].dt.year

# Features for clustering
cluster_features = ['Income','Expense','Needs','Wants','Net',
                    'Savings_Rate','EI_Ratio','Needs_Pct','Wants_Pct',
                    'Month_Num']
X_clust = monthly_df[cluster_features].fillna(0)
scaler  = StandardScaler()
X_scaled= scaler.fit_transform(X_clust)

# ── Step 1: Optimal K via Elbow + Silhouette ───────────────
print("\n[ STEP 1 ] Finding Optimal Number of Clusters")
print("-"*50)

inertias, silhouettes, db_scores = [], [], []
K_range = range(2, 8)

for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=20)
    labels = km.fit_predict(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, labels))
    db_scores.append(davies_bouldin_score(X_scaled, labels))
    print(f"  K={k}: Inertia={km.inertia_:,.0f} | "
          f"Silhouette={silhouette_score(X_scaled,labels):.3f} | "
          f"DB={davies_bouldin_score(X_scaled,labels):.3f}")

best_k_sil = K_range[np.argmax(silhouettes)]
best_k_db  = K_range[np.argmin(db_scores)]
optimal_k  = best_k_sil
print(f"\n  Best K by Silhouette Score : {best_k_sil}")
print(f"  Best K by Davies-Bouldin   : {best_k_db}")
print(f"  Selected K                 : {optimal_k}")

# ── Step 2: Fit Final Model ─────────────────────────────────
print("\n[ STEP 2 ] Fitting K-Means with K={0}".format(optimal_k))
print("-"*50)

km_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=20)
monthly_df['Cluster'] = km_final.fit_predict(X_scaled)
monthly_df['Silhouette'] = silhouette_score(X_scaled,
    km_final.labels_, sample_size=None)

print(f"  Final silhouette score : {silhouette_score(X_scaled,km_final.labels_):.3f}")
print(f"  (Range: -1 to 1. Values >0.5 = well-separated clusters)")

# ── Step 3: Profile Each Cluster ───────────────────────────
print("\n[ STEP 3 ] Cluster Profiles — What Each Cluster Means")
print("-"*50)

cluster_names = {}
cluster_profile = monthly_df.groupby('Cluster')[
    ['Income','Expense','Net','Savings_Rate',
     'Needs_Pct','Wants_Pct','EI_Ratio','Month_Num']
].agg(['mean','std']).round(1)

for c in sorted(monthly_df['Cluster'].unique()):
    grp = monthly_df[monthly_df['Cluster']==c]
    avg_net = grp['Net'].mean()
    avg_sr  = grp['Savings_Rate'].mean()
    avg_exp = grp['Expense'].mean()
    avg_inc = grp['Income'].mean()
    avg_wp  = grp['Wants_Pct'].mean()
    n_months= len(grp)

    if avg_sr >= 15:
        name = 'HEALTHY MONTHS'
        desc = '→ Income > Expenses, controlled spending'
        color= GREEN
    elif avg_sr >= -20 and avg_exp < avg_inc * 1.2:
        name = 'BORDERLINE MONTHS'
        desc = '→ Near breakeven, moderate overspend'
        color= AMBER
    elif avg_wp > 50:
        name = 'DEFICIT MONTHS'
        desc = '→ High wants spending drives deficit'
        color= RED
    else:
        name = 'DEFICIT MONTHS'
        desc = '→ Structural overspend across categories'
        color= PURPLE

    cluster_names[c] = name
    print(f"\n  CLUSTER {c} — {name}")
    print(f"  {desc}")
    print(f"    Months in cluster  : {n_months} ({n_months/len(monthly_df)*100:.0f}% of all months)")
    print(f"    Avg Income         : ${avg_inc:,.0f}")
    print(f"    Avg Expense        : ${avg_exp:,.0f}")
    print(f"    Avg Net Cashflow   : ${avg_net:+,.0f}")
    print(f"    Avg Savings Rate   : {avg_sr:.1f}%")
    print(f"    Avg Wants Spend %  : {avg_wp:.1f}%")
    print(f"    Peak months        : {grp['Month_Num'].mode().values}")

monthly_df['Cluster_Name'] = monthly_df['Cluster'].map(cluster_names)

# ── Step 4: Transition Analysis ────────────────────────────
print("\n[ STEP 4 ] Cluster Transition Analysis")
print("-"*50)
print("  How do months transition between cluster types?")

monthly_df_sorted = monthly_df.sort_values('Month_Dt')
transitions = {}
for i in range(len(monthly_df_sorted)-1):
    frm = monthly_df_sorted.iloc[i]['Cluster']
    to  = monthly_df_sorted.iloc[i+1]['Cluster']
    key = (frm, to)
    transitions[key] = transitions.get(key, 0) + 1

print(f"  {'From → To':<35} {'Count':>6} {'Interpretation'}")
print(f"  {'-'*70}")
for (frm, to), cnt in sorted(transitions.items(), key=lambda x:-x[1]):
    frm_name = cluster_names.get(frm, f'Cluster {frm}')[:20]
    to_name  = cluster_names.get(to,  f'Cluster {to}')[:20]
    interp   = '✓ Recovery' if (frm > to) else '✗ Deterioration' if (frm < to) else '→ Stable'
    print(f"  {frm_name:<20} → {to_name:<20} {cnt:>4}  {interp}")

# ── Step 5: Charts ──────────────────────────────────────────
print("\n[ STEP 5 ] Generating Clustering Charts")
print("-"*50)

CLUSTER_COLORS = [GREEN, RED, AMBER, PURPLE, TEAL][:optimal_k]

fig, axes = plt.subplots(2, 3, figsize=(19, 11))
fig.suptitle('K-Means Spending Profile Clustering\n'
             f'K={optimal_k} clusters | 60 months | 10 financial features',
             fontsize=14, fontweight='bold')
fig.patch.set_facecolor('#F8FAFC')

# Chart 1: Elbow + Silhouette
ax = axes[0,0]; ax.set_facecolor('white')
ax2 = ax.twinx()
ax.plot(list(K_range), inertias, color=BLUE, lw=2.2, marker='o',
        ms=7, label='Inertia (Elbow)')
ax2.plot(list(K_range), silhouettes, color=GREEN, lw=2.2,
         marker='s', ms=7, label='Silhouette Score')
ax.axvline(optimal_k, color=RED, lw=2, linestyle='--',
           label=f'Selected K={optimal_k}')
ax.set_xlabel('Number of Clusters (K)')
ax.set_ylabel('Inertia', color=BLUE)
ax2.set_ylabel('Silhouette Score', color=GREEN)
ax2.spines['top'].set_visible(False)
ax.set_title(f'Elbow Method + Silhouette Analysis\nOptimal K={optimal_k}')
lines1,lbl1 = ax.get_legend_handles_labels()
lines2,lbl2 = ax2.get_legend_handles_labels()
ax.legend(lines1+lines2, lbl1+lbl2, fontsize=8); ax.grid(alpha=0.3)

# Chart 2: PCA 2D cluster plot
ax = axes[0,1]; ax.set_facecolor('white')
pca_2d = PCA(n_components=2, random_state=42)
X_pca2 = pca_2d.fit_transform(X_scaled)

for c in sorted(monthly_df['Cluster'].unique()):
    mask  = monthly_df['Cluster'] == c
    label = f"C{c}: {cluster_names.get(c,'')[:20]}\n({mask.sum()} months)"
    ax.scatter(X_pca2[mask,0], X_pca2[mask,1],
               color=CLUSTER_COLORS[c], alpha=0.8, s=70,
               label=label, edgecolors='white', lw=0.8, zorder=3)
    centroid = pca_2d.transform(
        km_final.cluster_centers_[c].reshape(1,-1))
    ax.scatter(centroid[:,0], centroid[:,1], marker='*',
               color=CLUSTER_COLORS[c], s=300, zorder=5,
               edgecolors=NAVY, lw=1.5)

ax.set_xlabel(f'PC1 ({pca_2d.explained_variance_ratio_[0]*100:.0f}%)')
ax.set_ylabel(f'PC2 ({pca_2d.explained_variance_ratio_[1]*100:.0f}%)')
ax.set_title(f'Cluster Visualisation (PCA 2D)\n'
             f'Silhouette = {silhouette_score(X_scaled,km_final.labels_):.3f}')
ax.legend(fontsize=7, loc='best'); ax.grid(alpha=0.2)

# Chart 3: Cluster profiles radar / bar
ax = axes[0,2]; ax.set_facecolor('white')
metrics = ['Avg Income','Avg Expense','Avg Net','Savings Rate%']
cluster_means = []
for c in sorted(monthly_df['Cluster'].unique()):
    grp = monthly_df[monthly_df['Cluster']==c]
    cluster_means.append([
        grp['Income'].mean(), grp['Expense'].mean(),
        grp['Net'].mean(), grp['Savings_Rate'].mean()
    ])

x_m = np.arange(len(metrics))
w   = 0.8 / optimal_k
for i, (c, means) in enumerate(zip(
        sorted(monthly_df['Cluster'].unique()), cluster_means)):
    label = f'C{c}: {cluster_names.get(c,"")[:15]}'
    bars  = ax.bar(x_m + i*w - w*optimal_k/2 + w/2,
                   means, width=w*0.85,
                   color=CLUSTER_COLORS[c], alpha=0.85, label=label)

ax.set_xticks(x_m)
ax.set_xticklabels(metrics, rotation=15, ha='right')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'${v:,.0f}' if abs(v)>100 else f'{v:.0f}%'))
ax.axhline(0, color='#374151', lw=1)
ax.set_title('Cluster Financial Profiles\n(Average metrics per cluster)')
ax.legend(fontsize=7); ax.grid(axis='y', alpha=0.3)

# Chart 4: Timeline coloured by cluster
ax = axes[1,0]; ax.set_facecolor('white')
monthly_sorted = monthly_df.sort_values('Month_Dt')
x_t = range(len(monthly_sorted))
for i, (_, row) in enumerate(monthly_sorted.iterrows()):
    c = int(row['Cluster'])
    ax.bar(i, row['Expense'], color=CLUSTER_COLORS[c],
           alpha=0.75, width=0.85, zorder=2)
ax.plot(x_t, monthly_sorted['Income'], color=NAVY, lw=2,
        label='Income', zorder=4)
ax.set_xticks(list(x_t)[::12])
ax.set_xticklabels(monthly_sorted.index.tolist()[::12],
                   rotation=45, ha='right')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'${v:,.0f}'))
ax.set_title('Monthly Timeline Coloured by Cluster\n'
             '(Bars=Expense by cluster, Line=Income)')
handles = [mpatches.Patch(color=CLUSTER_COLORS[c], alpha=0.75,
           label=f'C{c}: {cluster_names.get(c,"")[:20]}')
           for c in sorted(monthly_df['Cluster'].unique())]
handles.append(plt.Line2D([0],[0], color=NAVY, lw=2, label='Income'))
ax.legend(handles=handles, fontsize=7, loc='upper left'); ax.grid(axis='y',alpha=0.3)

# Chart 5: Cluster distribution over time (stacked area of proportions)
ax = axes[1,1]; ax.set_facecolor('white')
yearly_cluster = monthly_df.groupby(['Year','Cluster']).size().unstack(fill_value=0)
yearly_cluster_pct = yearly_cluster.div(yearly_cluster.sum(axis=1), axis=0) * 100
bottom = np.zeros(len(yearly_cluster_pct))
for c in sorted(monthly_df['Cluster'].unique()):
    if c in yearly_cluster_pct.columns:
        ax.bar(yearly_cluster_pct.index, yearly_cluster_pct[c],
               bottom=bottom, color=CLUSTER_COLORS[c], alpha=0.85,
               label=f'C{c}: {cluster_names.get(c,"")[:15]}', width=0.6)
        bottom += yearly_cluster_pct[c].values
ax.set_ylabel('% of months in cluster')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'{v:.0f}%'))
ax.set_title('Cluster Composition by Year\n'
             '(Is financial behaviour improving over time?)')
ax.legend(fontsize=7); ax.grid(axis='y',alpha=0.3)

# Chart 6: Savings rate by cluster box plot
ax = axes[1,2]; ax.set_facecolor('white')
data_box = [monthly_df[monthly_df['Cluster']==c]['Savings_Rate'].values
            for c in sorted(monthly_df['Cluster'].unique())]
labels_box=[f'C{c}\n{cluster_names.get(c,"")[:12]}\n(n={len(d)})'
            for c,d in zip(sorted(monthly_df['Cluster'].unique()),data_box)]
bp = ax.boxplot(data_box, patch_artist=True, notch=False,
                medianprops=dict(color='white',linewidth=2.5))
for patch, color in zip(bp['boxes'], CLUSTER_COLORS):
    patch.set_facecolor(color); patch.set_alpha(0.75)
ax.axhline(20, color=BLUE, lw=2, linestyle='--', label='20% savings target')
ax.axhline(0,  color='#374151', lw=1.2)
ax.set_xticklabels(labels_box, fontsize=8)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'{v:.0f}%'))
ax.set_ylabel('Monthly Savings Rate (%)')
ax.set_title('Savings Rate Distribution by Cluster\n'
             '(How consistent is each cluster type?)')
ax.legend(fontsize=9); ax.grid(axis='y',alpha=0.3)

plt.tight_layout()
plt.savefig('charts/ML3_clustering.png', dpi=150,
            bbox_inches='tight', facecolor='#F8FAFC')
plt.close()
print("  ✓ ML3_clustering.png saved")

# Save cluster assignments
monthly_df_save = monthly_df.reset_index()[
    ['Month','Cluster','Cluster_Name','Income','Expense',
     'Net','Savings_Rate','EI_Ratio']]
monthly_df_save['EI_Ratio'] = monthly_df_save['EI_Ratio'].fillna(0).round(2)
monthly_df_save.to_csv('data/cluster_assignments.csv', index=False)
print(f"  ✓ cluster_assignments.csv saved")

print(f"\n  BUSINESS INSIGHT:")
dom_cluster = monthly_df['Cluster'].value_counts().idxmax()
print(f"  The dominant spending profile is Cluster {dom_cluster}:")
print(f"  '{cluster_names.get(dom_cluster,'')}'")
print(f"  occurring in {monthly_df['Cluster'].value_counts().max()} of 60 months.")
print(f"  The most financially dangerous cluster occurs in")
worst_c = monthly_df.groupby('Cluster')['Savings_Rate'].mean().idxmin()
print(f"  {len(monthly_df[monthly_df['Cluster']==worst_c])} months and averages")
print(f"  ${monthly_df[monthly_df['Cluster']==worst_c]['Net'].mean():+,.0f} net monthly.")
print(f"  Predicting which cluster type a month will fall into")
print(f"  is possible from early-month spending — enabling")
print(f"  proactive intervention before the month ends.")
