import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta

def generate_warehouse_data(n_samples=18600, random_state=42):
    np.random.seed(random_state)
    
    # Define Warehouse Coordinates (Lat, Lon)
    warehouses = {
        'WH1_CHICAGO': (41.8781, -87.6298),     # Existing Primary Central WH
        'WH2_ATLANTA': (33.7490, -84.3880),     # Candidate Southeast Hub
        'WH3_LOS_ANGELES': (34.0522, -118.2437),# Candidate West Coast Hub
        'WH4_DALLAS': (32.7767, -96.7970)       # Candidate Southwest Hub
    }
    
    # Regional Customer Centers (Lat Mean, Lat Std, Lon Mean, Lon Std, Weight Share)
    regions = {
        'Midwest': (41.5, 2.0, -88.0, 3.0, 0.20),
        'Northeast': (40.7, 1.8, -74.0, 2.5, 0.22),
        'Southeast': (33.8, 2.2, -82.5, 3.0, 0.20),
        'West Coast': (36.5, 2.5, -119.5, 2.0, 0.18),
        'Southwest': (32.0, 2.0, -97.0, 3.0, 0.12),
        'Northwest': (46.0, 1.5, -122.0, 2.0, 0.08)
    }
    
    region_names = list(regions.keys())
    region_probs = [regions[r][4] for r in region_names]
    
    # Assign regions to samples
    sample_regions = np.random.choice(region_names, size=n_samples, p=region_probs)
    
    # Generate Customer Coordinates based on region
    lats = np.zeros(n_samples)
    lons = np.zeros(n_samples)
    for i, r in enumerate(sample_regions):
        lat_m, lat_s, lon_m, lon_s, _ = regions[r]
        lats[i] = np.random.normal(lat_m, lat_s)
        lons[i] = np.random.normal(lon_m, lon_s)
        
    # Generate Dates over 12 months (2025-01-01 to 2025-12-31)
    start_date = datetime(2025, 1, 1)
    dates = [start_date + timedelta(days=int(d), hours=int(h)) for d, h in zip(
        np.random.uniform(0, 364, n_samples),
        np.random.uniform(0, 23, n_samples)
    )]
    dates.sort()
    
    # Categories & Product Attributes
    categories = ['Electronics', 'Apparel', 'Home & Kitchen', 'Beauty', 'Grocery', 'Footwear']
    category_probs = [0.25, 0.22, 0.20, 0.13, 0.12, 0.08]
    sample_categories = np.random.choice(categories, size=n_samples, p=category_probs)
    
    demand_units = np.random.randint(1, 6, size=n_samples)
    weight_kg = np.round(np.random.uniform(0.5, 15.0, size=n_samples) * demand_units, 2)
    order_value = np.round(weight_kg * np.random.uniform(15.0, 45.0, size=n_samples) + np.random.uniform(10, 50, size=n_samples), 2)
    
    shipping_modes = ['Standard Ground', 'Express Air', 'Economy Saver']
    mode_probs = [0.65, 0.20, 0.15]
    sample_modes = np.random.choice(shipping_modes, size=n_samples, p=mode_probs)
    
    # Haversine distance function (in km)
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0 # Earth radius in km
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat / 2.0)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        return R * c

    # Calculate Distances to all warehouses
    dist_wh1 = haversine(lats, lons, warehouses['WH1_CHICAGO'][0], warehouses['WH1_CHICAGO'][1])
    dist_wh2 = haversine(lats, lons, warehouses['WH2_ATLANTA'][0], warehouses['WH2_ATLANTA'][1])
    dist_wh3 = haversine(lats, lons, warehouses['WH3_LOS_ANGELES'][0], warehouses['WH3_LOS_ANGELES'][1])
    dist_wh4 = haversine(lats, lons, warehouses['WH4_DALLAS'][0], warehouses['WH4_DALLAS'][1])
    
    # Calculate baseline (WH1 only) costs & lead times
    base_rate_per_km = 0.012
    base_rate_per_kg = 0.45
    fixed_handling = 4.50
    
    # Shipping Cost Calculation with non-linear distance scaling & mode modifier
    mode_cost_mult = {'Standard Ground': 1.0, 'Express Air': 2.1, 'Economy Saver': 0.75}
    mode_mult_arr = np.array([mode_cost_mult[m] for m in sample_modes])
    
    cost_wh1 = (fixed_handling + (dist_wh1 * base_rate_per_km) + (weight_kg * base_rate_per_kg)) * mode_mult_arr
    cost_wh1 += np.random.normal(0, 1.5, size=n_samples)
    cost_wh1 = np.clip(cost_wh1, 3.50, None)
    
    # Lead time calculation (days)
    lead_wh1 = 1.0 + (dist_wh1 / 450.0) + (np.random.normal(0, 0.4, size=n_samples))
    lead_wh1 = np.clip(np.round(lead_wh1, 1), 1.0, 7.0)
    
    # Service level target: Delivery within <= 2 days
    service_met_wh1 = (lead_wh1 <= 2.0).astype(int)
    
    # Scenario 1: Dual WH (Chicago + Los Angeles)
    dist_s1 = np.minimum(dist_wh1, dist_wh3)
    wh_assigned_s1 = np.where(dist_wh3 < dist_wh1, 'WH3_LOS_ANGELES', 'WH1_CHICAGO')
    cost_s1 = (fixed_handling + (dist_s1 * base_rate_per_km) + (weight_kg * base_rate_per_kg)) * mode_mult_arr + np.random.normal(0, 1.2, size=n_samples)
    cost_s1 = np.clip(cost_s1, 3.50, None)
    lead_s1 = np.clip(np.round(1.0 + (dist_s1 / 450.0) + np.random.normal(0, 0.3, size=n_samples), 1), 1.0, 7.0)
    service_met_s1 = (lead_s1 <= 2.0).astype(int)

    # Scenario 2: Dual WH (Chicago + Atlanta)
    dist_s2 = np.minimum(dist_wh1, dist_wh2)
    wh_assigned_s2 = np.where(dist_wh2 < dist_wh1, 'WH2_ATLANTA', 'WH1_CHICAGO')
    cost_s2 = (fixed_handling + (dist_s2 * base_rate_per_km) + (weight_kg * base_rate_per_kg)) * mode_mult_arr + np.random.normal(0, 1.2, size=n_samples)
    cost_s2 = np.clip(cost_s2, 3.50, None)
    lead_s2 = np.clip(np.round(1.0 + (dist_s2 / 450.0) + np.random.normal(0, 0.3, size=n_samples), 1), 1.0, 7.0)
    service_met_s2 = (lead_s2 <= 2.0).astype(int)

    # Build dataframe
    df = pd.DataFrame({
        'order_id': [f'ORD-{10001+i}' for i in range(n_samples)],
        'order_date': [d.strftime('%Y-%m-%d %H:%M:%S') for d in dates],
        'month': [d.strftime('%b') for d in dates],
        'month_num': [d.month for d in dates],
        'region': sample_regions,
        'customer_lat': np.round(lats, 4),
        'customer_lon': np.round(lons, 4),
        'product_category': sample_categories,
        'demand_units': demand_units,
        'weight_kg': weight_kg,
        'order_value_usd': order_value,
        'shipping_mode': sample_modes,
        
        # Baseline (Single WH - Chicago)
        'dist_wh1_km': np.round(dist_wh1, 1),
        'cost_wh1_usd': np.round(cost_wh1, 2),
        'lead_wh1_days': lead_wh1,
        'service_met_wh1': service_met_wh1,
        
        # Distances to candidate WHs
        'dist_wh2_atlanta_km': np.round(dist_wh2, 1),
        'dist_wh3_la_km': np.round(dist_wh3, 1),
        'dist_wh4_dallas_km': np.round(dist_wh4, 1),
        
        # Scenario 1 (Chicago + LA)
        'wh_assigned_s1': wh_assigned_s1,
        'dist_s1_km': np.round(dist_s1, 1),
        'cost_s1_usd': np.round(cost_s1, 2),
        'lead_s1_days': lead_s1,
        'service_met_s1': service_met_s1,

        # Scenario 2 (Chicago + Atlanta)
        'wh_assigned_s2': wh_assigned_s2,
        'dist_s2_km': np.round(dist_s2, 1),
        'cost_s2_usd': np.round(cost_s2, 2),
        'lead_s2_days': lead_s2,
        'service_met_s2': service_met_s2
    })
    
    os.makedirs('data', exist_ok=True)
    output_path = os.path.join('data', 'warehouse_orders_dataset.csv')
    df.to_csv(output_path, index=False)
    print(f"Dataset generated successfully with {len(df)} records at {output_path}")

if __name__ == '__main__':
    generate_warehouse_data()
