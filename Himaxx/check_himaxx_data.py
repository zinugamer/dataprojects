import pandas as pd
from pathlib import Path

DATA_PATH = Path("/Users/jincheng/Desktop/Data_Science/03_Data_Analytics/dataprojects/Himaxx/Himaxx_Intelligent_Operating_System/02_data/raw")

files = [
    "sales_fact.csv",
    "inventory_fact.csv",
    "product_dim.csv",
    "store_dim.csv",
    "customer_dim.csv",
    "cost_fact.csv",
    "finance_fact.csv",
    "marketing_fact.csv"
]

for file in files:
    df = pd.read_csv(DATA_PATH / file)
    print("\n" + "=" * 60)
    print(file)
    print("shape:", df.shape)
    print("columns:", list(df.columns))
    print("missing values:")
    print(df.isna().sum()[df.isna().sum() > 0])
    print("sample:")
    print(df.head(3))