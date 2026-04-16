import pandas as pd
import mysql.connector

# 1. 读 CSV
df = pd.read_csv("/Users/jincheng/Desktop/Data_Science/Data_Analytics/dataprojects/Data_Analyst_Bootcamp/Data_Cleaning/Data_Project_Layoffs/layoffs.csv")

# Replace NaN with None for the entire DataFrame
df = df.replace({pd.NA: None, pd.NaT: None, float('nan'): None})

# 2. 连接 MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="sjc990809",
    database="world_layoffs"
)
cursor = conn.cursor()

# 3. 插入数据
for _, row in df.iterrows():
    print(tuple(row))  # Debugging: Print the row being inserted
    cursor.execute("""
        INSERT INTO layoffs (company, location, industry, total_laid_off, percentage_laid_off, date, stage, country, funds_raised_millions) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, tuple(row))

conn.commit()
cursor.close()
conn.close()