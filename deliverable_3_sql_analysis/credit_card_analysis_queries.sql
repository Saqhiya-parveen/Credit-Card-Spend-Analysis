-- =====================================================================
-- PROJECT DA-12: CREDIT CARD SPEND & CUSTOMER BEHAVIOUR
-- Student Name: Saqhiya Parveen
-- Business Question: How do customers spend and who is inactive?
-- Production SQL Analysis Script (DDL, Multi-Table Joins, CTEs, Window Functions)
-- =====================================================================


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


-- ---------------------------------------------------------------------
-- Query 1: Executive Portfolio Health & Spend Summary
-- Description: Calculates core portfolio KPIs: total customers, total cards, approved spend volume, total approved transactions, portfolio average ticket size (ATV), and active vs inactive customer count.
-- ---------------------------------------------------------------------
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
LEFT JOIN transactions t ON cd.card_id = t.card_id;;

-- ---------------------------------------------------------------------
-- Query 2: Monthly Spend Trends & Month-over-Month (MoM) Growth using Window Functions
-- Description: Aggregates spend volume and transaction count by calendar month and utilizes the LAG() window function to calculate Month-over-Month (MoM) spend velocity and growth rates.
-- ---------------------------------------------------------------------
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
ORDER BY spend_month;;

-- ---------------------------------------------------------------------
-- Query 3: Multi-Table 4-Way JOIN: Top 10 High-Value Spenders
-- Description: Performs an inner join across all 4 tables (customers, cards, transactions, categories) to identify the top 10 most profitable cardholders, their card tier, location, and lifetime spend.
-- ---------------------------------------------------------------------
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
LIMIT 10;;

-- ---------------------------------------------------------------------
-- Query 4: Category-wise Spend Distribution & Share of Wallet (SoW)
-- Description: Calculates total spend volume, transaction share, and percentage Share of Wallet for each merchant category using the SUM() OVER() analytic window function.
-- ---------------------------------------------------------------------
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
ORDER BY total_category_spend_inr DESC;;

-- ---------------------------------------------------------------------
-- Query 5: Deep Dive into Inactive Customers & Idle Credit Exposure
-- Description: Answers 'Who is inactive?' by identifying customers with no transactions in the last 180 days (or no transactions at all), calculating days since last spend and idle sanctioned credit limits.
-- ---------------------------------------------------------------------
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
LIMIT 15;;

-- ---------------------------------------------------------------------
-- Query 6: Demographic & Income Tier Spending Behavior
-- Description: Examines spend distributions across income tiers and age segments with HAVING clauses filtering out small sample sizes.
-- ---------------------------------------------------------------------
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
ORDER BY total_spend_inr DESC;;

-- ---------------------------------------------------------------------
-- Query 7: Card Tier Performance & Credit Utilization Analysis
-- Description: Compares card tiers (Silver, Gold, Platinum, Signature) on total cards, sanctioned limits, active spend volume, and credit line utilization.
-- ---------------------------------------------------------------------
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
ORDER BY total_spend_generated_inr DESC;;

-- ---------------------------------------------------------------------
-- Query 8: Customer RFM Segmentation via NTILE() Window Functions
-- Description: Scores customers on Recency, Frequency, and Monetary value using NTILE(4) quartiles to establish actionable retention cohorts.
-- ---------------------------------------------------------------------
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
LIMIT 15;;

-- ---------------------------------------------------------------------
-- Query 9: Inactivity Early Warning & Credit Exposure Summary
-- Description: Groups portfolio cardholders into behavioral recency risk buckets and computes total idle credit limits locked in dormant accounts.
-- ---------------------------------------------------------------------
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
ORDER BY inactivity_status_band;;

-- ---------------------------------------------------------------------
-- Query 10: Payment Channel Preference & Average Ticket Size by Category
-- Description: Calculates spend distribution across POS, Online, Contactless Tap, and ATM channels across all retail categories.
-- ---------------------------------------------------------------------
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
ORDER BY total_spend_inr DESC;;

