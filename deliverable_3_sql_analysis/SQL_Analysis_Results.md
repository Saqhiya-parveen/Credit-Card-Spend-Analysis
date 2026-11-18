# DELIVERABLE 3: PRODUCTION SQL ANALYSIS SCRIPT & QUERY RESULTS

**Student Name:** Saqhiya Parveen  
**Project ID:** DA-12  
**Project Title:** Credit Card Spend & Customer Behaviour  
**RDBMS Target:** MySQL / PostgreSQL / SQLite Compatible  
**Total Analytical Queries:** 10 Production Queries with Joins, CTEs, and Window Functions  

---

## Overview of Relational SQL Architecture
The database schema connects 4 normalized tables (`categories`, `customers`, `cards`, `transactions`). All queries answer the fundamental business mandate: **How do customers spend across categories, channels, and tiers, and who are the inactive cardholders tying up idle credit exposure?**

### Query 1: Executive Portfolio Health & Spend Summary

**Business Question / Objective:** Calculates core portfolio KPIs: total customers, total cards, approved spend volume, total approved transactions, portfolio average ticket size (ATV), and active vs inactive customer count.

```sql
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
```

**Query Execution Output (1 rows returned):**

| total_customers | total_cards_issued | total_transactions | total_approved_spend_inr | avg_ticket_size_inr | active_customers | inactive_customers | inactivity_rate_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1200.0 | 1480.0 | 21469.0 | 132317399.14 | 6551.99 | 963.0 | 237.0 | 19.75 |

---

### Query 2: Monthly Spend Trends & Month-over-Month (MoM) Growth using Window Functions

**Business Question / Objective:** Aggregates spend volume and transaction count by calendar month and utilizes the LAG() window function to calculate Month-over-Month (MoM) spend velocity and growth rates.

```sql
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
```

**Query Execution Output (18 rows returned):**

| spend_month | tx_count | monthly_spend_inr | avg_monthly_ticket_inr | prev_month_spend_inr | mom_growth_pct |
| --- | --- | --- | --- | --- | --- |
| 2024-07 | 1205 | 7550867.74 | 6266.28 |  |  |
| 2024-08 | 1239 | 7781207.57 | 6280.23 | 7550867.74 | 3.05 |
| 2024-09 | 1262 | 8292129.17 | 6570.63 | 7781207.57 | 6.57 |
| 2024-10 | 1180 | 7150652.81 | 6059.88 | 8292129.17 | -13.77 |
| 2024-11 | 1106 | 6604995.73 | 5971.97 | 7150652.81 | -7.63 |
| 2024-12 | 1134 | 8208255.12 | 7238.32 | 6604995.73 | 24.27 |
| 2025-01 | 1123 | 7615707.15 | 6781.57 | 8208255.12 | -7.22 |
| 2025-02 | 1029 | 6975810.79 | 6779.21 | 7615707.15 | -8.4 |
| 2025-03 | 1095 | 7308228.16 | 6674.18 | 6975810.79 | 4.77 |
| 2025-04 | 1082 | 7845113.29 | 7250.57 | 7308228.16 | 7.35 |
| 2025-05 | 1101 | 6921439.52 | 6286.5 | 7845113.29 | -11.77 |
| 2025-06 | 1086 | 7379316.99 | 6794.95 | 6921439.52 | 6.62 |
| 2025-07 | 1084 | 7166652.43 | 6611.3 | 7379316.99 | -2.88 |
| 2025-08 | 1107 | 7058746.59 | 6376.46 | 7166652.43 | -1.51 |
| 2025-09 | 1050 | 7240169.01 | 6895.4 | 7058746.59 | 2.57 |
| 2025-10 | 1127 | 7546652.75 | 6696.23 | 7240169.01 | 4.23 |
| 2025-11 | 1101 | 6859643.56 | 6230.38 | 7546652.75 | -9.1 |
| 2025-12 | 1084 | 6811810.76 | 6283.96 | 6859643.56 | -0.7 |

---

### Query 3: Multi-Table 4-Way JOIN: Top 10 High-Value Spenders

**Business Question / Objective:** Performs an inner join across all 4 tables (customers, cards, transactions, categories) to identify the top 10 most profitable cardholders, their card tier, location, and lifetime spend.

```sql
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
```

**Query Execution Output (10 rows returned):**

| customer_id | customer_full_name | city | income_tier | card_type | credit_limit | total_approved_txns | total_customer_spend_inr | avg_spend_per_txn_inr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CUST01069 | Aarti Khan | Bengaluru | Lower-Middle | Silver | 143000 | 41 | 357135.36 | 8710.62 |
| CUST00519 | Praveen Gupta | Ahmedabad | Upper-Middle | Signature | 1016000 | 25 | 342765.94 | 13710.64 |
| CUST00355 | Deepak Singh | Pune | Middle | Gold | 349000 | 21 | 312809.16 | 14895.67 |
| CUST00076 | Vikram Kulkarni | Bengaluru | Middle | Silver | 122000 | 25 | 303186.73 | 12127.47 |
| CUST00931 | Swati Singh | Lucknow | Middle | Silver | 109000 | 24 | 301356.63 | 12556.53 |
| CUST00709 | Siddharth Khan | Chennai | High-Net-Worth | Signature | 1749000 | 26 | 295503.42 | 11365.52 |
| CUST00616 | Manish Mehta | Kolkata | Middle | Silver | 74000 | 23 | 287787.81 | 12512.51 |
| CUST01200 | Kunal Reddy | Kolkata | High-Net-Worth | Signature | 1044000 | 17 | 284297.54 | 16723.38 |
| CUST00702 | Aarav Joshi | Mumbai | Lower-Middle | Gold | 324000 | 21 | 276252.04 | 13154.86 |
| CUST01057 | Ritu Khan | Kolkata | Upper-Middle | Platinum | 465000 | 22 | 275668.5 | 12530.39 |

---

### Query 4: Category-wise Spend Distribution & Share of Wallet (SoW)

**Business Question / Objective:** Calculates total spend volume, transaction share, and percentage Share of Wallet for each merchant category using the SUM() OVER() analytic window function.

```sql
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
```

**Query Execution Output (10 rows returned):**

| category_id | category_name | department | category_tx_count | total_category_spend_inr | avg_category_ticket_inr | share_of_wallet_pct | spend_rank |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CAT04 | Electronics & Gadgets | Electronics | 1774 | 42354060.09 | 23874.89 | 32.01 | 1 |
| CAT03 | Travel & Airlines | Travel | 1617 | 28628089.54 | 17704.45 | 21.64 | 2 |
| CAT10 | Jewellery & Luxury | Luxury | 355 | 17417605.46 | 49063.68 | 13.16 | 3 |
| CAT01 | Groceries & Supermarket | Retail | 4828 | 12395870.68 | 2567.5 | 9.37 | 4 |
| CAT02 | Dining & Restaurants | Food & Beverage | 3602 | 7490422.54 | 2079.52 | 5.66 | 5 |
| CAT05 | Utilities & Bill Pay | Bills | 2466 | 7254092.67 | 2941.64 | 5.48 | 6 |
| CAT09 | Fashion & Apparel | Retail | 961 | 6149590.68 | 6399.16 | 4.65 | 7 |
| CAT06 | Fuel & Transportation | Transport | 2336 | 5220741.26 | 2234.91 | 3.95 | 8 |
| CAT07 | Healthcare & Pharmacy | Medical | 1219 | 4127693.81 | 3386.13 | 3.12 | 9 |
| CAT08 | Entertainment & Movies | Leisure | 1037 | 1279232.41 | 1233.59 | 0.97 | 10 |

---

### Query 5: Deep Dive into Inactive Customers & Idle Credit Exposure

**Business Question / Objective:** Answers 'Who is inactive?' by identifying customers with no transactions in the last 180 days (or no transactions at all), calculating days since last spend and idle sanctioned credit limits.

```sql
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
```

**Query Execution Output (15 rows returned):**

| customer_id | customer_name | city | card_type | idle_credit_limit_inr | total_revolving_bal | last_spend_date | days_since_last_activity | total_lifetime_txns | inactivity_severity_tier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CUST01183 | Arjun Joshi | Lucknow | Signature | 1779000 | 134236.58 | 2024-08-04 | 514.0 | 1 | Severe Churn (>9 Months Inactive) |
| CUST01016 | Praveen Khan | Jaipur | Signature | 1769000 | 362921.83 | 2025-04-20 | 255.0 | 11 | High Inactivity (6-9 Months Inactive) |
| CUST00388 | Swati Kulkarni | Hyderabad | Signature | 1765000 | 1350655.55 | 2024-11-13 | 413.0 | 4 | Severe Churn (>9 Months Inactive) |
| CUST00017 | Manish Reddy | Chennai | Signature | 1729000 | 51777.54 | 2024-11-25 | 401.0 | 4 | Severe Churn (>9 Months Inactive) |
| CUST00936 | Swati Iyer | Lucknow | Signature | 1724000 | 86334.12 | 2024-10-25 | 432.0 | 2 | Severe Churn (>9 Months Inactive) |
| CUST00085 | Meera Sharma | Jaipur | Signature | 1677000 | 156115.38 | 2024-10-26 | 431.0 | 4 | Severe Churn (>9 Months Inactive) |
| CUST00094 | Vikram Mehta | Lucknow | Signature | 1671000 | 223848.85 | 2024-08-23 | 495.0 | 1 | Severe Churn (>9 Months Inactive) |
| CUST00334 | Shreya Reddy | Delhi | Signature | 1640000 | 170994.54 | 2024-11-05 | 421.0 | 3 | Severe Churn (>9 Months Inactive) |
| CUST00581 | Sneha Iyer | Ahmedabad | Signature | 1633000 | 197529.91 | Never Transacted | 548.0 | 0 | Dormant From Inception |
| CUST00676 | Aarti Das | Mumbai | Signature | 1618000 | 157228.36 | Never Transacted | 548.0 | 0 | Dormant From Inception |
| CUST00940 | Nikhil Bose | Kolkata | Signature | 1572000 | 68911.01 | Never Transacted | 548.0 | 0 | Dormant From Inception |
| CUST00840 | Ritu Rao | Bengaluru | Signature | 1557000 | 181202.61 | Never Transacted | 548.0 | 0 | Dormant From Inception |
| CUST01150 | Arjun Singh | Ahmedabad | Signature | 1499000 | 139079.87 | 2024-11-21 | 405.0 | 3 | Severe Churn (>9 Months Inactive) |
| CUST00046 | Siddharth Khan | Delhi | Signature | 1484000 | 109479.26 | Never Transacted | 548.0 | 0 | Dormant From Inception |
| CUST00345 | Kavita Kulkarni | Pune | Signature | 1470000 | 32526.83 | 2024-11-05 | 421.0 | 3 | Severe Churn (>9 Months Inactive) |

---

### Query 6: Demographic & Income Tier Spending Behavior

**Business Question / Objective:** Examines spend distributions across income tiers and age segments with HAVING clauses filtering out small sample sizes.

```sql
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
```

**Query Execution Output (12 rows returned):**

| income_tier | age_cohort | total_customers_in_cohort | total_txns | total_spend_inr | avg_ticket_inr | spend_per_customer_inr |
| --- | --- | --- | --- | --- | --- | --- |
| Middle | 30-45 (Core Working Class) | 283 | 4964 | 32995398.43 | 6646.94 | 116591.51 |
| Upper-Middle | 30-45 (Core Working Class) | 146 | 2618 | 17852708.17 | 6819.22 | 122278.82 |
| Lower-Middle | 30-45 (Core Working Class) | 127 | 2264 | 14407120.98 | 6363.57 | 113441.9 |
| Middle | 46-60 (Mature Affluent) | 110 | 1930 | 12949381.04 | 6709.52 | 117721.65 |
| Middle | 18-29 (Young Professionals) | 111 | 1999 | 12572153.61 | 6289.22 | 113262.65 |
| High-Net-Worth | 30-45 (Core Working Class) | 64 | 1249 | 8762603.05 | 7015.69 | 136915.67 |
| Upper-Middle | 46-60 (Mature Affluent) | 71 | 1206 | 7829866.98 | 6492.43 | 110279.82 |
| Lower-Middle | 46-60 (Mature Affluent) | 57 | 1184 | 7283799.94 | 6151.86 | 127785.96 |
| Upper-Middle | 18-29 (Young Professionals) | 43 | 861 | 5565827.11 | 6464.38 | 129437.84 |
| Lower-Middle | 18-29 (Young Professionals) | 34 | 597 | 3753534.49 | 6287.33 | 110398.07 |
| High-Net-Worth | 46-60 (Mature Affluent) | 25 | 405 | 2742601.75 | 6771.86 | 109704.07 |
| High-Net-Worth | 18-29 (Young Professionals) | 21 | 375 | 2392554.45 | 6380.15 | 113931.16 |

---

### Query 7: Card Tier Performance & Credit Utilization Analysis

**Business Question / Objective:** Compares card tiers (Silver, Gold, Platinum, Signature) on total cards, sanctioned limits, active spend volume, and credit line utilization.

```sql
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
```

**Query Execution Output (4 rows returned):**

| card_type | total_cards | active_cards | inactive_cards | card_inactivity_rate_pct | total_sanctioned_credit_inr | total_revolving_balance_inr | revolving_utilization_pct | total_spend_generated_inr | avg_spend_per_txn_inr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Gold | 522 | 407 | 115 | 22.03 | 1964203000.0 | 733913702.12 | 37.36 | 46490806.87 | 6529.61 |
| Silver | 411 | 328 | 83 | 20.19 | 570770000.0 | 221483753.06 | 38.8 | 35866687.05 | 6464.8 |
| Platinum | 348 | 273 | 75 | 21.55 | 2831325000.0 | 1111734727.44 | 39.27 | 31078232.96 | 6591.35 |
| Signature | 199 | 159 | 40 | 20.1 | 3638984000.0 | 1352971352.27 | 37.18 | 18881672.26 | 6714.68 |

---

### Query 8: Customer RFM Segmentation via NTILE() Window Functions

**Business Question / Objective:** Scores customers on Recency, Frequency, and Monetary value using NTILE(4) quartiles to establish actionable retention cohorts.

```sql
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
```

**Query Execution Output (15 rows returned):**

| customer_id | customer_name | recency_days | frequency | monetary_value | composite_rfm_score | rfm_segment |
| --- | --- | --- | --- | --- | --- | --- |
| CUST00561 | Ananya Rao | 2.0 | 44 | 399967.56 | 12 | Champions / VIP High Value |
| CUST00066 | Aarti Patel | 0.0 | 47 | 389187.24 | 12 | Champions / VIP High Value |
| CUST00533 | Suresh Nair | 0.0 | 47 | 374911.45 | 12 | Champions / VIP High Value |
| CUST00493 | Manish Kulkarni | 6.0 | 46 | 373223.1 | 12 | Champions / VIP High Value |
| CUST00548 | Suresh Nair | 1.0 | 46 | 368014.84 | 12 | Champions / VIP High Value |
| CUST00622 | Manish Sharma | 1.0 | 46 | 367506.53 | 12 | Champions / VIP High Value |
| CUST01129 | Siddharth Choudhury | 7.0 | 43 | 346901.59 | 12 | Champions / VIP High Value |
| CUST00093 | Rahul Kulkarni | 1.0 | 45 | 342508.97 | 12 | Champions / VIP High Value |
| CUST00792 | Aarav Kulkarni | 7.0 | 43 | 342242.78 | 12 | Champions / VIP High Value |
| CUST00040 | Swati Iyer | 9.0 | 34 | 340773.34 | 12 | Champions / VIP High Value |
| CUST00601 | Aarav Iyer | 7.0 | 39 | 340236.27 | 12 | Champions / VIP High Value |
| CUST00640 | Vikram Verma | 0.0 | 48 | 338244.36 | 12 | Champions / VIP High Value |
| CUST01000 | Priya Verma | 0.0 | 47 | 333920.95 | 12 | Champions / VIP High Value |
| CUST00444 | Vikram Gupta | 2.0 | 51 | 333762.96 | 12 | Champions / VIP High Value |
| CUST00337 | Aditya Singh | 1.0 | 26 | 318066.35 | 12 | Champions / VIP High Value |

---

### Query 9: Inactivity Early Warning & Credit Exposure Summary

**Business Question / Objective:** Groups portfolio cardholders into behavioral recency risk buckets and computes total idle credit limits locked in dormant accounts.

```sql
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
```

**Query Execution Output (4 rows returned):**

| inactivity_status_band | customer_count | card_count | total_sanctioned_limit_inr | avg_limit_per_card_inr | customer_pct_share |
| --- | --- | --- | --- | --- | --- |
| 1. Highly Active (<= 30 Days) | 605 | 675 | 289546000.0 | 428957.04 | 50.42 |
| 2. Moderate Activity (31 - 90 Days) | 370 | 394 | 181312000.0 | 460182.74 | 30.83 |
| 3. Early Inactivity Warning (91 - 180 Days) | 91 | 92 | 40888000.0 | 444434.78 | 7.58 |
| 4. Critical Dormancy / Inactive (> 180 Days) | 278 | 319 | 138818000.0 | 435166.14 | 23.17 |

---

### Query 10: Payment Channel Preference & Average Ticket Size by Category

**Business Question / Objective:** Calculates spend distribution across POS, Online, Contactless Tap, and ATM channels across all retail categories.

```sql
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
```

**Query Execution Output (10 rows returned):**

| category_name | total_transactions | total_spend_inr | pos_spend_inr | online_spend_inr | contactless_spend_inr | atm_spend_inr | online_penetration_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Electronics & Gadgets | 1774 | 42354060.09 | 20164342.23 | 16398152.61 | 4794537.96 | 997027.29 | 38.72 |
| Travel & Airlines | 1617 | 28628089.54 | 13200735.3 | 11204930.16 | 3325433.4 | 896990.68 | 39.14 |
| Jewellery & Luxury | 355 | 17417605.46 | 8496718.21 | 6285731.51 | 2006700.17 | 628455.57 | 36.09 |
| Groceries & Supermarket | 4828 | 12395870.68 | 5464556.48 | 4960946.49 | 1613007.06 | 357360.65 | 40.02 |
| Dining & Restaurants | 3602 | 7490422.54 | 3535436.09 | 2841083.48 | 906643.43 | 207259.54 | 37.93 |
| Utilities & Bill Pay | 2466 | 7254092.67 | 3334080.76 | 2850289.46 | 900949.69 | 168772.76 | 39.29 |
| Fashion & Apparel | 961 | 6149590.68 | 2696721.64 | 2621026.32 | 663900.81 | 167941.91 | 42.62 |
| Fuel & Transportation | 2336 | 5220741.26 | 2332553.46 | 2135633.08 | 581434.88 | 171119.84 | 40.91 |
| Healthcare & Pharmacy | 1219 | 4127693.81 | 1808595.91 | 1613080.4 | 549625.0 | 156392.5 | 39.08 |
| Entertainment & Movies | 1037 | 1279232.41 | 586113.3 | 482860.25 | 158289.52 | 51969.34 | 37.75 |

---

