# =============================================
# 오피넷 유가 CSV → DB 저장 코드
# =============================================

import pandas as pd
import pymysql
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db_config import DB_CONFIG

# 지역명 → region_code 매핑
REGION_NAME_MAP = {
    '서울': '11', '부산': '26', '대구': '27', '인천': '28',
    '광주': '29', '대전': '30', '울산': '31', '경기': '41',
    '강원': '42', '충북': '43', '충남': '44', '전북': '45',
    '전남': '46', '경북': '47', '경남': '48', '제주': '50',
    '세종': '36'
}

def save_oil_price(conn, date_str, region_code, fuel_code, price):
    """유가 데이터 DB 저장"""
    cursor = conn.cursor()

    # region_id 조회
    cursor.execute("SELECT region_id FROM region WHERE region_code = %s", (region_code,))
    row = cursor.fetchone()
    if not row:
        return
    region_id = row[0]

    # 날짜 변환 (2024년01월 → 2024-01-01)
    year  = date_str[:4]
    month = date_str[5:7]
    price_date = f"{year}-{month}-01"

    cursor.execute("""
        INSERT INTO oil_price (price_date, region_id, fuel_code, price)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE price = VALUES(price)
    """, (price_date, region_id, fuel_code, price))
    conn.commit()


def load_csv(file_path, fuel_code):
    """CSV 파일 읽어서 DB 저장"""
    conn = pymysql.connect(**DB_CONFIG)
    print(f"[{fuel_code}] 파일 읽는 중: {file_path}")

    df = pd.read_csv(file_path, encoding='cp949')
    total = 0

    for _, row in df.iterrows():
        date_str = row['구분']  # 예: 2024년01월

        for region_name, region_code in REGION_NAME_MAP.items():
            if region_name not in df.columns:
                continue
            price = row[region_name]

            if pd.isna(price):
                continue

            save_oil_price(conn, date_str, region_code, fuel_code, float(price))
            total += 1

        print(f"[저장] {date_str} → {total}건 누적")

    conn.close()
    print(f"[완료] {fuel_code} 총 {total}건 저장!")


# =============================================
# 실행
# =============================================
if __name__ == '__main__':
    # 파일 경로 설정 (본인 경로로 수정)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 휘발유
    load_csv(
        r'/DB/주유소_지역별_평균판매가격_휘발유.csv',
        fuel_code='GAS'
    )

    # 경유
    load_csv(
        r'/DB/주유소_지역별_평균판매가격_경유.csv',  # ← 괄호 없음
        fuel_code='DSL'
    )

    print("=" * 50)
    print("유가 데이터 저장 완료!")
