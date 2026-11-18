import os
import sqlite3
import pandas as pd

base_dir = r"C:\Users\hp\.gemini\antigravity\scratch\DA12_Credit_Card_Spend_Customer_Behaviour"
clean_dir = os.path.join(base_dir, "data", "cleaned")
sql_dir = os.path.join(base_dir, "deliverable_3_sql_analysis")
os.makedirs(sql_dir, exist_ok=True)

db_path = os.path.join(sql_dir, "credit_card_db.sqlite")
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Setting up SQLite Database and importing cleaned tables...")

# Load cleaned CSVs
df_cat = pd.read_csv(os.path.join(clean_dir, "categories_cleaned.csv"))
df_cust = pd.read_csv(os.path.join(clean_dir, "customers_cleaned.csv"))
df_cards = pd.read_csv(os.path.join(clean_dir, "cards_cleaned.csv"))
df_tx = pd.read_csv(os.path.join(clean_dir, "transactions_cleaned.csv"))

# Write DDL & tables
ddl_script = """
CREATE TABLE categories (
    category_id VARCHAR(10) PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL,
    department VARCHAR(30) NOT NULL,
    reward_points_multiplier DECIMAL(3,1) NOT NULL,
    risk_category VARCHAR(15) NOT NULL
);

CREATE TABLE customers (
    customer_id VARCHAR(12) PRIMARY KEY,
    first_name VARCHAR(40) NOT NULL,
    last_name VARCHAR(40) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    age INTEGER NOT NULL,
    city VARCHAR(40) NOT NULL,
    state VARCHAR(40) NOT NULL,
    income_tier VARCHAR(25) NOT NULL,
    annual_income DECIMAL(12,2) NOT NULL,
    credit_score INTEGER NOT NULL,
    join_date DATE NOT NULL,
    customer_status VARCHAR(15) NOT NULL
);

CREATE TABLE cards (
    card_id VARCHAR(12) PRIMARY KEY,
    customer_id VARCHAR(12) NOT NULL,
    card_type VARCHAR(20) NOT NULL,
    credit_limit DECIMAL(12,2) NOT NULL,
    interest_rate_apr DECIMAL(5,2) NOT NULL,
    issue_date DATE NOT NULL,
    card_status VARCHAR(15) NOT NULL,
    total_revolving_bal DECIMAL(12,2) NOT NULL,
    open_to_buy DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE transactions (
    transaction_id VARCHAR(15) PRIMARY KEY,
    card_id VARCHAR(12) NOT NULL,
    category_id VARCHAR(10) NOT NULL,
    transaction_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_channel VARCHAR(25) NOT NULL,
    transaction_status VARCHAR(15) NOT NULL,
    merchant_name VARCHAR(60) NOT NULL,
    FOREIGN KEY (card_id) REFERENCES cards(card_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);
"""

cursor.executescript(ddl_script)

# Insert Data
df_cat.to_sql("categories", conn, if_exists="append", index=False)
df_cust.to_sql("customers", conn, if_exists="append", index=False)
df_cards.to_sql("cards", conn, if_exists="append", index=False)
df_tx.to_sql("transactions", conn, if_exists="append", index=False)
conn.commit()

print("Tables populated successfully!")

# Define the 10 Production Queries
queries = [
    {
        "id": "Query 1",
        "title": "Executive Portfolio Health & Spend Summary",
        "description": "Calculates core portfolio KPIs: total customers, total cards, approved spend volume, total approved transactions, portfolio average ticket size (ATV), and active vs inactive customer count.",
        "sql": """
SELECT 
    COUNT(DISTINCT c.customer_id) AS total_customers,
    COUNT(DISTINCT cd.card_id) AS total_cards_issued,
    COUNT(t.transaction_id) AS total_transactions,
    ROUND(SUM(CASE WHEN t.transaction_status = 'Approved' THEN t.amount ELSE 0 END), 2) AS total_approved_spend_inr,
    ROUND(AVG(CASE WHEN t.transaction_status = 'Approved' THEN t.amount ELSE NULL END), 2) AS avg_ticket_size_inr,
    COUNT(DISTINCT CASE WHEN c.customer_status = 'Active' THEN c.customer_id END) AS active_customers,
    COUNT(DISTINCT CASE WHEN c.customer_status = 'Inactive' THEN c.customer_id END) AS inactive_customers,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN c.customer_status = 'Inactive' THEN c.customer_id END) / COUNT(DISTINCT c.customer_id), 2) AS inactivity_rate_pct
FROM customers c
LEFT JOIN cards cd ON c.customer_id = cd.customer_id
LEFT JOIN transactions t ON cd.card_id = t.card_id;
"""
    },
    {
        "id": "Query 2",
        "title": "Monthly Spend Trends & Month-over-Month (MoM) Growth using Window Functions",
        "description": "Aggregates spend volume and transaction count by calendar month and utilizes the LAG() window function to calculate Month-over-Month (MoM) spend velocity and growth rates.",
        "sql": """
WITH monthly_metrics AS (
    SELECT 
        STRFTIME('%Y-%m', transaction_date) AS spend_month,
        COUNT(transaction_id) AS tx_count,
        ROUND(SUM(amount), 2) AS monthly_spend_inr,
        ROUND(AVG(amount), 2) AS avg_monthly_ticket_inr
    FROM transactions
    WHERE transaction_status = 'Approved'
    GROUP BY STRFTIME('%Y-%m', transaction_date)
)
SELECT 
    spend_month,
    tx_count,
    monthly_spend_inr,
    avg_monthly_ticket_inr,
    LAG(monthly_spend_inr, 1) OVER (ORDER BY spend_month) AS prev_month_spend_inr,
    ROUND(
        100.0 * (monthly_spend_inr - LAG(monthly_spend_inr, 1) OVER (ORDER BY spend_month)) 
        / LAG(monthly_spend_inr, 1) OVER (ORDER BY spend_month), 
        2
    ) AS mom_growth_pct
FROM monthly_metrics
ORDER BY spend_month;
"""
    },
    {
        "id": "Query 3",
        "title": "Multi-Table 4-Way JOIN: Top 10 High-Value Spenders",
        "description": "Performs an inner join across all 4 tables (customers, cards, transactions, categories) to identify the top 10 most profitable cardholders, their card tier, location, and lifetime spend.",
        "sql": """
SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_full_name,
    c.city,
    c.income_tier,
    cd.card_type,
    cd.credit_limit,
    COUNT(t.transaction_id) AS total_approved_txns,
    ROUND(SUM(t.amount), 2) AS total_customer_spend_inr,
    ROUND(AVG(t.amount), 2) AS avg_spend_per_txn_inr
FROM customers c
JOIN cards cd ON c.customer_id = cd.customer_id
JOIN transactions t ON cd.card_id = t.card_id
JOIN categories cat ON t.category_id = cat.category_id
WHERE t.transaction_status = 'Approved'
GROUP BY c.customer_id, customer_full_name, c.city, c.income_tier, cd.card_type, cd.credit_limit
ORDER BY total_customer_spend_inr DESC
LIMIT 10;
"""
    },
    {
        "id": "Query 4",
        "title": "Category-wise Spend Distribution & Share of Wallet (SoW)",
        "description": "Calculates total spend volume, transaction share, and percentage Share of Wallet for each merchant category using the SUM() OVER() analytic window function.",
        "sql": """
WITH category_aggregates AS (
    SELECT 
        cat.category_id,
        cat.category_name,
        cat.department,
        COUNT(t.transaction_id) AS category_tx_count,
        ROUND(SUM(t.amount), 2) AS total_category_spend_inr,
        ROUND(AVG(t.amount), 2) AS avg_category_ticket_inr
    FROM categories cat
    JOIN transactions t ON cat.category_id = t.category_id
    WHERE t.transaction_status = 'Approved'
    GROUP BY cat.category_id, cat.category_name, cat.department
)
SELECT 
    category_id,
    category_name,
    department,
    category_tx_count,
    total_category_spend_inr,
    avg_category_ticket_inr,
    ROUND(100.0 * total_category_spend_inr / SUM(total_category_spend_inr) OVER(), 2) AS share_of_wallet_pct,
    DENSE_RANK() OVER (ORDER BY total_category_spend_inr DESC) AS spend_rank
FROM category_aggregates
ORDER BY total_category_spend_inr DESC;
"""
    },
    {
        "id": "Query 5",
        "title": "Deep Dive into Inactive Customers & Idle Credit Exposure",
        "description": "Answers 'Who is inactive?' by identifying customers with no transactions in the last 180 days (or no transactions at all), calculating days since last spend and idle sanctioned credit limits.",
        "sql": """
WITH customer_last_activity AS (
    SELECT 
        c.customer_id,
        c.first_name || ' ' || c.last_name AS customer_name,
        c.city,
        c.customer_status,
        cd.card_id,
        cd.card_type,
        cd.credit_limit,
        cd.total_revolving_bal,
        MAX(t.transaction_date) AS latest_tx_date,
        COUNT(t.transaction_id) AS total_lifetime_txns
    FROM customers c
    JOIN cards cd ON c.customer_id = cd.customer_id
    LEFT JOIN transactions t ON cd.card_id = t.card_id AND t.transaction_status = 'Approved'
    GROUP BY c.customer_id, customer_name, c.city, c.customer_status, cd.card_id, cd.card_type, cd.credit_limit, cd.total_revolving_bal
)
SELECT 
    customer_id,
    customer_name,
    city,
    card_type,
    credit_limit AS idle_credit_limit_inr,
    total_revolving_bal,
    COALESCE(latest_tx_date, 'Never Transacted') AS last_spend_date,
    ROUND(JULIANDAY('2025-12-31') - JULIANDAY(COALESCE(latest_tx_date, '2024-07-01'))) AS days_since_last_activity,
    total_lifetime_txns,
    CASE 
        WHEN latest_tx_date IS NULL THEN 'Dormant From Inception'
        WHEN JULIANDAY('2025-12-31') - JULIANDAY(latest_tx_date) > 270 THEN 'Severe Churn (>9 Months Inactive)'
        WHEN JULIANDAY('2025-12-31') - JULIANDAY(latest_tx_date) > 180 THEN 'High Inactivity (6-9 Months Inactive)'
        ELSE 'Moderate Inactivity (3-6 Months)'
    END AS inactivity_severity_tier
FROM customer_last_activity
WHERE latest_tx_date IS NULL OR (JULIANDAY('2025-12-31') - JULIANDAY(latest_tx_date)) >= 180
ORDER BY idle_credit_limit_inr DESC, days_since_last_activity DESC
LIMIT 15;
"""
    },
    {
        "id": "Query 6",
        "title": "Demographic & Income Tier Spending Behavior",
        "description": "Examines spend distributions across income tiers and age segments with HAVING clauses filtering out small sample sizes.",
        "sql": """
SELECT 
    c.income_tier,
    CASE 
        WHEN c.age < 30 THEN '18-29 (Young Professionals)'
        WHEN c.age BETWEEN 30 AND 45 THEN '30-45 (Core Working Class)'
        WHEN c.age BETWEEN 46 AND 60 THEN '46-60 (Mature Affluent)'
        ELSE '60+ (Senior / Retired)'
    END AS age_cohort,
    COUNT(DISTINCT c.customer_id) AS total_customers_in_cohort,
    COUNT(t.transaction_id) AS total_txns,
    ROUND(SUM(t.amount), 2) AS total_spend_inr,
    ROUND(AVG(t.amount), 2) AS avg_ticket_inr,
    ROUND(SUM(t.amount) / COUNT(DISTINCT c.customer_id), 2) AS spend_per_customer_inr
FROM customers c
JOIN cards cd ON c.customer_id = cd.customer_id
JOIN transactions t ON cd.card_id = t.card_id
WHERE t.transaction_status = 'Approved'
GROUP BY c.income_tier, age_cohort
HAVING COUNT(DISTINCT c.customer_id) >= 15
ORDER BY total_spend_inr DESC;
"""
    },
    {
        "id": "Query 7",
        "title": "Card Tier Performance & Credit Utilization Analysis",
        "description": "Compares card tiers (Silver, Gold, Platinum, Signature) on total cards, sanctioned limits, active spend volume, and credit line utilization.",
        "sql": """
SELECT 
    cd.card_type,
    COUNT(DISTINCT cd.card_id) AS total_cards,
    COUNT(DISTINCT CASE WHEN cd.card_status = 'Active' THEN cd.card_id END) AS active_cards,
    COUNT(DISTINCT CASE WHEN cd.card_status IN ('Inactive', 'Blocked') THEN cd.card_id END) AS inactive_cards,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN cd.card_status IN ('Inactive', 'Blocked') THEN cd.card_id END) / COUNT(DISTINCT cd.card_id), 2) AS card_inactivity_rate_pct,
    ROUND(SUM(cd.credit_limit), 2) AS total_sanctioned_credit_inr,
    ROUND(SUM(cd.total_revolving_bal), 2) AS total_revolving_balance_inr,
    ROUND(100.0 * SUM(cd.total_revolving_bal) / SUM(cd.credit_limit), 2) AS revolving_utilization_pct,
    ROUND(SUM(t.amount), 2) AS total_spend_generated_inr,
    ROUND(AVG(t.amount), 2) AS avg_spend_per_txn_inr
FROM cards cd
LEFT JOIN transactions t ON cd.card_id = t.card_id AND t.transaction_status = 'Approved'
GROUP BY cd.card_type
ORDER BY total_spend_generated_inr DESC;
"""
    },
    {
        "id": "Query 8",
        "title": "Customer RFM Segmentation via NTILE() Window Functions",
        "description": "Scores customers on Recency, Frequency, and Monetary value using NTILE(4) quartiles to establish actionable retention cohorts.",
        "sql": """
WITH rfm_base AS (
    SELECT 
        c.customer_id,
        c.first_name || ' ' || c.last_name AS customer_name,
        c.customer_status,
        ROUND(JULIANDAY('2025-12-31') - JULIANDAY(MAX(t.transaction_date))) AS recency_days,
        COUNT(t.transaction_id) AS frequency,
        ROUND(SUM(t.amount), 2) AS monetary_value
    FROM customers c
    JOIN cards cd ON c.customer_id = cd.customer_id
    JOIN transactions t ON cd.card_id = t.card_id
    WHERE t.transaction_status = 'Approved'
    GROUP BY c.customer_id, customer_name, c.customer_status
),
rfm_scores AS (
    SELECT 
        customer_id,
        customer_name,
        customer_status,
        recency_days,
        frequency,
        monetary_value,
        NTILE(4) OVER (ORDER BY recency_days DESC) AS r_score, -- Lower recency days gets higher quartile
        NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary_value ASC) AS m_score
    FROM rfm_base
)
SELECT 
    customer_id,
    customer_name,
    recency_days,
    frequency,
    monetary_value,
    (r_score + f_score + m_score) AS composite_rfm_score,
    CASE 
        WHEN (r_score >= 3 AND f_score >= 3 AND m_score >= 3) THEN 'Champions / VIP High Value'
        WHEN (r_score >= 3 AND f_score >= 2) THEN 'Loyal Active Spenders'
        WHEN (r_score <= 2 AND f_score >= 2) THEN 'At-Risk (High Historical Value, Slipping)'
        ELSE 'Dormant / Churned Low Value'
    END AS rfm_segment
FROM rfm_scores
ORDER BY composite_rfm_score DESC, monetary_value DESC
LIMIT 15;
"""
    },
    {
        "id": "Query 9",
        "title": "Inactivity Early Warning & Credit Exposure Summary",
        "description": "Groups portfolio cardholders into behavioral recency risk buckets and computes total idle credit limits locked in dormant accounts.",
        "sql": """
WITH inactivity_buckets AS (
    SELECT 
        c.customer_id,
        cd.card_id,
        cd.credit_limit,
        ROUND(JULIANDAY('2025-12-31') - JULIANDAY(COALESCE(MAX(t.transaction_date), '2024-07-01'))) AS days_inactive
    FROM customers c
    JOIN cards cd ON c.customer_id = cd.customer_id
    LEFT JOIN transactions t ON cd.card_id = t.card_id AND t.transaction_status = 'Approved'
    GROUP BY c.customer_id, cd.card_id, cd.credit_limit
)
SELECT 
    CASE 
        WHEN days_inactive <= 30 THEN '1. Highly Active (<= 30 Days)'
        WHEN days_inactive BETWEEN 31 AND 90 THEN '2. Moderate Activity (31 - 90 Days)'
        WHEN days_inactive BETWEEN 91 AND 180 THEN '3. Early Inactivity Warning (91 - 180 Days)'
        ELSE '4. Critical Dormancy / Inactive (> 180 Days)'
    END AS inactivity_status_band,
    COUNT(DISTINCT customer_id) AS customer_count,
    COUNT(DISTINCT card_id) AS card_count,
    ROUND(SUM(credit_limit), 2) AS total_sanctioned_limit_inr,
    ROUND(AVG(credit_limit), 2) AS avg_limit_per_card_inr,
    ROUND(100.0 * COUNT(DISTINCT customer_id) / (SELECT COUNT(*) FROM customers), 2) AS customer_pct_share
FROM inactivity_buckets
GROUP BY inactivity_status_band
ORDER BY inactivity_status_band;
"""
    },
    {
        "id": "Query 10",
        "title": "Payment Channel Preference & Average Ticket Size by Category",
        "description": "Calculates spend distribution across POS, Online, Contactless Tap, and ATM channels across all retail categories.",
        "sql": """
SELECT 
    cat.category_name,
    COUNT(t.transaction_id) AS total_transactions,
    ROUND(SUM(t.amount), 2) AS total_spend_inr,
    ROUND(SUM(CASE WHEN t.payment_channel = 'POS Swipe' THEN t.amount ELSE 0 END), 2) AS pos_spend_inr,
    ROUND(SUM(CASE WHEN t.payment_channel = 'Online Payment' THEN t.amount ELSE 0 END), 2) AS online_spend_inr,
    ROUND(SUM(CASE WHEN t.payment_channel = 'Contactless Tap' THEN t.amount ELSE 0 END), 2) AS contactless_spend_inr,
    ROUND(SUM(CASE WHEN t.payment_channel = 'ATM Withdrawal' THEN t.amount ELSE 0 END), 2) AS atm_spend_inr,
    ROUND(100.0 * SUM(CASE WHEN t.payment_channel = 'Online Payment' THEN t.amount ELSE 0 END) / SUM(t.amount), 2) AS online_penetration_pct
FROM categories cat
JOIN transactions t ON cat.category_id = t.category_id
WHERE t.transaction_status = 'Approved'
GROUP BY cat.category_name
ORDER BY total_spend_inr DESC;
"""
    }
]

def df_to_markdown_table(df):
    headers = list(df.columns)
    header_line = "| " + " | ".join(str(h) for h in headers) + " |"
    sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    data_lines = []
    for _, row in df.iterrows():
        row_str = "| " + " | ".join(str(val) if pd.notna(val) else "" for val in row) + " |"
        data_lines.append(row_str)
    return "\n".join([header_line, sep_line] + data_lines)

# Run each query and build output documentation
results_md_path = os.path.join(sql_dir, "SQL_Analysis_Results.md")
raw_sql_path = os.path.join(sql_dir, "credit_card_analysis_queries.sql")

with open(raw_sql_path, "w", encoding="utf-8") as f_sql, open(results_md_path, "w", encoding="utf-8") as f_md:
    f_sql.write("-- =====================================================================\n")
    f_sql.write("-- PROJECT DA-12: CREDIT CARD SPEND & CUSTOMER BEHAVIOUR\n")
    f_sql.write("-- Student Name: Saqhiya Parveen\n")
    f_sql.write("-- Business Question: How do customers spend and who is inactive?\n")
    f_sql.write("-- Production SQL Analysis Script (DDL, Multi-Table Joins, CTEs, Window Functions)\n")
    f_sql.write("-- =====================================================================\n\n")
    f_sql.write(ddl_script)
    f_sql.write("\n\n")

    f_md.write("# DELIVERABLE 3: PRODUCTION SQL ANALYSIS SCRIPT & QUERY RESULTS\n\n")
    f_md.write("**Student Name:** Saqhiya Parveen  \n")
    f_md.write("**Project ID:** DA-12  \n")
    f_md.write("**Project Title:** Credit Card Spend & Customer Behaviour  \n")
    f_md.write("**RDBMS Target:** MySQL / PostgreSQL / SQLite Compatible  \n")
    f_md.write("**Total Analytical Queries:** 10 Production Queries with Joins, CTEs, and Window Functions  \n\n")
    f_md.write("---\n\n")
    f_md.write("## Overview of Relational SQL Architecture\n")
    f_md.write("The database schema connects 4 normalized tables (`categories`, `customers`, `cards`, `transactions`). All queries answer the fundamental business mandate: **How do customers spend across categories, channels, and tiers, and who are the inactive cardholders tying up idle credit exposure?**\n\n")

    for q in queries:
        qid = q["id"]
        title = q["title"]
        desc = q["description"]
        sql_text = q["sql"].strip()

        print(f"Executing {qid}: {title}...")
        df_res = pd.read_sql_query(sql_text, conn)

        # Write to raw SQL file
        f_sql.write(f"-- ---------------------------------------------------------------------\n")
        f_sql.write(f"-- {qid}: {title}\n")
        f_sql.write(f"-- Description: {desc}\n")
        f_sql.write(f"-- ---------------------------------------------------------------------\n")
        f_sql.write(sql_text + ";\n\n")

        # Write to Markdown Results Document
        f_md.write(f"### {qid}: {title}\n\n")
        f_md.write(f"**Business Question / Objective:** {desc}\n\n")
        f_md.write("```sql\n" + sql_text + "\n```\n\n")
        f_md.write(f"**Query Execution Output ({len(df_res)} rows returned):**\n\n")
        f_md.write(df_to_markdown_table(df_res))
        f_md.write("\n\n---\n\n")

conn.close()
print("SQL Analysis execution complete! Saved SQL script and execution outputs.")
