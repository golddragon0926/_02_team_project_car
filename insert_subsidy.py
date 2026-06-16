#----------------------------------------------
# MySQL 저장 코드
#----------------------------------------------

import pymysql
import pandas as pd

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

# ① 기존 데이터 삭제
cursor.execute("DELETE FROM subsidy")
conn.commit()
print("기존 데이터 삭제 완료! ✅")

# ② CSV 읽기
df = pd.read_csv("보조금데이터.csv", encoding="utf-8-sig")
print(f"CSV 읽기 완료! 총 {len(df)}개 ✅")

# ③ 쉼표 제거 함수
def to_int(val):
    try:
        return int(str(val).replace(",", "").strip())
    except:
        return 0

# ④ 데이터 삽입
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

# ⑤ 확인
cursor.execute("SELECT COUNT(*) FROM subsidy")
count = cursor.fetchone()[0]
print(f"DB 저장된 총 데이터: {count}개")

cursor.execute("SELECT DISTINCT 시도 FROM subsidy")
sidos = [r[0] for r in cursor.fetchall()]
print(f"시도 목록: {sidos}")

conn.close()
print("\n완료! ✅")