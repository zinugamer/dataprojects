# ============================================================
# Himaxx Offline Outlet Intelligent Operating Dashboard
# Raw Data Generator
#
# Business Context:
# - Himaxx = 76 offline multi-brand discount outlet stores
# - E-commerce / live commerce are NOT included in this first version
# - Cole Haan is an external brand used for inventory clearance
# - Brand A and Brand B are Himaxx Own private-label brands
# - Business modes include Buyout, Consignment, Own Brand
#
# Output:
# Himaxx_Intelligent_Operating_System/02_data/raw/
#
# Tables:
# 1. sales_fact.csv
# 2. inventory_fact.csv
# 3. product_dim.csv
# 4. store_dim.csv
# 5. customer_dim.csv
# 6. cost_fact.csv
# 7. finance_fact.csv
# 8. marketing_fact.csv
# ============================================================

import os
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker


# ============================================================
# 0. Basic setup
# ============================================================

fake = Faker()
Faker.seed(42)
np.random.seed(42)
rng = np.random.default_rng(42)

PROJECT_PATH = Path(
    "/Users/jincheng/Desktop/Data_Science/03_Data_Analytics/dataprojects/Himaxx/"
    "Himaxx_Intelligent_Operating_System/02_data/raw"
)

PROJECT_PATH.mkdir(parents=True, exist_ok=True)

print(f"Data will be saved to: {PROJECT_PATH.resolve()}")


# ============================================================
# 1. Configuration
# ============================================================

N_STORES = 76
N_SKUS = 500
N_MEMBERS = 1000
N_SALES_ROWS = 25000

START_DATE = datetime(2026, 1, 1)
END_DATE = datetime(2026, 4, 30)

MONTHS = pd.date_range("2026-01-01", "2026-04-01", freq="MS")

CHANNEL_NAME = "Himaxx Outlet"

brands = [
    "Nike", "Adidas", "Puma", "Under Armour", "New Balance",
    "Asics", "Skechers", "Fila", "Champion", "Columbia",
    "The North Face", "Patagonia", "Lululemon", "On Running",
    "Hoka", "Salomon", "Brooks Brothers", "Reebok Underwear",
    "Cole Haan", "Brand A", "Brand B"
]

brand_weights = np.array([
    0.075, 0.075, 0.050, 0.040, 0.050,
    0.040, 0.040, 0.040, 0.040, 0.035,
    0.035, 0.030, 0.035, 0.040,
    0.040, 0.035, 0.065, 0.065,
    0.090, 0.080, 0.080
])

# Normalize weights to make sure they sum to 1
brand_weights = brand_weights / brand_weights.sum()

categories = [
    "Running Shoes",
    "Training Shoes",
    "Basketball Shoes",
    "Outdoor Apparel",
    "Sportswear",
    "Yoga Apparel",
    "Underwear",
    "Accessories",
    "Bags",
    "Kids Apparel",
    "Lifestyle Apparel",
    "Performance Apparel"
]

regions = [
    "East China",
    "South China",
    "North China",
    "West China",
    "Central China"
]

city_pool = [
    "Shanghai", "Beijing", "Shenzhen", "Guangzhou", "Hangzhou",
    "Chengdu", "Wuhan", "Nanjing", "Suzhou", "Xi'an",
    "Chongqing", "Tianjin", "Qingdao", "Xiamen", "Changsha"
]

store_formats = [
    "Mall Outlet",
    "Community Outlet",
    "Shopping Center Store",
    "Street Store",
    "Pop-up Clearance Store"
]

store_format_weights = [0.28, 0.25, 0.25, 0.15, 0.07]


# ============================================================
# 2. Generate store_dim.csv
# ============================================================

store_rows = []

for i in range(1, N_STORES + 1):
    store_id = f"S{i:03d}"

    region = rng.choice(regions)
    city = rng.choice(city_pool)

    store_format = rng.choice(
        store_formats,
        p=store_format_weights
    )

    store_level = rng.choice(
        ["A", "B", "C"],
        p=[0.30, 0.45, 0.25]
    )

    store_size_sqm = int(np.clip(rng.normal(260, 80), 80, 600))

    open_date = fake.date_between(
        start_date="-6y",
        end_date="-3m"
    )

    # This profile is used later to create mixed P&L results.
    # Some stores will be profitable, some stable, some risky, some loss-making.
    profit_profile = rng.choice(
        ["High Profit", "Stable", "At Risk", "Loss Making"],
        p=[0.25, 0.40, 0.22, 0.13]
    )

    if profit_profile == "High Profit":
        sales_power_index = rng.uniform(1.35, 1.80)
        cost_pressure_index = rng.uniform(0.70, 0.90)
    elif profit_profile == "Stable":
        sales_power_index = rng.uniform(1.00, 1.30)
        cost_pressure_index = rng.uniform(0.85, 1.05)
    elif profit_profile == "At Risk":
        sales_power_index = rng.uniform(0.70, 1.00)
        cost_pressure_index = rng.uniform(1.05, 1.30)
    else:
        sales_power_index = rng.uniform(0.45, 0.75)
        cost_pressure_index = rng.uniform(1.25, 1.60)

    store_rows.append({
        "store_id": store_id,
        "store_name": f"Himaxx {city} Outlet {i}",
        "channel": CHANNEL_NAME,
        "store_format": store_format,
        "region": region,
        "city": city,
        "store_level": store_level,
        "store_size_sqm": store_size_sqm,
        "open_date": open_date,
        "profit_profile": profit_profile,
        "sales_power_index": round(sales_power_index, 3),
        "cost_pressure_index": round(cost_pressure_index, 3),
        "is_active": 1
    })

store_dim = pd.DataFrame(store_rows)
store_dim.to_csv(PROJECT_PATH / "store_dim.csv", index=False)


# ============================================================
# 3. Generate product_dim.csv
# ============================================================

product_rows = []

for i in range(1, N_SKUS + 1):
    sku = f"SKU{i:05d}"

    brand = rng.choice(brands, p=brand_weights)

    # Brand A and Brand B are examples under Himaxx Own.
    if brand in ["Brand A", "Brand B"]:
        brand_owner = "Himaxx Own"
    else:
        brand_owner = "External Brand"

    category = rng.choice(categories)

    # Business mode logic
    if brand_owner == "Himaxx Own":
        business_mode = "Own Brand"
    elif brand == "Cole Haan":
        business_mode = rng.choice(["Buyout", "Consignment"], p=[0.70, 0.30])
    elif brand in ["Nike", "Adidas", "Lululemon", "On Running", "Hoka"]:
        business_mode = rng.choice(["Consignment", "Buyout"], p=[0.65, 0.35])
    else:
        business_mode = rng.choice(["Buyout", "Consignment"], p=[0.58, 0.42])

    # MSRP by category
    if "Shoes" in category:
        msrp = rng.uniform(79, 229)
    elif category in ["Outdoor Apparel", "Performance Apparel"]:
        msrp = rng.uniform(69, 299)
    elif category in ["Underwear", "Accessories"]:
        msrp = rng.uniform(15, 89)
    elif category == "Bags":
        msrp = rng.uniform(39, 199)
    else:
        msrp = rng.uniform(29, 169)

    msrp = round(msrp, 2)

    # Cost and margin logic
    if business_mode == "Own Brand":
        standard_cost = msrp * rng.uniform(0.22, 0.38)
        gross_margin_target = rng.uniform(0.55, 0.72)
        take_rate = 1.0
    elif business_mode == "Buyout":
        standard_cost = msrp * rng.uniform(0.38, 0.58)
        gross_margin_target = rng.uniform(0.35, 0.55)
        take_rate = 1.0
    else:
        # For consignment, Himaxx recognizes commission revenue.
        # Standard cost is not the main inventory burden here.
        standard_cost = msrp * rng.uniform(0.05, 0.15)
        gross_margin_target = rng.uniform(0.18, 0.35)
        take_rate = rng.uniform(0.18, 0.35)

    product_lifecycle = rng.choice(
        ["New", "Growth", "Mature", "Clearance"],
        p=[0.18, 0.30, 0.35, 0.17]
    )

    product_rows.append({
        "sku": sku,
        "product_name": f"{brand} {category} {fake.word().title()}",
        "brand_owner": brand_owner,
        "brand": brand,
        "category": category,
        "business_mode": business_mode,
        "msrp": round(msrp, 2),
        "standard_cost": round(standard_cost, 2),
        "take_rate": round(take_rate, 4),
        "gross_margin_target": round(gross_margin_target, 4),
        "season": rng.choice(["Spring", "Summer", "Fall", "Winter", "Core"]),
        "product_lifecycle": product_lifecycle,
        "launch_date": fake.date_between(start_date="-3y", end_date="-1m")
    })

product_dim = pd.DataFrame(product_rows)
product_dim.to_csv(PROJECT_PATH / "product_dim.csv", index=False)


# ============================================================
# 4. Generate customer_dim.csv
# ============================================================

customer_rows = []

for i in range(1, N_MEMBERS + 1):
    member_id = f"M{i:05d}"

    age = int(np.clip(rng.normal(33, 9), 18, 65))

    customer_rows.append({
        "member_id": member_id,
        "customer_name": fake.name(),
        "gender": rng.choice(["Female", "Male", "Unknown"], p=[0.48, 0.45, 0.07]),
        "age": age,
        "city": rng.choice(city_pool),
        "region": rng.choice(regions),
        "membership_tier": rng.choice(
            ["Silver", "Gold", "Platinum", "Diamond"],
            p=[0.50, 0.30, 0.15, 0.05]
        ),
        "join_date": fake.date_between(start_date="-4y", end_date="today"),
        "preferred_store_format": rng.choice(store_formats, p=store_format_weights),
        "is_active_member": rng.choice([1, 0], p=[0.88, 0.12])
    })

customer_dim = pd.DataFrame(customer_rows)
customer_dim.to_csv(PROJECT_PATH / "customer_dim.csv", index=False)


# ============================================================
# 5. Generate sales_fact.csv
# ============================================================

sales_rows = []

store_lookup = store_dim.set_index("store_id").to_dict("index")
product_lookup = product_dim.set_index("sku").to_dict("index")

store_ids = store_dim["store_id"].tolist()
sku_ids = product_dim["sku"].tolist()
member_ids = customer_dim["member_id"].tolist()

# Store sampling weight: better stores get more transactions.
store_weights = store_dim["sales_power_index"].values
store_weights = store_weights / store_weights.sum()

# SKU popularity: create natural bestsellers and slow movers.
sku_popularity = rng.gamma(shape=2.0, scale=1.0, size=N_SKUS)

# Give Brand A / Brand B and Cole Haan slightly stronger sales exposure.
for idx, sku in enumerate(sku_ids):
    p = product_lookup[sku]
    if p["brand_owner"] == "Himaxx Own":
        sku_popularity[idx] *= 1.35
    if p["brand"] == "Cole Haan":
        sku_popularity[idx] *= 1.25
    if p["product_lifecycle"] == "Clearance":
        sku_popularity[idx] *= 1.15

sku_weights = sku_popularity / sku_popularity.sum()

date_range_days = (END_DATE - START_DATE).days + 1

for i in range(1, N_SALES_ROWS + 1):
    transaction_id = f"T{i:08d}"
    order_id = f"O{i:08d}"

    date = START_DATE + timedelta(days=int(rng.integers(0, date_range_days)))

    store_id = rng.choice(store_ids, p=store_weights)
    store_info = store_lookup[store_id]

    sku = rng.choice(sku_ids, p=sku_weights)
    product_info = product_lookup[sku]

    member_id = rng.choice(member_ids)

    brand_owner = product_info["brand_owner"]
    brand = product_info["brand"]
    category = product_info["category"]
    business_mode = product_info["business_mode"]
    msrp = float(product_info["msrp"])
    standard_cost = float(product_info["standard_cost"])
    take_rate = float(product_info["take_rate"])

    # Units per transaction
    gross_units = int(
        rng.choice(
            [1, 1, 1, 2, 2, 3, 4],
            p=[0.42, 0.20, 0.10, 0.12, 0.08, 0.05, 0.03]
        )
    )

    # Offline outlet return rate is lower than e-commerce.
    returned_units = int(rng.binomial(gross_units, 0.04))
    net_units = gross_units - returned_units

    # Discount logic based on store format.
    if store_info["store_format"] == "Pop-up Clearance Store":
        discount_rate = rng.uniform(0.50, 0.75)
    elif store_info["store_format"] == "Community Outlet":
        discount_rate = rng.uniform(0.35, 0.62)
    elif store_info["store_format"] == "Mall Outlet":
        discount_rate = rng.uniform(0.30, 0.58)
    elif store_info["store_format"] == "Shopping Center Store":
        discount_rate = rng.uniform(0.28, 0.55)
    else:
        discount_rate = rng.uniform(0.38, 0.68)

    # Clearance products get deeper discounts.
    if product_info["product_lifecycle"] == "Clearance":
        discount_rate += rng.uniform(0.06, 0.15)

    discount_rate = min(discount_rate, 0.78)

    transaction_price = round(msrp * (1 - discount_rate), 2)
    discount_amount = round((msrp - transaction_price) * gross_units, 2)

    gmv = round(msrp * gross_units, 2)
    net_sales = round(transaction_price * net_units, 2)

    # Core revenue recognition logic.
    if business_mode in ["Buyout", "Own Brand"]:
        recognized_revenue = net_sales
        cogs = round(standard_cost * net_units, 2)
    else:
        recognized_revenue = round(net_sales * take_rate, 2)
        cogs = round(recognized_revenue * rng.uniform(0.10, 0.25), 2)

    gross_profit = round(recognized_revenue - cogs, 2)

    sales_rows.append({
        "transaction_id": transaction_id,
        "order_id": order_id,
        "date": date.date(),
        "store_id": store_id,
        "channel": CHANNEL_NAME,
        "store_format": store_info["store_format"],
        "member_id": member_id,
        "sku": sku,
        "brand_owner": brand_owner,
        "brand": brand,
        "category": category,
        "business_mode": business_mode,
        "gross_units": gross_units,
        "returned_units": returned_units,
        "net_units": net_units,
        "msrp": round(msrp, 2),
        "transaction_price": transaction_price,
        "discount_rate": round(discount_rate, 4),
        "discount_amount": discount_amount,
        "gmv": gmv,
        "net_sales": net_sales,
        "recognized_revenue": recognized_revenue,
        "cogs": cogs,
        "gross_profit": gross_profit
    })

sales_fact = pd.DataFrame(sales_rows)
sales_fact.to_csv(PROJECT_PATH / "sales_fact.csv", index=False)


# ============================================================
# 6. Generate inventory_fact.csv
# Supports:
# - inventory_value
# - sell-through
# - inventory_age
# - GMROI
# ============================================================

sales_fact["month"] = pd.to_datetime(sales_fact["date"]).values.astype("datetime64[M]")

monthly_sku_store_sales = (
    sales_fact
    .groupby(["store_id", "sku", "month"], as_index=False)
    .agg(
        sold_units=("net_units", "sum"),
        sales_revenue=("recognized_revenue", "sum"),
        gross_profit=("gross_profit", "sum")
    )
)

monthly_sales_lookup = {
    (row["store_id"], row["sku"], row["month"]): {
        "sold_units": row["sold_units"],
        "sales_revenue": row["sales_revenue"],
        "gross_profit": row["gross_profit"]
    }
    for _, row in monthly_sku_store_sales.iterrows()
}

inventory_rows = []

for month in MONTHS:
    for store_id in store_ids:
        store_info = store_lookup[store_id]

        for sku in sku_ids:
            product_info = product_lookup[sku]

            key = (store_id, sku, month)
            sales_data = monthly_sales_lookup.get(
                key,
                {
                    "sold_units": 0,
                    "sales_revenue": 0.0,
                    "gross_profit": 0.0
                }
            )

            sold_units = int(sales_data["sold_units"])
            sales_revenue = float(sales_data["sales_revenue"])
            gross_profit = float(sales_data["gross_profit"])

            # Inventory depth logic
            if store_info["store_format"] == "Pop-up Clearance Store":
                base_inventory = rng.integers(20, 120)
            elif store_info["store_format"] == "Community Outlet":
                base_inventory = rng.integers(10, 70)
            elif store_info["store_format"] == "Mall Outlet":
                base_inventory = rng.integers(8, 60)
            elif store_info["store_format"] == "Shopping Center Store":
                base_inventory = rng.integers(8, 55)
            else:
                base_inventory = rng.integers(12, 80)

            if product_info["brand"] == "Cole Haan":
                base_inventory = int(base_inventory * rng.uniform(1.15, 1.45))

            if product_info["brand_owner"] == "Himaxx Own":
                base_inventory = int(base_inventory * rng.uniform(1.05, 1.30))

            beginning_inventory_units = int(base_inventory + rng.integers(0, 25))
            received_units = int(max(0, sold_units + rng.integers(-5, 30)))
            ending_inventory_units = max(
                0,
                beginning_inventory_units + received_units - sold_units
            )

            available_units = beginning_inventory_units + received_units
            sell_through_rate = sold_units / available_units if available_units > 0 else 0

            standard_cost = float(product_info["standard_cost"])
            inventory_value = round(ending_inventory_units * standard_cost, 2)

            # Inventory aging logic
            if product_info["product_lifecycle"] == "Clearance":
                inventory_age_days = int(rng.integers(120, 420))
            elif store_info["store_format"] == "Pop-up Clearance Store":
                inventory_age_days = int(rng.integers(90, 360))
            elif product_info["brand"] == "Cole Haan":
                inventory_age_days = int(rng.integers(80, 300))
            else:
                inventory_age_days = int(rng.integers(20, 220))

            avg_inventory_units = (beginning_inventory_units + ending_inventory_units) / 2
            avg_inventory_value = avg_inventory_units * standard_cost
            gmroi = gross_profit / avg_inventory_value if avg_inventory_value > 0 else 0

            inventory_rows.append({
                "snapshot_month": month.date(),
                "store_id": store_id,
                "channel": CHANNEL_NAME,
                "store_format": store_info["store_format"],
                "sku": sku,
                "brand_owner": product_info["brand_owner"],
                "brand": product_info["brand"],
                "category": product_info["category"],
                "business_mode": product_info["business_mode"],
                "beginning_inventory_units": beginning_inventory_units,
                "received_units": received_units,
                "sold_units": sold_units,
                "ending_inventory_units": ending_inventory_units,
                "standard_cost": round(standard_cost, 2),
                "inventory_value": inventory_value,
                "inventory_age_days": inventory_age_days,
                "sell_through_rate": round(sell_through_rate, 4),
                "sales_revenue": round(sales_revenue, 2),
                "gross_profit": round(gross_profit, 2),
                "avg_inventory_value": round(avg_inventory_value, 2),
                "gmroi": round(gmroi, 4)
            })

inventory_fact = pd.DataFrame(inventory_rows)
inventory_fact.to_csv(PROJECT_PATH / "inventory_fact.csv", index=False)


# ============================================================
# 7. Generate cost_fact.csv
# Monthly SKU-level cost assumptions
# ============================================================

cost_rows = []

for month in MONTHS:
    for sku in sku_ids:
        product_info = product_lookup[sku]

        standard_cost = float(product_info["standard_cost"])

        inbound_freight_rate = rng.uniform(0.02, 0.08)
        packaging_cost = rng.uniform(0.50, 5.00)
        handling_cost = rng.uniform(0.30, 3.50)

        if product_info["business_mode"] == "Own Brand":
            product_development_cost = rng.uniform(3.00, 15.00)
        else:
            product_development_cost = rng.uniform(0.00, 4.00)

        landed_cost = (
            standard_cost * (1 + inbound_freight_rate)
            + packaging_cost
            + handling_cost
            + product_development_cost
        )

        cost_rows.append({
            "month": month.date(),
            "sku": sku,
            "brand_owner": product_info["brand_owner"],
            "brand": product_info["brand"],
            "category": product_info["category"],
            "business_mode": product_info["business_mode"],
            "standard_cost": round(standard_cost, 2),
            "inbound_freight_rate": round(inbound_freight_rate, 4),
            "packaging_cost_per_unit": round(packaging_cost, 2),
            "handling_cost_per_unit": round(handling_cost, 2),
            "product_development_cost_per_unit": round(product_development_cost, 2),
            "landed_cost_per_unit": round(landed_cost, 2)
        })

cost_fact = pd.DataFrame(cost_rows)
cost_fact.to_csv(PROJECT_PATH / "cost_fact.csv", index=False)


# ============================================================
# 8. Generate finance_fact.csv
# Monthly store-level P&L
#
# Important:
# Because this is simulated data, operating expenses are generated
# based on store profit profile to intentionally create:
# - profitable stores
# - stable stores
# - at-risk stores
# - loss-making stores
# This makes Tableau Store P&L analysis more useful.
# ============================================================

monthly_store_sales = (
    sales_fact
    .groupby(["store_id", "channel", "store_format", "month"], as_index=False)
    .agg(
        orders=("order_id", "nunique"),
        gmv=("gmv", "sum"),
        net_sales=("net_sales", "sum"),
        recognized_revenue=("recognized_revenue", "sum"),
        cogs=("cogs", "sum"),
        gross_profit=("gross_profit", "sum")
    )
)

monthly_store_lookup = {
    (row["store_id"], row["month"]): {
        "orders": row["orders"],
        "gmv": row["gmv"],
        "net_sales": row["net_sales"],
        "recognized_revenue": row["recognized_revenue"],
        "cogs": row["cogs"],
        "gross_profit": row["gross_profit"]
    }
    for _, row in monthly_store_sales.iterrows()
}

finance_rows = []

for month in MONTHS:
    for store_id in store_ids:
        store_info = store_lookup[store_id]

        data = monthly_store_lookup.get(
            (store_id, month),
            {
                "orders": 0,
                "gmv": 0.0,
                "net_sales": 0.0,
                "recognized_revenue": 0.0,
                "cogs": 0.0,
                "gross_profit": 0.0
            }
        )

        orders = int(data["orders"])
        gmv = float(data["gmv"])
        net_sales = float(data["net_sales"])
        recognized_revenue = float(data["recognized_revenue"])
        cogs = float(data["cogs"])
        gross_profit = float(data["gross_profit"])

        profile = store_info["profit_profile"]
        cost_pressure = float(store_info["cost_pressure_index"])

        # Target opex ratio by store profit profile
        if gross_profit <= 0:
            total_opex = rng.uniform(1500, 5000) * cost_pressure
        else:
            if profile == "High Profit":
                opex_ratio = rng.uniform(0.15, 0.40)
            elif profile == "Stable":
                opex_ratio = rng.uniform(0.45, 0.80)
            elif profile == "At Risk":
                opex_ratio = rng.uniform(0.95, 1.30)
            else:
                opex_ratio = rng.uniform(1.35, 2.00)

            fixed_cost = rng.uniform(50, 500) * cost_pressure
            total_opex = gross_profit * opex_ratio + fixed_cost

        # Split total opex into required finance categories.
        rent_pct = rng.uniform(0.20, 0.30)
        payroll_pct = rng.uniform(0.28, 0.38)
        utilities_pct = rng.uniform(0.03, 0.07)
        local_marketing_pct = rng.uniform(0.05, 0.10)
        logistics_pct = rng.uniform(0.08, 0.14)
        warehouse_pct = rng.uniform(0.06, 0.12)
        hq_sga_pct = rng.uniform(0.08, 0.15)

        allocated_pct = (
            rent_pct + payroll_pct + utilities_pct + local_marketing_pct
            + logistics_pct + warehouse_pct + hq_sga_pct
        )

        brand_marketing_pct = max(0.03, 1 - allocated_pct)

        total_pct = (
            rent_pct + payroll_pct + utilities_pct + local_marketing_pct
            + logistics_pct + warehouse_pct + hq_sga_pct + brand_marketing_pct
        )

        rent_expense = total_opex * rent_pct / total_pct
        payroll_expense = total_opex * payroll_pct / total_pct
        utilities_expense = total_opex * utilities_pct / total_pct
        local_marketing_expense = total_opex * local_marketing_pct / total_pct
        logistics_expense = total_opex * logistics_pct / total_pct
        warehouse_expense = total_opex * warehouse_pct / total_pct
        hq_sga = total_opex * hq_sga_pct / total_pct
        brand_marketing_expense = total_opex * brand_marketing_pct / total_pct

        total_opex_final = (
            rent_expense
            + payroll_expense
            + utilities_expense
            + local_marketing_expense
            + logistics_expense
            + warehouse_expense
            + hq_sga
            + brand_marketing_expense
        )

        operating_profit = gross_profit - total_opex_final
        operating_margin = operating_profit / recognized_revenue if recognized_revenue > 0 else 0

        finance_rows.append({
            "month": month.date(),
            "store_id": store_id,
            "channel": CHANNEL_NAME,
            "store_format": store_info["store_format"],
            "region": store_info["region"],
            "city": store_info["city"],
            "profit_profile": profile,
            "orders": orders,
            "gmv": round(gmv, 2),
            "net_sales": round(net_sales, 2),
            "recognized_revenue": round(recognized_revenue, 2),
            "cogs": round(cogs, 2),
            "gross_profit": round(gross_profit, 2),
            "rent_expense": round(rent_expense, 2),
            "payroll_expense": round(payroll_expense, 2),
            "utilities_expense": round(utilities_expense, 2),
            "local_marketing_expense": round(local_marketing_expense, 2),
            "logistics_expense": round(logistics_expense, 2),
            "warehouse_expense": round(warehouse_expense, 2),
            "hq_sga": round(hq_sga, 2),
            "brand_marketing_expense": round(brand_marketing_expense, 2),
            "total_opex": round(total_opex_final, 2),
            "operating_profit": round(operating_profit, 2),
            "operating_margin": round(operating_margin, 4)
        })

finance_fact = pd.DataFrame(finance_rows)
finance_fact.to_csv(PROJECT_PATH / "finance_fact.csv", index=False)


# ============================================================
# 9. Generate marketing_fact.csv
# Monthly store-level marketing efficiency
# Supports:
# - marketing_spend
# - new_customers
# - orders
# - GMV
# - recognized_revenue
# - gross_profit
# - CAC
# - ROAS
# ============================================================

first_purchase = (
    sales_fact
    .sort_values("date")
    .groupby("member_id", as_index=False)
    .first()[["member_id", "date", "store_id", "channel", "store_format"]]
)

first_purchase["month"] = pd.to_datetime(first_purchase["date"]).values.astype("datetime64[M]")

new_customer_monthly = (
    first_purchase
    .groupby(["store_id", "month"], as_index=False)
    .agg(new_customers=("member_id", "nunique"))
)

new_customer_lookup = {
    (row["store_id"], row["month"]): row["new_customers"]
    for _, row in new_customer_monthly.iterrows()
}

marketing_channels = [
    "Xiaohongshu",
    "WeChat",
    "Local Community Ads",
    "Offline Event",
    "KOL Collaboration",
    "Search Ads",
    "Mall Promotion",
    "Member Coupon"
]

marketing_rows = []

for month in MONTHS:
    for store_id in store_ids:
        store_info = store_lookup[store_id]

        data = monthly_store_lookup.get(
            (store_id, month),
            {
                "orders": 0,
                "gmv": 0.0,
                "recognized_revenue": 0.0,
                "gross_profit": 0.0
            }
        )

        orders = int(data["orders"])
        gmv = float(data["gmv"])
        recognized_revenue = float(data["recognized_revenue"])
        gross_profit = float(data["gross_profit"])

        new_customers = int(
            new_customer_lookup.get(
                (store_id, month),
                max(0, rng.normal(max(orders * 0.12, 1), 3))
            )
        )

        if store_info["store_format"] == "Mall Outlet":
            primary_marketing_channel = rng.choice(["Mall Promotion", "WeChat", "Member Coupon"])
            spend_rate = rng.uniform(0.025, 0.060)
        elif store_info["store_format"] == "Community Outlet":
            primary_marketing_channel = rng.choice(["Local Community Ads", "WeChat", "Member Coupon"])
            spend_rate = rng.uniform(0.018, 0.050)
        elif store_info["store_format"] == "Shopping Center Store":
            primary_marketing_channel = rng.choice(["Mall Promotion", "Offline Event", "Xiaohongshu"])
            spend_rate = rng.uniform(0.025, 0.070)
        elif store_info["store_format"] == "Pop-up Clearance Store":
            primary_marketing_channel = rng.choice(["Xiaohongshu", "KOL Collaboration", "Member Coupon"])
            spend_rate = rng.uniform(0.035, 0.090)
        else:
            primary_marketing_channel = rng.choice(["WeChat", "Offline Event", "Search Ads"])
            spend_rate = rng.uniform(0.020, 0.060)

        marketing_spend = max(300, gmv * spend_rate)
        cac = marketing_spend / new_customers if new_customers > 0 else 0
        roas = gmv / marketing_spend if marketing_spend > 0 else 0

        marketing_rows.append({
            "month": month.date(),
            "store_id": store_id,
            "channel": CHANNEL_NAME,
            "store_format": store_info["store_format"],
            "primary_marketing_channel": primary_marketing_channel,
            "marketing_spend": round(marketing_spend, 2),
            "new_customers": new_customers,
            "orders": orders,
            "gmv": round(gmv, 2),
            "recognized_revenue": round(recognized_revenue, 2),
            "gross_profit": round(gross_profit, 2),
            "cac": round(cac, 2),
            "roas": round(roas, 4),
            "revenue_per_order": round(recognized_revenue / orders, 2) if orders > 0 else 0,
            "gross_profit_per_order": round(gross_profit / orders, 2) if orders > 0 else 0
        })

marketing_fact = pd.DataFrame(marketing_rows)
marketing_fact.to_csv(PROJECT_PATH / "marketing_fact.csv", index=False)


# ============================================================
# 10. Data quality checks
# ============================================================

print("\n================ Data Generation Completed ================")

files = {
    "sales_fact.csv": sales_fact,
    "inventory_fact.csv": inventory_fact,
    "product_dim.csv": product_dim,
    "store_dim.csv": store_dim,
    "customer_dim.csv": customer_dim,
    "cost_fact.csv": cost_fact,
    "finance_fact.csv": finance_fact,
    "marketing_fact.csv": marketing_fact
}

for file_name, df in files.items():
    print(f"{file_name}: {df.shape[0]:,} rows, {df.shape[1]} columns")

print("\nFiles saved under:")
print(PROJECT_PATH.resolve())

print("\n================ Business Logic Checks ================")

print("\n1. Store profile profitability check:")
print(
    finance_fact
    .groupby("profit_profile")["operating_profit"]
    .mean()
    .round(2)
)

print("\n2. Business mode sales logic check:")
print(
    sales_fact
    .groupby("business_mode")[["net_sales", "recognized_revenue", "cogs", "gross_profit"]]
    .sum()
    .round(2)
)

print("\n3. Brand owner contribution check:")
print(
    sales_fact
    .groupby("brand_owner")[["recognized_revenue", "gross_profit"]]
    .sum()
    .round(2)
)

print("\n4. Top 10 brands by recognized revenue:")
print(
    sales_fact
    .groupby("brand")[["recognized_revenue", "gross_profit"]]
    .sum()
    .sort_values("recognized_revenue", ascending=False)
    .head(10)
    .round(2)
)

print("\n5. Inventory health check:")
print(
    inventory_fact[["inventory_value", "sell_through_rate", "inventory_age_days", "gmroi"]]
    .describe()
    .round(2)
)

print("\nDone. You can now connect these CSV files to Tableau.")