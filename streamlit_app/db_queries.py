# =============================================
# DB 쿼리 함수 모음
# =============================================

import streamlit as st
import pymysql
import pandas as pd
import requests
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db_config import DB_CONFIG, OPINET_API_KEY, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET


@st.cache_data
def load_oil_data(region_name='전체', fuel_code='GAS'):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    if region_name == '전체':
        cursor.execute("""
            SELECT DATE_FORMAT(price_date, '%%Y-%%m') AS 월, AVG(price) AS 평균유가
            FROM oil_price WHERE fuel_code = %s
            GROUP BY DATE_FORMAT(price_date, '%%Y-%%m') ORDER BY 월
        """, (fuel_code,))
    else:
        cursor.execute("""
            SELECT DATE_FORMAT(o.price_date, '%%Y-%%m') AS 월, AVG(o.price) AS 평균유가
            FROM oil_price o JOIN region r ON o.region_id = r.region_id
            WHERE o.fuel_code = %s AND r.region_name = %s
            GROUP BY DATE_FORMAT(o.price_date, '%%Y-%%m') ORDER BY 월
        """, (fuel_code, region_name))
    df = pd.DataFrame(cursor.fetchall(), columns=['월', '평균유가'])
    df['평균유가'] = df['평균유가'].astype(float)
    conn.close()
    return df


@st.cache_data
def load_registration_data(region_name='전체'):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    if region_name == '전체':
        cursor.execute("""
            SELECT CONCAT(n.reg_year, '-', LPAD(n.reg_month, 2, '0')) AS 월,
                   f.fuel_name AS 연료, SUM(n.count) AS 등록대수
            FROM new_registration n JOIN fuel_type f ON n.fuel_id = f.fuel_id
            WHERE n.vehicle_type = '승용'
            GROUP BY 월, f.fuel_name ORDER BY 월
        """)
    else:
        cursor.execute("""
            SELECT CONCAT(n.reg_year, '-', LPAD(n.reg_month, 2, '0')) AS 월,
                   f.fuel_name AS 연료, SUM(n.count) AS 등록대수
            FROM new_registration n
            JOIN fuel_type f ON n.fuel_id = f.fuel_id
            JOIN region r ON n.region_id = r.region_id
            WHERE n.vehicle_type = '승용' AND r.region_name = %s
            GROUP BY 월, f.fuel_name ORDER BY 월
        """, (region_name,))
    df = pd.DataFrame(cursor.fetchall(), columns=['월', '연료', '등록대수'])
    df['등록대수'] = df['등록대수'].astype(float)
    conn.close()
    return df


@st.cache_data
def load_region_map_data():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.region_name, AVG(o.price) AS 평균유가
        FROM oil_price o JOIN region r ON o.region_id = r.region_id
        WHERE o.fuel_code = 'GAS'
          AND r.region_id != 0
          AND o.price_date = (SELECT MAX(price_date) FROM oil_price)
        GROUP BY r.region_name
    """)
    oil_df = pd.DataFrame(cursor.fetchall(), columns=['지역', '평균유가'])
    oil_df['평균유가'] = oil_df['평균유가'].astype(float).round(0)

    cursor.execute("""
        SELECT r.region_name,
               SUM(CASE WHEN f.fuel_code IN ('ELC','HYD','HEV') THEN n.count ELSE 0 END) AS 친환경,
               SUM(n.count) AS 전체
        FROM new_registration n
        JOIN region r ON n.region_id = r.region_id
        JOIN fuel_type f ON n.fuel_id = f.fuel_id
        WHERE n.vehicle_type = '승용'
        GROUP BY r.region_name
    """)
    eco_df = pd.DataFrame(cursor.fetchall(), columns=['지역', '친환경', '전체'])
    eco_df['친환경'] = eco_df['친환경'].astype(float)
    eco_df['전체'] = eco_df['전체'].astype(float)
    eco_df['친환경비율'] = (eco_df['친환경'] / eco_df['전체'] * 100).round(1)
    conn.close()
    return pd.merge(oil_df, eco_df[['지역', '친환경비율']], on='지역')


@st.cache_data
def load_region_list():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT region_name FROM region WHERE region_id != 0 ORDER BY region_id")
    regions = ['전체'] + [row[0] for row in cursor.fetchall()]
    conn.close()
    return regions


@st.cache_data(ttl=3600)
def get_current_gas_price():
    today = datetime.now().strftime("%Y년 %m월 %d일")
    try:
        url = "http://www.opinet.co.kr/api/avgAllPrice.do"
        params = {"code": OPINET_API_KEY, "out": "json"}
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        oils = data.get("RESULT", {}).get("OIL", [])
        for oil in oils:
            if oil.get("PRODCD") == "B027":
                return float(oil.get("PRICE", 0)), today
    except:
        pass
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(price), MAX(price_date) FROM oil_price WHERE fuel_code = 'GAS'
        AND price_date = (SELECT MAX(price_date) FROM oil_price)
    """)
    row = cursor.fetchone()
    price = float(row[0] or 1750)
    date = row[1].strftime("%Y년 %m월 %d일") if row[1] else today
    conn.close()
    return price, date


@st.cache_data(ttl=1800)
def get_news_by_date(keyword, display=10):
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id"    : NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {"query": keyword, "display": display, "sort": "date"}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        return r.json().get("items", [])
    except:
        return []


@st.cache_data
def load_oil_surge_data():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT CONCAT(YEAR(price_date), '-', LPAD(MONTH(price_date), 2, '0')) AS 월,
               AVG(price) AS 평균유가
        FROM oil_price WHERE fuel_code = 'GAS'
        GROUP BY YEAR(price_date), MONTH(price_date),
                 CONCAT(YEAR(price_date), '-', LPAD(MONTH(price_date), 2, '0'))
        ORDER BY 월
    """)
    df = pd.DataFrame(cursor.fetchall(), columns=['월', '평균유가'])
    df['평균유가'] = df['평균유가'].astype(float)
    df['전월대비'] = df['평균유가'].pct_change() * 100
    df['급등여부'] = df['전월대비'] >= 3
    conn.close()
    return df
