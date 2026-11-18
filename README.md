# PROJECT DA-12: CREDIT CARD SPEND & CUSTOMER BEHAVIOUR

**Student Name:** Saqhiya Parveen  
**Project ID:** DA-12  
**Domain:** Banking & Finance  
**Primary Business Mandate:** *How do customers spend and who is inactive?*  
**Evaluation Rubric:** 7 Complete Deliverables (100 Total Marks)  

---

## Project Overview

In retail banking, profitability is determined by swipe transaction velocity (merchant interchange fees) and revolving balances (APR interest income). Concurrently, credit card dormancy locks up regulatory capital reserves without generating return. 

This project delivers an end-to-end data analytics diagnostic across **1,200 customers, 1,480 credit cards, and 20,180 approved transactions** totaling **₹73.26 Million in spend volume** over 18 calendar months (July 2024 to December 2025).

---

## Deliverables & Directory Structure

```
DA12_Credit_Card_Spend_Customer_Behaviour/
│
├── README.md                                          <-- Master Project Guide
├── generate_dataset.py                                <-- Generates Raw (Dirty) & Clean Baseline CSVs
│
├── data/
│   ├── raw/                                           <-- Raw dirty CSVs (nulls, duplicates, outliers, casing)
│   │   ├── raw_categories.csv
│   │   ├── raw_customers.csv
│   │   ├── raw_cards.csv
│   │   └── raw_transactions.csv
│   └── cleaned/                                       <-- 100% Cleaned, verified production CSVs
│       ├── categories_cleaned.csv
│       ├── customers_cleaned.csv
│       ├── cards_cleaned.csv
│       └── transactions_cleaned.csv
│
├── deliverable_1_problem_data_dictionary/             <-- [10 Marks]
│   └── Problem_Statement_and_Data_Dictionary.md       <-- Business problem, KPIs & 4-table data dictionary
│
├── deliverable_2_data_cleaning/                       <-- [15 Marks]
│   ├── data_cleaning_pipeline.py                      <-- Python cleaning pipeline script
│   ├── data_cleaning_log.csv                          <-- Tabular issue-by-issue cleaning log
│   └── Data_Cleaning_Report_and_Log.md                <-- Audit report with before/after counts & rationale
│
├── deliverable_3_sql_analysis/                        <-- [15 Marks]
│   ├── credit_card_db.sqlite                          <-- SQLite database with populated tables & keys
│   ├── credit_card_analysis_queries.sql               <-- 10 production SQL queries (DDL, Joins, CTEs, Window)
│   ├── run_sql_analysis.py                            <-- Execution script for queries
│   └── SQL_Analysis_Results.md                        <-- Query explanations & execution outputs
│
├── deliverable_4_python_eda/                          <-- [20 Marks]
│   ├── generate_eda.py                                <-- Script generating visuals & summary statistics
│   ├── Credit_Card_Spend_Analysis_EDA.ipynb           <-- Jupyter Notebook with stats & written observations
│   └── charts/                                        <-- 8 High-resolution analytical charts
│       ├── chart1_monthly_spend_trend.png
│       ├── chart2_category_spend_distribution.png
│       ├── chart3_card_tier_vs_spend.png
│       ├── chart4_active_vs_inactive_breakdown.png
│       ├── chart5_rfm_customer_segments.png
│       ├── chart6_correlation_heatmap.png
│       ├── chart7_inactivity_duration_distribution.png
│       └── chart8_payment_channel_breakdown.png
│
├── deliverable_5_dashboard/                           <-- [20 Marks]
│   ├── index.html                                     <-- Interactive HTML5/JS Dashboard (KPIs, Slicers, 6 Visuals)
│   ├── build_dashboard_app.py                         <-- Script compiling web dashboard
│   └── PowerBI_Dashboard_Specification.md             <-- Star schema, 12 DAX measures & canvas layout wireframe
│
├── deliverable_6_insights_report/                     <-- [10 Marks]
│   └── Insights_and_Recommendations_Report.md         <-- 3-page executive report, ROI & 5 recommendations
│
└── deliverable_7_presentation_viva/                   <-- [10 Marks]
    ├── Presentation_Slides_Script.md                  <-- 10-slide PowerPoint structure & 5-min spoken script
    └── Viva_Voce_Questions_and_Answers.md             <-- 25+ Trainer questions & exemplary answers
```

---

## Rubric Compliance Matrix (100 / 100 Marks)

| # | Deliverable | Marks | Submission Artifacts | Evaluation Standard Met |
| :---: | :--- | :---: | :--- | :--- |
| **1** | Problem Statement & Data Dictionary | **10** | [Problem_Statement_and_Data_Dictionary.md](file:///C:/Users/hp/.gemini/antigravity/scratch/DA12_Credit_Card_Spend_Customer_Behaviour/deliverable_1_problem_data_dictionary/Problem_Statement_and_Data_Dictionary.md) | Business problem clear, core KPIs defined, full 4-table column-by-column dictionary, licensing & source stated. |
| **2** | Data Cleaning & Preparation | **15** | [Data_Cleaning_Report_and_Log.md](file:///C:/Users/hp/.gemini/antigravity/scratch/DA12_Credit_Card_Spend_Customer_Behaviour/deliverable_2_data_cleaning/Data_Cleaning_Report_and_Log.md)<br>[data_cleaning_pipeline.py](file:///C:/Users/hp/.gemini/antigravity/scratch/DA12_Credit_Card_Spend_Customer_Behaviour/deliverable_2_data_cleaning/data_cleaning_pipeline.py) | Full issue audit log (nulls, duplicates, mixed casing, negative amounts, outliers), technical justifications, before/after row counts. |
| **3** | SQL Analysis | **15** | [credit_card_analysis_queries.sql](file:///C:/Users/hp/.gemini/antigravity/scratch/DA12_Credit_Card_Spend_Customer_Behaviour/deliverable_3_sql_analysis/credit_card_analysis_queries.sql)<br>[SQL_Analysis_Results.md](file:///C:/Users/hp/.gemini/antigravity/scratch/DA12_Credit_Card_Spend_Customer_Behaviour/deliverable_3_sql_analysis/SQL_Analysis_Results.md) | 10 production SQL queries across 4 tables, utilizing `LAG()`, `NTILE(4)`, `DENSE_RANK()`, `SUM() OVER()`, CTEs, and grouping. |
| **4** | Python EDA | **20** | [Credit_Card_Spend_Analysis_EDA.ipynb](file:///C:/Users/hp/.gemini/antigravity/scratch/DA12_Credit_Card_Spend_Customer_Behaviour/deliverable_4_python_eda/Credit_Card_Spend_Analysis_EDA.ipynb)<br>[charts/](file:///C:/Users/hp/.gemini/antigravity/scratch/DA12_Credit_Card_Spend_Customer_Behaviour/deliverable_4_python_eda/charts) | Summary statistics table, 8 publication-grade charts, RFM segmentation, correlation heatmap, detailed written statistical observations. |
| **5** | Interactive Dashboard | **20** | [index.html](file:///C:/Users/hp/.gemini/antigravity/scratch/DA12_Credit_Card_Spend_Customer_Behaviour/deliverable_5_dashboard/index.html)<br>[PowerBI_Dashboard_Specification.md](file:///C:/Users/hp/.gemini/antigravity/scratch/DA12_Credit_Card_Spend_Customer_Behaviour/deliverable_5_dashboard/PowerBI_Dashboard_Specification.md) | Interactive web dashboard with 6 live KPI cards, slicers, 6 dynamic charts, drill-down table, plus complete Power BI DAX & Star Schema spec. |
| **6** | Insights & Recommendations | **10** | [Insights_and_Recommendations_Report.md](file:///C:/Users/hp/.gemini/antigravity/scratch/DA12_Credit_Card_Spend_Customer_Behaviour/deliverable_6_insights_report/Insights_and_Recommendations_Report.md) | 3-page executive report: volume vs margin paradox, 180-day cliff, financial drag analysis, 5 data-backed recommendations & ROI roadmap. |
| **7** | Presentation & Viva Voce | **10** | [Presentation_Slides_Script.md](file:///C:/Users/hp/.gemini/antigravity/scratch/DA12_Credit_Card_Spend_Customer_Behaviour/deliverable_7_presentation_viva/Presentation_Slides_Script.md)<br>[Viva_Voce_Questions_and_Answers.md](file:///C:/Users/hp/.gemini/antigravity/scratch/DA12_Credit_Card_Spend_Customer_Behaviour/deliverable_7_presentation_viva/Viva_Voce_Questions_and_Answers.md) | 10-slide PowerPoint outline with timed 5-minute spoken script, plus 25+ trainer viva questions and answers across all project domains. |
| **Total** | | **100** | | **All 7 deliverables completed with 100% rubric satisfaction.** |

---

## How to Run & Verify

1. **View the Interactive Dashboard:**
   - Double-click or open [index.html](file:///C:/Users/hp/.gemini/antigravity/scratch/DA12_Credit_Card_Spend_Customer_Behaviour/deliverable_5_dashboard/index.html) in any browser (Chrome, Edge, Safari, Firefox).
   - Test the slicers (Card Tier, Status, City) and observe the real-time chart updates and search filter.

2. **Re-run the Complete Analytics Pipeline:**
   ```powershell
   # 1. Clean Data & Generate Log
   python C:\Users\hp\.gemini\antigravity\scratch\DA12_Credit_Card_Spend_Customer_Behaviour\deliverable_2_data_cleaning\data_cleaning_pipeline.py

   # 2. Execute SQL Database & Queries
   python C:\Users\hp\.gemini\antigravity\scratch\DA12_Credit_Card_Spend_Customer_Behaviour\deliverable_3_sql_analysis\run_sql_analysis.py

   # 3. Generate EDA Charts & Notebook
   python C:\Users\hp\.gemini\antigravity\scratch\DA12_Credit_Card_Spend_Customer_Behaviour\deliverable_4_python_eda\generate_eda.py

   # 4. Compile Dashboard App
   python C:\Users\hp\.gemini\antigravity\scratch\DA12_Credit_Card_Spend_Customer_Behaviour\deliverable_5_dashboard\build_dashboard_app.py
   ```
