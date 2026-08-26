import pandas as pd
import numpy as np
import os
import json
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def run_analysis():
    df = pd.read_csv(os.path.join('data', 'warehouse_orders_dataset.csv'))
    results = {}
    
    # 1. Summary Statistics across scenarios
    scenarios = {
        'Baseline (S0: WH1 Chicago Only)': ('cost_wh1_usd', 'lead_wh1_days', 'service_met_wh1', 'dist_wh1_km'),
        'Scenario 1 (S1: Chicago + LA)': ('cost_s1_usd', 'lead_s1_days', 'service_met_s1', 'dist_s1_km'),
        'Scenario 2 (S2: Chicago + Atlanta)': ('cost_s2_usd', 'lead_s2_days', 'service_met_s2', 'dist_s2_km')
    }
    
    summary_list = []
    for s_name, (c_col, l_col, sm_col, d_col) in scenarios.items():
        avg_cost = df[c_col].mean()
        tot_cost = df[c_col].sum()
        avg_lead = df[l_col].mean()
        service_lvl = df[sm_col].mean() * 100
        avg_dist = df[d_col].mean()
        summary_list.append({
            'Scenario': s_name,
            'Avg Distance (km)': round(avg_dist, 1),
            'Avg Shipping Cost ($)': round(avg_cost, 2),
            'Total Annual Freight ($)': round(tot_cost, 2),
            'Avg Lead Time (Days)': round(avg_lead, 2),
            '2-Day Service Level (%)': round(service_lvl, 1)
        })
    
    results['summary_table'] = summary_list
    
    # 2. Zonal Breakdown under Baseline
    zonal_summary = df.groupby('region').agg(
        Order_Count=('order_id', 'count'),
        Avg_Distance_km=('dist_wh1_km', 'mean'),
        Avg_Cost_S0=('cost_wh1_usd', 'mean'),
        Total_Cost_S0=('cost_wh1_usd', 'sum'),
        Avg_Lead_S0=('lead_wh1_days', 'mean'),
        Service_Lvl_S0=('service_met_wh1', lambda x: x.mean() * 100),
        Avg_Cost_S1=('cost_s1_usd', 'mean'),
        Service_Lvl_S1=('service_met_s1', lambda x: x.mean() * 100)
    ).reset_index()
    
    results['zonal_table'] = zonal_summary.to_dict(orient='records')
    
    # 3. Statistical Analysis
    # Chi-Square Test of Independence: Region vs Baseline Service Level Met
    contingency_table = pd.crosstab(df['region'], df['service_met_wh1'])
    chi2, p_chi2, dof, _ = stats.chi2_contingency(contingency_table)
    
    # One-Way ANOVA: Baseline Shipping Cost across Regions
    region_groups = [group['cost_wh1_usd'].values for name, group in df.groupby('region')]
    f_stat, p_anova = stats.f_oneway(*region_groups)
    
    # Pearson Correlation: Distance vs Baseline Shipping Cost
    r_val, p_corr = stats.pearsonr(df['dist_wh1_km'], df['cost_wh1_usd'])
    
    results['stats'] = {
        'chi2_stat': round(chi2, 2),
        'chi2_p': float(p_chi2),
        'chi2_dof': dof,
        'anova_f': round(f_stat, 2),
        'anova_p': float(p_anova),
        'pearson_r': round(r_val, 4),
        'pearson_p': float(p_corr)
    }
    
    # 4. Predictive Modeling for Shipping Cost
    # Features: Distance, Weight, Demand Units, Mode (One-hot), Category (One-hot)
    features_df = pd.get_dummies(
        df[['dist_wh1_km', 'weight_kg', 'demand_units', 'shipping_mode', 'product_category']], 
        drop_first=True
    )
    y = df['cost_wh1_usd']
    
    X_train, X_test, y_train, y_test = train_test_split(features_df, y, test_size=0.2, random_state=42)
    
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, max_depth=6, random_state=42)
    }
    
    model_results = []
    for m_name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        model_results.append({
            'Model': m_name,
            'MAE ($)': round(mae, 3),
            'RMSE ($)': round(rmse, 3),
            'R2 Score': round(r2, 4),
            'Accuracy (%)': round(r2 * 100, 1)
        })
        
    results['model_table'] = model_results
    
    # 5. Prescriptive Optimization / Center of Gravity
    total_weight = df['weight_kg'].sum()
    cog_lat = (df['customer_lat'] * df['weight_kg']).sum() / total_weight
    cog_lon = (df['customer_lon'] * df['weight_kg']).sum() / total_weight
    
    results['optimization'] = {
        'cog_latitude': round(cog_lat, 4),
        'cog_longitude': round(cog_lon, 4),
        'nearest_city': 'Saint Louis / Springfield, MO area',
        'annual_freight_s0': round(df['cost_wh1_usd'].sum(), 2),
        'annual_freight_s1': round(df['cost_s1_usd'].sum(), 2),
        'annual_freight_savings_s1': round(df['cost_wh1_usd'].sum() - df['cost_s1_usd'].sum(), 2),
        'est_additional_wh_holding_cost': 450000.0,
        'net_annual_benefit': round((df['cost_wh1_usd'].sum() - df['cost_s1_usd'].sum()) - 450000.0, 2)
    }
    
    # Save analysis results
    os.makedirs('results', exist_ok=True)
    with open(os.path.join('results', 'analysis_results.json'), 'w') as f:
        json.dump(results, f, indent=2)
        
    print("Analysis complete. Results written to results/analysis_results.json")
    print(f"Summary Table:\n{pd.DataFrame(summary_list).to_string(index=False)}")
    print(f"\nModel Performance:\n{pd.DataFrame(model_results).to_string(index=False)}")
    print(f"\nStatistical Tests: Chi2={chi2:.2f} (p={p_chi2:.4e}), ANOVA F={f_stat:.2f} (p={p_anova:.4e}), Pearson r={r_val:.4f}")

if __name__ == '__main__':
    run_analysis()
