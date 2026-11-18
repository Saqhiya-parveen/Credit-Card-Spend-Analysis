import os
import random
import datetime
import pandas as pd
import numpy as np

# Set fixed seed for reproducibility
np.random.seed(42)
random.seed(42)

base_dir = r"C:\Users\hp\.gemini\antigravity\scratch\DA12_Credit_Card_Spend_Customer_Behaviour"
raw_dir = os.path.join(base_dir, "data", "raw")
clean_dir = os.path.join(base_dir, "data", "cleaned")
os.makedirs(raw_dir, exist_ok=True)
os.makedirs(clean_dir, exist_ok=True)

print("Generating Data for Credit Card Spend & Customer Behaviour (DA-12)...")

# 1. Categories Table (Master Table)
categories_data = [
    {"category_id": "CAT01", "category_name": "Groceries & Supermarket", "department": "Retail", "reward_points_multiplier": 1.5, "risk_category": "Low"},
    {"category_id": "CAT02", "category_name": "Dining & Restaurants", "department": "Food & Beverage", "reward_points_multiplier": 2.0, "risk_category": "Low"},
    {"category_id": "CAT03", "category_name": "Travel & Airlines", "department": "Travel", "reward_points_multiplier": 3.0, "risk_category": "Medium"},
    {"category_id": "CAT04", "category_name": "Electronics & Gadgets", "department": "Electronics", "reward_points_multiplier": 1.0, "risk_category": "Medium"},
    {"category_id": "CAT05", "category_name": "Utilities & Bill Pay", "department": "Bills", "reward_points_multiplier": 1.0, "risk_category": "Low"},
    {"category_id": "CAT06", "category_name": "Fuel & Transportation", "department": "Transport", "reward_points_multiplier": 1.2, "risk_category": "Low"},
    {"category_id": "CAT07", "category_name": "Healthcare & Pharmacy", "department": "Medical", "reward_points_multiplier": 1.0, "risk_category": "Low"},
    {"category_id": "CAT08", "category_name": "Entertainment & Movies", "department": "Leisure", "reward_points_multiplier": 2.5, "risk_category": "Low"},
    {"category_id": "CAT09", "category_name": "Fashion & Apparel", "department": "Retail", "reward_points_multiplier": 2.0, "risk_category": "Medium"},
    {"category_id": "CAT10", "category_name": "Jewellery & Luxury", "department": "Luxury", "reward_points_multiplier": 1.0, "risk_category": "High"}
]
df_categories = pd.DataFrame(categories_data)

# 2. Customers Table (Master Table: 1,200 rows)
n_customers = 1200
first_names_m = ["Aarav", "Rohan", "Vikram", "Aditya", "Rahul", "Kunal", "Amit", "Suresh", "Manish", "Deepak", "Nikhil", "Arjun", "Praveen", "Karthik", "Siddharth"]
first_names_f = ["Pooja", "Priya", "Ananya", "Sneha", "Neha", "Divya", "Kavita", "Ritu", "Meera", "Swati", "Shreya", "Tanvi", "Sunita", "Simran", "Aarti"]
last_names = ["Sharma", "Verma", "Patel", "Reddy", "Mehta", "Nair", "Iyer", "Khan", "Singh", "Gupta", "Rao", "Joshi", "Das", "Choudhury", "Bose", "Kulkarni"]
cities_states = [
    ("Mumbai", "Maharashtra"),
    ("Bengaluru", "Karnataka"),
    ("Delhi", "Delhi"),
    ("Hyderabad", "Telangana"),
    ("Chennai", "Tamil Nadu"),
    ("Kolkata", "West Bengal"),
    ("Pune", "Maharashtra"),
    ("Ahmedabad", "Gujarat"),
    ("Jaipur", "Rajasthan"),
    ("Lucknow", "Uttar Pradesh")
]

customers_list = []
start_join_date = datetime.date(2021, 1, 1)

for i in range(1, n_customers + 1):
    cid = f"CUST{i:05d}"
    gender = random.choice(["Male", "Female"])
    fname = random.choice(first_names_m if gender == "Male" else first_names_f)
    lname = random.choice(last_names)
    age = int(np.random.normal(39, 11))
    age = max(21, min(72, age))
    
    city, state = random.choice(cities_states)
    
    # Income distribution (skewed towards middle/upper middle class in INR)
    income_tier = random.choices(["Lower-Middle", "Middle", "Upper-Middle", "High-Net-Worth"], weights=[0.20, 0.45, 0.25, 0.10])[0]
    if income_tier == "Lower-Middle":
        annual_income = round(random.uniform(300000, 600000), -3)
        credit_score = int(np.random.normal(670, 40))
    elif income_tier == "Middle":
        annual_income = round(random.uniform(600000, 1200000), -3)
        credit_score = int(np.random.normal(725, 35))
    elif income_tier == "Upper-Middle":
        annual_income = round(random.uniform(1200000, 2500000), -3)
        credit_score = int(np.random.normal(770, 30))
    else:
        annual_income = round(random.uniform(2500000, 6000000), -3)
        credit_score = int(np.random.normal(810, 25))
        
    credit_score = max(550, min(850, credit_score))
    
    join_days = random.randint(0, 1400)
    join_date = start_join_date + datetime.timedelta(days=join_days)
    
    # Customer churn / activity probability (about 18% inactive/churned)
    is_inactive = random.random() < 0.185
    customer_status = "Inactive" if is_inactive else "Active"
    
    customers_list.append({
        "customer_id": cid,
        "first_name": fname,
        "last_name": lname,
        "gender": gender,
        "age": age,
        "city": city,
        "state": state,
        "income_tier": income_tier,
        "annual_income": annual_income,
        "credit_score": credit_score,
        "join_date": join_date.strftime("%Y-%m-%d"),
        "customer_status": customer_status
    })

df_customers = pd.DataFrame(customers_list)

# 3. Cards Table (1,500 cards issued across 1,200 customers; some customers have 2 cards)
card_types = ["Silver", "Gold", "Platinum", "Signature"]
card_limit_map = {
    "Silver": (50000, 150000, 0.38),
    "Gold": (150000, 400000, 0.35),
    "Platinum": (400000, 800000, 0.30),
    "Signature": (800000, 1800000, 0.24)
}

cards_list = []
card_counter = 1

for _, cust in df_customers.iterrows():
    # Number of cards: 75% have 1 card, 25% have 2 cards
    num_cards = 1 if random.random() < 0.75 else 2
    for _ in range(num_cards):
        cid = cust["customer_id"]
        # Map card tier based on income tier
        if cust["income_tier"] == "Lower-Middle":
            ctype = random.choices(["Silver", "Gold"], weights=[0.85, 0.15])[0]
        elif cust["income_tier"] == "Middle":
            ctype = random.choices(["Silver", "Gold", "Platinum"], weights=[0.25, 0.60, 0.15])[0]
        elif cust["income_tier"] == "Upper-Middle":
            ctype = random.choices(["Gold", "Platinum", "Signature"], weights=[0.15, 0.65, 0.20])[0]
        else:
            ctype = random.choices(["Platinum", "Signature"], weights=[0.20, 0.80])[0]
            
        limit_min, limit_max, apr = card_limit_map[ctype]
        credit_limit = round(random.uniform(limit_min, limit_max), -3)
        
        # Inactive cards: if customer is inactive, 80% card is inactive. If customer active, 5% card inactive
        if cust["customer_status"] == "Inactive":
            card_status = random.choices(["Inactive", "Blocked", "Active"], weights=[0.75, 0.15, 0.10])[0]
        else:
            card_status = random.choices(["Active", "Inactive"], weights=[0.95, 0.05])[0]
            
        join_dt = datetime.datetime.strptime(cust["join_date"], "%Y-%m-%d").date()
        issue_offset = random.randint(0, 90)
        issue_date = join_dt + datetime.timedelta(days=issue_offset)
        
        # Balance & revolving credit
        if card_status == "Active":
            utilization = random.uniform(0.05, 0.75)
            revolving_bal = round(credit_limit * utilization, 2)
        elif card_status == "Inactive":
            utilization = random.uniform(0.0, 0.15)
            revolving_bal = round(credit_limit * utilization, 2)
        else:
            revolving_bal = round(credit_limit * random.uniform(0.70, 0.95), 2)
            
        open_to_buy = round(credit_limit - revolving_bal, 2)
        
        cards_list.append({
            "card_id": f"CRD{card_counter:05d}",
            "customer_id": cid,
            "card_type": ctype,
            "credit_limit": credit_limit,
            "interest_rate_apr": round(apr * 100, 2),
            "issue_date": issue_date.strftime("%Y-%m-%d"),
            "card_status": card_status,
            "total_revolving_bal": revolving_bal,
            "open_to_buy": open_to_buy
        })
        card_counter += 1

df_cards = pd.DataFrame(cards_list)

# 4. Transactions Table (18,000 transactions over 18 months: July 2024 to Dec 2025)
tx_start_date = datetime.date(2024, 7, 1)
tx_end_date = datetime.date(2025, 12, 31)
total_days = (tx_end_date - tx_start_date).days

merchants = {
    "CAT01": ["Reliance Smart", "BigBasket", "DMart", "Nature's Basket", "Blinkit", "Zomato Blinkit"],
    "CAT02": ["Swiggy", "Zomato", "Barbeque Nation", "Mainland China", "Starbucks", "Social Cafe"],
    "CAT03": ["MakeMyTrip", "IndiGo Airlines", "Air India", "Yatra", "Taj Hotels", "Booking.com"],
    "CAT04": ["Croma", "Reliance Digital", "Apple Store", "Amazon Electronics", "Vijay Sales"],
    "CAT05": ["Tata Power", "BESCOM", "Adani Gas", "Airtel Postpaid", "Jio Fiber"],
    "CAT06": ["Indian Oil", "Bharat Petroleum", "HPCL Petrol", "Uber India", "Ola Cabs"],
    "CAT07": ["Apollo Pharmacy", "MedPlus", "Netmeds", "Fortis Healthcare", "Max Healthcare"],
    "CAT08": ["BookMyShow", "PVR INOX", "Netflix India", "SonyLIV", "Hotstar Premium"],
    "CAT09": ["Myntra", "Zara India", "Shoppers Stop", "Westside", "Ajio Trends"],
    "CAT10": ["Tanishq", "Kalyan Jewellers", "Malabar Gold", "CaratLane", "Titan Watch Studio"]
}

payment_channels = ["POS Swipe", "Online Payment", "Contactless Tap", "ATM Withdrawal"]
channel_weights = [0.45, 0.40, 0.12, 0.03]

active_cards = df_cards[df_cards["card_status"] == "Active"]["card_id"].tolist()
inactive_cards = df_cards[df_cards["card_status"].isin(["Inactive", "Blocked"])]["card_id"].tolist()

transactions_list = []
tx_counter = 1

# Active cards make between 8 to 28 transactions across the timeline
for cid in active_cards:
    n_tx = random.randint(8, 28)
    for _ in range(n_tx):
        # Evenly spread across 18 months, with seasonal festival spikes in Oct-Nov
        day_offset = random.randint(0, total_days)
        tx_dt = tx_start_date + datetime.timedelta(days=day_offset)
        
        # Category selection
        cat_id = random.choices(
            [c["category_id"] for c in categories_data],
            weights=[0.24, 0.18, 0.08, 0.09, 0.12, 0.11, 0.06, 0.05, 0.05, 0.02]
        )[0]
        
        merchant = random.choice(merchants[cat_id])
        channel = random.choices(payment_channels, weights=channel_weights)[0]
        
        # Spend amount ranges by category
        if cat_id == "CAT01": # Groceries
            amt = round(random.uniform(450, 4800), 2)
        elif cat_id == "CAT02": # Dining
            amt = round(random.uniform(350, 3800), 2)
        elif cat_id == "CAT03": # Travel
            amt = round(random.uniform(3500, 32000), 2)
        elif cat_id == "CAT04": # Electronics
            amt = round(random.uniform(2500, 45000), 2)
        elif cat_id == "CAT05": # Utilities
            amt = round(random.uniform(400, 5500), 2)
        elif cat_id == "CAT06": # Fuel
            amt = round(random.uniform(500, 4000), 2)
        elif cat_id == "CAT07": # Healthcare
            amt = round(random.uniform(300, 6500), 2)
        elif cat_id == "CAT08": # Entertainment
            amt = round(random.uniform(250, 2200), 2)
        elif cat_id == "CAT09": # Fashion
            amt = round(random.uniform(800, 12000), 2)
        else: # CAT10 Luxury
            amt = round(random.uniform(15000, 85000), 2)
            
        status = random.choices(["Approved", "Declined", "Refunded"], weights=[0.94, 0.04, 0.02])[0]
        
        transactions_list.append({
            "transaction_id": f"TXN{tx_counter:07d}",
            "card_id": cid,
            "category_id": cat_id,
            "transaction_date": tx_dt.strftime("%Y-%m-%d"),
            "amount": amt,
            "payment_channel": channel,
            "transaction_status": status,
            "merchant_name": merchant
        })
        tx_counter += 1

# Inactive cards: they only transacted early in the window (e.g., between day 0 and day 180), zero transactions in past 6-12 months!
for cid in inactive_cards:
    # Some inactive cards have 1-4 historical transactions, some have 0 (dormant since creation)
    if random.random() < 0.65:
        n_tx = random.randint(1, 4)
        for _ in range(n_tx):
            day_offset = random.randint(0, 150) # Only early in the period (Jul 2024 - Nov 2024)
            tx_dt = tx_start_date + datetime.timedelta(days=day_offset)
            cat_id = random.choice(["CAT01", "CAT02", "CAT05", "CAT06"])
            merchant = random.choice(merchants[cat_id])
            channel = random.choices(payment_channels, weights=channel_weights)[0]
            amt = round(random.uniform(250, 3200), 2)
            
            transactions_list.append({
                "transaction_id": f"TXN{tx_counter:07d}",
                "card_id": cid,
                "category_id": cat_id,
                "transaction_date": tx_dt.strftime("%Y-%m-%d"),
                "amount": amt,
                "payment_channel": channel,
                "transaction_status": "Approved",
                "merchant_name": merchant
            })
            tx_counter += 1

df_transactions = pd.DataFrame(transactions_list)

# Sort transactions by date
df_transactions = df_transactions.sort_values("transaction_date").reset_index(drop=True)
df_transactions["transaction_id"] = [f"TXN{i+1:07d}" for i in range(len(df_transactions))]

print(f"Clean Data Generated:")
print(f"- Categories: {len(df_categories)} rows")
print(f"- Customers: {len(df_customers)} rows")
print(f"- Cards: {len(df_cards)} rows")
print(f"- Transactions: {len(df_transactions)} rows")

# Save Clean Tables
df_categories.to_csv(os.path.join(clean_dir, "categories_cleaned.csv"), index=False)
df_customers.to_csv(os.path.join(clean_dir, "customers_cleaned.csv"), index=False)
df_cards.to_csv(os.path.join(clean_dir, "cards_cleaned.csv"), index=False)
df_transactions.to_csv(os.path.join(clean_dir, "transactions_cleaned.csv"), index=False)

# NOW CREATE DIRTY RAW DATASETS (incorporating realistic real-world data issues as required by Rubric 2)
# Issues to introduce:
# 1. Null values (~3-5% missing in annual_income, city, payment_channel)
# 2. Inconsistent casing ('mUMBAI', 'bengaluru', 'DELHI', 'male', 'FEMALE', 'silver', 'PLATINUM')
# 3. Duplicate rows (15 duplicate rows in customers, 20 duplicate rows in transactions)
# 4. Outlier values (erroneous negative amounts, extreme outliers)
# 5. Non-standard date formats (e.g. DD/MM/YYYY vs YYYY-MM-DD vs DD-MM-YYYY)
# 6. Leading/trailing whitespace

df_raw_cust = df_customers.copy()
# Inject nulls
df_raw_cust.loc[np.random.choice(df_raw_cust.index, 35, replace=False), "annual_income"] = np.nan
df_raw_cust.loc[np.random.choice(df_raw_cust.index, 25, replace=False), "city"] = np.nan
# Inconsistent text & casing
casing_choices = [lambda s: s.lower(), lambda s: s.upper(), lambda s: f"  {s}  "]
for idx in np.random.choice(df_raw_cust.index, 60, replace=False):
    func = random.choice(casing_choices)
    df_raw_cust.loc[idx, "city"] = func(str(df_raw_cust.loc[idx, "city"])) if pd.notna(df_raw_cust.loc[idx, "city"]) else np.nan
for idx in np.random.choice(df_raw_cust.index, 40, replace=False):
    df_raw_cust.loc[idx, "gender"] = str(df_raw_cust.loc[idx, "gender"]).lower()
# Add duplicate rows
dupe_cust = df_raw_cust.sample(n=18, random_state=101)
df_raw_cust = pd.concat([df_raw_cust, dupe_cust], ignore_index=True)

df_raw_cards = df_cards.copy()
# Inconsistent casing in card_type
for idx in np.random.choice(df_raw_cards.index, 45, replace=False):
    df_raw_cards.loc[idx, "card_type"] = random.choice([lambda s: s.lower(), lambda s: s.upper()])(df_raw_cards.loc[idx, "card_type"])
# A few null credit limits or negative interest rates
df_raw_cards.loc[np.random.choice(df_raw_cards.index, 12, replace=False), "credit_limit"] = np.nan
dupe_cards = df_raw_cards.sample(n=15, random_state=102)
df_raw_cards = pd.concat([df_raw_cards, dupe_cards], ignore_index=True)

df_raw_tx = df_transactions.copy()
# Nulls
df_raw_tx.loc[np.random.choice(df_raw_tx.index, 75, replace=False), "payment_channel"] = np.nan
# Outliers: negative amount or fat-finger amount (e.g. 999999)
outlier_neg_idx = np.random.choice(df_raw_tx.index, 8, replace=False)
df_raw_tx.loc[outlier_neg_idx, "amount"] = -df_raw_tx.loc[outlier_neg_idx, "amount"]
outlier_extreme_idx = np.random.choice(df_raw_tx.index, 4, replace=False)
df_raw_tx.loc[outlier_extreme_idx, "amount"] = 8500000.00
# Inconsistent dates
for idx in np.random.choice(df_raw_tx.index, 120, replace=False):
    raw_d = df_raw_tx.loc[idx, "transaction_date"]
    dt = datetime.datetime.strptime(raw_d, "%Y-%m-%d")
    df_raw_tx.loc[idx, "transaction_date"] = dt.strftime("%d/%m/%Y")
# Duplicate transactions
dupe_tx = df_raw_tx.sample(n=35, random_state=103)
df_raw_tx = pd.concat([df_raw_tx, dupe_tx], ignore_index=True)

# Save Raw Tables
df_categories.to_csv(os.path.join(raw_dir, "raw_categories.csv"), index=False)
df_raw_cust.to_csv(os.path.join(raw_dir, "raw_customers.csv"), index=False)
df_raw_cards.to_csv(os.path.join(raw_dir, "raw_cards.csv"), index=False)
df_raw_tx.to_csv(os.path.join(raw_dir, "raw_transactions.csv"), index=False)

print(f"Raw Dirty Data Generated:")
print(f"- Raw Customers: {len(df_raw_cust)} rows (18 duplicates added, nulls injected)")
print(f"- Raw Cards: {len(df_raw_cards)} rows (15 duplicates added, casing issues)")
print(f"- Raw Transactions: {len(df_raw_tx)} rows (35 duplicates added, negative amounts, outliers, mixed dates)")
print("Dataset generation complete!")
