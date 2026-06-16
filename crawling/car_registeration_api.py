# =============================================
# 한국교통안전공단 신규등록 데이터 수집 코드
# =============================================

import requests
import pymysql
import time
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db_config import PUBLIC_API_KEY, DB_CONFIG

# =============================================
# 코드 매핑
# =============================================

# 지역 코드 (API → DB region_id)
REGION_MAP = {
    '1' : ('11', '서울특별시'),
    '2' : ('26', '부산광역시'),
    '3' : ('27', '대구광역시'),
    '4' : ('28', '인천광역시'),
    '5' : ('29', '광주광역시'),
    '6' : ('30', '대전광역시'),
    '7' : ('31', '울산광역시'),
    '8' : ('36', '세종특별자치시'),
    '9' : ('41', '경기도'),
    '10': ('42', '강원도'),
    '11': ('43', '충청북도'),
    '12': ('44', '충청남도'),
    '13': ('45', '전라북도'),
    '14': ('46', '전라남도'),
    '15': ('47', '경상북도'),
    '16': ('48', '경상남도'),
    '17': ('50', '제주특별자치도'),
}

# 연료 코드 (5개)
FUEL_MAP = {
    '2' : 'DSL',  # 경유
    '3' : 'HYD',  # 수소
    '5' : 'ELC',  # 전기
    '7' : 'HEV',  # 하이브리드
    '8' : 'GAS',  # 휘발유
}

# 차종 코드 (승용만)
VEHICLE_MAP = {
    '1': '승용',
}

# =============================================
# API 호출
# =============================================
def get_new_registration(year, month, region_code, fuel_code, vehicle_code):
    url = 'https://apis.data.go.kr/B553881/newRegistlnfoService_02/getnewRegistlnfoService02'
    params = f'serviceKey={PUBLIC_API_KEY}&registYy={year}&registMt={str(month).zfill(2)}&registGrcCode={region_code}&useFuelCode={fuel_code}&vhctyAsortCode={vehicle_code}'
    full_url = f'{url}?{params}'

    try:
        r = requests.get(full_url, timeout=10)
        if r.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(r.text)
            result_code = root.find('.//resultCode').text
            if result_code == '00':
                dta_co = root.find('.//dtaCo')
                return int(dta_co.text) if dta_co is not None else 0
        elif r.status_code == 401:
            print(f'[경고] 트래픽 한도 초과! 수집 중단')
            return None
        return 0
    except Exception as e:
        print(f'[오류] {year}-{month} 지역:{region_code} 연료:{fuel_code} → {e}')
        return 0


# =============================================
# DB 저장
# =============================================
def save_registration(conn, year, month, region_id, fuel_id, vehicle_type, count):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO new_registration 
                (reg_year, reg_month, region_id, fuel_id, vehicle_type, count)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE count = VALUES(count)
        """, (year, month, region_id, fuel_id, vehicle_type, count))
        conn.commit()
    except Exception as e:
        print(f'[DB오류] {e}')


# =============================================
# region_id, fuel_id 조회
# =============================================
def get_ids(conn, region_code, fuel_code):
    cursor = conn.cursor()
    cursor.execute("SELECT region_id FROM region WHERE region_code = %s", (region_code,))
    region_row = cursor.fetchone()

    cursor.execute("SELECT fuel_id FROM fuel_type WHERE fuel_code = %s", (fuel_code,))
    fuel_row = cursor.fetchone()

    if region_row and fuel_row:
        return region_row[0], fuel_row[0]
    return None, None


# =============================================
# 메인 수집 함수
# =============================================
def collect_new_registration(start_year, end_year, start_month=1, end_month=12):
    conn = pymysql.connect(**DB_CONFIG)
    print(f'DB 연결 성공!')
    print(f'수집 기간: {start_year}년 {start_month}월 ~ {end_year}년 {end_month}월')
    print('=' * 50)

    total = 0
    errors = 0

    for year in range(start_year, end_year + 1):
        # 시작/종료 월 처리
        m_start = start_month if year == start_year else 1
        m_end   = end_month   if year == end_year   else 12

        for month in range(m_start, m_end + 1):

            # 미래 날짜 스킵
            now = datetime.now()
            if year > now.year or (year == now.year and month > now.month):
                continue

            for region_code, (db_region_code, region_name) in REGION_MAP.items():
                for fuel_code, db_fuel_code in FUEL_MAP.items():
                    for vehicle_code, vehicle_type in VEHICLE_MAP.items():

                        count = get_new_registration(
                            year, month, region_code, fuel_code, vehicle_code
                        )

                        # 트래픽 한도 초과시 중단
                        if count is None:
                            conn.close()
                            print(f'[중단] 총 {total}건 저장 완료')
                            return

                        region_id, fuel_id = get_ids(conn, db_region_code, db_fuel_code)

                        if region_id and fuel_id:
                            save_registration(
                                conn, year, month,
                                region_id, fuel_id,
                                vehicle_type, count
                            )
                            total += 1
                            print(f'[{year}-{str(month).zfill(2)}] {region_name} {db_fuel_code} → {count}건 (누적:{total})')
                        else:
                            errors += 1

                        time.sleep(0.1)

            print(f'[완료] {year}년 {month}월 수집 완료')

    conn.close()
    print('=' * 50)
    print(f'수집 완료! 총 {total}건 저장, 오류 {errors}건')


# =============================================
# 실행
# =============================================
if __name__ == '__main__':
    # 한 달씩 수집 (월 변경해가며 실행)
    collect_new_registration(
        start_year=2026,
        end_year=2026,
        start_month=1,
        end_month=5
    )