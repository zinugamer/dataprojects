import pandas as pd
import mysql.connector

# 1. 读 CSV
df = pd.read_csv("/Users/jincheng/Desktop/Data_Science/03_Data_Analytics/dataprojects/Himaxx/weekly_report_0426/himaxx_opns_0426.csv")

# 添加报告周期字段
df["report_month"] = "2026-04-01"
df["report_week_end"] = "2026-04-26"

# Replace NaN with None for the entire DataFrame
df = df.replace({pd.NA: None, pd.NaT: None, float('nan'): None})

# 2. 连接 MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="sjc990809",
    database="himaxx_bi"
)
cursor = conn.cursor()

# 3. 插入数据
for _, row in df.iterrows():
    print(tuple(row))  # Debugging: Print the row being inserted
    cursor.execute("""
        INSERT INTO staging_store_weekly_summary (store_number, store_type, store_level, store_name, open_date, annual_bep, strategic_brand, annual_target_sales, annual_actual_sales, yoy_annual_sales, monthly_target_sales, monthly_target_traffic, monthly_target_trans_num_ppl, monthly_target_cr, monthly_target_atv, monthly_actual_sales, monthly_actual_traffic, monthly_actual_new_traffic, monthly_actual_cr, monthly_actual_trans_num_ppl, monthly_actual_atv, yoy_monthly_sales, yoy_monthly_traffic, yoy_monthly_new_traffic, yoy_monthly_cr, yoy_monthly_trans_num_ppl, yoy_monthly_atv, yoy_monthly_sales_pct, yoy_monthly_traffic_pct, yoy_monthly_cr_pct, yoy_monthly_atv_pct, report_month, report_week_end) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, tuple(row))

conn.commit()
cursor.close()
conn.close()