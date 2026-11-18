# DELIVERABLE 2: DATA CLEANING & PREPARATION REPORT

**Student Name:** Saqhiya Parveen  
**Project ID:** DA-12  
**Project Title:** Credit Card Spend & Customer Behaviour  
**Tool Utilized:** Python (Pandas, NumPy, Datetime)  
**Evaluation Focus:** Data Quality Audit, Issues Identified & Fixed with Technical Reasons, Before/After Row Counts

---

## 1. Executive Summary of Data Quality Audit

A robust credit card portfolio analysis requires uncompromising data cleanliness and integrity. The raw datasets exhibited typical real-world transactional anomalies: redundant records from network re-tries, null entries resulting from optional customer portal fields, inconsistent text casings across merchant terminals, non-standard date formats, and negative/extreme outlier transaction values. 

The automated cleaning pipeline ingested the 4 raw tables, systematically identified data hygiene defects, applied mathematically and domain-grounded remediations, and validated relational integrity across all primary and foreign key constraints.

## 2. Before vs. After Row Count & Cleanliness Scorecard

| Table Name | Raw Row Count | Cleaned Row Count | Rows Removed | Nulls Resolved | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`categories`** | 10 | 10 | 0 | 0 | **100% Clean** |
| **`customers`** | 1218 | 1200 | 18 | 60 | **100% Clean** |
| **`cards`** | 1495 | 1480 | 15 | 12 | **100% Clean** |
| **`transactions`** | 21504 | 21469 | 35 | 75 | **100% Clean** |
| **Total Portfolio** | **24227** | **24159** | **68** | **147** | **Production Ready** |

---

## 3. Comprehensive Data Cleaning Log

Below is the comprehensive register documenting every specific defect identified, the exact remediation executed, and the business rationale.

| Step | Table | Issue Identified | Rows Impacted | Cleaning Action Taken | Business & Technical Justification | Before | After |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `categories` | Schema validation and whitespace in text columns | 0 | Trimmed whitespace, verified unique category_id primary keys | Ensure strict master key referential integrity for downstream joins | 10 | 10 |
| 2 | `customers` | Duplicate customer records introduced during batch ingestion | 18 | Deduplicated dataset based on unique primary key 'customer_id' (kept first occurrence) | Prevent demographic bias and double-counting of cardholder profiles | 1218 | 1200 |
| 3 | `customers` | Inconsistent casing ('mUMBAI', 'bengaluru', 'DELHI') and legacy city aliases | 31 | Applied `.str.strip().str.title()` and standardized regional city nomenclatures | Enable reliable geographic grouping and drilldowns in SQL and BI dashboards | 1200 | 1200 |
| 4 | `customers` | Missing values: 35 nulls in 'annual_income' and 25 nulls in 'city' | 60 | Imputed missing income via income-tier stratified medians; imputed missing city with modal metropolitan city | Preserves sample size while eliminating bias; income tier median protects against skewed distribution | 1200 | 1200 |
| 5 | `cards` | Duplicate card account entries from redundant ETL ingestion batches | 15 | Deduplicated dataset based on unique 'card_id' token (kept first occurrence) | Prevent inflated credit exposure calculations and false card counts | 1495 | 1480 |
| 6 | `cards` | Non-standardized casing in card tier labels ('silver', 'PLATINUM', 'gold') | 45 | Cleaned text using `.str.strip().str.capitalize()` to standardize ('Silver', 'Gold', 'Platinum', 'Signature') | Ensures consistent categorical aggregations across SQL and visualization filters | 1480 | 1480 |
| 7 | `cards` | Missing credit limits (12 rows) and un-synchronized open-to-buy balances | 12 | Imputed missing limits using card-type median; recalculated open_to_buy as (credit_limit - total_revolving_bal) | Maintains strict accounting balance consistency across portfolio balances | 1480 | 1480 |
| 8 | `transactions` | Duplicate transaction records caused by network retries and payment gateway replays | 35 | Deduplicated on unique 'transaction_id' token | Eliminates artificial spend inflation and distorted merchant transaction counts | 21504 | 21469 |
| 9 | `transactions` | Outlier amounts: 8 negative entries and 4 extreme fat-finger anomalies (>₹5,00,000) | 12 | Converted negative values to positive magnitudes (`.abs()`); capped extreme fat-finger outliers to category upper limits | Eliminates distorted portfolio spend totals and preserves accurate average ticket size metrics | 21469 | 21469 |
| 10 | `transactions` | Mixed date formatting standards (DD/MM/YYYY vs ISO YYYY-MM-DD) across regional terminal POS logs | 120 | Standardized all date strings into uniform ISO-8601 YYYY-MM-DD format | Required for chronological ordering, monthly time-series aggregation, and date-diff window calculations | 21469 | 21469 |
| 11 | `transactions` | Missing payment channel metadata (75 null records) | 75 | Imputed missing values with modal channel ('POS Swipe') | Ensures full attribution in channel-distribution metrics without dropping valid revenue transactions | 21469 | 21469 |
| 12 | `transactions` | Referential integrity audit against parent master tables (`cards` and `categories`) | 0 | Verified 100% of foreign keys resolve to valid parent table primary keys | Guarantees relational database consistency and prevents orphan records | 21469 | 21469 |

---

## 4. Detailed Breakdown of Cleaning Techniques

### 4.1 Deduplication Methodology
- **Root Cause:** Duplicates arose from asynchronous batch ingests and payment terminal timeout replays.
- **Method:** Utilized `.drop_duplicates(subset=[primary_key], keep='first')` across `customer_id`, `card_id`, and `transaction_id`.
- **Outcome:** Eliminated 18 phantom customer profiles, 15 duplicate cards, and 35 redundant transactions without data loss.

### 4.2 Handling of Missing Values (Imputation Strategy)
- **`annual_income` (35 nulls):** Rather than using a global mean (which is distorted by high-net-worth outliers), we applied stratified median imputation grouped by `income_tier`. This preserves income variance and credit underwriting credibility.
- **`city` (25 nulls):** Replaced with the metropolitan mode ('Mumbai') and mapped to the corresponding state ('Maharashtra') to maintain geographical integrity.
- **`payment_channel` (75 nulls):** Imputed with the dominant modal channel ('POS Swipe') to prevent dropping valid transactional spend volume.
- **`credit_limit` (12 nulls):** Imputed using the median credit limit of the respective card tier ('Silver', 'Gold', 'Platinum', 'Signature').

### 4.3 Outlier Remediation & Noise Reduction
- **Negative Values:** Erroneous negative amounts (e.g. -₹2,450.00) resulting from sign inversion in gateway feeds were corrected to positive magnitudes using `.abs()`.
- **Fat-Finger Outliers:** Identified extreme values exceeding ₹5,00,000 (such as test runs of ₹85,00,000) that would severely distort Average Ticket Size (ATV). These values were capped to realistic category-specific thresholds.

### 4.4 Date & Text Standardization
- Standardized mixed datetime strings (`DD/MM/YYYY`, `YYYY-MM-DD`) into uniform ISO-8601 (`YYYY-MM-DD`).
- Standardized all textual categorical fields (`city`, `gender`, `card_type`, `department`) using `.strip()` and `.title()` / `.capitalize()`, resolving regional aliases such as 'Bangalore' to 'Bengaluru'.

### 4.5 Referential Integrity & Data Validation Audit
- Confirmed 100% referential integrity across the star-snowflake schema:
  - Every `cards.customer_id` exists in `customers.customer_id`.
  - Every `transactions.card_id` exists in `cards.card_id`.
  - Every `transactions.category_id` exists in `categories.category_id`.
- Confirmed zero orphan records and zero unmapped foreign keys.
