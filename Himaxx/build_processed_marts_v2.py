# ============================================================
# Himaxx Intelligent Operating Dashboard V3
# Processed Mart Builder
#
# Input:
#   Himaxx_Intelligent_Operating_System/02_data/raw/
#
# Output:
#   Himaxx_Intelligent_Operating_System/02_data/processed/
#
# Generated marts:
#   1. store_pnl_mart.csv
#   2. store_funnel_mart.csv
#   3. store_target_achievement_mart.csv
#   4. brand_product_mart.csv
#   5. inventory_gmroi_mart.csv
#   6. product_quadrant_mart.csv
#   7. brand_scorecard_mart.csv
#   8. risk_warning_mart.csv
# ============================================================

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd


# ============================================================
# 0. Path setup
# ============================================================

BASE_DIR = Path(
    "/Users/jincheng/Desktop/Data_Science/03_Data_Analytics/dataprojects/Himaxx/"
    "Himaxx_Intelligent_Operating_System"
)

RAW_DIR = BASE_DIR / "02_data" / "raw"
PROCESSED_DIR = BASE_DIR / "02_data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

print(f"Raw input path: {RAW_DIR}")
print(f"Processed output path: {PROCESSED_DIR}")


# ============================================================
# 1. Helper functions
# ============================================================

def read_csv_required(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return pd.read_csv(path)


def safe_divide(numerator, denominator):
    """Safely divide Series or scalar values. Returns 0 where denominator is 0/NaN/inf."""
    if isinstance(numerator, pd.Series) or isinstance(denominator, pd.Series):
        num = numerator if isinstance(numerator, pd.Series) else pd.Series(numerator, index=denominator.index)
        den = denominator if isinstance(denominator, pd.Series) else pd.Series(denominator, index=numerator.index)
        result = num / den.replace(0, np.nan)
        return result.replace([np.inf, -np.inf], np.nan).fillna(0)
    if denominator in [0, None] or pd.isna(denominator):
        return 0
    result = numerator / denominator
    return 0 if pd.isna(result) or np.isinf(result) else result


def clean_numeric(df: pd.DataFrame) -> pd.DataFrame:
    df = df.replace([np.inf, -np.inf], np.nan)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    return df


def clean_object_na(df: pd.DataFrame) -> pd.DataFrame:
    object_cols = df.select_dtypes(include=["object"]).columns
    df[object_cols] = df[object_cols].fillna("")
    return df


def percentile_score(series: pd.Series, reverse: bool = False) -> pd.Series:
    """Convert a numeric Series into 0-100 percentile scores."""
    s = series.replace([np.inf, -np.inf], np.nan).fillna(0)
    if s.nunique() <= 1:
        return pd.Series([50.0] * len(s), index=s.index)
    score = s.rank(pct=True) * 100
    if reverse:
        score = 100 - score
    return score.round(2)


def weighted_average(df: pd.DataFrame, value_col: str, weight_col: str) -> float:
    if df.empty or value_col not in df or weight_col not in df:
        return 0.0
    weights = df[weight_col].replace([np.inf, -np.inf], np.nan).fillna(0)
    values = df[value_col].replace([np.inf, -np.inf], np.nan).fillna(0)
    if weights.sum() == 0:
        return float(values.mean()) if len(values) else 0.0
    return float(np.average(values, weights=weights))


def print_mart(name: str, df: pd.DataFrame) -> None:
    print("\n" + "=" * 90)
    print(f"{name}: {df.shape[0]:,} rows, {df.shape[1]} columns")
    print(df.head())
    print("=" * 90)


def to_month(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series).values.astype("datetime64[M]")


def save_mart(df: pd.DataFrame, filename: str) -> None:
    df = clean_numeric(df.copy())
    df = clean_object_na(df)
    df.to_csv(PROCESSED_DIR / filename, index=False)
    print_mart(filename, df)


# ============================================================
# 2. Load raw tables
# ============================================================

sales_fact = read_csv_required(RAW_DIR / "sales_fact.csv")
inventory_fact = read_csv_required(RAW_DIR / "inventory_fact.csv")
product_dim = read_csv_required(RAW_DIR / "product_dim.csv")
store_dim = read_csv_required(RAW_DIR / "store_dim.csv")
customer_dim = read_csv_required(RAW_DIR / "customer_dim.csv")
cost_fact = read_csv_required(RAW_DIR / "cost_fact.csv")
finance_fact = read_csv_required(RAW_DIR / "finance_fact.csv")
marketing_fact = read_csv_required(RAW_DIR / "marketing_fact.csv")
store_traffic_fact = read_csv_required(RAW_DIR / "store_traffic_fact.csv")
store_target_fact = read_csv_required(RAW_DIR / "store_target_fact.csv")
product_action_fact = read_csv_required(RAW_DIR / "product_action_fact.csv")

# Normalize dates
sales_fact["date"] = pd.to_datetime(sales_fact["date"])
store_traffic_fact["date"] = pd.to_datetime(store_traffic_fact["date"])

for df, col in [
    (finance_fact, "month"),
    (store_target_fact, "month"),
    (marketing_fact, "month"),
    (cost_fact, "month"),
]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col])

inventory_fact["snapshot_month"] = pd.to_datetime(inventory_fact["snapshot_month"])
product_action_fact["snapshot_month"] = pd.to_datetime(product_action_fact["snapshot_month"])

sales_fact["month"] = to_month(sales_fact["date"])
store_traffic_fact["month"] = to_month(store_traffic_fact["date"])

# Ensure V3 fields exist even if old raw files are accidentally used
if "gross_sales" not in sales_fact.columns:
    sales_fact["gross_sales"] = sales_fact.get("transaction_gmv", sales_fact.get("gmv", 0))
if "transaction_gmv" not in sales_fact.columns:
    sales_fact["transaction_gmv"] = sales_fact.get("gmv", 0)
if "msrp_gmv" not in sales_fact.columns:
    sales_fact["msrp_gmv"] = sales_fact.get("msrp", 0) * sales_fact.get("gross_units", 0)
if "discount_factor" not in sales_fact.columns:
    sales_fact["discount_factor"] = safe_divide(sales_fact["transaction_gmv"], sales_fact["msrp_gmv"])
if "discount_depth" not in sales_fact.columns:
    sales_fact["discount_depth"] = 1 - sales_fact["discount_factor"]
if "cost_to_msrp_ratio" not in sales_fact.columns:
    sales_fact["cost_to_msrp_ratio"] = safe_divide(sales_fact.get("cogs", 0), sales_fact.get("msrp_gmv", 0))
if "price_cost_spread" not in sales_fact.columns:
    sales_fact["price_cost_spread"] = sales_fact["discount_factor"] - sales_fact["cost_to_msrp_ratio"]


# ============================================================
# 3. store_pnl_mart.csv
# ============================================================

store_attributes_cols = [
    "store_id",
    "store_name",
    "store_size_sqm",
    "staff_count",
    "store_maturity",
    "trade_area_type",
]
store_attributes = store_dim[[c for c in store_attributes_cols if c in store_dim.columns]].drop_duplicates("store_id")

# If finance_fact is missing V3 gross fields, backfill from sales_fact monthly aggregates
monthly_sales_for_finance = (
    sales_fact.groupby(["month", "store_id"], as_index=False)
    .agg(
        gmv=("gmv", "sum"),
        msrp_gmv=("msrp_gmv", "sum"),
        transaction_gmv=("transaction_gmv", "sum"),
        gross_sales=("gross_sales", "sum"),
        net_sales=("net_sales", "sum"),
        recognized_revenue=("recognized_revenue", "sum"),
        cogs=("cogs", "sum"),
        gross_profit=("gross_profit", "sum"),
    )
)

finance_base = finance_fact.copy()
for col in ["gmv", "msrp_gmv", "transaction_gmv", "gross_sales", "net_sales"]:
    if col not in finance_base.columns:
        finance_base = finance_base.merge(
            monthly_sales_for_finance[["month", "store_id", col]],
            on=["month", "store_id"],
            how="left",
        )

store_pnl_mart = finance_base.merge(store_attributes, on="store_id", how="left")

if "staff_count" not in store_pnl_mart.columns:
    store_pnl_mart["staff_count"] = np.maximum((store_pnl_mart["store_size_sqm"] / 250).round(), 20)

store_pnl_mart["sales_per_sqm"] = safe_divide(
    store_pnl_mart["recognized_revenue"], store_pnl_mart["store_size_sqm"]
)
store_pnl_mart["sales_per_staff"] = safe_divide(
    store_pnl_mart["recognized_revenue"], store_pnl_mart["staff_count"]
)
store_pnl_mart["gross_profit_per_staff"] = safe_divide(
    store_pnl_mart["gross_profit"], store_pnl_mart["staff_count"]
)
store_pnl_mart["store_cm_per_staff"] = safe_divide(
    store_pnl_mart["store_cm"], store_pnl_mart["staff_count"]
)

store_pnl_mart["store_health_flag"] = np.select(
    [
        (store_pnl_mart["store_cm"] > 0) & (store_pnl_mart["store_cm_pct"] >= 0.10),
        (store_pnl_mart["store_cm"] > 0) & (store_pnl_mart["store_cm_pct"] < 0.10),
        (store_pnl_mart["store_cm"] <= 0),
    ],
    ["Healthy", "Watch", "Loss Making"],
    default="Unknown",
)
store_pnl_mart["rent_pressure_flag"] = np.where(
    store_pnl_mart["rent_to_sales_ratio"] > 0.20, "High Rent Pressure", "Normal"
)
store_pnl_mart["payroll_pressure_flag"] = np.where(
    store_pnl_mart["payroll_to_sales_ratio"] > 0.18, "High Payroll Pressure", "Normal"
)
store_pnl_mart["bep_gap"] = store_pnl_mart["recognized_revenue"] - store_pnl_mart["bep_revenue"]

store_pnl_cols = [
    "month", "store_id", "store_name", "city", "region", "channel", "store_format",
    "profit_profile", "store_size_sqm", "staff_count", "store_maturity", "trade_area_type",
    "gmv", "msrp_gmv", "transaction_gmv", "gross_sales", "net_sales",
    "recognized_revenue", "cogs", "gross_profit", "gross_margin_pct",
    "rent_expense", "payroll_expense", "utilities_expense", "local_marketing_expense",
    "store_direct_costs", "store_cm", "store_cm_pct", "market_contribution",
    "ebitda_proxy", "operating_profit", "operating_margin", "bep_revenue",
    "rent_to_sales_ratio", "payroll_to_sales_ratio", "sales_per_sqm", "sales_per_staff",
    "gross_profit_per_staff", "store_cm_per_staff", "store_health_flag", "rent_pressure_flag",
    "payroll_pressure_flag", "bep_gap",
]
store_pnl_mart = store_pnl_mart[[c for c in store_pnl_cols if c in store_pnl_mart.columns]]
save_mart(store_pnl_mart, "store_pnl_mart.csv")


# ============================================================
# 4. store_funnel_mart.csv
# ============================================================

store_funnel_mart = (
    store_traffic_fact.groupby(
        ["month", "store_id", "channel", "store_format", "region", "city"], as_index=False
    )
    .agg(
        traffic=("traffic", "sum"),
        member_uv=("member_uv", "sum"),
        new_member_uv=("new_member_uv", "sum"),
        returning_member_uv=("returning_member_uv", "sum"),
        assisted_visits=("assisted_visits", "sum"),
        try_on_count=("try_on_count", "sum"),
        orders=("orders", "sum"),
        buyers=("buyers", "sum"),
        gross_units=("gross_units", "sum"),
        gmv=("gmv", "sum"),
        recognized_revenue=("recognized_revenue", "sum"),
    )
)
store_funnel_mart = store_funnel_mart.merge(
    store_dim[["store_id", "store_name"]].drop_duplicates("store_id"), on="store_id", how="left"
)
store_funnel_mart["traffic_to_order_cvr"] = safe_divide(store_funnel_mart["orders"], store_funnel_mart["traffic"])
store_funnel_mart["member_cvr"] = safe_divide(store_funnel_mart["buyers"], store_funnel_mart["member_uv"])
store_funnel_mart["try_on_cvr"] = safe_divide(store_funnel_mart["orders"], store_funnel_mart["try_on_count"])
store_funnel_mart["upt"] = safe_divide(store_funnel_mart["gross_units"], store_funnel_mart["orders"])
store_funnel_mart["aur"] = safe_divide(store_funnel_mart["gmv"], store_funnel_mart["gross_units"])

store_funnel_cols = [
    "month", "store_id", "store_name", "city", "region", "channel", "store_format",
    "traffic", "member_uv", "new_member_uv", "returning_member_uv", "assisted_visits",
    "try_on_count", "orders", "buyers", "gross_units", "gmv", "recognized_revenue",
    "traffic_to_order_cvr", "member_cvr", "try_on_cvr", "upt", "aur",
]
store_funnel_mart = store_funnel_mart[store_funnel_cols]
save_mart(store_funnel_mart, "store_funnel_mart.csv")


# ============================================================
# 5. store_target_achievement_mart.csv
# ============================================================

achievement = store_pnl_mart[
    [
        "month", "store_id", "store_name", "city", "region", "channel", "store_format",
        "recognized_revenue", "gross_profit", "gross_margin_pct", "store_cm",
    ]
].merge(
    store_funnel_mart[["month", "store_id", "traffic", "traffic_to_order_cvr", "upt", "aur"]],
    on=["month", "store_id"],
    how="left",
).merge(
    store_target_fact[
        [
            "month", "store_id", "target_recognized_revenue", "target_gross_profit",
            "target_gross_margin_pct", "target_store_cm", "target_traffic",
            "target_order_cvr", "target_upt", "target_aur",
        ]
    ],
    on=["month", "store_id"],
    how="left",
)

achievement["revenue_achievement_rate"] = safe_divide(achievement["recognized_revenue"], achievement["target_recognized_revenue"])
achievement["gross_profit_achievement_rate"] = safe_divide(achievement["gross_profit"], achievement["target_gross_profit"])
achievement["gross_margin_gap"] = achievement["gross_margin_pct"] - achievement["target_gross_margin_pct"]
achievement["store_cm_achievement_rate"] = safe_divide(achievement["store_cm"], achievement["target_store_cm"])
achievement["traffic_achievement_rate"] = safe_divide(achievement["traffic"], achievement["target_traffic"])
achievement["cvr_gap"] = achievement["traffic_to_order_cvr"] - achievement["target_order_cvr"]
achievement["upt_gap"] = achievement["upt"] - achievement["target_upt"]
achievement["aur_gap"] = achievement["aur"] - achievement["target_aur"]

# Weekly operating achievement should be driven by controllable operating drivers,
# not by structural P&L items such as rent/payroll/Store CM. Store CM remains as context.
achievement_score = (
    0.50 * achievement["revenue_achievement_rate"]
    + 0.30 * achievement["gross_profit_achievement_rate"]
    + 0.20 * achievement["traffic_achievement_rate"]
)

achievement["achievement_flag"] = np.select(
    [
        achievement_score >= 1.05,
        achievement_score >= 0.90,
        achievement_score >= 0.75,
        achievement_score < 0.75,
    ],
    ["Exceed Target", "On Track", "Behind Target", "Critical"],
    default="Unknown",
)

store_target_achievement_cols = [
    "month", "store_id", "store_name", "city", "region", "channel", "store_format",
    "recognized_revenue", "target_recognized_revenue", "revenue_achievement_rate",
    "gross_profit", "target_gross_profit", "gross_profit_achievement_rate",
    "gross_margin_pct", "target_gross_margin_pct", "gross_margin_gap",
    "store_cm", "target_store_cm", "store_cm_achievement_rate",
    "traffic", "target_traffic", "traffic_achievement_rate",
    "traffic_to_order_cvr", "target_order_cvr", "cvr_gap",
    "upt", "target_upt", "upt_gap", "aur", "target_aur", "aur_gap",
    "achievement_flag",
]
store_target_achievement_mart = achievement[store_target_achievement_cols]
save_mart(store_target_achievement_mart, "store_target_achievement_mart.csv")


# ============================================================
# 6. brand_product_mart.csv
# ============================================================

brand_product_mart = (
    sales_fact.groupby(["brand", "brand_owner", "brand_tier", "category", "business_mode"], as_index=False)
    .agg(
        msrp_gmv=("msrp_gmv", "sum"),
        transaction_gmv=("transaction_gmv", "sum"),
        gross_sales=("gross_sales", "sum"),
        gmv=("gmv", "sum"),
        net_sales=("net_sales", "sum"),
        recognized_revenue=("recognized_revenue", "sum"),
        cogs=("cogs", "sum"),
        gross_profit=("gross_profit", "sum"),
        gross_units=("gross_units", "sum"),
        returned_units=("returned_units", "sum"),
        net_units=("net_units", "sum"),
        discount_amount=("discount_amount", "sum"),
        markdown_amount=("markdown_amount", "sum"),
        orders=("order_id", "nunique"),
        cost_to_msrp_ratio=("cost_to_msrp_ratio", "mean"),
    )
)

brand_product_mart["gross_margin_pct"] = safe_divide(brand_product_mart["gross_profit"], brand_product_mart["recognized_revenue"])
brand_product_mart["return_rate"] = safe_divide(brand_product_mart["returned_units"], brand_product_mart["gross_units"])
brand_product_mart["markdown_rate"] = safe_divide(brand_product_mart["markdown_amount"], brand_product_mart["msrp_gmv"])
brand_product_mart["discount_factor"] = safe_divide(brand_product_mart["transaction_gmv"], brand_product_mart["msrp_gmv"])
brand_product_mart["discount_depth"] = 1 - brand_product_mart["discount_factor"]
brand_product_mart["price_cost_spread"] = brand_product_mart["discount_factor"] - brand_product_mart["cost_to_msrp_ratio"]
brand_product_mart["net_aur"] = safe_divide(brand_product_mart["recognized_revenue"], brand_product_mart["net_units"])

total_revenue = brand_product_mart["recognized_revenue"].sum()
total_gp = brand_product_mart["gross_profit"].sum()
brand_product_mart["revenue_share"] = safe_divide(brand_product_mart["recognized_revenue"], pd.Series(total_revenue, index=brand_product_mart.index))
brand_product_mart["gross_profit_share"] = safe_divide(brand_product_mart["gross_profit"], pd.Series(total_gp, index=brand_product_mart.index))

brand_product_cols = [
    "brand", "brand_owner", "brand_tier", "category", "business_mode",
    "msrp_gmv", "transaction_gmv", "gross_sales", "gmv", "net_sales", "recognized_revenue",
    "cogs", "gross_profit", "gross_margin_pct", "gross_units", "returned_units",
    "net_units", "return_rate", "discount_amount", "markdown_amount", "discount_depth",
    "discount_factor", "cost_to_msrp_ratio", "price_cost_spread", "markdown_rate",
    "net_aur", "orders", "revenue_share", "gross_profit_share",
]
brand_product_mart = brand_product_mart[brand_product_cols]
save_mart(brand_product_mart, "brand_product_mart.csv")


# ============================================================
# 7. inventory_gmroi_mart.csv
# ============================================================

inventory_gmroi_mart = (
    inventory_fact.groupby(
        [
            "snapshot_month", "store_id", "channel", "store_format", "brand", "brand_tier",
            "category", "business_mode", "inventory_risk_owner",
        ],
        as_index=False,
    )
    .agg(
        avg_inventory_value=("avg_inventory_value", "mean"),
        inventory_value=("inventory_value", "sum"),
        ending_inventory_units=("ending_inventory_units", "sum"),
        sold_units=("sold_units", "sum"),
        recognized_revenue=("sales_revenue", "sum"),
        gross_profit=("gross_profit", "sum"),
        cogs=("cogs", "sum"),
        inventory_age_days=("inventory_age_days", "mean"),
        weeks_of_supply=("weeks_of_supply", "mean"),
        stockout_rate=("stockout_flag", "mean"),
        overstock_rate=("overstock_flag", "mean"),
        clearance_rate=("clearance_flag", "mean"),
    )
)

inventory_gmroi_mart["gmroi"] = safe_divide(inventory_gmroi_mart["gross_profit"], inventory_gmroi_mart["avg_inventory_value"])
inventory_gmroi_mart["inventory_turnover"] = safe_divide(inventory_gmroi_mart["cogs"], inventory_gmroi_mart["avg_inventory_value"])
inventory_gmroi_mart["sales_to_inventory_ratio"] = safe_divide(inventory_gmroi_mart["recognized_revenue"], inventory_gmroi_mart["avg_inventory_value"])
inventory_gmroi_mart["sell_through_rate"] = safe_divide(
    inventory_gmroi_mart["sold_units"], inventory_gmroi_mart["sold_units"] + inventory_gmroi_mart["ending_inventory_units"]
)

inventory_gmroi_mart["inventory_risk_flag"] = np.select(
    [
        (inventory_gmroi_mart["gmroi"] < 1)
        | (inventory_gmroi_mart["sell_through_rate"] < 0.25)
        | (inventory_gmroi_mart["inventory_age_days"] > 300)
        | (inventory_gmroi_mart["weeks_of_supply"] > 16),
        (inventory_gmroi_mart["gmroi"] < 2)
        | (inventory_gmroi_mart["sell_through_rate"] < 0.40)
        | (inventory_gmroi_mart["inventory_age_days"] > 180)
        | (inventory_gmroi_mart["weeks_of_supply"] > 10),
    ],
    ["High Risk", "Medium Risk"],
    default="Low Risk",
)

inventory_gmroi_cols = [
    "snapshot_month", "store_id", "channel", "store_format", "brand", "brand_tier",
    "category", "business_mode", "inventory_risk_owner", "avg_inventory_value",
    "inventory_value", "ending_inventory_units", "sold_units", "recognized_revenue",
    "gross_profit", "cogs", "gmroi", "inventory_turnover", "sales_to_inventory_ratio",
    "sell_through_rate", "inventory_age_days", "weeks_of_supply", "stockout_rate",
    "overstock_rate", "clearance_rate", "inventory_risk_flag",
]
inventory_gmroi_mart = inventory_gmroi_mart[inventory_gmroi_cols]
save_mart(inventory_gmroi_mart, "inventory_gmroi_mart.csv")


# ============================================================
# 8. product_quadrant_mart.csv
# ============================================================

sku_discount = (
    sales_fact.groupby("sku", as_index=False)
    .agg(
        msrp_gmv=("msrp_gmv", "sum"),
        transaction_gmv=("transaction_gmv", "sum"),
        cost_to_msrp_ratio=("cost_to_msrp_ratio", "mean"),
    )
)
sku_discount["discount_factor"] = safe_divide(sku_discount["transaction_gmv"], sku_discount["msrp_gmv"])
sku_discount["discount_depth"] = 1 - sku_discount["discount_factor"]
sku_discount["price_cost_spread"] = sku_discount["discount_factor"] - sku_discount["cost_to_msrp_ratio"]

product_quadrant_mart = product_action_fact.merge(
    product_dim[
        [
            "sku", "brand_tier", "price_band", "gender_segment", "style_type",
            "core_or_seasonal", "clearance_flag", "replenishable_flag",
        ]
    ].drop_duplicates("sku"),
    on="sku",
    how="left",
).merge(
    sku_discount[["sku", "discount_factor", "discount_depth", "cost_to_msrp_ratio", "price_cost_spread"]],
    on="sku",
    how="left",
)

if "quadrant_label" not in product_quadrant_mart.columns:
    margin_median = product_quadrant_mart["gross_margin_pct"].median()
    sell_median = product_quadrant_mart["sell_through_rate"].median()
    product_quadrant_mart["quadrant_label"] = np.select(
        [
            (product_quadrant_mart["gross_margin_pct"] >= margin_median) & (product_quadrant_mart["sell_through_rate"] >= sell_median),
            (product_quadrant_mart["gross_margin_pct"] >= margin_median) & (product_quadrant_mart["sell_through_rate"] < sell_median),
            (product_quadrant_mart["gross_margin_pct"] < margin_median) & (product_quadrant_mart["sell_through_rate"] >= sell_median),
            (product_quadrant_mart["gross_margin_pct"] < margin_median) & (product_quadrant_mart["sell_through_rate"] < sell_median),
        ],
        [
            "High Margin + High Sell-through",
            "High Margin + Low Sell-through",
            "Low Margin + High Sell-through",
            "Low Margin + Low Sell-through",
        ],
        default="Unknown",
    )

for col, default in [("recommended_action", "Monitor"), ("action_priority", "Low")]:
    if col not in product_quadrant_mart.columns:
        product_quadrant_mart[col] = default

product_quadrant_cols = [
    "snapshot_month", "sku", "brand", "brand_tier", "category", "business_mode",
    "price_band", "gender_segment", "style_type", "core_or_seasonal", "clearance_flag",
    "replenishable_flag", "gross_margin_pct", "sell_through_rate", "gmroi",
    "inventory_value", "sold_units", "ending_inventory_units", "inventory_age_days",
    "weeks_of_supply", "discount_factor", "discount_depth", "cost_to_msrp_ratio",
    "price_cost_spread", "quadrant_label", "recommended_action", "action_priority",
]
product_quadrant_mart = product_quadrant_mart[product_quadrant_cols]
save_mart(product_quadrant_mart, "product_quadrant_mart.csv")


# ============================================================
# 9. brand_scorecard_mart.csv
# ============================================================

brand_sales = (
    brand_product_mart.groupby(["brand", "brand_owner", "brand_tier"], as_index=False)
    .agg(
        recognized_revenue=("recognized_revenue", "sum"),
        gross_profit=("gross_profit", "sum"),
        revenue_share=("revenue_share", "sum"),
        gross_profit_share=("gross_profit_share", "sum"),
        gross_units=("gross_units", "sum"),
        returned_units=("returned_units", "sum"),
        markdown_amount=("markdown_amount", "sum"),
        msrp_gmv=("msrp_gmv", "sum"),
        transaction_gmv=("transaction_gmv", "sum"),
        discount_factor=("discount_factor", "mean"),
        discount_depth=("discount_depth", "mean"),
        price_cost_spread=("price_cost_spread", "mean"),
    )
)
brand_sales["gross_margin_pct"] = safe_divide(brand_sales["gross_profit"], brand_sales["recognized_revenue"])
brand_sales["return_rate"] = safe_divide(brand_sales["returned_units"], brand_sales["gross_units"])
brand_sales["markdown_rate"] = safe_divide(brand_sales["markdown_amount"], brand_sales["msrp_gmv"])

brand_inventory = (
    inventory_gmroi_mart.groupby("brand", as_index=False)
    .agg(
        gmroi=("gmroi", "mean"),
        sell_through_rate=("sell_through_rate", "mean"),
        inventory_value=("inventory_value", "sum"),
        inventory_age_days=("inventory_age_days", "mean"),
        weeks_of_supply=("weeks_of_supply", "mean"),
    )
)

mode_revenue = brand_product_mart.pivot_table(
    index="brand", columns="business_mode", values="recognized_revenue", aggfunc="sum", fill_value=0
).reset_index()
for col in ["Buyout", "Consignment", "Own Brand"]:
    if col not in mode_revenue.columns:
        mode_revenue[col] = 0
mode_revenue["total_mode_revenue"] = mode_revenue["Buyout"] + mode_revenue["Consignment"] + mode_revenue["Own Brand"]
mode_revenue["buyout_revenue_share"] = safe_divide(mode_revenue["Buyout"], mode_revenue["total_mode_revenue"])
mode_revenue["consignment_revenue_share"] = safe_divide(mode_revenue["Consignment"], mode_revenue["total_mode_revenue"])
mode_revenue["own_brand_revenue_share"] = safe_divide(mode_revenue["Own Brand"], mode_revenue["total_mode_revenue"])

brand_scorecard_mart = brand_sales.merge(brand_inventory, on="brand", how="left").merge(
    mode_revenue[["brand", "buyout_revenue_share", "consignment_revenue_share", "own_brand_revenue_share"]],
    on="brand",
    how="left",
)
brand_scorecard_mart = clean_numeric(brand_scorecard_mart)

brand_scorecard_mart["revenue_score"] = percentile_score(brand_scorecard_mart["recognized_revenue"])
brand_scorecard_mart["margin_score"] = percentile_score(brand_scorecard_mart["gross_margin_pct"])
brand_scorecard_mart["gmroi_score"] = percentile_score(brand_scorecard_mart["gmroi"])
brand_scorecard_mart["inventory_score"] = percentile_score(brand_scorecard_mart["inventory_value"], reverse=True)
brand_scorecard_mart["markdown_score"] = percentile_score(brand_scorecard_mart["markdown_rate"], reverse=True)
brand_scorecard_mart["spread_score"] = percentile_score(brand_scorecard_mart["price_cost_spread"])

brand_scorecard_mart["final_brand_score"] = (
    0.22 * brand_scorecard_mart["revenue_score"]
    + 0.22 * brand_scorecard_mart["margin_score"]
    + 0.22 * brand_scorecard_mart["gmroi_score"]
    + 0.14 * brand_scorecard_mart["inventory_score"]
    + 0.10 * brand_scorecard_mart["markdown_score"]
    + 0.10 * brand_scorecard_mart["spread_score"]
).round(2)

brand_scorecard_mart["brand_tier_score_label"] = np.select(
    [
        brand_scorecard_mart["final_brand_score"] >= 80,
        brand_scorecard_mart["final_brand_score"] >= 60,
        brand_scorecard_mart["final_brand_score"] >= 40,
        brand_scorecard_mart["final_brand_score"] < 40,
    ],
    ["A", "B", "C", "D"],
    default="Unknown",
)

brand_scorecard_cols = [
    "brand", "brand_owner", "brand_tier", "recognized_revenue", "gross_profit",
    "gross_margin_pct", "revenue_share", "gross_profit_share", "gmroi",
    "sell_through_rate", "inventory_value", "inventory_age_days", "weeks_of_supply",
    "return_rate", "markdown_rate", "discount_factor", "discount_depth",
    "price_cost_spread", "buyout_revenue_share", "consignment_revenue_share",
    "own_brand_revenue_share", "revenue_score", "margin_score", "gmroi_score",
    "inventory_score", "markdown_score", "spread_score", "final_brand_score",
    "brand_tier_score_label",
]
brand_scorecard_mart = brand_scorecard_mart[brand_scorecard_cols]
save_mart(brand_scorecard_mart, "brand_scorecard_mart.csv")


# ============================================================
# 10. risk_warning_mart.csv
# ============================================================

risk_rows: List[Dict] = []
risk_counter = 1


def add_risk(
    risk_type: str,
    entity_type: str,
    entity_name: str,
    month_or_snapshot,
    channel: Optional[str],
    store_id: Optional[str],
    brand: Optional[str],
    sku: Optional[str],
    key_metric: str,
    metric_value,
    risk_level: str,
    risk_reason: str,
    recommended_action: str,
    owner_department: str,
) -> None:
    global risk_counter
    risk_rows.append(
        {
            "risk_id": f"RISK{risk_counter:06d}",
            "risk_type": risk_type,
            "entity_type": entity_type,
            "entity_name": entity_name,
            "month_or_snapshot": month_or_snapshot,
            "channel": channel,
            "store_id": store_id,
            "brand": brand,
            "sku": sku,
            "key_metric": key_metric,
            "metric_value": round(float(metric_value), 4) if pd.notna(metric_value) else 0,
            "risk_level": risk_level,
            "risk_reason": risk_reason,
            "recommended_action": recommended_action,
            "owner_department": owner_department,
        }
    )
    risk_counter += 1


# 1. Negative Store CM
for _, row in store_pnl_mart[store_pnl_mart["store_cm"] < 0].iterrows():
    add_risk(
        "Negative Store CM", "Store", row["store_name"], row["month"], row["channel"], row["store_id"],
        None, None, "store_cm", row["store_cm"], "High",
        "Store contribution margin is negative.",
        "Review rent, payroll, gross margin, local marketing, and store positioning.",
        "Store Operations / Finance",
    )

# 2. High Rent Pressure
for _, row in store_pnl_mart[store_pnl_mart["rent_to_sales_ratio"] > 0.20].iterrows():
    add_risk(
        "High Rent Pressure", "Store", row["store_name"], row["month"], row["channel"], row["store_id"],
        None, None, "rent_to_sales_ratio", row["rent_to_sales_ratio"], "Medium",
        "Rent to sales ratio is above 20%.",
        "Renegotiate rent terms or review store format and location value.",
        "Store Operations / Leasing",
    )

# 3. High Payroll Pressure
for _, row in store_pnl_mart[store_pnl_mart["payroll_to_sales_ratio"] > 0.18].iterrows():
    add_risk(
        "High Payroll Pressure", "Store", row["store_name"], row["month"], row["channel"], row["store_id"],
        None, None, "payroll_to_sales_ratio", row["payroll_to_sales_ratio"], "Medium",
        "Payroll to sales ratio is above 18%.",
        "Review staff scheduling, sales productivity, commission structure, and labor allocation.",
        "Store Operations / HR",
    )

# 4. Behind Target Store
behind = store_target_achievement_mart[store_target_achievement_mart["achievement_flag"].isin(["Critical", "Behind Target"])]
for _, row in behind.iterrows():
    risk_level = "High" if row["achievement_flag"] == "Critical" else "Medium"
    add_risk(
        "Behind Target Store", "Store", row["store_name"], row["month"], row["channel"], row["store_id"],
        None, None, "revenue_achievement_rate", row["revenue_achievement_rate"], risk_level,
        f"Store achievement status is {row['achievement_flag']}.",
        "Review traffic, conversion, UPT, AUR, gross margin, and product mix gap.",
        "Store Operations",
    )

# 5. Low Traffic Conversion
cvr_q25 = store_funnel_mart["traffic_to_order_cvr"].quantile(0.25)
for _, row in store_funnel_mart[store_funnel_mart["traffic_to_order_cvr"] < cvr_q25].iterrows():
    add_risk(
        "Low Traffic Conversion", "Store", row["store_name"], row["month"], row["channel"], row["store_id"],
        None, None, "traffic_to_order_cvr", row["traffic_to_order_cvr"], "Medium",
        "Traffic-to-order conversion is below the 25th percentile.",
        "Review store display, sales associate training, try-on conversion, and promotion matching.",
        "Store Operations / Training",
    )

# 6. High Inventory Low GMROI
inventory_value_median = inventory_gmroi_mart["inventory_value"].median()
high_inventory_low_gmroi = inventory_gmroi_mart[(inventory_gmroi_mart["gmroi"] < 1) & (inventory_gmroi_mart["inventory_value"] > inventory_value_median)]
for _, row in high_inventory_low_gmroi.iterrows():
    add_risk(
        "High Inventory Low GMROI", "Brand-Store", f"{row['brand']} / {row['store_id']}", row["snapshot_month"],
        row["channel"], row["store_id"], row["brand"], None, "gmroi", row["gmroi"], "High",
        "Inventory value is high while GMROI is below 1.",
        "Stop replenishment, review buyout exposure, and prepare clearance or transfer plan.",
        "Merchandise / Supply Chain",
    )

# 7. Low Sell-through Product
for _, row in product_quadrant_mart[product_quadrant_mart["sell_through_rate"] < 0.25].iterrows():
    add_risk(
        "Low Sell-through Product", "SKU", row["sku"], row["snapshot_month"], None, None, row["brand"], row["sku"],
        "sell_through_rate", row["sell_through_rate"], "Medium",
        "SKU sell-through rate is below 25%.",
        "Review pricing, display, transfer, markdown, or clearance strategy.",
        "Merchandise",
    )

# 8. Clearance Candidate
clearance = product_quadrant_mart[product_quadrant_mart["recommended_action"] == "Clearance / Eliminate"]
for _, row in clearance.iterrows():
    add_risk(
        "Clearance Candidate", "SKU", row["sku"], row["snapshot_month"], None, None, row["brand"], row["sku"],
        "recommended_action", 1, "High",
        "SKU is recommended for clearance or elimination.",
        "Launch markdown, transfer inventory, or stop future replenishment.",
        "Merchandise / Store Operations",
    )

# 9. Low Price-Cost Spread
pqs_inventory_median = product_quadrant_mart["inventory_value"].median()
low_spread = product_quadrant_mart[(product_quadrant_mart["price_cost_spread"] < 0.03) & (product_quadrant_mart["inventory_value"] > pqs_inventory_median)]
for _, row in low_spread.iterrows():
    add_risk(
        "Low Price-Cost Spread", "SKU", row["sku"], row["snapshot_month"], None, None, row["brand"], row["sku"],
        "price_cost_spread", row["price_cost_spread"], "High",
        "SKU has low price-cost spread while holding above-median inventory value.",
        "Review sourcing cost, retail price, discount policy, and replenishment strategy.",
        "Merchandise / Pricing",
    )

# 10. Risk Brand
risk_brands = brand_scorecard_mart[brand_scorecard_mart["brand_tier_score_label"].isin(["C", "D"])]
for _, row in risk_brands.iterrows():
    risk_level = "High" if row["brand_tier_score_label"] == "D" else "Medium"
    add_risk(
        "Risk Brand", "Brand", row["brand"], None, None, None, row["brand"], None,
        "final_brand_score", row["final_brand_score"], risk_level,
        f"Brand score is {row['brand_tier_score_label']}.",
        "Review brand cooperation strategy, margin, inventory pressure, markdown pressure, price-cost spread, and business mode mix.",
        "Brand Management / Strategy",
    )

risk_warning_mart = pd.DataFrame(risk_rows)
risk_warning_cols = [
    "risk_id", "risk_type", "entity_type", "entity_name", "month_or_snapshot", "channel",
    "store_id", "brand", "sku", "key_metric", "metric_value", "risk_level",
    "risk_reason", "recommended_action", "owner_department",
]
risk_warning_mart = risk_warning_mart[risk_warning_cols]
save_mart(risk_warning_mart, "risk_warning_mart.csv")


# ============================================================
# 11. Final data quality checks
# ============================================================

print("\n" + "=" * 100)
print("All processed marts generated successfully.")
print(f"Output folder: {PROCESSED_DIR.resolve()}")
print("=" * 100)

print("\nRisk type counts:")
print(risk_warning_mart["risk_type"].value_counts())

print("\nOwner department risk counts:")
print(risk_warning_mart["owner_department"].value_counts())

print("\nData quality check: discount_factor distribution")
print(brand_product_mart["discount_factor"].describe().round(4))

print("\nData quality check: discount_depth distribution")
print(brand_product_mart["discount_depth"].describe().round(4))

print("\nData quality check: price_cost_spread distribution")
print(brand_product_mart["price_cost_spread"].describe().round(4))

print("\nStore health flag counts:")
print(store_pnl_mart["store_health_flag"].value_counts())

print("\nInventory risk flag counts:")
print(inventory_gmroi_mart["inventory_risk_flag"].value_counts())

print("\nBrand tier score label counts:")
print(brand_scorecard_mart["brand_tier_score_label"].value_counts())

print("\nGenerated files:")
for file in [
    "store_pnl_mart.csv",
    "store_funnel_mart.csv",
    "store_target_achievement_mart.csv",
    "brand_product_mart.csv",
    "inventory_gmroi_mart.csv",
    "product_quadrant_mart.csv",
    "brand_scorecard_mart.csv",
    "risk_warning_mart.csv",
]:
    print(f"- {file}")
