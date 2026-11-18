# DELIVERABLE 7A: 5-MINUTE PRESENTATION SLIDES & SCRIPT

**Student Name:** Saqhiya Parveen  
**Project ID:** DA-12  
**Project Title:** Credit Card Spend & Customer Behaviour  
**Domain:** Banking & Finance  
**Target Duration:** Exactly 5 Minutes (300 Seconds)  
**Tools:** PowerPoint / Google Slides Deck Script  

---

## Slide-by-Slide Timing & Presentation Deck

```
[Slide 1: 0:00 - 0:30] Title & Project Mandate
[Slide 2: 0:30 - 1:00] Business Problem & Financial Stakes
[Slide 3: 1:00 - 1:30] Relational Data Architecture & Cleaning Pipeline
[Slide 4: 1:30 - 2:00] Spend Velocity & Category Dynamics
[Slide 5: 2:00 - 2:45] The Core Question: "Who is Inactive?"
[Slide 6: 2:45 - 3:15] Advanced SQL Analytics & RFM Segmentation
[Slide 7: 3:15 - 3:45] Interactive Executive Dashboard Tour
[Slide 8: 3:45 - 4:15] Financial Drag & Business Impact
[Slide 9: 4:15 - 4:45] Strategic Recommendations & Roadmap
[Slide 10: 4:45 - 5:00] Conclusion & Viva Handover
```

---

### Slide 1: Title & Executive Overview (0:00 - 0:30)
- **Slide Title:** Credit Card Spend Dynamics & Inactivity Analytics
- **Subtitle:** Uncovering Customer Spending Behaviour and Diagnosing Account Dormancy (DA-12)
- **Presenter:** Saqhiya Parveen | Domain: Banking & Finance
- **Key Visual:** Portfolio at a glance — 1,200 Customers | 1,480 Cards | 20,180 Swipes | ₹73.26M GMV

> **Speaker Script (0:00 - 0:30):**  
> *"Good morning respected evaluators and trainers. My name is Saqhiya Parveen, and today I am presenting Project DA-12: Credit Card Spend and Customer Behaviour. In retail banking, credit card profitability is driven by two engines: swipe velocity, which yields merchant interchange fees, and revolving credit balances, which generate interest income. However, portfolio managers face an ongoing dilemma: how do customers actually spend across categories, and which accounts have become inactive, tying up idle capital without generating revenue? Over the next five minutes, I will walk you through our data pipeline, analytical discoveries, and strategic recommendations."*

---

### Slide 2: The Business Problem & Financial Stakes (0:30 - 1:00)
- **Slide Title:** The Business Challenge: Capital Lockup & Churn
- **Bullet Points:**
  - Card issuers incur ₹3,500 Customer Acquisition Cost (CAC) per customer.
  - Breakeven requires 14 months of sustained active spend velocity.
  - Industry attrition averages 15% to 22%.
  - Unused credit limits lock up regulatory capital reserves under RBI/Basel III norms.
- **Core Question Highlighted:** *"How do customers spend across categories, channels, and tiers, and who are the inactive cardholders?"*

> **Speaker Script (0:30 - 1:00):**  
> *"Acquiring a credit card customer is expensive, averaging ₹3,500 in onboarding and underwriting costs. A bank only recoups this investment after 14 months of continuous active usage. In our portfolio, we observed that an alarming proportion of accounts had gone completely silent. Inactive cards are not merely passive — they represent locked-up regulatory capital reserves under RBI guidelines that cannot be deployed elsewhere. Our objective was to trace customer transactions over 18 months, pinpoint where spending thrives, isolate the markers of account dormancy, and establish an early-warning retention framework."*

---

### Slide 3: Relational Architecture & Data Cleaning Pipeline (1:00 - 1:30)
- **Slide Title:** Star-Snowflake Data Architecture & Rigorous Data Cleaning
- **Bullet Points:**
  - 4 Normalized Tables: `customers` (1,200 rows), `cards` (1,480 rows), `transactions` (20,180 rows), `categories` (10 rows).
  - Deduplicated on composite primary keys (removed 18 duplicate customers and 35 duplicate transactions).
  - Imputed missing income using income-tier stratified medians; standardized city names and ISO-8601 dates.
  - Remediated negative authorization anomalies and capped extreme outlier transactions.
  - 100% referential integrity verified across all foreign keys.

> **Speaker Script (1:00 - 1:30):**  
> *"To address this, we modeled an enterprise relational schema comprising four entities: customers, issued cards, transactional fact logs, and merchant categories. Real-world financial feeds are inherently messy. Our Python cleaning pipeline detected and eliminated duplicate transactions caused by gateway retries, imputed missing annual income values using stratified income-tier medians to avoid distortion, standardized regional city nomenclatures, corrected negative transaction amounts, and converted all dates into uniform ISO-8601 format. The result is a 100% clean, verified production database."*

---

### Slide 4: Spending Habits: The Everyday vs. Luxury Volume Paradox (1:30 - 2:00)
- **Slide Title:** Spending Dynamics: Frequency vs. Margin Dichotomy
- **Bullet Points:**
  - **Everyday Anchors:** Groceries (CAT01) and Dining (CAT02) account for **42.0% of all transaction swipes** (ATV: ₹1,620 and ₹1,240).
  - **High-Ticket Monetization:** Travel (CAT03) and Jewellery/Luxury (CAT10) represent only 10.4% of swipes, but generate **₹24.9M (34.0% of total spend)**.
  - **Seasonality:** Strong Diwali festive surge (+36% MoM in Oct–Nov) followed by post-holiday normalization in January.

> **Speaker Script (1:30 - 2:00):**  
> *"When analyzing customer spend, our first major finding is what I term the 'Everyday versus Luxury Paradox'. Over 42% of all card swipes occur in Groceries and Dining. While their average ticket size is modest — around ₹1,500 — customers who swipe in these categories weekly show an 89% lower probability of churn. On the other hand, Travel and Luxury account for only 10% of swipes, but contribute 34% of our entire portfolio revenue. Furthermore, we identified an annual festive surge during October and November, where portfolio GMV jumped by 36% month-over-month."*

---

### Slide 5: The Core Question: "Who is Inactive?" (2:00 - 2:45)
- **Slide Title:** Diagnosing Inactivity: The 180-Day Cliff
- **Bullet Points:**
  - **18.5% Portfolio Inactivity:** 222 cardholders have zero transactions in $\ge 180$ days.
  - **Idle Credit Exposure:** ₹4.82 Crores in sanctioned credit lines sitting completely unutilized.
  - **Income Vulnerability:** Inactivity rate is **24.8% in Lower-Middle class** vs. only 9.2% in High-Net-Worth cardholders.
  - **The Decay Curve:** Once a customer crosses 90 days of inactivity, the probability of permanent churn climbs to 78%.

> **Speaker Script (2:00 - 2:45):**  
> *"Now, turning to our primary mandate: Who is inactive? Exactly 222 cardholders — representing 18.5% of our portfolio — have not transacted in over 180 days. Collectively, they hold ₹4.82 Crores in sanctioned credit limits sitting entirely idle. When we drill down demographically, inactivity is highest among lower-middle-income cardholders holding basic Silver cards, where attrition reaches 24.8%. Most importantly, our recency analysis revealed an 'inactivity cliff': while a customer who has been silent for 45 days can be easily re-activated with a simple incentive, once silence exceeds 90 days, the re-activation rate plummets from 64% down to just 26%."*

---

### Slide 6: Advanced SQL Analytics & RFM Segmentation (2:45 - 3:15)
- **Slide Title:** Production SQL Analytics: CTEs, Window Functions & RFM
- **Bullet Points:**
  - 10 Production Queries executed in SQLite / PostgreSQL.
  - MoM Spend Velocity tracked using `LAG()` window function.
  - Share of Wallet calculated via `SUM() OVER(PARTITION BY...)`.
  - Customer RFM Segmentation engineered using `NTILE(4)` quartiles:
    * Champions (15.2%): High spend, high frequency, recency $<45$ days.
    * At-Risk (21.4%): High historical value, but recency slipping (90–180 days).
    * Dormant (18.5%): Beyond 180 days.

> **Speaker Script (2:45 - 3:15):**  
> *"To segment our portfolio programmatically, we engineered 10 production SQL queries using multi-table joins, CTEs, and window functions. Using the LAG() function, we tracked Month-over-Month spend velocity. Using NTILE(4), we constructed an algorithmic RFM score across Recency, Frequency, and Monetary value. This isolated our top 15% 'Champions' who drive baseline stability, and critically identified our 21% 'At-Risk' segment — cardholders who previously generated strong spend but whose activity has begun to slip. This is the exact cohort where automated intervention yields the highest return."*

---

### Slide 7: Interactive Executive Dashboard Tour (3:15 - 3:45)
- **Slide Title:** Live Interactive Executive Console (Power BI / Web)
- **Bullet Points:**
  - Real-time KPI Cards: Total GMV, Active Ratio (81.5%), Inactive Count (222), ATV (₹3,630), Utilization (31.4%).
  - Dynamic Multi-Dimensional Slicers: Filter by Card Tier, Gender, City, and Status.
  - 6 Synchronized Charts: Monthly Spend Trend, Share of Wallet, Tier Comparison, Inactivity Risk Funnel, Channel Polar, and Live Drill-Down Table.

> **Speaker Script (3:15 - 3:45):**  
> *"To empower our portfolio managers with real-time visibility, we developed an interactive executive dashboard. It presents six vital KPI cards, dynamic slicers for card tiers, metropolitan cities, and customer status, and six synchronized visual charts. Managers can immediately filter to any region, inspect the Inactivity Risk Funnel, and drill down into individual cardholder accounts to review lifetime spend, utilization, and days since last transaction."*

---

### Slide 8: Business Drag & Financial Impact (3:45 - 4:15)
- **Slide Title:** Quantifying the Financial Drag of Inactivity
- **Bullet Points:**
  - **Idle Capital Cost:** ₹28.9 Lakhs/year in opportunity cost of capital (@ 6% risk-free rate on ₹4.82 Cr idle limits).
  - **Lost Interchange Revenue:** ₹2.88 Lakhs/year in uncollected merchant discount fees.
  - **Sunk CAC Loss:** ₹7.77 Lakhs in unrecovered customer acquisition expenditures.
  - **Total Annual Drag:** Over **₹40 Lakhs annually** in lost profitability.

> **Speaker Script (3:45 - 4:15):**  
> *"What is the financial cost of this inactivity? The numbers are striking. The ₹4.82 Crores in locked-up credit lines represents an annual capital opportunity cost of nearly ₹29 Lakhs. When you add lost merchant interchange fees of ₹2.9 Lakhs and unrecovered customer acquisition costs of nearly ₹8 Lakhs, our bank suffers a cumulative financial drag exceeding ₹40 Lakhs every single year. Account inactivity is not just lost revenue — it is a severe drain on return on capital."*

---

### Slide 9: 5 Strategic Recommendations & Projected ROI (4:15 - 4:45)
- **Slide Title:** Strategic Turnaround: 5 Data-Backed Initiatives
- **Bullet Points:**
  1. **Automated Multi-Stage Re-activation Funnel:** Triggers at Day 45 (cashback nudge) and Day 90 (spend challenge).
  2. **Everyday Spend Loyalty Loop:** 5x reward points on supermarket and food delivery swipes.
  3. **Premium Milestone Spend Waivers:** Waive annual fees upon achieving spend milestones on Platinum/Signature.
  4. **Contactless Tap & Pay Tie-ups:** 5% instant discount on contactless transactions up to ₹5,000.
  5. **Dormant Line Rationalization:** Trim limits on unrecoverable dormant accounts by 60%, freeing ₹2.9 Crores in capital.
- **Projected Impact:** **+₹42.5 Lakhs net financial benefit**, reducing portfolio dormancy from **18.5% to 11.8%**.

> **Speaker Script (4:15 - 4:45):**  
> *"To resolve this, we propose five prioritized, data-backed initiatives: First, deploy an automated multi-stage re-activation funnel that triggers SMS and WhatsApp nudges at Day 45, capturing customers before they cross the 90-day cliff. Second, institute a 5x reward point multiplier on everyday groceries and dining to cement top-of-wallet habits. Third, introduce milestone spend fee waivers for premium Signature cardholders. Fourth, promote contactless tap-and-pay transactions through retail merchant partnerships. And fifth, systematically rationalise credit limits on irreversibly dormant accounts, freeing up ₹2.9 Crores in regulatory capital to deploy toward active borrowers. Together, these initiatives will deliver ₹42.5 Lakhs in annual financial turnaround."*

---

### Slide 10: Conclusion & Viva Handover (4:45 - 5:00)
- **Slide Title:** Conclusion & Summary of Deliverables
- **Bullet Points:**
  - Full end-to-end data analytics lifecycle completed (Problem Statement, Data Cleaning, SQL, EDA, Dashboard, Recommendations, Viva Prep).
  - Business Question Decisively Answered: Detailed spend patterns charted; inactive accounts diagnosed and segmented.
- **Analyst:** Saqhiya Parveen | Project DA-12

> **Speaker Script (4:45 - 5:00):**  
> *"In conclusion, Project DA-12 successfully transforms raw transactional records into an actionable commercial roadmap. We have definitively answered how our customers spend and who is inactive, providing the bank with the exact levers needed to boost engagement and capital efficiency. Thank you for your time, and I am now ready for your questions in the viva session."*
