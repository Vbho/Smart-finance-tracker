"""
ML MODEL 1: TIME SERIES FORECASTING
Technique: Holt's Exponential Smoothing + Polynomial Regression
Author: Vaishnavi Jitendra Bhor | Business Analyst Portfolio
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import warnings; warnings.filterwarnings('ignore')
import os
os.makedirs('charts', exist_ok=True)
os.makedirs('data',   exist_ok=True)

plt.rcParams.update({'figure.facecolor':'#F8FAFC','axes.facecolor':'#F8FAFC',
    'axes.spines.top':False,'axes.spines.right':False,'font.family':'DejaVu Sans',
    'axes.titlesize':12,'axes.titleweight':'bold'})
BLUE='#2563EB';GREEN='#16A34A';RED='#DC2626';AMBER='#D97706';NAVY='#1E3A5F';PURPLE='#7C3AED'

print("="*60)
print("ML MODEL 1: TIME SERIES FORECASTING")
print("Vaishnavi Jitendra Bhor | Business Analyst Portfolio")
print("="*60)

df = pd.read_csv('data/Personal_Finance_Dataset.csv')
df.loc[df['Category']=='Salary','Type'] = 'Income'
df['Date']        = pd.to_datetime(df['Date'])
df['Month_Period']= df['Date'].dt.to_period('M').astype(str)
monthly_exp = df[df['Type']=='Expense'].groupby('Month_Period')['Amount'].sum()
monthly_inc = df[df['Type']=='Income'].groupby('Month_Period')['Amount'].sum()
cashflow    = pd.DataFrame({'Expense':monthly_exp,'Income':monthly_inc}).fillna(0)
cashflow.index = pd.to_datetime(cashflow.index); cashflow = cashflow.sort_index()
cashflow['Net'] = cashflow['Income'] - cashflow['Expense']

def holt_forecast(series, n_ahead, alpha=0.4, beta=0.1):
    L = [series.iloc[0]]; T = [series.iloc[1]-series.iloc[0]]
    for i in range(1,len(series)):
        L_new = alpha*series.iloc[i]+(1-alpha)*(L[-1]+T[-1])
        T_new = beta*(L_new-L[-1])+(1-beta)*T[-1]
        L.append(L_new); T.append(T_new)
    return np.array([L[-1]+h*T[-1] for h in range(1,n_ahead+1)]), np.array(L)

def seasonal_adjust(series, forecasts, period=12):
    n = len(series)
    if n < period*2: return forecasts
    seasonal = np.array([np.mean([series.iloc[j] for j in range(i,n,period)]) for i in range(period)])
    seasonal /= np.mean(seasonal)
    return forecasts * np.array([seasonal[(n+i)%period] for i in range(len(forecasts))])

n_forecast = 12
exp_fc, exp_fit = holt_forecast(cashflow['Expense'], n_forecast, 0.4, 0.1)
inc_fc, inc_fit = holt_forecast(cashflow['Income'],  n_forecast, 0.4, 0.15)
exp_fc = seasonal_adjust(cashflow['Expense'], exp_fc)
inc_fc = seasonal_adjust(cashflow['Income'],  inc_fc)

np.random.seed(42)
resid = cashflow['Expense'].values - exp_fit
boot  = np.array([exp_fc + np.random.choice(resid, n_forecast) for _ in range(500)])
exp_lo, exp_hi = np.percentile(boot,10,axis=0), np.percentile(boot,90,axis=0)

last_date    = cashflow.index[-1]
future_dates = pd.date_range(start=last_date+pd.DateOffset(months=1), periods=n_forecast, freq='MS')
net_fc   = inc_fc - exp_fc
fdf      = pd.DataFrame({'Month':future_dates,'Exp_Forecast':exp_fc,'Exp_Lower_80':exp_lo,
    'Exp_Upper_80':exp_hi,'Inc_Forecast':inc_fc,'Net_Forecast':net_fc})
fdf['Breakeven'] = fdf['Net_Forecast'] >= 0

mae  = np.mean(np.abs(cashflow['Expense'].values-exp_fit))
mape = np.mean(np.abs((cashflow['Expense'].values-exp_fit)/cashflow['Expense'].values))*100

print(f"\n  12-Month Forecast:")
print(f"  {'Month':<12} {'Expense':>12} {'Income':>12} {'Net':>10} {'Status'}")
for _,r in fdf.iterrows():
    st = '✓ SURPLUS' if r['Breakeven'] else '✗ DEFICIT'
    print(f"  {r['Month'].strftime('%Y-%m'):<12} ${r['Exp_Forecast']:>11,.0f} ${r['Inc_Forecast']:>11,.0f} ${r['Net_Forecast']:>+9,.0f} {st}")

be = fdf[fdf['Breakeven']]
print(f"\n  Breakeven: {'PROJECTED ' + be.iloc[0]['Month'].strftime('%b %Y') if len(be)>0 else 'Not projected in 12 months'}")
print(f"  MAE: ${mae:,.0f} | MAPE: {mape:.1f}% | Accuracy: {100-mape:.1f}%")

# Linear trend for net
x_h = np.arange(len(cashflow)).reshape(-1,1)
x_f = np.arange(len(cashflow),len(cashflow)+n_forecast).reshape(-1,1)
p2  = PolynomialFeatures(1)
lr  = LinearRegression().fit(p2.fit_transform(x_h), cashflow['Net'].values)
net_trend = lr.predict(p2.transform(x_f))
std_r     = (cashflow['Net'].values - lr.predict(p2.transform(x_h))).std()
print(f"\n  Net cashflow trend R²: {lr.score(p2.transform(x_h), cashflow['Net'].values):.3f}")
print(f"  Monthly improvement : ${lr.coef_[1]:+,.0f}/month")

# Charts
fig, axes = plt.subplots(2,2,figsize=(18,10))
fig.suptitle('Time Series Forecasting — 12-Month Forward Projection\nHolt Exponential Smoothing + Bootstrap Confidence Intervals',fontsize=14,fontweight='bold')
fig.patch.set_facecolor('#F8FAFC')

ax=axes[0,0]; ax.set_facecolor('white')
ax.plot(cashflow.index,cashflow['Expense'],color=RED,lw=2.2,label='Historical')
ax.plot(future_dates,fdf['Exp_Forecast'],color=RED,lw=2.2,linestyle='--',label='Forecast')
ax.fill_between(future_dates,fdf['Exp_Lower_80'],fdf['Exp_Upper_80'],alpha=0.2,color=RED,label='80% CI')
ax.plot(cashflow.index,exp_fit,color=AMBER,lw=1.2,linestyle=':',alpha=0.8,label='Fitted')
ax.axvline(last_date,color=NAVY,lw=1.5,linestyle=':'); ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'${v:,.0f}'))
ax.set_title(f'Expense Forecast\nMAE=${mae:,.0f} | Accuracy={100-mape:.0f}%'); ax.legend(fontsize=8); ax.grid(alpha=0.3)

ax=axes[0,1]; ax.set_facecolor('white')
ax.plot(cashflow.index,cashflow['Income'],color=GREEN,lw=2.2,label='Historical')
ax.plot(future_dates,fdf['Inc_Forecast'],color=GREEN,lw=2.2,linestyle='--',label='Forecast')
ax.plot(cashflow.index,inc_fit,color=AMBER,lw=1.2,linestyle=':',alpha=0.8,label='Fitted')
ax.axvline(last_date,color=NAVY,lw=1.5,linestyle=':'); ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'${v:,.0f}'))
ax.set_title('Income Forecast\n(Holt Exponential Smoothing)'); ax.legend(fontsize=8); ax.grid(alpha=0.3)

ax=axes[1,0]; ax.set_facecolor('white')
cf=[GREEN if v>=0 else RED for v in cashflow['Net']]
ax.bar(cashflow.index,cashflow['Net'],color=cf,alpha=0.55,width=20)
ax.plot(future_dates,net_fc,color=BLUE,lw=2.5,marker='o',ms=5,label='Holt Forecast')
ax.plot(future_dates,net_trend,color=PURPLE,lw=2,linestyle='--',label='Linear Trend')
ax.fill_between(future_dates,net_trend-1.28*std_r,net_trend+1.28*std_r,alpha=0.15,color=BLUE,label='80% CI')
ax.axhline(0,color='#374151',lw=1.5); ax.axvline(last_date,color=NAVY,lw=1.5,linestyle=':',label='Forecast start')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'${v:+,.0f}'))
ax.set_title('Net Cashflow Forecast\n(Holt + Linear Trend + Confidence Interval)'); ax.legend(fontsize=8); ax.grid(alpha=0.3)

ax=axes[1,1]; ax.set_facecolor('white')
hist_cum  = cashflow['Net'].cumsum()
all_net   = pd.concat([cashflow['Net'], pd.Series(net_fc, index=future_dates)])
all_cum   = all_net.cumsum()
ax.fill_between(all_cum.index, all_cum.where(all_cum>=0), 0, alpha=0.2, color=GREEN)
ax.fill_between(all_cum.index, all_cum.where(all_cum<0),  0, alpha=0.2, color=RED)
ax.plot(hist_cum.index,  hist_cum.values, color=NAVY, lw=2.5, label='Historical cumulative')
ax.plot(all_cum.index[-n_forecast:], all_cum.values[-n_forecast:], color=BLUE, lw=2.5, linestyle='--', label='Projected')
ax.axhline(0, color='#374151', lw=1.5); ax.axvline(last_date, color=NAVY, lw=1.5, linestyle=':')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,p:f'${v:,.0f}'))
ax.set_title('Cumulative Net Position\n(Path to financial recovery)'); ax.legend(fontsize=8); ax.grid(alpha=0.3)

for ax in axes.flat: ax.tick_params(axis='x',rotation=30)
plt.tight_layout()
plt.savefig('charts/ML1_timeseries_forecast.png',dpi=150,bbox_inches='tight',facecolor='#F8FAFC')
plt.close()
fdf.to_csv('data/forecast_results.csv', index=False)
print("\n  ✓ ML1_timeseries_forecast.png saved")
print("  ✓ forecast_results.csv saved")
