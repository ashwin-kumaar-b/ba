import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

def generate_charts():
    df = pd.read_csv(os.path.join('data', 'warehouse_orders_dataset.csv'))
    with open(os.path.join('results', 'analysis_results.json'), 'r') as f:
        results = json.load(f)
        
    os.makedirs('images', exist_ok=True)
    sns.set_theme(style="whitegrid")
    
    # Custom color palette matching sample report
    colors_green = '#2E7D32'
    colors_orange = '#F57C00'
    colors_red = '#C62828'
    colors_blue = '#1565C0'
    palette_pie = ['#2E7D32', '#1976D2', '#F57C00', '#D32F2F', '#7B1FA2', '#0097A7']
    
    # -------------------------------------------------------------
    # Figure 1: Overall Customer Demand Distribution Across Regions (Pie Chart)
    # -------------------------------------------------------------
    plt.figure(figsize=(8, 6), dpi=300)
    region_counts = df['region'].value_counts()
    plt.pie(
        region_counts, 
        labels=region_counts.index, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=palette_pie,
        wedgeprops=dict(width=0.7, edgecolor='w', linewidth=2)
    )
    plt.title('Figure 1: Customer Order Demand Share by Geographic Region', fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join('images', 'fig1_customer_demand_distribution.png'))
    plt.close()
    
    # -------------------------------------------------------------
    # Figure 2: Shipping Breakdown by Region (Stacked / Grouped Bar)
    # -------------------------------------------------------------
    fig, ax1 = plt.subplots(figsize=(10, 5), dpi=300)
    
    region_agg = df.groupby('region').agg({
        'cost_wh1_usd': 'mean',
        'lead_wh1_days': 'mean'
    }).reindex(['Midwest', 'Northeast', 'Southeast', 'Southwest', 'West Coast', 'Northwest'])
    
    x = np.arange(len(region_agg))
    width = 0.35
    
    rects1 = ax1.bar(x - width/2, region_agg['cost_wh1_usd'], width, label='Avg Shipping Cost ($)', color='#1976D2')
    ax2 = ax1.twinx()
    rects2 = ax2.bar(x + width/2, region_agg['lead_wh1_days'], width, label='Avg Lead Time (Days)', color='#E64A19')
    
    ax1.set_xlabel('Geographic Region', fontweight='bold')
    ax1.set_ylabel('Average Shipping Cost ($)', color='#1976D2', fontweight='bold')
    ax2.set_ylabel('Average Lead Time (Days)', color='#E64A19', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(region_agg.index)
    
    # Grid lines
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax2.grid(False)
    
    plt.title('Figure 2: Baseline Logistics Cost & Delivery Days by Region (WH1 Chicago)', fontsize=12, fontweight='bold', pad=15)
    fig.tight_layout()
    plt.savefig(os.path.join('images', 'fig2_shipping_cost_by_zone.png'))
    plt.close()

    # -------------------------------------------------------------
    # Figure 3: Shipping Distance vs. Cost Scatter Plot
    # -------------------------------------------------------------
    plt.figure(figsize=(9, 6), dpi=300)
    sample_scatter = df.sample(n=1000, random_state=42)
    
    sns.regplot(
        data=sample_scatter, 
        x='dist_wh1_km', 
        y='cost_wh1_usd', 
        scatter_kws={'alpha': 0.4, 'color': '#1565C0', 's': 25},
        line_kws={'color': '#C62828', 'linewidth': 2.5, 'label': 'Linear Regression Trend (r = 0.5586)'}
    )
    plt.title('Figure 3: Shipping Distance (km) vs. Freight Cost ($USD)', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Distance to Warehouse (km)', fontweight='bold')
    plt.ylabel('Baseline Freight Shipping Cost ($USD)', fontweight='bold')
    plt.legend(loc='upper left', frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join('images', 'fig3_distance_vs_shipping_cost.png'))
    plt.close()

    # -------------------------------------------------------------
    # Figure 4: Geographic Customer Network & Candidate Warehouse Locations
    # -------------------------------------------------------------
    plt.figure(figsize=(10, 6), dpi=300)
    
    # Sample customer points
    sns.scatterplot(
        data=df.sample(n=2000, random_state=42), 
        x='customer_lon', 
        y='customer_lat', 
        hue='region', 
        palette='tab10', 
        alpha=0.4, 
        s=15,
        legend='full'
    )
    
    # Mark Warehouses
    wh_coords = {
        'WH1: Chicago (Existing)': (41.8781, -87.6298, 'red', 's'),
        'WH2: Atlanta (Candidate)': (33.7490, -84.3880, 'green', '^'),
        'WH3: Los Angeles (Candidate)': (34.0522, -118.2437, 'purple', '^'),
        'WH4: Dallas (Candidate)': (32.7767, -96.7970, 'orange', '^')
    }
    
    for name, (lat, lon, color, marker) in wh_coords.items():
        plt.scatter(lon, lat, color=color, s=150, marker=marker, edgecolors='black', linewidth=1.5, zorder=5, label=name)
        plt.text(lon + 0.8, lat + 0.5, name.split(':')[0], fontsize=9, fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        
    plt.title('Figure 4: Spatial Distribution of Customer Orders & Candidate Warehouse Hubs', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Longitude', fontweight='bold')
    plt.ylabel('Latitude', fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join('images', 'fig4_warehouse_network_map.png'))
    plt.close()

    # -------------------------------------------------------------
    # Figure 5: Monthly Freight Cost Trend (Line Chart)
    # -------------------------------------------------------------
    plt.figure(figsize=(10, 5), dpi=300)
    
    monthly_trend = df.groupby('month_num').agg({
        'cost_wh1_usd': 'sum',
        'cost_s1_usd': 'sum',
        'cost_s2_usd': 'sum'
    }).reset_index()
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_trend['Month_Name'] = months
    
    plt.plot(monthly_trend['Month_Name'], monthly_trend['cost_wh1_usd'] / 1000, marker='o', color='#C62828', linewidth=2.5, label='Baseline S0 (Chicago Only)')
    plt.plot(monthly_trend['Month_Name'], monthly_trend['cost_s1_usd'] / 1000, marker='s', color='#2E7D32', linewidth=2.5, label='Scenario 1 S1 (Chicago + Los Angeles)')
    plt.plot(monthly_trend['Month_Name'], monthly_trend['cost_s2_usd'] / 1000, marker='^', color='#F57C00', linewidth=2.5, label='Scenario 2 S2 (Chicago + Atlanta)')
    
    plt.title('Figure 5: 12-Month Total Freight Expenditure Trend ($ Thousands)', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Month', fontweight='bold')
    plt.ylabel('Total Freight Cost ($K)', fontweight='bold')
    plt.legend(loc='lower right', frameon=True)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join('images', 'fig5_monthly_freight_cost_trend.png'))
    plt.close()

    # -------------------------------------------------------------
    # Figure 6: Model Performance Comparison Bar Chart
    # -------------------------------------------------------------
    plt.figure(figsize=(8, 5), dpi=300)
    
    model_df = pd.DataFrame(results['model_table'])
    
    x = np.arange(len(model_df))
    width = 0.35
    
    plt.bar(x - width/2, model_df['R2 Score'] * 100, width, label='R² Score (%)', color='#1565C0')
    plt.bar(x + width/2, 100 - (model_df['MAE ($)'] / df['cost_wh1_usd'].mean() * 100), width, label='Cost Accuracy (100 - %MAE)', color='#2E7D32')
    
    plt.title('Figure 6: Shipping Cost Predictive Model Performance Comparison', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Machine Learning Model', fontweight='bold')
    plt.ylabel('Score (%)', fontweight='bold')
    plt.xticks(x, model_df['Model'])
    plt.ylim(80, 105)
    plt.legend(loc='lower right', frameon=True)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join('images', 'fig6_model_comparison.png'))
    plt.close()
    
    print("All 6 figures generated successfully in images/ directory.")

if __name__ == '__main__':
    generate_charts()
