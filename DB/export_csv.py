"""
car_oil_db의 테이블들을 data/ 폴더의 CSV로 다시 export하는 스크립트
(DB 접근 권한 없는 팀원들도 Streamlit을 CSV 기반으로 돌릴 수 있게 하기 위함)

사용법:
    python export_csv.py
"""

import os
import pymysql
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "car_oil_db"),
    "charset": "utf8mb4",
}

BASE_PATH = os.getcwd()
DATA_PATH = os.path.join(BASE_PATH, "../data")
os.makedirs(DATA_PATH, exist_ok=True)

# region.csv의 풀네임 -> sido 축약형 (subsidy export에서 사용)
FULLNAME_TO_SIDO = {
    "서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구", "인천광역시": "인천",
    "광주광역시": "광주", "대전광역시": "대전", "울산광역시": "울산", "세종특별자치시": "세종",
    "경기도": "경기", "강원도": "강원", "충청북도": "충북", "충청남도": "충남",
    "전라북도": "전북", "전라남도": "전남", "경상북도": "경북", "경상남도": "경남",
    "제주특별자치도": "제주",
}


def run_query(cursor, sql):
    cursor.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)


def export_region(cursor):
    df = run_query(cursor, "SELECT region_name AS 지역 FROM Region ORDER BY region_id")
    path = os.path.join(DATA_PATH, "region.csv")
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"✅ region.csv 저장 완료 ({len(df)}건)")


def export_oil_price(cursor):
    sql = """
        SELECT o.price_date AS 날짜, r.region_name AS 지역, o.fuel_code AS 유종, o.price AS 가격
        FROM Oil_price o
        JOIN Region r ON o.region_id = r.region_id
        ORDER BY o.price_date, r.region_name, o.fuel_code
    """
    df = run_query(cursor, sql)
    path = os.path.join(DATA_PATH, "oil_price.csv")
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"✅ oil_price.csv 저장 완료 ({len(df)}건)")


def export_new_registration(cursor):
    sql = """
        SELECT n.reg_year AS 연도, n.reg_month AS 월, r.region_name AS 지역,
               f.fuel_name AS 연료, n.vehicle_type AS 차종, n.count AS 등록대수
        FROM New_Registration n
        JOIN Region r ON n.region_id = r.region_id
        JOIN Fuel_Type f ON n.fuel_id = f.fuel_id
        ORDER BY n.reg_year, n.reg_month, r.region_name
    """
    df = run_query(cursor, sql)
    path = os.path.join(DATA_PATH, "new_registration.csv")
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"✅ new_registration.csv 저장 완료 ({len(df)}건)")


def export_subsidy(cursor):
    sql = """
        SELECT s.year, r.region_name AS region_name_full, s.sigungu, s.vehicle_type,
               s.manufacturer, s.model_name, s.national_subsidy, s.local_subsidy, s.total_subsidy
        FROM Subsidy s
        JOIN Region r ON s.region_id = r.region_id
        ORDER BY s.year, r.region_name
    """
    df = run_query(cursor, sql)
    df["sido"] = df["region_name_full"].map(FULLNAME_TO_SIDO)
    df = df[["year", "sido", "sigungu", "vehicle_type", "manufacturer",
             "model_name", "national_subsidy", "local_subsidy", "total_subsidy"]]
    path = os.path.join(DATA_PATH, "subsidy.csv")
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"✅ subsidy.csv 저장 완료 ({len(df)}건)")


def export_faq(cursor):
    df = run_query(cursor, "SELECT brand, title, content, category FROM FAQ ORDER BY id")
    path = os.path.join(DATA_PATH, "faq.csv")
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"✅ faq.csv 저장 완료 ({len(df)}건)")


def main():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        export_region(cursor)
        export_oil_price(cursor)
        export_new_registration(cursor)
        export_subsidy(cursor)
        export_faq(cursor)
        print("\n🎉 전체 CSV export 완료!")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
