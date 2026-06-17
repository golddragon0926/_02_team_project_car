# =============================================
# 데이터 로드 함수 (CSV 기반)
# =============================================

import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime

# CSV 파일 경로
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db_config import OPINET_API_KEY, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET


@st.cache_data
def load_oil_price_csv():
    """유가 CSV 로드"""
    df = pd.read_csv(f'{DATA_DIR}/oil_price.csv', encoding='utf-8-sig')
    df['날짜'] = pd.to_datetime(df['날짜'])
    df['가격'] = df['가격'].astype(float)
    df['월'] = df['날짜'].dt.strftime('%Y-%m')
    return df


@st.cache_data
def load_registration_csv():
    """차량등록 CSV 로드"""
    df = pd.read_csv(f'{DATA_DIR}/new_registration.csv', encoding='utf-8-sig')
    df['등록대수'] = df['등록대수'].astype(float)
    df['월'] = df['연도'].astype(str) + '-' + df['월'].astype(str).str.zfill(2)
    return df


@st.cache_data
def load_region_list():
    """지역 목록"""
    df = pd.read_csv(f'{DATA_DIR}/region.csv', encoding='utf-8-sig')
    return ['전체'] + df['지역'].tolist()


@st.cache_data
def load_oil_data(region_name='전체', fuel_code='GAS'):
    """유가 시계열 데이터"""
    df = load_oil_price_csv()
    df = df[df['유종'] == fuel_code]
    if region_name != '전체':
        df = df[df['지역'] == region_name]
    result = df.groupby('월')['가격'].mean().reset_index()
    result.columns = ['월', '평균유가']
    return result.sort_values('월')


@st.cache_data
def load_registration_data(region_name='전체'):
    """차량 신규등록 데이터"""
    df = load_registration_csv()
    df = df[df['차종'] == '승용']
    if region_name != '전체':
        df = df[df['지역'] == region_name]
    result = df.groupby(['월', '연료'])['등록대수'].sum().reset_index()
    return result.sort_values('월')


@st.cache_data
def load_region_map_data():
    """지역별 유가 + 친환경차 비율"""
    oil_df = load_oil_price_csv()
    max_date = oil_df['날짜'].max()
    oil_latest = oil_df[(oil_df['날짜'] == max_date) & (oil_df['유종'] == 'GAS')]
    oil_latest = oil_latest.groupby('지역')['가격'].mean().reset_index()
    oil_latest.columns = ['지역', '평균유가']
    oil_latest['평균유가'] = oil_latest['평균유가'].round(0)

    reg_df = load_registration_csv()
    reg_df = reg_df[reg_df['차종'] == '승용']
    eco_fuels = ['전기', '수소', '하이브리드']
    eco = reg_df.groupby('지역').apply(
        lambda x: pd.Series({
            '친환경': x[x['연료'].isin(eco_fuels)]['등록대수'].sum(),
            '전체': x['등록대수'].sum()
        })
    ).reset_index()
    eco['친환경비율'] = (eco['친환경'] / eco['전체'] * 100).round(1)

    return pd.merge(oil_latest, eco[['지역', '친환경비율']], on='지역')


@st.cache_data
def load_oil_surge_data():
    """유가 급등 시점 감지"""
    df = load_oil_price_csv()
    df = df[df['유종'] == 'GAS']
    result = df.groupby('월')['가격'].mean().reset_index()
    result.columns = ['월', '평균유가']
    result = result.sort_values('월').reset_index(drop=True)
    result['전월대비'] = result['평균유가'].pct_change() * 100
    result['급등여부'] = result['전월대비'] >= 3
    return result


@st.cache_data(ttl=3600)
def get_current_gas_price():
    """실시간 유가"""
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
    # API 실패시 CSV에서 최근값
    df = load_oil_price_csv()
    df = df[df['유종'] == 'GAS']
    latest = df.sort_values('날짜').iloc[-1]
    price = float(latest['가격'])
    date = latest['날짜'].strftime("%Y년 %m월 %d일")
    return price, date


@st.cache_data(ttl=1800)
def get_news_by_date(keyword, display=10):
    """네이버 뉴스 검색"""
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