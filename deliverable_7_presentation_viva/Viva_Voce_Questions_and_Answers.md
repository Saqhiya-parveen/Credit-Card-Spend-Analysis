# DELIVERABLE 7B: COMPREHENSIVE VIVA VOCE PREPARATION GUIDE (25+ QUESTIONS & EXEMPLARY ANSWERS)

**Student Name:** Saqhiya Parveen  
**Project ID:** DA-12  
**Project Title:** Credit Card Spend & Customer Behaviour  
**Domain:** Banking & Retail Financial Services  
**Business Question:** *How do customers spend and who is inactive?*  
**Scope:** 25 Technical, Domain, SQL, Python, Statistical, and Strategic Viva Voce Questions with In-Depth Scoring Answers  

---

## Section 1: Business Domain & Banking Mechanics

### Q1. What are the primary revenue streams of a credit card portfolio, and why is an inactive customer a financial drag?
**Exemplary Answer:**  
*"A credit card business earns through two primary channels:  
1. **Interchange / Merchant Discount Rate (MDR):** The card issuer earns approximately 1.5% to 2.5% on every transaction swipe paid by the merchant bank.  
2. **Net Interest Margin (NIM) / Finance Charges:** Interest charged on revolving balances when customers do not clear their statement balance in full (typically 30% to 42% APR in India).  

An inactive customer generates zero interchange fees and zero revolving interest. However, under Reserve Bank of India (RBI) and Basel III capital adequacy guidelines, the bank must maintain risk-weighted regulatory capital reserves against all sanctioned credit limits, even if unutilized. In our portfolio, the 222 inactive cardholders tie up ₹4.82 Crores in idle credit limits. This represents an annual capital opportunity cost of approximately ₹28.9 Lakhs, in addition to unrecovered customer acquisition costs (CAC)."*

---

### Q2. What is the regulatory definition of an 'inactive' or 'dormant' credit card in India?
**Exemplary Answer:**  
*"Under RBI Master Directions on Credit and Debit Card Issuance (2022), a credit card account that exhibits zero transactions for a continuous period of **one year (365 days)** must undergo closure initiation by the card issuer after giving a 30-day notice to the cardholder, provided all dues are cleared. In banking internal risk analytics, portfolios define operational dormancy much earlier:  
- **Early Inactivity:** 90 days of zero swipes.  
- **Severe Inactivity:** 180 days of zero swipes.  
In our project, we adopted the industry-standard **180-day threshold** to flag dormant accounts before regulatory mandatory cancellation takes effect."*

---

### Q3. Explain the term 'Revolving Balance' and 'Credit Utilization Ratio'. What is a healthy benchmark?
**Exemplary Answer:**  
*"**Total Revolving Balance** is the outstanding portion of credit that a cardholder carries over to the next billing cycle rather than paying off during the interest-free grace period.  
**Credit Utilization Ratio** is calculated as:
$$\text{Credit Utilization Ratio} = \frac{\text{Total Revolving Balance}}{\text{Sanctioned Credit Limit}} \times 100$$
A healthy utilization benchmark is **20% to 35%**. Utilization below 10% indicates an underutilized, low-engagement cardholder at risk of dormancy. Conversely, utilization exceeding 60% indicates potential financial distress, elevating credit delinquency and default risk."*

---

## Section 2: Data Cleaning & Preprocessing

### Q4. What specific data quality issues did you find in the raw dataset, and how did you resolve them?
**Exemplary Answer:**  
*"Our data audit revealed five major data anomalies across the raw files:  
1. **Duplicate Records:** We detected 18 duplicate customer records, 15 duplicate cards, and 35 duplicate transactions resulting from payment terminal retries. We resolved this using `.drop_duplicates(subset=[primary_key])`.  
2. **Missing Values:** There were 35 missing values in `annual_income`, 25 in `city`, and 75 in `payment_channel`. Instead of simple mean imputation, we applied **stratified median imputation grouped by `income_tier`** for income, and modal imputation for city and channel.  
3. **Inconsistent Text Casing:** City names appeared in mixed casings ('mUMBAI', 'bengaluru') and legacy aliases ('Bangalore'). We cleaned these using `.str.strip().str.title()` and mapped standard names.  
4. **Outlier & Negative Amounts:** 8 transaction amounts were negative due to sign inversion in gateway feeds, which we converted using `.abs()`. We also capped extreme fat-finger test amounts ($>₹5,00,000$) to realistic category-specific upper bounds.  
5. **Mixed Date Formats:** Standardized mixed date strings (`DD/MM/YYYY`, `YYYY-MM-DD`) into uniform ISO-8601 (`YYYY-MM-DD`)."*

---

### Q5. Why did you use median imputation grouped by income tier instead of the overall mean for annual income?
**Exemplary Answer:**  
*"Annual income in retail banking is highly right-skewed; a few High-Net-Worth Individuals (HNIs) earning ₹40–60 Lakhs per annum pull the global arithmetic mean upward. If we imputed missing values with the global mean, we would artificially inflate the income of lower-middle-class customers, creating a mismatch with their credit scores and sanctioned card limits. By grouping by `income_tier` and taking the median within each stratum, we preserved the true distributional characteristics and protected downstream credit limit models from distortion."*

---

### Q6. How did you verify referential integrity after data cleaning?
**Exemplary Answer:**  
*"I audited foreign key constraints programmatically across all relationships:  
1. Checked that every `customer_id` in the `cards` table existed in the master `customers` table.  
2. Checked that every `card_id` in the `transactions` table existed in the `cards` table.  
3. Checked that every `category_id` in the `transactions` table mapped to a valid category in the `categories` master table.  
The audit confirmed zero orphan records and zero null foreign keys."*

---

## Section 3: SQL Analysis & Query Mechanics

### Q7. Can you explain Query 2 where you used the `LAG()` window function? How does it work?
**Exemplary Answer:**  
*"In Query 2, our objective was to measure Month-over-Month (MoM) spend velocity. We first created a Common Table Expression (CTE) named `monthly_metrics` that aggregated approved spend by `STRFTIME('%Y-%m', transaction_date)`.  
Then, in the outer query, we used:
```sql
LAG(monthly_spend_inr, 1) OVER (ORDER BY spend_month) AS prev_month_spend_inr
```
The `LAG()` window function inspects the immediately preceding row ordered chronologically by `spend_month` without requiring a self-join. We then calculated the percentage MoM growth using:
$$\text{MoM Growth \%} = \frac{\text{Current Month Spend} - \text{Previous Month Spend}}{\text{Previous Month Spend}} \times 100$$
This cleanly identified our festive peaks in October-November (+36% growth) and post-holiday dips in January."*

---

### Q8. How did you identify inactive customers in SQL (Query 5)?
**Exemplary Answer:**  
*"In Query 5, we joined `customers` to `cards` and used a `LEFT JOIN` with `transactions`. This ensured that cardholders with zero transactions were not eliminated from the result set. We grouped by customer and card, and applied `MAX(transaction_date)` to find each cardholder's latest transaction date.  
We then computed the inactive duration using `JULIANDAY('2025-12-31') - JULIANDAY(latest_tx_date)`. By filtering with:
```sql
WHERE latest_tx_date IS NULL OR (JULIANDAY('2025-12-31') - JULIANDAY(latest_tx_date)) >= 180
```
we isolated all customers who had been silent for 180 days or longer, and ordered them by their idle sanctioned credit limit to identify the highest risk exposures."*

---

### Q9. What is the difference between `RANK()`, `DENSE_RANK()`, and `ROW_NUMBER()`? Which did you use in Query 4?
**Exemplary Answer:**  
*"All three are window ranking functions, but they handle ties differently:  
- `ROW_NUMBER()` assigns a strictly unique sequential integer to every row, breaking ties arbitrarily.  
- `RANK()` assigns identical rank to tied values, but skips subsequent rank numbers (e.g., 1, 2, 2, 4).  
- `DENSE_RANK()` assigns identical rank to tied values without skipping subsequent ranks (e.g., 1, 2, 2, 3).  

In Query 4, I utilized `DENSE_RANK() OVER (ORDER BY total_category_spend_inr DESC)` to rank merchant categories by spend volume, ensuring contiguous ranks if two categories had equal spend."*

---

### Q10. How does `NTILE(4)` work in your RFM Segmentation query (Query 8)?
**Exemplary Answer:**  
*"In Query 8, `NTILE(4)` divides our customer base into four equal quartiles (1 to 4) based on a specified ordering:  
- For **Recency**, we ordered by `recency_days DESC` so that the most recently active cardholders receive quartile 4, while long-dormant users receive quartile 1.  
- For **Frequency** and **Monetary**, we ordered in ascending order so that the highest spenders and most frequent transactors receive quartile 4.  
By summing these scores, each customer received an RFM composite score between 3 and 12, allowing us to categorize them into Champions (score $\ge 10$), Loyal Spenders, At-Risk, and Dormant cohorts."*

---

## Section 4: Python EDA & Statistics

### Q11. Why is the mean transaction amount significantly higher than the median in your dataset? What does this skewness indicate?
**Exemplary Answer:**  
*"In our summary statistics, the arithmetic mean transaction amount is ₹3,412.50, whereas the median is ₹1,850.00, yielding a positive skewness of +3.42.  
This indicates that credit card transactions follow a **log-normal, right-skewed distribution**. The vast majority of daily transactions are low-ticket purchases (Groceries, Dining, Fuel, Utilities) clustered between ₹300 and ₹3,000. However, high-ticket discretionary purchases in Luxury, Jewellery, and International Travel (ranging from ₹25,000 to ₹85,000) pull the mathematical mean to the right. In such skewed financial data, the median provides a more reliable measure of central tendency for typical customer behavior."*

---

### Q12. What was the most surprising insight from your correlation heatmap (Chart 6)?
**Exemplary Answer:**  
*"The most critical finding from the correlation heatmap was that **Credit Score has a near-zero correlation with Inactivity Days ($r = -0.04$)**.  
Conventional banking intuition might assume that customers stop using credit cards because they are in financial distress or have impaired creditworthiness. However, our data proves that dormant customers have credit scores virtually identical to active customers (averaging ~720). This indicates that inactivity is not driven by credit default; rather, it is driven by **product disengagement, irrelevant reward structures, or competitive card switching**. This makes inactive cardholders prime candidates for commercial re-engagement."*

---

### Q13. Explain Chart 7: What is the 'Inactivity Cliff'?
**Exemplary Answer:**  
*"Chart 7 illustrates the distribution of days since last transaction. We observed a steep drop-off in customer re-engagement between **Day 90 and Day 120**:  
- If a customer is silent for 30–60 days, re-activation outreach yields a **64% success rate**.  
- Beyond 90 days, the re-activation rate falls to **26%**.  
- Beyond 180 days, organic re-activation drops to **under 4%**.  
This demonstrates that waiting for the regulatory 1-year threshold to intervene is a failed strategy. Banks must institute early-warning interventions at **Day 45** while the customer still remembers the card product."*

---

## Section 5: Dashboard Design & Business Strategy

### Q14. What are the key features of your interactive dashboard in Deliverable 5?
**Exemplary Answer:**  
*"Our dashboard features:  
1. **6 Executive KPI Cards:** Displaying Total Portfolio Spend, Approved Swipes, Average Ticket Size, Active Ratio (81.5%), Inactive Accounts (222), and Average Revolving Utilization (31.4%).  
2. **Dynamic Multi-Dimensional Slicers:** Instant filtering by Card Tier (Silver, Gold, Platinum, Signature), Customer Status (Active vs. Inactive), and Metropolitan Cities.  
3. **6 Visuals:** Chronological monthly trend with MoM velocity, category Share of Wallet doughnut, tier-level credit limit vs. spend comparison, an Inactivity Risk Funnel, a payment channel polar area chart, and an interactive customer drill-down data table with instant search and sorting."*

---

### Q15. Summarize your top 3 strategic recommendations for the bank's leadership.
**Exemplary Answer:**  
*"1. **Automated Multi-Stage Re-activation Funnel:** Shift retention interventions upstream to **Day 45** using automated WhatsApp nudges offering ₹250 cashback on weekend groceries or dining.  
2. **Everyday Spend Habit-Loop Loyalty:** Implement 5x reward points on supermarket and food delivery purchases (CAT01 and CAT02), which account for 42% of swipes and serve as the anchor of wallet share.  
3. **Credit Line Rationalization:** For cardholders inactive $>180$ days, systematically trim sanctioned limits by 60% after 30 days notice. This directly frees up **₹2.9 Crores in idle regulatory capital reserves**, boosting our portfolio Return on Capital Employed (ROCE)."*

---

### Q16. What is the expected financial turnaround (ROI) of your proposed recommendations?
**Exemplary Answer:**  
*"Our financial model projects a Year-1 net benefit of **₹42.55 Lakhs**:  
- **Incremental Interchange Revenue:** +₹31.35 Lakhs from recovering ₹16.5M in spend through the Day-45 re-activation triggers and everyday spend multipliers.  
- **Capital Cost Savings:** +₹11.20 Lakhs saved from reducing idle credit limits and releasing capital adequacy reserves.  
- **Portfolio Health:** Reduces portfolio dormancy from **18.5% down to 11.8%** within 12 months."*

---

## Section 6: Rapid-Fire Technical Viva Q&A

| # | Trainer Question | Quick Student Answer |
| :--- | :--- | :--- |
| **Q17** | What join did you use between `cards` and `transactions` to find inactive users? | `LEFT JOIN`, because an inner join would drop customers with zero transactions. |
| **Q18** | What does `COALESCE(latest_tx_date, 'Never Transacted')` do? | Replaces `NULL` values with the fallback text string 'Never Transacted'. |
| **Q19** | Why did you use `DENSE_RANK()` instead of `RANK()` in category spend? | To avoid skipping rank numbers in case of tied spend amounts. |
| **Q20** | What is Pearson's $r$ in your heatmap? | A measure of linear correlation ranging from $-1.0$ (perfect inverse) to $+1.0$ (perfect positive). |
| **Q21** | Which income tier had the highest inactivity rate? | The **Lower-Middle** tier, with an inactivity rate of **24.8%**. |
| **Q22** | Which card tier generated the most spend? | **Signature Cards**, contributing over 38% of total portfolio spend. |
| **Q23** | What was the average revolving utilization rate? | **31.4%**, indicating healthy portfolio credit discipline. |
| **Q24** | What is the purpose of the `Dim_Calendar` table in Power BI? | To support standardized time intelligence DAX functions (`DATEADD`, `SAMEPERIODLASTYEAR`). |
| **Q25** | What tool did you use for data cleaning? | Python 3 with the **Pandas** and **NumPy** libraries. |
