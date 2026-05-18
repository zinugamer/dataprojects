# ============================================================
# Himaxx Intelligent Operating Dashboard
# Raw Data Generator V3
#
# Business Context:
# - Himaxx = 大仓式折扣零售渠道 / warehouse-style discount retail
# - 门店面积通常 10,000 sqm+
# - 商品成交价通常为吊牌价 1-3 折
# - 业务模式包括 Buyout, Consignment, Own Brand
# - Brand A / Brand B = Himaxx 自有品牌
# - Cole Haan = 外部品牌清货场景
# - Brooks Brothers / Reebok Underwear may include royalty
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
# 9. store_traffic_fact.csv
# 10. store_target_fact.csv
# 11. product_action_fact.csv
# ============================================================

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

# 修改这里为你的项目路径
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
N_SALES_ROWS = 80000  # V3 focus: enough transaction density for store-level monthly funnel analysis

START_DATE = datetime(2026, 1, 1)
END_DATE = datetime(2026, 4, 30)

MONTHS = pd.date_range("2026-01-01", "2026-04-01", freq="MS")

CHANNEL_NAME = "Himaxx Warehouse Outlet"

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

# Fixed city-region mapping. Do NOT randomly assign region, otherwise regional dashboard logic breaks.
city_region_map = {
    "Beijing": "North China",
    "Tianjin": "North China",
    "Qingdao": "North China",
    "Shanghai": "East China",
    "Hangzhou": "East China",
    "Nanjing": "East China",
    "Suzhou": "East China",
    "Shenzhen": "South China",
    "Guangzhou": "South China",
    "Xiamen": "South China",
    "Wuhan": "Central China",
    "Changsha": "Central China",
    "Chengdu": "West China",
    "Chongqing": "West China",
    "Xi'an": "West China",
}

store_formats = [
    "Warehouse Outlet",
    "Mall Warehouse",
    "Community Warehouse",
    "Shopping Center Warehouse",
    "Pop-up Clearance Warehouse"
]

store_format_weights = [0.38, 0.22, 0.18, 0.15, 0.07]


# ============================================================
# 2. Generate store_dim.csv
# ============================================================

store_rows = []

for i in range(1, N_STORES + 1):
    store_id = f"S{i:03d}"
    city = rng.choice(city_pool)
    region = city_region_map[city]

    store_format = rng.choice(store_formats, p=store_format_weights)

    store_level = rng.choice(["A", "B", "C"], p=[0.30, 0.45, 0.25])

    # Himaxx 荟品仓是大仓式折扣零售业态，门店面积通常在 10,000 sqm 以上
    if store_format == "Pop-up Clearance Warehouse":
        store_size_sqm = int(rng.uniform(6000, 12000))
    elif store_format == "Community Warehouse":
        store_size_sqm = int(rng.uniform(8000, 14000))
    elif store_format == "Mall Warehouse":
        store_size_sqm = int(rng.uniform(10000, 18000))
    elif store_format == "Shopping Center Warehouse":
        store_size_sqm = int(rng.uniform(10000, 20000))
    else:
        store_size_sqm = int(rng.uniform(12000, 22000))

    # 大仓模式下 staff_count 与面积相关，但不是普通门店比例
    if store_size_sqm < 10000:
        staff_count = int(rng.integers(20, 40))
    elif store_size_sqm < 14000:
        staff_count = int(rng.integers(35, 60))
    elif store_size_sqm < 18000:
        staff_count = int(rng.integers(50, 80))
    else:
        staff_count = int(rng.integers(70, 110))

    open_date = fake.date_between(start_date="-6y", end_date="-3m")

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

    store_maturity = rng.choice(
        ["New Store", "Ramp-up", "Mature", "Aging"],
        p=[0.10, 0.20, 0.55, 0.15]
    )

    trade_area_type = rng.choice(
        ["Suburban Mall", "Community", "Industrial Park", "Transport Hub", "Outlet Cluster"],
        p=[0.30, 0.22, 0.16, 0.14, 0.18]
    )

    rent_model = rng.choice(
        ["Fixed Rent", "Revenue Share", "Fixed + Revenue Share"],
        p=[0.45, 0.20, 0.35]
    )

    store_rows.append({
        "store_id": store_id,
        "store_name": f"Himaxx {city} Warehouse {i}",
        "channel": CHANNEL_NAME,
        "store_format": store_format,
        "region": region,
        "city": city,
        "store_level": store_level,
        "store_size_sqm": store_size_sqm,
        "staff_count": staff_count,
        "open_date": open_date,
        "store_maturity": store_maturity,
        "trade_area_type": trade_area_type,
        "rent_model": rent_model,
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

    if brand in ["Brand A", "Brand B"]:
        brand_owner = "Himaxx Own"
    else:
        brand_owner = "External Brand"

    category = rng.choice(categories)

    if brand_owner == "Himaxx Own":
        business_mode = "Own Brand"
        inventory_risk_owner = "Himaxx"
    elif brand == "Cole Haan":
        business_mode = rng.choice(["Buyout", "Consignment"], p=[0.75, 0.25])
        inventory_risk_owner = "Himaxx" if business_mode == "Buyout" else "Brand Partner"
    elif brand in ["Nike", "Adidas", "Lululemon", "On Running", "Hoka"]:
        business_mode = rng.choice(["Consignment", "Buyout"], p=[0.62, 0.38])
        inventory_risk_owner = "Brand Partner" if business_mode == "Consignment" else "Himaxx"
    else:
        business_mode = rng.choice(["Buyout", "Consignment"], p=[0.60, 0.40])
        inventory_risk_owner = "Himaxx" if business_mode == "Buyout" else "Brand Partner"

    if "Shoes" in category:
        msrp = rng.uniform(399, 1699)
    elif category in ["Outdoor Apparel", "Performance Apparel"]:
        msrp = rng.uniform(299, 2299)
    elif category in ["Underwear", "Accessories"]:
        msrp = rng.uniform(99, 699)
    elif category == "Bags":
        msrp = rng.uniform(199, 1599)
    else:
        msrp = rng.uniform(129, 1299)

    msrp = round(msrp, 2)

    product_lifecycle = rng.choice(
        ["New", "Growth", "Mature", "Clearance"],
        p=[0.18, 0.30, 0.35, 0.17]
    )

    # Himaxx 是深折扣渠道：采购成本也应该是吊牌价的低比例
    if business_mode == "Own Brand":
        standard_cost = msrp * rng.uniform(0.10, 0.22)
        gross_margin_target = rng.uniform(0.35, 0.60)
        take_rate = 1.0
    elif business_mode == "Buyout":
        if product_lifecycle == "Clearance" or brand == "Cole Haan":
            standard_cost = msrp * rng.uniform(0.05, 0.14)
        else:
            standard_cost = msrp * rng.uniform(0.08, 0.18)

        gross_margin_target = rng.uniform(0.25, 0.50)
        take_rate = 1.0
    else:
        standard_cost = msrp * rng.uniform(0.01, 0.05)
        gross_margin_target = rng.uniform(0.18, 0.35)
        take_rate = rng.uniform(0.18, 0.35)

    if msrp < 300:
        price_band = "Entry"
    elif msrp < 800:
        price_band = "Mass"
    elif msrp < 1600:
        price_band = "Premium"
    else:
        price_band = "Luxury"

    gender_segment = rng.choice(
        ["Men", "Women", "Unisex", "Kids"],
        p=[0.32, 0.34, 0.24, 0.10]
    )

    age_segment = rng.choice(
        ["Youth", "Young Adult", "Adult", "Senior"],
        p=[0.12, 0.38, 0.42, 0.08]
    )

    color_family = rng.choice(
        ["Black", "White", "Grey", "Blue", "Red", "Green", "Brown", "Multi"],
        p=[0.24, 0.18, 0.16, 0.12, 0.08, 0.07, 0.08, 0.07]
    )

    size_group = rng.choice(
        ["XS-S", "M-L", "XL-XXL", "One Size"],
        p=[0.22, 0.46, 0.22, 0.10]
    )

    style_type = rng.choice(
        ["Core Basic", "Fashion", "Performance", "Limited", "Clearance"],
        p=[0.35, 0.22, 0.25, 0.06, 0.12]
    )

    core_or_seasonal = (
        "Core"
        if product_lifecycle in ["Growth", "Mature"] and style_type == "Core Basic"
        else "Seasonal"
    )

    clearance_flag = 1 if product_lifecycle == "Clearance" or style_type == "Clearance" else 0

    replenishable_flag = 1 if product_lifecycle in ["Growth", "Mature"] and clearance_flag == 0 else 0

    if brand in ["Nike", "Adidas", "Lululemon", "On Running", "Hoka", "Brooks Brothers"]:
        brand_tier = "Tier 1"
    elif brand in ["Cole Haan", "Reebok Underwear", "Brand A", "Brand B"]:
        brand_tier = "Tier 2"
    else:
        brand_tier = "Tier 3"

    product_rows.append({
        "sku": sku,
        "product_name": f"{brand} {category} {fake.word().title()}",
        "brand_owner": brand_owner,
        "brand": brand,
        "brand_tier": brand_tier,
        "category": category,
        "business_mode": business_mode,
        "inventory_risk_owner": inventory_risk_owner,
        "msrp": round(msrp, 2),
        "standard_cost": round(standard_cost, 2),
        "take_rate": round(take_rate, 4),
        "gross_margin_target": round(gross_margin_target, 4),
        "season": rng.choice(["Spring", "Summer", "Fall", "Winter", "Core"]),
        "product_lifecycle": product_lifecycle,
        "price_band": price_band,
        "gender_segment": gender_segment,
        "age_segment": age_segment,
        "color_family": color_family,
        "size_group": size_group,
        "style_type": style_type,
        "core_or_seasonal": core_or_seasonal,
        "clearance_flag": clearance_flag,
        "replenishable_flag": replenishable_flag,
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
    customer_city = rng.choice(city_pool)

    customer_rows.append({
        "member_id": member_id,
        "customer_name": fake.name(),
        "gender": rng.choice(["Female", "Male", "Unknown"], p=[0.48, 0.45, 0.07]),
        "age": age,
        "city": customer_city,
        "region": city_region_map[customer_city],
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

store_weights = store_dim["sales_power_index"].values
store_weights = store_weights / store_weights.sum()

sku_popularity = rng.gamma(shape=2.0, scale=1.0, size=N_SKUS)

for idx, sku in enumerate(sku_ids):
    p = product_lookup[sku]
    if p["brand_owner"] == "Himaxx Own":
        sku_popularity[idx] *= 1.30
    if p["brand"] == "Cole Haan":
        sku_popularity[idx] *= 1.25
    if p["product_lifecycle"] == "Clearance":
        sku_popularity[idx] *= 1.20

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
    brand_tier = product_info["brand_tier"]
    category = product_info["category"]
    business_mode = product_info["business_mode"]
    inventory_risk_owner = product_info["inventory_risk_owner"]
    msrp = float(product_info["msrp"])
    standard_cost = float(product_info["standard_cost"])
    take_rate = float(product_info["take_rate"])

    gross_units = int(
        rng.choice(
            [1, 1, 1, 2, 2, 3, 4, 5],
            p=[0.35, 0.18, 0.10, 0.14, 0.10, 0.06, 0.04, 0.03]
        )
    )

    returned_units = int(rng.binomial(gross_units, 0.04))
    net_units = gross_units - returned_units

    # ========================================================
    # Himaxx deep-discount pricing logic
    # 商品成交价通常为吊牌价 1-3 折
    # discount_factor = transaction_price / msrp
    # discount_rate = 1 - discount_factor
    # ========================================================

    if product_info["product_lifecycle"] == "Clearance":
        discount_factor = rng.uniform(0.10, 0.18)
    elif product_info["brand"] == "Cole Haan":
        discount_factor = rng.uniform(0.12, 0.22)
    elif product_info["brand_owner"] == "Himaxx Own":
        discount_factor = rng.uniform(0.20, 0.35)
    elif product_info["brand_tier"] == "Tier 1":
        discount_factor = rng.uniform(0.20, 0.30)
    else:
        discount_factor = rng.uniform(0.15, 0.28)

    if store_info["store_format"] == "Pop-up Clearance Warehouse":
        discount_factor *= rng.uniform(0.75, 0.90)
    elif store_info["store_format"] == "Warehouse Outlet":
        discount_factor *= rng.uniform(0.90, 1.05)
    elif store_info["store_format"] == "Shopping Center Warehouse":
        discount_factor *= rng.uniform(0.95, 1.10)
    else:
        discount_factor *= rng.uniform(0.90, 1.08)

    promotion_type = rng.choice(
        ["No Promo", "Member Coupon", "Clearance Markdown", "Bundle Discount", "Mall Event"],
        p=[0.28, 0.22, 0.25, 0.15, 0.10]
    )

    if promotion_type == "Clearance Markdown":
        discount_factor *= rng.uniform(0.80, 0.92)
    elif promotion_type == "Member Coupon":
        discount_factor *= rng.uniform(0.90, 0.97)
    elif promotion_type == "Bundle Discount":
        discount_factor *= rng.uniform(0.88, 0.95)

    discount_factor = float(np.clip(discount_factor, 0.08, 0.35))

    transaction_price = round(msrp * discount_factor, 2)

    discount_rate = round(1 - discount_factor, 4)
    discount_depth = discount_rate

    msrp_gmv = round(msrp * gross_units, 2)
    transaction_gmv = round(transaction_price * gross_units, 2)
    gross_sales = transaction_gmv

    discount_amount = round(msrp_gmv - transaction_gmv, 2)
    markdown_amount = discount_amount

    # Dashboard 默认 GMV 采用实际成交交易额，而不是吊牌价交易额
    gmv = transaction_gmv

    return_amount = round(transaction_price * returned_units, 2)
    net_sales = round(transaction_price * net_units, 2)

    tax_rate = 0.06
    tax_amount = round(net_sales * tax_rate / (1 + tax_rate), 2)

    if business_mode in ["Buyout", "Own Brand"]:
        recognized_revenue = net_sales
        cogs = round(standard_cost * net_units, 2)
    else:
        recognized_revenue = round(net_sales * take_rate, 2)
        cogs = round(recognized_revenue * rng.uniform(0.10, 0.25), 2)

    gross_profit = round(recognized_revenue - cogs, 2)
    net_price = round(recognized_revenue / net_units, 2) if net_units > 0 else 0

    cost_to_msrp_ratio = round(standard_cost / msrp, 4) if msrp > 0 else 0
    price_cost_spread = round(discount_factor - cost_to_msrp_ratio, 4)

    sales_associate_id = f"SA{rng.integers(1, 300):04d}"
    order_type = rng.choice(["Normal", "Exchange", "Return Adjusted"], p=[0.88, 0.07, 0.05])

    sales_rows.append({
        "transaction_id": transaction_id,
        "order_id": order_id,
        "date": date.date(),
        "store_id": store_id,
        "channel": CHANNEL_NAME,
        "store_format": store_info["store_format"],
        "region": store_info["region"],
        "city": store_info["city"],
        "member_id": member_id,
        "sku": sku,
        "brand_owner": brand_owner,
        "brand": brand,
        "brand_tier": brand_tier,
        "category": category,
        "business_mode": business_mode,
        "inventory_risk_owner": inventory_risk_owner,
        "gross_units": gross_units,
        "returned_units": returned_units,
        "net_units": net_units,
        "msrp": round(msrp, 2),
        "transaction_price": transaction_price,
        "discount_factor": round(discount_factor, 4),
        "discount_rate": discount_rate,
        "discount_depth": discount_depth,
        "discount_amount": discount_amount,
        "markdown_amount": markdown_amount,
        "msrp_gmv": msrp_gmv,
        "transaction_gmv": transaction_gmv,
        "gross_sales": gross_sales,
        "gmv": gmv,
        "return_amount": return_amount,
        "net_sales": net_sales,
        "tax_amount": tax_amount,
        "recognized_revenue": recognized_revenue,
        "cogs": cogs,
        "gross_profit": gross_profit,
        "net_price": net_price,
        "cost_to_msrp_ratio": cost_to_msrp_ratio,
        "price_cost_spread": price_cost_spread,
        "sales_associate_id": sales_associate_id,
        "promotion_type": promotion_type,
        "order_type": order_type
    })

sales_fact = pd.DataFrame(sales_rows)
sales_fact.to_csv(PROJECT_PATH / "sales_fact.csv", index=False)


# ============================================================
# 6. Generate store_traffic_fact.csv
# ============================================================

daily_store_sales = (
    sales_fact
    .groupby(["date", "store_id", "store_format", "channel"], as_index=False)
    .agg(
        orders=("order_id", "nunique"),
        buyers=("member_id", "nunique"),
        gross_units=("gross_units", "sum"),
        gmv=("gmv", "sum"),
        recognized_revenue=("recognized_revenue", "sum")
    )
)

traffic_rows = []

for _, row in daily_store_sales.iterrows():
    store_info = store_lookup[row["store_id"]]
    orders = int(row["orders"])

    # Warehouse discount retail has a lot of browsing traffic.
    # Keep monthly aggregated CVR in a realistic operating range after grouping.
    if store_info["profit_profile"] == "High Profit":
        order_cvr = rng.uniform(0.08, 0.14)
    elif store_info["profit_profile"] == "Stable":
        order_cvr = rng.uniform(0.06, 0.11)
    elif store_info["profit_profile"] == "At Risk":
        order_cvr = rng.uniform(0.04, 0.08)
    else:
        order_cvr = rng.uniform(0.03, 0.06)

    traffic = int(max(orders / order_cvr, orders + rng.integers(80, 400)))

    member_uv = int(traffic * rng.uniform(0.30, 0.65))
    new_member_uv = int(member_uv * rng.uniform(0.10, 0.35))
    returning_member_uv = member_uv - new_member_uv

    assisted_visits = int(traffic * rng.uniform(0.25, 0.65))
    try_on_count = int(assisted_visits * rng.uniform(0.20, 0.55))

    traffic_to_order_cvr = orders / traffic if traffic > 0 else 0
    member_cvr = row["buyers"] / member_uv if member_uv > 0 else 0
    try_on_cvr = orders / try_on_count if try_on_count > 0 else 0
    upt = row["gross_units"] / orders if orders > 0 else 0
    aur = row["gmv"] / row["gross_units"] if row["gross_units"] > 0 else 0

    traffic_rows.append({
        "date": row["date"],
        "store_id": row["store_id"],
        "channel": row["channel"],
        "store_format": row["store_format"],
        "region": store_info["region"],
        "city": store_info["city"],
        "traffic": traffic,
        "member_uv": member_uv,
        "new_member_uv": new_member_uv,
        "returning_member_uv": returning_member_uv,
        "assisted_visits": assisted_visits,
        "try_on_count": try_on_count,
        "orders": orders,
        "buyers": int(row["buyers"]),
        "gross_units": int(row["gross_units"]),
        "gmv": round(row["gmv"], 2),
        "recognized_revenue": round(row["recognized_revenue"], 2),
        "traffic_to_order_cvr": round(traffic_to_order_cvr, 4),
        "member_cvr": round(member_cvr, 4),
        "try_on_cvr": round(try_on_cvr, 4),
        "upt": round(upt, 4),
        "aur": round(aur, 2)
    })

store_traffic_fact = pd.DataFrame(traffic_rows)
store_traffic_fact.to_csv(PROJECT_PATH / "store_traffic_fact.csv", index=False)


# ============================================================
# 7. Generate inventory_fact.csv
# ============================================================

sales_fact["month"] = pd.to_datetime(sales_fact["date"]).values.astype("datetime64[M]")

monthly_sku_store_sales = (
    sales_fact
    .groupby(["store_id", "sku", "month"], as_index=False)
    .agg(
        sold_units=("net_units", "sum"),
        sales_revenue=("recognized_revenue", "sum"),
        gross_profit=("gross_profit", "sum"),
        cogs=("cogs", "sum")
    )
)

monthly_sales_lookup = {
    (row["store_id"], row["sku"], row["month"]): {
        "sold_units": row["sold_units"],
        "sales_revenue": row["sales_revenue"],
        "gross_profit": row["gross_profit"],
        "cogs": row["cogs"]
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
                    "gross_profit": 0.0,
                    "cogs": 0.0
                }
            )

            sold_units = int(sales_data["sold_units"])
            sales_revenue = float(sales_data["sales_revenue"])
            gross_profit = float(sales_data["gross_profit"])
            cogs = float(sales_data["cogs"])

            if store_info["store_format"] == "Pop-up Clearance Warehouse":
                base_inventory = rng.integers(20, 130)
            elif store_info["store_format"] == "Warehouse Outlet":
                base_inventory = rng.integers(25, 160)
            elif store_info["store_format"] == "Mall Warehouse":
                base_inventory = rng.integers(18, 120)
            else:
                base_inventory = rng.integers(15, 110)

            if product_info["brand"] == "Cole Haan":
                base_inventory = int(base_inventory * rng.uniform(1.15, 1.50))

            if product_info["brand_owner"] == "Himaxx Own":
                base_inventory = int(base_inventory * rng.uniform(1.05, 1.30))

            beginning_inventory_units = int(base_inventory + rng.integers(0, 35))
            received_units = int(max(0, sold_units + rng.integers(-5, 40)))
            ending_inventory_units = max(0, beginning_inventory_units + received_units - sold_units)

            available_units = beginning_inventory_units + received_units
            sell_through_rate = sold_units / available_units if available_units > 0 else 0

            standard_cost = float(product_info["standard_cost"])
            inventory_value = round(ending_inventory_units * standard_cost, 2)

            if product_info["product_lifecycle"] == "Clearance":
                inventory_age_days = int(rng.integers(150, 450))
            elif store_info["store_format"] == "Pop-up Clearance Warehouse":
                inventory_age_days = int(rng.integers(100, 380))
            elif product_info["brand"] == "Cole Haan":
                inventory_age_days = int(rng.integers(90, 330))
            else:
                inventory_age_days = int(rng.integers(20, 240))

            avg_inventory_units = (beginning_inventory_units + ending_inventory_units) / 2
            avg_inventory_value = avg_inventory_units * standard_cost
            gmroi = gross_profit / avg_inventory_value if avg_inventory_value > 0 else 0

            avg_weekly_sales = sold_units / 4 if sold_units > 0 else 0
            weeks_of_supply = ending_inventory_units / avg_weekly_sales if avg_weekly_sales > 0 else 999

            stockout_flag = 1 if ending_inventory_units <= 3 and sold_units > 5 else 0
            overstock_flag = 1 if weeks_of_supply > 12 or inventory_age_days > 240 else 0
            clearance_flag = 1 if product_info["clearance_flag"] == 1 or inventory_age_days > 300 else 0

            if stockout_flag == 1 and gmroi > 2:
                replenishment_recommendation = "Replenish"
            elif overstock_flag == 1 and sell_through_rate < 0.25:
                replenishment_recommendation = "Clearance"
            elif gmroi > 3 and sell_through_rate > 0.45:
                replenishment_recommendation = "Main Push"
            elif gmroi < 1:
                replenishment_recommendation = "Stop Replenishment"
            else:
                replenishment_recommendation = "Monitor"

            inventory_rows.append({
                "snapshot_month": month.date(),
                "store_id": store_id,
                "channel": CHANNEL_NAME,
                "store_format": store_info["store_format"],
                "sku": sku,
                "brand_owner": product_info["brand_owner"],
                "brand": product_info["brand"],
                "brand_tier": product_info["brand_tier"],
                "category": product_info["category"],
                "business_mode": product_info["business_mode"],
                "inventory_risk_owner": product_info["inventory_risk_owner"],
                "beginning_inventory_units": beginning_inventory_units,
                "received_units": received_units,
                "sold_units": sold_units,
                "ending_inventory_units": ending_inventory_units,
                "available_units": available_units,
                "standard_cost": round(standard_cost, 2),
                "inventory_value": inventory_value,
                "inventory_age_days": inventory_age_days,
                "sell_through_rate": round(sell_through_rate, 4),
                "sales_revenue": round(sales_revenue, 2),
                "gross_profit": round(gross_profit, 2),
                "cogs": round(cogs, 2),
                "avg_inventory_value": round(avg_inventory_value, 2),
                "gmroi": round(gmroi, 4),
                "weeks_of_supply": round(weeks_of_supply, 2),
                "stockout_flag": stockout_flag,
                "overstock_flag": overstock_flag,
                "clearance_flag": clearance_flag,
                "replenishment_recommendation": replenishment_recommendation
            })

inventory_fact = pd.DataFrame(inventory_rows)
inventory_fact.to_csv(PROJECT_PATH / "inventory_fact.csv", index=False)


# ============================================================
# 8. Generate product_action_fact.csv
# ============================================================

product_action_base = (
    inventory_fact
    .groupby(["snapshot_month", "sku", "brand", "category", "business_mode"], as_index=False)
    .agg(
        gross_profit=("gross_profit", "sum"),
        sales_revenue=("sales_revenue", "sum"),
        inventory_value=("inventory_value", "sum"),
        sold_units=("sold_units", "sum"),
        ending_inventory_units=("ending_inventory_units", "sum"),
        sell_through_rate=("sell_through_rate", "mean"),
        inventory_age_days=("inventory_age_days", "mean"),
        gmroi=("gmroi", "mean"),
        weeks_of_supply=("weeks_of_supply", "mean")
    )
)

product_action_base["gross_margin_pct"] = (
    product_action_base["gross_profit"] /
    product_action_base["sales_revenue"].replace(0, np.nan)
).replace([np.inf, -np.inf], np.nan).fillna(0)

margin_median = product_action_base["gross_margin_pct"].median()
sell_through_median = product_action_base["sell_through_rate"].median()


def assign_quadrant(row):
    high_margin = row["gross_margin_pct"] >= margin_median
    high_sell = row["sell_through_rate"] >= sell_through_median

    if high_margin and high_sell:
        return "High Margin + High Sell-through"
    elif high_margin and not high_sell:
        return "High Margin + Low Sell-through"
    elif not high_margin and high_sell:
        return "Low Margin + High Sell-through"
    else:
        return "Low Margin + Low Sell-through"


product_action_base["quadrant_label"] = product_action_base.apply(assign_quadrant, axis=1)


def assign_action(row):
    if row["quadrant_label"] == "High Margin + High Sell-through":
        if row["weeks_of_supply"] < 6:
            return "Main Push / Replenish"
        else:
            return "Main Push / Monitor Inventory"

    elif row["quadrant_label"] == "High Margin + Low Sell-through":
        return "Targeted Marketing / Control Inventory"

    elif row["quadrant_label"] == "Low Margin + High Sell-through":
        return "Traffic Driver / Control Discount"

    elif row["quadrant_label"] == "Low Margin + Low Sell-through":
        if row["inventory_age_days"] > 240 or row["weeks_of_supply"] > 16:
            return "Clearance / Eliminate"
        else:
            return "Monitor / Limited Markdown"

    else:
        return "Monitor"


def assign_priority(row):
    if row["recommended_action"] in ["Clearance / Eliminate", "Main Push / Replenish"]:
        return "High"
    elif row["recommended_action"] in [
        "Targeted Marketing / Control Inventory",
        "Traffic Driver / Control Discount",
        "Monitor / Limited Markdown"
    ]:
        return "Medium"
    else:
        return "Low"


product_action_base["recommended_action"] = product_action_base.apply(assign_action, axis=1)
product_action_base["action_priority"] = product_action_base.apply(assign_priority, axis=1)

product_action_fact = product_action_base
product_action_fact.to_csv(PROJECT_PATH / "product_action_fact.csv", index=False)


# ============================================================
# 9. Generate cost_fact.csv
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

        royalty_rate = 0
        if product_info["brand"] in ["Brooks Brothers", "Reebok Underwear"]:
            royalty_rate = rng.uniform(0.03, 0.08)

        royalty_cost = float(product_info["msrp"]) * royalty_rate

        landed_cost = (
            standard_cost * (1 + inbound_freight_rate)
            + packaging_cost
            + handling_cost
            + product_development_cost
        )

        unit_economic_cost = landed_cost + royalty_cost

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
            "royalty_rate": round(royalty_rate, 4),
            "royalty_cost_per_unit": round(royalty_cost, 2),
            "landed_cost_per_unit": round(landed_cost, 2),
            "unit_economic_cost": round(unit_economic_cost, 2)
        })

cost_fact = pd.DataFrame(cost_rows)
cost_fact.to_csv(PROJECT_PATH / "cost_fact.csv", index=False)


# ============================================================
# 10. Generate finance_fact.csv
# ============================================================

monthly_store_sales = (
    sales_fact
    .groupby(["store_id", "channel", "store_format", "month"], as_index=False)
    .agg(
        orders=("order_id", "nunique"),
        gmv=("gmv", "sum"),
        msrp_gmv=("msrp_gmv", "sum"),
        transaction_gmv=("transaction_gmv", "sum"),
        gross_sales=("gross_sales", "sum"),
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
        "msrp_gmv": row["msrp_gmv"],
        "transaction_gmv": row["transaction_gmv"],
        "gross_sales": row["gross_sales"],
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
                "msrp_gmv": 0.0,
                "transaction_gmv": 0.0,
                "gross_sales": 0.0,
                "net_sales": 0.0,
                "recognized_revenue": 0.0,
                "cogs": 0.0,
                "gross_profit": 0.0
            }
        )

        orders = int(data["orders"])
        gmv = float(data["gmv"])
        msrp_gmv = float(data["msrp_gmv"])
        transaction_gmv = float(data["transaction_gmv"])
        gross_sales = float(data["gross_sales"])
        net_sales = float(data["net_sales"])
        recognized_revenue = float(data["recognized_revenue"])
        cogs = float(data["cogs"])
        gross_profit = float(data["gross_profit"])

        profile = store_info["profit_profile"]
        cost_pressure = float(store_info["cost_pressure_index"])
        staff_count = int(store_info["staff_count"])

        if gross_profit <= 0:
            total_opex = rng.uniform(20000, 80000) * cost_pressure
        else:
            if profile == "High Profit":
                opex_ratio = rng.uniform(0.15, 0.40)
            elif profile == "Stable":
                opex_ratio = rng.uniform(0.45, 0.80)
            elif profile == "At Risk":
                opex_ratio = rng.uniform(0.95, 1.30)
            else:
                opex_ratio = rng.uniform(1.35, 2.00)

            fixed_cost = rng.uniform(20000, 80000) * cost_pressure
            total_opex = gross_profit * opex_ratio + fixed_cost

        rent_pct = rng.uniform(0.18, 0.28)
        payroll_pct = rng.uniform(0.28, 0.40)
        utilities_pct = rng.uniform(0.04, 0.08)
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

        store_direct_costs = rent_expense + payroll_expense + utilities_expense + local_marketing_expense

        store_cm = gross_profit - store_direct_costs
        store_cm_pct = store_cm / recognized_revenue if recognized_revenue > 0 else 0

        market_contribution = store_cm - logistics_expense - warehouse_expense
        ebitda_proxy = market_contribution - hq_sga - brand_marketing_expense

        gross_margin_pct = gross_profit / recognized_revenue if recognized_revenue > 0 else 0

        bep_revenue = (
            store_direct_costs / gross_margin_pct
            if recognized_revenue > 0 and gross_margin_pct > 0
            else 0
        )

        rent_to_sales_ratio = rent_expense / recognized_revenue if recognized_revenue > 0 else 0
        payroll_to_sales_ratio = payroll_expense / recognized_revenue if recognized_revenue > 0 else 0
        sales_per_staff = recognized_revenue / staff_count if staff_count > 0 else 0

        finance_rows.append({
            "month": month.date(),
            "store_id": store_id,
            "channel": CHANNEL_NAME,
            "store_format": store_info["store_format"],
            "region": store_info["region"],
            "city": store_info["city"],
            "profit_profile": profile,
            "staff_count": staff_count,
            "orders": orders,
            "gmv": round(gmv, 2),
            "msrp_gmv": round(msrp_gmv, 2),
            "transaction_gmv": round(transaction_gmv, 2),
            "gross_sales": round(gross_sales, 2),
            "net_sales": round(net_sales, 2),
            "recognized_revenue": round(recognized_revenue, 2),
            "cogs": round(cogs, 2),
            "gross_profit": round(gross_profit, 2),
            "gross_margin_pct": round(gross_margin_pct, 4),
            "rent_expense": round(rent_expense, 2),
            "payroll_expense": round(payroll_expense, 2),
            "utilities_expense": round(utilities_expense, 2),
            "local_marketing_expense": round(local_marketing_expense, 2),
            "logistics_expense": round(logistics_expense, 2),
            "warehouse_expense": round(warehouse_expense, 2),
            "hq_sga": round(hq_sga, 2),
            "brand_marketing_expense": round(brand_marketing_expense, 2),
            "total_opex": round(total_opex_final, 2),
            "store_direct_costs": round(store_direct_costs, 2),
            "store_cm": round(store_cm, 2),
            "store_cm_pct": round(store_cm_pct, 4),
            "market_contribution": round(market_contribution, 2),
            "ebitda_proxy": round(ebitda_proxy, 2),
            "operating_profit": round(operating_profit, 2),
            "operating_margin": round(operating_margin, 4),
            "bep_revenue": round(bep_revenue, 2),
            "rent_to_sales_ratio": round(rent_to_sales_ratio, 4),
            "payroll_to_sales_ratio": round(payroll_to_sales_ratio, 4),
            "sales_per_staff": round(sales_per_staff, 2)
        })

finance_fact = pd.DataFrame(finance_rows)
finance_fact.to_csv(PROJECT_PATH / "finance_fact.csv", index=False)


# ============================================================
# 11. Generate store_target_fact.csv
# Monthly store-level operating targets
# ============================================================

# Target should be generated from actual monthly operating baselines,
# not independently from store area. Otherwise all stores become Critical.
# This makes the target table useful for weekly driver diagnosis:
# actual vs target can reveal whether the gap is traffic, CVR, UPT, AUR, or margin.
store_traffic_fact["month"] = pd.to_datetime(store_traffic_fact["date"]).values.astype("datetime64[M]")

monthly_store_funnel = (
    store_traffic_fact
    .groupby(["store_id", "month"], as_index=False)
    .agg(
        traffic=("traffic", "sum"),
        orders=("orders", "sum"),
        gross_units=("gross_units", "sum"),
        gmv=("gmv", "sum"),
    )
)
monthly_store_funnel["actual_order_cvr"] = monthly_store_funnel["orders"] / monthly_store_funnel["traffic"].replace(0, np.nan)
monthly_store_funnel["actual_upt"] = monthly_store_funnel["gross_units"] / monthly_store_funnel["orders"].replace(0, np.nan)
monthly_store_funnel["actual_aur"] = monthly_store_funnel["gmv"] / monthly_store_funnel["gross_units"].replace(0, np.nan)
monthly_store_funnel = monthly_store_funnel.replace([np.inf, -np.inf], np.nan).fillna(0)

monthly_funnel_lookup = {
    (row["store_id"], row["month"]): {
        "traffic": row["traffic"],
        "actual_order_cvr": row["actual_order_cvr"],
        "actual_upt": row["actual_upt"],
        "actual_aur": row["actual_aur"],
    }
    for _, row in monthly_store_funnel.iterrows()
}

target_rows = []

for month in MONTHS:
    for store_id in store_ids:
        store_info = store_lookup[store_id]
        cost_pressure = float(store_info["cost_pressure_index"])

        actual_finance = monthly_store_lookup.get(
            (store_id, month),
            {
                "gmv": 0.0,
                "recognized_revenue": 0.0,
                "gross_profit": 0.0,
            },
        )
        actual_funnel = monthly_funnel_lookup.get(
            (store_id, month),
            {
                "traffic": 0,
                "actual_order_cvr": 0.08,
                "actual_upt": 1.7,
                "actual_aur": 160,
            },
        )

        actual_revenue = float(actual_finance["recognized_revenue"])
        actual_gmv = float(actual_finance["gmv"])
        actual_gross_profit = float(actual_finance["gross_profit"])
        actual_margin = actual_gross_profit / actual_revenue if actual_revenue > 0 else rng.uniform(0.30, 0.45)

        # Target stretch is intentionally mixed to create realistic achievement distribution.
        # Better stores receive slightly more stretch, weaker stores get attainable but still challenging targets.
        profile = store_info["profit_profile"]
        if profile == "High Profit":
            revenue_factor = rng.uniform(0.95, 1.25)
            traffic_factor = rng.uniform(0.95, 1.20)
        elif profile == "Stable":
            revenue_factor = rng.uniform(0.90, 1.18)
            traffic_factor = rng.uniform(0.90, 1.15)
        elif profile == "At Risk":
            revenue_factor = rng.uniform(0.85, 1.12)
            traffic_factor = rng.uniform(0.85, 1.12)
        else:
            revenue_factor = rng.uniform(0.80, 1.08)
            traffic_factor = rng.uniform(0.80, 1.08)

        target_recognized_revenue = max(actual_revenue * revenue_factor, 1000)
        target_gmv = max(actual_gmv * rng.uniform(0.92, 1.18), target_recognized_revenue)

        target_gross_margin_pct = float(np.clip(actual_margin * rng.uniform(0.92, 1.12), 0.25, 0.58))
        target_gross_profit = target_recognized_revenue * target_gross_margin_pct

        # Keep Store CM target as contextual monthly health target; it should not dominate weekly driver flags.
        target_store_cm = target_gross_profit * rng.uniform(0.15, 0.40) / max(cost_pressure, 0.1)

        actual_traffic = float(actual_funnel["traffic"])
        actual_cvr = float(actual_funnel["actual_order_cvr"])
        actual_upt = float(actual_funnel["actual_upt"])
        actual_aur = float(actual_funnel["actual_aur"])

        target_traffic = int(max(actual_traffic * traffic_factor, 100))
        target_order_cvr = float(np.clip(actual_cvr * rng.uniform(0.90, 1.15), 0.025, 0.18))
        target_upt = float(np.clip(actual_upt * rng.uniform(0.92, 1.12), 1.1, 3.2))
        target_aur = float(np.clip(actual_aur * rng.uniform(0.92, 1.12), 60, 350))

        target_rows.append({
            "month": month.date(),
            "store_id": store_id,
            "channel": CHANNEL_NAME,
            "store_format": store_info["store_format"],
            "region": store_info["region"],
            "city": store_info["city"],
            "target_gmv": round(target_gmv, 2),
            "target_recognized_revenue": round(target_recognized_revenue, 2),
            "target_gross_profit": round(target_gross_profit, 2),
            "target_gross_margin_pct": round(target_gross_margin_pct, 4),
            "target_store_cm": round(target_store_cm, 2),
            "target_traffic": target_traffic,
            "target_order_cvr": round(target_order_cvr, 4),
            "target_upt": round(target_upt, 4),
            "target_aur": round(target_aur, 2),
            "target_gmroi": round(rng.uniform(1.5, 4.5), 2),
        })

store_target_fact = pd.DataFrame(target_rows)
store_target_fact.to_csv(PROJECT_PATH / "store_target_fact.csv", index=False)


# ============================================================
# 12. Generate marketing_fact.csv
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

        if store_info["store_format"] == "Warehouse Outlet":
            primary_marketing_channel = rng.choice(["WeChat", "Member Coupon", "Local Community Ads"])
            spend_rate = rng.uniform(0.018, 0.050)
        elif store_info["store_format"] == "Pop-up Clearance Warehouse":
            primary_marketing_channel = rng.choice(["Xiaohongshu", "KOL Collaboration", "Member Coupon"])
            spend_rate = rng.uniform(0.030, 0.080)
        elif store_info["store_format"] == "Mall Warehouse":
            primary_marketing_channel = rng.choice(["Mall Promotion", "WeChat", "Offline Event"])
            spend_rate = rng.uniform(0.022, 0.060)
        else:
            primary_marketing_channel = rng.choice(["WeChat", "Offline Event", "Search Ads"])
            spend_rate = rng.uniform(0.020, 0.060)

        marketing_spend = max(3000, gmv * spend_rate)
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
# 13. Data quality checks
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
    "marketing_fact.csv": marketing_fact,
    "store_traffic_fact.csv": store_traffic_fact,
    "store_target_fact.csv": store_target_fact,
    "product_action_fact.csv": product_action_fact
}

for file_name, df in files.items():
    print(f"{file_name}: {df.shape[0]:,} rows, {df.shape[1]} columns")

print("\nFiles saved under:")
print(PROJECT_PATH.resolve())


print("\n================ Business Logic Checks ================")

print("\n1. Store profile profitability check:")
print(
    finance_fact
    .groupby("profit_profile")[["store_cm", "operating_profit", "ebitda_proxy"]]
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

print("\n4. Discount channel pricing check:")
print(
    sales_fact[[
        "discount_factor",
        "discount_depth",
        "cost_to_msrp_ratio",
        "price_cost_spread"
    ]]
    .describe()
    .round(4)
)

print("\n5. Top 10 brands by recognized revenue:")
print(
    sales_fact
    .groupby("brand")[["recognized_revenue", "gross_profit"]]
    .sum()
    .sort_values("recognized_revenue", ascending=False)
    .head(10)
    .round(2)
)

print("\n6. Inventory health check:")
print(
    inventory_fact[[
        "inventory_value",
        "sell_through_rate",
        "inventory_age_days",
        "gmroi",
        "weeks_of_supply"
    ]]
    .describe()
    .round(2)
)

print("\n7. Store traffic funnel check:")
print(
    store_traffic_fact[[
        "traffic",
        "member_uv",
        "orders",
        "traffic_to_order_cvr",
        "member_cvr",
        "upt",
        "aur"
    ]]
    .describe()
    .round(2)
)

print("\n8. Product action recommendation check:")
print(
    product_action_fact
    .groupby(["quadrant_label", "recommended_action"])["sku"]
    .count()
    .sort_values(ascending=False)
    .head(20)
)

print("\nDone. You can now build processed marts and connect CSV files to Tableau / PowerBI.")