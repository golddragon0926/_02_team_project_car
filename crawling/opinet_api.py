# =============================================
# 오피넷 유가 데이터 수집 코드 (수정본)
# =============================================

import requests
import pymysql
from datetime import datetime, timedelta
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db_config import OPINET_API_KEY, DB_CONFIG

# =============================================
# 1. 전국 평균 유가 수집
# =============================================
def get_national_oil_price(date_str):
    url = "http://www.opinet.co.kr/api/avgAllPrice.do"
    params = {
        "code": OPINET_API_KEY,
        "date": date_str,
        "out" : "json"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        # 응답 구조 디버깅 (처음 한 번만 확인용)
        if date_str == "20220101":
            print(f"[DEBUG] 응답 구조: {data}")

        result = data.get("RESULT", {}).get("OIL", [])
        print(f"[전국] {date_str} → {len(result)}개 수집")
        return result
    except Exception as e:
        print(f"[오류] 전국 유가 수집 실패 ({date_str}): {e}")
        return []


# =============================================
# 2. 시도별 평균 유가 수집
# =============================================
def get_region_oil_price(date_str):
    url = "http://www.opinet.co.kr/api/avgSidoPrice.do"
    params = {
        "code": OPINET_API_KEY,
        "date": date_str,
        "out" : "json"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        result = data.get("RESULT", {}).get("OIL", [])
        print(f"[시도별] {date_str} → {len(result)}개 수집")
        return result
    except Exception as e:
        print(f"[오류] 시도별 유가 수집 실패 ({date_str}): {e}")
        return []


# =============================================
# 3. DB 저장 - 전국 유가
# =============================================
def save_national_price(conn, date_str, oil_list):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT IGNORE INTO region (region_id, region_code, region_name)
        VALUES (0, '00', '전국')
    """)

    price_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

    fuel_map = {
        "B027": "GAS",
        "D047": "DSL",
        "K015": "LPG",
    }

    count = 0
    for oil in oil_list:
        fuel_code = fuel_map.get(oil.get("PRODCD"), None)
        if not fuel_code:
            continue
        price = oil.get("PRICE", 0)

        cursor.execute("""
            INSERT INTO oil_price (price_date, region_id, fuel_code, price)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE price = VALUES(price)
        """, (price_date, 0, fuel_code, price))
        count += 1

    conn.commit()
    print(f"[저장] 전국 유가 {count}건")


# =============================================
# 4. DB 저장 - 시도별 유가
# =============================================
def save_region_price(conn, date_str, oil_list):
    cursor = conn.cursor()
    price_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

    sido_map = {
        "01": "11",  # 서울
        "02": "26",  # 부산
        "03": "27",  # 대구
        "04": "28",  # 인천
        "05": "29",  # 광주
        "06": "30",  # 대전
        "07": "31",  # 울산
        "08": "36",  # 세종
        "09": "41",  # 경기
        "10": "42",  # 강원
        "11": "43",  # 충북
        "12": "44",  # 충남
        "13": "45",  # 전북
        "14": "46",  # 전남
        "15": "47",  # 경북
        "16": "48",  # 경남
        "17": "50",  # 제주
    }

    fuel_map = {
        "B027": "GAS",
        "D047": "DSL",
        "K015": "LPG",
    }

    count = 0
    for oil in oil_list:
        fuel_code    = fuel_map.get(oil.get("PRODCD"), None)
        region_code  = sido_map.get(oil.get("SIDOCD"), None)
        price        = oil.get("PRICE", 0)

        if not fuel_code or not region_code:
            continue

        cursor.execute(
            "SELECT region_id FROM region WHERE region_code = %s",
            (region_code,)
        )
        row = cursor.fetchone()
        if not row:
            continue
        region_id = row[0]

        cursor.execute("""
            INSERT INTO oil_price (price_date, region_id, fuel_code, price)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE price = VALUES(price)
        """, (price_date, region_id, fuel_code, price))
        count += 1

    conn.commit()
    print(f"[저장] 시도별 유가 {count}건")


# =============================================
# 5. API 응답 구조 테스트 (먼저 실행해서 확인)
# =============================================
def test_api_response():
    print("=" * 40)
    print("API 응답 구조 테스트")
    print("=" * 40)

    test_dates = ["20240101", "20230101", "20220101", "20210101"]

    for date in test_dates:
        url = "http://www.opinet.co.kr/api/avgAllPrice.do"
        params = {"code": OPINET_API_KEY, "date": date, "out": "json"}
        try:
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            oil_list = data.get("RESULT", {}).get("OIL", [])
            print(f"{date} → {len(oil_list)}개 | 응답: {str(data)[:100]}")
        except Exception as e:
            print(f"{date} → 오류: {e}")

    print("=" * 40)


# =============================================
# 6. 기간별 수집 실행 (메인 함수)
# =============================================
def collect_oil_price(start_date, end_date):
    conn = pymysql.connect(**DB_CONFIG)
    print(f"DB 연결 성공!")
    print(f"수집 기간: {start_date} ~ {end_date}")
    print("=" * 40)

    current = datetime.strptime(start_date, "%Y%m%d")
    end     = datetime.strptime(end_date,   "%Y%m%d")

    total = 0
    while current <= end:
        date_str = current.strftime("%Y%m%d")

        national = get_national_oil_price(date_str)
        if national:
            save_national_price(conn, date_str, national)
            total += len(national)

        region = get_region_oil_price(date_str)
        if region:
            save_region_price(conn, date_str, region)
            total += len(region)

        current += timedelta(days=1)
        time.sleep(0.3)  # API 과부하 방지

    conn.close()
    print("=" * 40)
    print(f"수집 완료! 총 {total}건")


# =============================================
# 실행
# =============================================
if __name__ == "__main__":

    # ① 먼저 API 응답 테스트 실행
    test_api_response()

    # ② 테스트 결과 확인 후 아래 주석 해제해서 실행
    # collect_oil_price(
    #     start_date="20220101",
    #     end_date="20261231"
    # )