#----------------------------------------------
# MySQL 저장 코드
#----------------------------------------------

import pymysql
import pandas as pd
import os
import sys

# 절대경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from config.db_config import DB_CONFIG

conn   = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()
print("MySQL 연결 성공! ✅")

# 기존 데이터 삭제
cursor.execute("DELETE FROM subsidy")
conn.commit()
print("기존 데이터 삭제 완료! ✅")

# CSV 읽기
csv_path = os.path.join(BASE_DIR, "data", "보조금데이터.csv")
print(f"CSV 경로: {csv_path}")
df = pd.read_csv(csv_path, encoding="cp949")
print(f"CSV 읽기 완료! 총 {len(df)}개 ✅")

# 쉼표 제거 함수
def to_int(val):
    try:
        return int(str(val).replace(",", "").strip())
    except:
        return 0

# 데이터 삽입
success = 0
fail    = 0

for _, row in df.iterrows():
    try:
        cursor.execute("""
            INSERT INTO subsidy
            (연도, 시도, 시군구, 차종, 제조사, 모델명, 국비, 지방비, 보조금)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            str(row["연도"]),
            str(row["시도"]),
            str(row["시군구"]),
            str(row["차종"]),
            str(row["제조사"]),
            str(row["모델명"]),
            to_int(row["국비(만원)"]),
            to_int(row["지방비(만원)"]),
            to_int(row["보조금(만원)"])
        ))
        success += 1
    except Exception as e:
        fail += 1
        print(f"  삽입 실패: {e}")

conn.commit()
print(f"\n삽입 완료! 성공: {success}개 / 실패: {fail}개 ✅")

# 연도별 확인
cursor.execute("SELECT 연도, COUNT(*) FROM subsidy GROUP BY 연도")
rows = cursor.fetchall()
print("\n=== 연도별 데이터 수 ===")
for row in rows:
    print(f"{row[0]}년: {row[1]}개")

conn.close()
print("\n완료! ✅")
