"""
원본 CSV(region.csv, oil_price.csv, new_registration.csv, subsidy.csv)를
car_oil_db의 Region / Fuel_Type / Oil_price / New_Registration / Subsidy
테이블에 적재하는 스크립트

사용법:
    python load_all_data.py
"""

import os
import csv
import pymysql
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

REGION_CSV = os.path.join(DATA_PATH, "region.csv")
OIL_PRICE_CSV = os.path.join(DATA_PATH, "oil_price.csv")
NEW_REG_CSV = os.path.join(DATA_PATH, "new_registration.csv")
SUBSIDY_CSV = os.path.join(DATA_PATH, "subsidy.csv")

# 17개 시도 표준 코드 (통계청/행안부 시도코드 기준)
REGION_CODE_MAP = {
    "서울특별시": "11", "부산광역시": "26", "대구광역시": "27", "인천광역시": "28",
    "광주광역시": "29", "대전광역시": "30", "울산광역시": "31", "세종특별자치시": "36",
    "경기도": "41", "강원도": "42", "충청북도": "43", "충청남도": "44",
    "전라북도": "45", "전라남도": "46", "경상북도": "47", "경상남도": "48",
    "제주특별자치도": "50",
}

# subsidy.csv의 축약형 sido -> region.csv 풀네임 매핑
SIDO_TO_FULLNAME = {
    "서울": "서울특별시", "부산": "부산광역시", "대구": "대구광역시", "인천": "인천광역시",
    "광주": "광주광역시", "대전": "대전광역시", "울산": "울산광역시", "세종": "세종특별자치시",
    "경기": "경기도", "강원": "강원도", "충북": "충청북도", "충남": "충청남도",
    "전북": "전라북도", "전남": "전라남도", "경북": "경상북도", "경남": "경상남도",
    "제주": "제주특별자치도",
}

# Fuel_Type 고정 5종 (fuel_code, fuel_name)
FUEL_TYPES = [
    ("GAS", "휘발유"),
    ("DSL", "경유"),
    ("ELC", "전기"),
    ("HEV", "하이브리드"),
    ("HYD", "수소"),
]

# new_registration.csv의 한글 연료명 -> fuel_code
FUEL_NAME_TO_CODE = {
    "휘발유": "GAS", "경유": "DSL", "전기": "ELC", "하이브리드": "HEV", "수소": "HYD",
}


def read_csv_rows(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_region(cursor):
    rows = read_csv_rows(REGION_CSV)
    region_id_map = {}  # region_name -> region_id

    for row in rows:
        name = row["지역"].strip()
        code = REGION_CODE_MAP.get(name)
        if not code:
            print(f"⚠️ region_code 매핑 없음, 스킵: {name}")
            continue
        cursor.execute(
            "INSERT INTO Region (region_code, region_name) VALUES (%s, %s)",
            (code, name),
        )
        region_id_map[name] = cursor.lastrowid

    print(f"✅ Region 적재 완료: {len(region_id_map)}건")
    return region_id_map


def load_fuel_type(cursor):
    fuel_id_map = {}  # fuel_code -> fuel_id

    for fuel_code, fuel_name in FUEL_TYPES:
        cursor.execute(
            "INSERT INTO Fuel_Type (fuel_code, fuel_name) VALUES (%s, %s)",
            (fuel_code, fuel_name),
        )
        fuel_id_map[fuel_code] = cursor.lastrowid

    print(f"✅ Fuel_Type 적재 완료: {len(fuel_id_map)}건")
    return fuel_id_map


def load_oil_price(cursor, region_id_map):
    rows = read_csv_rows(OIL_PRICE_CSV)
    insert_rows = []
    skipped = 0

    for row in rows:
        region_name = row["지역"].strip()
        region_id = region_id_map.get(region_name)
        if region_id is None:
            skipped += 1
            continue
        insert_rows.append((
            region_id,
            row["날짜"].strip(),
            row["유종"].strip(),
            float(row["가격"]),
        ))

    cursor.executemany(
        """INSERT INTO Oil_price (region_id, price_date, fuel_code, price)
           VALUES (%s, %s, %s, %s)""",
        insert_rows,
    )
    print(f"✅ Oil_price 적재 완료: {len(insert_rows)}건 (스킵 {skipped}건)")


def load_new_registration(cursor, region_id_map, fuel_id_map):
    rows = read_csv_rows(NEW_REG_CSV)
    insert_rows = []
    skipped = 0

    for row in rows:
        vehicle_type = row["차종"].strip()
        if vehicle_type != "승용":
            skipped += 1
            continue

        region_name = row["지역"].strip()
        fuel_name = row["연료"].strip()
        region_id = region_id_map.get(region_name)
        fuel_code = FUEL_NAME_TO_CODE.get(fuel_name)
        fuel_id = fuel_id_map.get(fuel_code) if fuel_code else None

        if region_id is None or fuel_id is None:
            skipped += 1
            continue

        insert_rows.append((
            region_id,
            fuel_id,
            int(row["연도"]),
            int(row["월"]),
            row["차종"].strip(),
            int(row["등록대수"]),
        ))

    cursor.executemany(
        """INSERT INTO New_Registration
           (region_id, fuel_id, reg_year, reg_month, vehicle_type, count)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        insert_rows,
    )
    print(f"✅ New_Registration 적재 완료: {len(insert_rows)}건 (스킵 {skipped}건)")


def load_subsidy(cursor, region_id_map):
    rows = read_csv_rows(SUBSIDY_CSV)
    insert_rows = []
    skipped = 0

    for row in rows:
        sido = row["sido"].strip()
        full_name = SIDO_TO_FULLNAME.get(sido)
        region_id = region_id_map.get(full_name) if full_name else None

        if region_id is None:
            skipped += 1  # 예: '공단'(한국환경공단) 등 지역 매핑 불가 행
            continue

        insert_rows.append((
            region_id,
            int(row["year"]),
            row["sigungu"].strip(),
            row["vehicle_type"].strip(),
            row["manufacturer"].strip(),
            row["model_name"].strip(),
            float(row["national_subsidy"]),
            float(row["local_subsidy"]),
            float(row["total_subsidy"]),
        ))

    cursor.executemany(
        """INSERT INTO Subsidy
           (region_id, year, sigungu, vehicle_type, manufacturer, model_name,
            national_subsidy, local_subsidy, total_subsidy)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        insert_rows,
    )
    print(f"✅ Subsidy 적재 완료: {len(insert_rows)}건 (스킵 {skipped}건, 지역 매핑 불가)")


def main():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 기존 데이터 초기화 (재실행 대비) - FK 역순으로 비움
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for table in ["Subsidy", "Oil_price", "New_Registration", "Fuel_Type", "Region"]:
            cursor.execute(f"TRUNCATE TABLE {table}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        region_id_map = load_region(cursor)
        fuel_id_map = load_fuel_type(cursor)
        load_oil_price(cursor, region_id_map)
        load_new_registration(cursor, region_id_map, fuel_id_map)
        load_subsidy(cursor, region_id_map)

        conn.commit()
        print("\n🎉 전체 데이터 적재 완료!")

    except Exception as e:
        conn.rollback()
        print(f"❌ 에러 발생, 롤백됨: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
