#------------------------------------
# DB 조회 코드
#------------------------------------


import pymysql
import pandas as pd

# ① MySQL 연결
DB_CONFIG = {
    "host"    : "localhost",
    "user"    : "skn_ai",
    "password": "1234",
    "port"    : 3306,
    "db"      : "car_project",
    "charset" : "utf8mb4"
}

conn   = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()
print("MySQL 연결 성공! ✅")

# ② 전체 데이터 조회
print("\n=== 전체 데이터 ===")
cursor.execute("SELECT * FROM subsidy LIMIT 10")
rows = cursor.fetchall()
for row in rows:
    print(row)

# ③ 시도별 평균 보조금 조회
print("\n=== 시도별 평균 보조금 ===")
cursor.execute("""
    SELECT 시도, 
           ROUND(AVG(보조금), 0) AS 평균보조금,
           ROUND(AVG(국비), 0)   AS 평균국비,
           ROUND(AVG(지방비), 0) AS 평균지방비,
           COUNT(*)              AS 모델수
    FROM subsidy
    GROUP BY 시도
    ORDER BY 평균보조금 DESC
""")
rows = cursor.fetchall()
for row in rows:
    print(f"  {row[0]}: 평균 {row[1]}만원 (국비 {row[2]} + 지방비 {row[3]}) / {row[4]}개 모델")

# ④ 보조금 TOP 10 모델
print("\n=== 보조금 TOP 10 모델 ===")
cursor.execute("""
    SELECT 시도, 시군구, 제조사, 모델명, 보조금
    FROM subsidy
    ORDER BY 보조금 DESC
    LIMIT 10
""")
rows = cursor.fetchall()
for i, row in enumerate(rows):
    print(f"  {i+1}위. {row[0]} {row[1]} | {row[2]} {row[3]} | {row[4]}만원")

# ⑤ 제조사별 모델 수
print("\n=== 제조사별 모델 수 ===")
cursor.execute("""
    SELECT 제조사, COUNT(DISTINCT 모델명) AS 모델수
    FROM subsidy
    GROUP BY 제조사
    ORDER BY 모델수 DESC
    LIMIT 10
""")
rows = cursor.fetchall()
for row in rows:
    print(f"  {row[0]}: {row[1]}개 모델")

conn.close()
print("\n조회 완료! ✅")
