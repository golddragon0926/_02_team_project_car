# =============================================
# DB 데이터 CSV로 내보내기
# =============================================

import pymysql
import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.db_config import DB_CONFIG

# 저장 경로
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

# =============================================
# 1. 유가 데이터
# =============================================
cursor.execute("""
    SELECT 
        o.price_date AS 날짜,
        r.region_name AS 지역,
        o.fuel_code AS 유종,
        o.price AS 가격
    FROM oil_price o
    JOIN region r ON o.region_id = r.region_id
    ORDER BY o.price_date, r.region_name
""")
oil_df = pd.DataFrame(cursor.fetchall(), columns=['날짜', '지역', '유종', '가격'])
oil_df.to_csv(f'{DATA_DIR}/oil_price.csv', index=False, encoding='utf-8-sig')
print(f"유가 데이터: {len(oil_df)}건 저장")

# =============================================
# 2. 차량 신규등록 데이터
# =============================================
cursor.execute("""
    SELECT 
        n.reg_year AS 연도,
        n.reg_month AS 월,
        r.region_name AS 지역,
        f.fuel_name AS 연료,
        n.vehicle_type AS 차종,
        n.count AS 등록대수
    FROM new_registration n
    JOIN region r ON n.region_id = r.region_id
    JOIN fuel_type f ON n.fuel_id = f.fuel_id
    ORDER BY n.reg_year, n.reg_month, r.region_name
""")
reg_df = pd.DataFrame(cursor.fetchall(), columns=['연도', '월', '지역', '연료', '차종', '등록대수'])
reg_df.to_csv(f'{DATA_DIR}/new_registration.csv', index=False, encoding='utf-8-sig')
print(f"차량등록 데이터: {len(reg_df)}건 저장")

# =============================================
# 3. 지역 데이터
# =============================================
cursor.execute("SELECT region_name FROM region WHERE region_id != 0 ORDER BY region_id")
region_df = pd.DataFrame(cursor.fetchall(), columns=['지역'])
region_df.to_csv(f'{DATA_DIR}/region.csv', index=False, encoding='utf-8-sig')
print(f"지역 데이터: {len(region_df)}건 저장")

conn.close()
print("\n✅ 모든 CSV 파일 저장 완료!")
print(f"저장 위치: {DATA_DIR}")
