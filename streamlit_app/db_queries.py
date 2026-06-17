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

# 보조금 데이터의 시도 축약형 → Region 풀네임 매핑
SIDO_TO_REGION_NAME = {
    '서울': '서울특별시', '부산': '부산광역시', '대구': '대구광역시',
    '인천': '인천광역시', '광주': '광주광역시', '대전': '대전광역시',
    '울산': '울산광역시', '세종': '세종특별자치시', '경기': '경기도',
    '강원': '강원도', '충북': '충청북도', '충남': '충청남도',
    '전북': '전라북도', '전남': '전라남도', '경북': '경상북도',
    '경남': '경상남도', '제주': '제주특별자치도'
}


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
def load_registration_data(region_name='전체', start_month='2024-01', end_month='2026-05'):
    df = load_registration_csv()
    df = df[df['차종'] == '승용']
    df = df[(df['월'] >= start_month) & (df['월'] <= end_month)]
    if region_name != '전체':
        df = df[df['지역'] == region_name]
    result = df.groupby(['월', '연료'])['등록대수'].sum().reset_index()
    return result.sort_values('월')


@st.cache_data
def load_region_map_data(start_month='2024-01', end_month='2026-05'):
    oil_df = load_oil_price_csv()
    oil_filtered = oil_df[
        (oil_df['유종'] == 'GAS') &
        (oil_df['월'] >= start_month) &
        (oil_df['월'] <= end_month)
    ]
    oil_latest = oil_filtered.groupby('지역')['가격'].mean().reset_index()
    oil_latest.columns = ['지역', '평균유가']
    oil_latest['평균유가'] = oil_latest['평균유가'].round(0)

    reg_df = load_registration_csv()
    reg_filtered = reg_df[
        (reg_df['차종'] == '승용') &
        (reg_df['월'] >= start_month) &
        (reg_df['월'] <= end_month)
    ]
    eco_fuels = ['전기', '수소', '하이브리드']
    eco = reg_filtered.groupby('지역').apply(
        lambda x: pd.Series({
            '친환경': x[x['연료'].isin(eco_fuels)]['등록대수'].sum(),
            '전체': x['등록대수'].sum()
        })
    ).reset_index()
    eco['친환경비율'] = (eco['친환경'] / eco['전체'] * 100).round(1)

    result = pd.merge(oil_latest, eco[['지역', '친환경비율']], on='지역')

    # 보조금 데이터 병합 (sido 축약형 → 지역 풀네임 매핑, 연도 무관 전체 평균)
    subsidy_df = load_subsidy_csv()
    subsidy_df = subsidy_df[subsidy_df['sido'] != '공단']  # 시도 단위가 아닌 별도 채널 제외
    subsidy_avg = subsidy_df.groupby('sido')['total_subsidy'].mean().reset_index()
    subsidy_avg.columns = ['sido', '평균보조금']
    subsidy_avg['평균보조금'] = subsidy_avg['평균보조금'].round(0)
    subsidy_avg['지역'] = subsidy_avg['sido'].map(SIDO_TO_REGION_NAME)

    result = pd.merge(result, subsidy_avg[['지역', '평균보조금']], on='지역', how='left')
    return result


@st.cache_data
def load_subsidy_csv():
    """전기차 보조금 CSV 로드"""
    df = pd.read_csv(f'{DATA_DIR}/subsidy.csv', encoding='utf-8-sig')
    return df


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