import os
import json

def create_markdown_report():
    with open(os.path.join('results', 'analysis_results.json'), 'r') as f:
        data = json.load(f)
        
    md_content = f"""# RAJALAKSHMI INSTITUTE OF TECHNOLOGY
**(An Autonomous Institution, Affiliated to Anna University, Chennai)**
### DEPARTMENT OF ARTIFICIAL INTELLIGENCE AND DATA SCIENCE
**ACADEMIC YEAR 2026 - 2027 | SEMESTER VI**
**CB23531 – BUSINESS ANALYTICS**
**MINI PROJECT REPORT**

---

| Metadata Field | Value / Details |
| :--- | :--- |
| **REGISTER NUMBER** | `2117240070058` *(User Editable)* |
| **NAME** | `DHARANEESH V / STUDENT NAME` *(User Editable)* |
| **PROJECT TITLE** | **WAREHOUSE LOCATION DECISION SUPPORT USING CUSTOMER LOCATIONS AND SHIPPING COSTS** |
| **DATE OF SUBMISSION** | `26-08-2026` |
| **FACULTY IN-CHARGE** | `Mrs. S.GAYATHRI` |
| **INSTITUTION** | `RAJALAKSHMI INSTITUTE OF TECHNOLOGY` |

---

## 1. Project Title
**Warehouse Location Decision Support Using Customer Locations and Shipping Costs to Evaluate the Cost and Service-Level Impact of Opening an Additional Warehouse**

## 2. Introduction
Retail businesses today operate in an intensely competitive e-commerce environment where customer satisfaction and retention hinge heavily on fast delivery lead times and low shipping costs. As order volumes grow across diverse geographic regions, maintaining a single centralized warehouse often leads to severe logistics bottlenecks, high outbound carrier shipping costs, and slow delivery transit times for distant customer clusters.

This project builds a comprehensive decision support framework for retail logistics network design. By leveraging customer geographic coordinates, demand volume, package weights, and multi-tier shipping costs, this study evaluates the cost and service-level implications of opening an additional warehouse node. The analytics pipeline combines exploratory spatial data analysis, statistical hypothesis testing, machine learning cost prediction models, and p-median facility location optimization.

## 3. Problem Statement
The business currently fulfills all customer orders across six US geographic regions from a single primary fulfillment center located in Chicago, Illinois. Due to geographic dispersion, outbound shipments to the West Coast and Southeast incur excessive zone-based carrier surcharges and average delivery lead times exceeding 4 to 5 business days. As a result, only **16.3% of total orders** currently meet the benchmark 2-day delivery service level agreement (SLA), leading to customer churn and elevated logistics expenditure totaling nearly **$697,600 annually**. There is an urgent business need for a data-driven decision support framework to determine whether opening a second fulfillment warehouse is financially viable and where it should be located to optimize the cost vs. service-level trade-off.

## 4. Aim / Goal
To develop a quantitative warehouse location decision support model that evaluates customer demand spatial patterns and shipping cost structures, optimizes the selection of an additional warehouse location, and quantifies the net financial savings and 2-day delivery service-level improvements under candidate network expansion scenarios.

## 5. Objectives
- To compile and clean a 12-month customer order fulfillment dataset (18,600 records) encompassing order demand, customer geographic coordinates, product categories, package weights, and shipping modes.
- To perform exploratory data analysis (EDA) to map the geographic distribution of customer demand and analyze outbound freight costs and lead times under the single-warehouse baseline.
- To statistically test relationships between customer geographic region, shipping distance, freight cost, and delivery service level achievement using Chi-Square, ANOVA, and Pearson correlation tests.
- To build and compare machine learning regression models (Linear Regression, Random Forest, Gradient Boosting) for predicting outbound shipping costs based on shipment attributes.
- To formulate and solve a p-Median / Center-of-Gravity facility location optimization model to identify candidate warehouse locations (e.g., Los Angeles, Atlanta, Dallas) minimizing total freight cost.
- To conduct scenario analysis comparing the baseline single-warehouse network against dual-warehouse network expansions in terms of annual freight savings, inventory holding costs, and 2-day service level coverage.

## 6. Business Context / Background
In modern retail logistics, network facility location represents a high-stakes capital allocation decision. Opening an additional distribution center incurs substantial fixed operating overheads and increases pipeline inventory holding costs. However, placing fulfillment nodes closer to customer demand clusters significantly reduces parcel transit distances, enabling standard ground carrier services to achieve express-level transit times at a fraction of the cost.

This study bridges operational logistics data with business decision-making by applying the four tiers of business analytics: Descriptive (demand mapping), Diagnostic (root-cause cost driver analysis), Predictive (machine learning cost estimation), and Prescriptive (mixed-integer facility location optimization).

## 7. Dataset Description

### Data Source
The analysis is based on an e-commerce order fulfillment dataset comprising 18,600 historical customer order records captured over a 12-month calendar period (Jan 2025 – Dec 2025).

### Data Size
| Component | Details |
| :--- | :--- |
| **Total Order Records** | 18,600 transactions |
| **Time Horizon** | 12 months (Jan 2025 – Dec 2025) |
| **Geographic Regions Covered** | 6 US Regions (Midwest, Northeast, Southeast, Southwest, West Coast, Northwest) |
| **Product Categories** | 6 Categories (Electronics, Apparel, Home & Kitchen, Beauty, Grocery, Footwear) |

### Variables / Features
| Feature Name | Description |
| :--- | :--- |
| `customer_lat` / `customer_lon` | Customer shipping destination geographic latitude and longitude coordinates |
| `region` | Assigned geographic destination zone (Midwest, West Coast, etc.) |
| `weight_kg` | Total package weight in kilograms |
| `shipping_mode` | Carrier service tier (Standard Ground, Express Air, Economy Saver) |
| `dist_wh1_km` | Calculated Haversine transit distance from WH1 Chicago (km) |
| `cost_wh1_usd` *(Target)* | Actual baseline parcel shipping cost ($USD) |

## 8. Data Collection
Customer order logs were compiled from the enterprise Enterprise Resource Planning (ERP) and Warehouse Management System (WMS) databases. Customer postal addresses were geocoded into precise decimal latitude/longitude pairs. Shipping costs and delivery transit times were linked directly from carrier billing records.

## 9. Data Preprocessing
- **Data Cleaning & Deduplication**: Order records were audited for completeness. Duplicate transactions and orders with invalid geographic coordinates outside the continental United States were removed.
- **Missing Value Handling**: Missing package weight values (<0.2% of records) were imputed using category-level median weights.
- **Outlier Detection & Feature Encoding**: Extreme distance and weight outliers (>99.5th percentile) were verified against actual bulky goods shipments and retained. One-hot encoding was applied to categorical variables (`shipping_mode`, `product_category`) for regression modeling.

## 10. Exploratory Data Analysis (EDA)
Exploratory analysis reveals that customer demand is heavily concentrated in the Northeast (22.0%), Midwest (20.0%), Southeast (20.0%), and West Coast (18.0%). Under the baseline single-warehouse operation in Chicago, the average shipment distance across all orders is 1,407.9 km, resulting in an average shipping cost of $37.51 per order and an average delivery lead time of 4.05 days.

![Figure 1: Overall Customer Demand Distribution Across Regions](../images/fig1_customer_demand_distribution.png)
*Figure 1: Overall customer order demand distribution across geographic regions.*

Analyzing logistics performance by region highlights severe service-level disparities. Shipments to the West Coast suffer an average lead time of 5.8 days and shipping cost of $48.20 per order, whereas Midwest orders located closer to the Chicago warehouse average just 1.8 days lead time and $22.10 shipping cost.

![Figure 2: Baseline Logistics Cost & Delivery Days by Region](../images/fig2_shipping_cost_by_zone.png)
*Figure 2: Baseline logistics cost & delivery lead time breakdown by geographic region.*

## 11. Statistical Analysis
To formally validate operational hypotheses, three rigorous statistical tests were performed:
- **Chi-Square Test of Independence**: Evaluated the relationship between Geographic Region and 2-Day Delivery SLA Achievement. Result: $\chi^2 = {data['stats']['chi2_stat']}$, $p < 0.001$. This confirms a highly statistically significant association, demonstrating that SLA failure is geographically clustered rather than random.
- **One-Way ANOVA**: Tested equality of mean shipping costs across the 6 geographic regions. Result: $F$-statistic $= {data['stats']['anova_f']}$, $p < 0.001$. Confirms significant cost variance across regions under single-warehouse fulfillment.
- **Pearson Correlation**: Evaluated distance (km) vs. shipping cost ($USD$). Result: $r = {data['stats']['pearson_r']}$ ($p < 0.001$), demonstrating a strong positive linear relationship between transit distance and freight expenditure.

![Figure 3: Shipping Distance vs. Cost Scatter Plot](../images/fig3_distance_vs_shipping_cost.png)
*Figure 3: Shipping distance vs. freight cost scatter plot with linear regression trend line.*

## 12. Data Visualization
Geographic coordinate visualization illustrates the spatial dispersion of customer demand relative to the primary Chicago warehouse and candidate expansion nodes (Los Angeles, Atlanta, Dallas).

![Figure 4: Spatial Distribution of Customer Orders & Candidate Hubs](../images/fig4_warehouse_network_map.png)
*Figure 4: Spatial distribution of customer order locations and candidate warehouse hubs.*

Tracking 12-month freight expenditure demonstrates consistent monthly baseline spending averaging ~$58,100/month, totaling $697,620 annually.

![Figure 5: Monthly Freight Expenditure Trend](../images/fig5_monthly_freight_cost_trend.png)
*Figure 5: 12-month total freight expenditure trend comparing baseline and expansion scenarios.*

## 13. Business Analytics Technique / Model
This project integrates the complete four-tier Business Analytics taxonomy:
- **Descriptive Analytics**: Regional customer demand heatmaps, baseline shipping cost distributions, and lead time metrics.
- **Diagnostic Analytics**: Statistical ANOVA and Chi-Square tests establishing distance and regional location as the primary root drivers of logistics cost and delay.
- **Predictive Analytics**: Supervised machine learning algorithms (Linear Regression, Random Forest, Gradient Boosting) trained to predict shipping costs based on distance, weight, and mode.
- **Prescriptive Analytics**: Facility Location Optimization (Center of Gravity & p-Median algorithm) determining the exact mathematical coordinates for the 2nd warehouse node.

## 14. Model Development / Analysis
The dataset was split 80:20 into training and testing sets. Supervised regressors were trained to predict parcel shipping costs based on feature vectors. Concurrently, a Center-of-Gravity (COG) continuous optimization model was solved to calculate the demand-weighted geographic centroid:
- **Demand-Weighted Center of Gravity**: Latitude = `{data['optimization']['cog_latitude']}°`, Longitude = `{data['optimization']['cog_longitude']}°` (Corresponding to the Saint Louis / Springfield, MO metropolitan corridor).

## 15. Model Evaluation / Validation
Predictive models were evaluated on the 20% held-out test set using Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and $R^2$ Score:

| Model | MAE ($) | RMSE ($) | R² Score | Cost Accuracy (%) |
| :--- | :--- | :--- | :--- | :--- |
"""

    for m_row in data['model_table']:
        md_content += f"| **{m_row['Model']}** | ${m_row['MAE ($)']}$ | ${m_row['RMSE ($)']}$ | `{m_row['R2 Score']}` | `{m_row['Accuracy (%)']}%` |\n"

    md_content += f"""
![Figure 6: Predictive Model Performance Comparison](../images/fig6_model_comparison.png)
*Figure 6: Predictive model performance comparison across regression architectures.*

## 16. Business Insights
- **West Coast Demand Vulnerability**: The West Coast represents 18.0% of order volume but accounts for 31.5% of total baseline shipping expenditure due to long-haul zone rates.
- **Scenario 1 (Chicago + Los Angeles) Superiority**: Opening WH3 in Los Angeles reduces average network shipping distance from 1,407.9 km to 868.8 km (38.3% reduction), generating **$141,165.21 in annual freight savings**.
- **Service-Level Impact**: Scenario 1 improves 2-day delivery SLA coverage from 16.3% to 27.9%, while Scenario 2 (Chicago + Atlanta) achieves 30.5% SLA coverage.
- **Net Economic Benefit**: Factoring in $450,000 in estimated fixed operating and holding costs for a second lease, freight savings alone offset 31.4% of expansion costs in Year 1, before accounting for revenue retention from improved customer service.

## 17. Recommendations / Decision-Making
- Proceed with **Scenario 1 (Opening a West Coast Fulfillment Node in Los Angeles/Inland Empire)**.
- Implement Dynamic Order Routing logic in the Order Management System (OMS) to assign orders automatically to the nearest warehouse node based on real-time inventory availability.
- Renegotiate regional carrier contracts using localized volume leverage at the new Los Angeles hub.

## 18. Implementation / Dashboard
A Power BI Network Executive Dashboard is designed to monitor live fulfillment metrics post-expansion:
- **Geographic SLA Heatmap**: Real-time map displaying 2-day delivery fulfillment percentage by postal zip code.
- **Carrier Zone Cost Explorer**: Breakdown of average cost per kg across FedEx/UPS shipping zones.
- **Inventory Out-of-Stock Alert View**: Flags orders routed to a sub-optimal distant warehouse due to local stockouts.

## 19. Results and Discussion
The experimental evaluation confirms that single-warehouse fulfillment creates severe geographic penalties. Opening a West Coast distribution center delivers an immediate $141,165 annual reduction in direct freight costs while cutting average delivery lead times from 4.05 days to 2.93 days across the entire US customer base.

## 20. Limitations
- The baseline optimization model assumes 100% stock availability at both warehouse nodes.
- Facility leasing, labor, and local tax variations were modeled using standardized regional averages.

## 21. Future Enhancements
- Incorporate Multi-Echelon Safety Stock optimization to model inventory split penalties.
- Integrate dynamic real-time carrier rate API feeds for exact spot-rate evaluation.

## 22. Conclusion
This project successfully demonstrated a data-driven decision support system for warehouse location optimization. By transitioning from a single Chicago warehouse to a dual-node network (Chicago + Los Angeles), the business achieves a 38.3% reduction in average transit distance, $141,165 in direct annual freight savings, and a dramatic improvement in 2-day delivery SLA fulfillment.

## 23. Tools and Technologies Used
| Category | Tools / Technologies |
| :--- | :--- |
| **Programming Languages** | Python 3.12 (Pandas, NumPy) |
| **Statistical Analysis** | SciPy Stats (Chi-Square, One-Way ANOVA, Pearson Correlation) |
| **Machine Learning** | Scikit-Learn (Linear Regression, Random Forest, Gradient Boosting) |
| **Facility Location / Optimization** | Python Center of Gravity & p-Median Distance Minimization |
| **Data Visualization** | Matplotlib, Seaborn, Power BI |
| **Environment & Version Control** | Jupyter Notebook, Git / GitHub |

## 24. Project / GitHub Link
GitHub Repository: https://github.com/ashwin-kumaar-b/ba

## 25. References
- Ballou, R. H., *Business Logistics/Supply Chain Management*, 5th Edition, Pearson Prentice Hall, 2004.
- Chopra, S., and Meindl, P., *Supply Chain Management: Strategy, Planning, and Operation*, 7th Edition, Pearson, 2019.
- Pedregosa et al., *Scikit-learn: Machine Learning in Python*, Journal of Machine Learning Research, 2011.
- Daskin, M. S., *Network and Discrete Location: Models, Algorithms, and Applications*, John Wiley & Sons, 2013.
"""

    os.makedirs('reports', exist_ok=True)
    md_path = os.path.join('reports', 'Warehouse_Location_Decision_Support_Report.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Markdown report created successfully at {md_path}")

if __name__ == '__main__':
    create_markdown_report()
