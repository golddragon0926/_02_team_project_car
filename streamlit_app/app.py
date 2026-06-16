# =============================================
# 유가 변동에 따른 자동차 현황 파악 대시보드
# =============================================

import streamlit as st
import pymysql
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db_config import DB_CONFIG

# =============================================
# 페이지 설정
# =============================================
st.set_page_config(
    page_title="유가 변동 & 자동차 등록 현황",
    page_icon="🚗",
    layout="wide"
)

# =============================================
# DB 연결 함수
# =============================================
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
def load_region_comparison():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.region_name, AVG(o.price) AS 평균유가
        FROM oil_price o JOIN region r ON o.region_id = r.region_id
        WHERE o.fuel_code = 'GAS' AND r.region_id != 0
        GROUP BY r.region_name ORDER BY 평균유가 DESC
    """)
    oil_df = pd.DataFrame(cursor.fetchall(), columns=['지역', '평균유가'])
    oil_df['평균유가'] = oil_df['평균유가'].astype(float)

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


def get_current_gas_price():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(price) FROM oil_price WHERE fuel_code = 'GAS'
        AND price_date = (SELECT MAX(price_date) FROM oil_price)
    """)
    price = float(cursor.fetchone()[0] or 1750)
    conn.close()
    return price


# =============================================
# 사이드바
# =============================================
st.sidebar.title("🔧 필터")
regions = load_region_list()
selected_region = st.sidebar.selectbox("지역 선택", regions)
oil_fuel = st.sidebar.radio("유가 기준 유종", ['휘발유', '경유'])
oil_fuel_code = 'GAS' if oil_fuel == '휘발유' else 'DSL'
group_mode = st.sidebar.toggle("내연기관 vs 친환경 그룹화")

# =============================================
# 타이틀
# =============================================
st.title("🚗 유가 변동에 따른 자동차 현황 대시보드")
st.caption("유가는 신규 자동차 선택 및 운행 등에 영향을 미쳤을까?")
st.markdown("---")

# =============================================
# 탭
# =============================================
tab1, tab2, tab3 = st.tabs(["📈 종합 트렌드", "🗺️ 지역별 비교", "💰 유류비 시뮬레이터"])

# =============================================
# TAB 1
# =============================================
with tab1:
    oil_df = load_oil_data(selected_region, oil_fuel_code)
    reg_df = load_registration_data(selected_region)

    if reg_df.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없어요.")
    else:
        if group_mode:
            reg_df['연료그룹'] = reg_df['연료'].apply(
                lambda x: '친환경 (전기/수소/하이브리드)' if x in ['전기', '수소', '하이브리드']
                else '내연기관 (휘발유/경유)'
            )
            reg_pivot = reg_df.groupby(['월', '연료그룹'])['등록대수'].sum().reset_index()
            reg_pivot = reg_pivot.pivot(index='월', columns='연료그룹', values='등록대수').fillna(0)
        else:
            reg_pivot = reg_df.pivot(index='월', columns='연료', values='등록대수').fillna(0)

        common_months = sorted(set(oil_df['월']) & set(reg_pivot.index))

        if common_months:
            oil_filtered = oil_df[oil_df['월'].isin(common_months)].set_index('월')
            reg_filtered = reg_pivot[reg_pivot.index.isin(common_months)]

            fig = make_subplots(specs=[[{"secondary_y": True}]])
            colors = ['#636EFA', '#00CC96', '#EF553B', '#AB63FA', '#FFA15A']

            for i, col in enumerate(reg_filtered.columns):
                fig.add_trace(go.Bar(
                    x=common_months, y=reg_filtered[col],
                    name=col, marker_color=colors[i % len(colors)], opacity=0.75
                ), secondary_y=False)

            fig.add_trace(go.Scatter(
                x=common_months, y=oil_filtered['평균유가'],
                name=f'{oil_fuel} 평균가격',
                line=dict(color='#FF4B4B', width=3), mode='lines+markers'
            ), secondary_y=True)

            fig.update_layout(
                title='유가 추이 & 신규 등록 대수 (월별)',
                barmode='stack', height=500,
                legend=dict(orientation='h', y=-0.2),
            )
            fig.update_yaxes(title_text="등록 대수", secondary_y=False)
            fig.update_yaxes(title_text=f"유가 (원/리터)", secondary_y=True)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("연료별 신규등록 비율")
        total_by_fuel = reg_df.groupby('연료')['등록대수'].sum().reset_index()
        fig2 = px.pie(total_by_fuel, values='등록대수', names='연료', hole=0.4,
                      color_discrete_sequence=px.colors.qualitative.Set3)
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

# =============================================
# TAB 2
# =============================================
with tab2:
    st.subheader("지역별 유가 vs 친환경차 선택 비율")
    merged = load_region_comparison()

    col1, col2 = st.columns(2)
    with col1:
        fig3 = px.bar(merged.sort_values('평균유가'), x='평균유가', y='지역',
                      orientation='h', title='지역별 평균 휘발유 가격',
                      color='평균유가', color_continuous_scale='Reds')
        fig3.update_layout(height=500)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        fig4 = px.bar(merged.sort_values('친환경비율'), x='친환경비율', y='지역',
                      orientation='h', title='지역별 친환경차 선택 비율 (%)',
                      color='친환경비율', color_continuous_scale='Greens')
        fig4.update_layout(height=500)
        st.plotly_chart(fig4, use_container_width=True)

    fig5 = px.scatter(merged, x='평균유가', y='친환경비율', text='지역',
                      title='유가 vs 친환경차 선택 비율 상관관계', trendline='ols',
                      color_discrete_sequence=['#00CC96'])
    fig5.update_traces(textposition='top center')
    fig5.update_layout(height=450)
    st.plotly_chart(fig5, use_container_width=True)

# =============================================
# TAB 3
# =============================================
with tab3:
    st.subheader("💰 휘발유 vs 전기차 연간 유류비 시뮬레이터")

    current_gas_price = get_current_gas_price()
    st.metric("현재 전국 평균 휘발유 가격", f"{current_gas_price:,.0f} 원/리터")
    st.markdown("---")

    annual_km       = st.slider("연간 주행거리 (km)", 5000, 50000, 15000, 1000)
    gas_efficiency  = st.slider("휘발유차 연비 (km/L)", 8, 20, 12, 1)
    electric_cost   = st.slider("전기차 충전 단가 (원/kWh)", 150, 400, 250, 10)
    elec_efficiency = st.slider("전기차 전비 (km/kWh)", 4, 8, 6, 1)

    gas_cost  = (annual_km / gas_efficiency) * current_gas_price
    elec_cost = (annual_km / elec_efficiency) * electric_cost
    savings   = gas_cost - elec_cost

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("휘발유차 연간 유류비", f"{gas_cost:,.0f} 원")
    with col2:
        st.metric("전기차 연간 충전비", f"{elec_cost:,.0f} 원")
    with col3:
        st.metric("전기차 전환 시 절감액", f"{savings:,.0f} 원",
                  delta="절감" if savings > 0 else "추가 비용")

    fig6 = go.Figure(data=[
        go.Bar(name='휘발유차', x=['연간 유류비'], y=[gas_cost], marker_color='#FF4B4B'),
        go.Bar(name='전기차',   x=['연간 유류비'], y=[elec_cost], marker_color='#00CC96'),
    ])
    fig6.update_layout(title='휘발유차 vs 전기차 연간 유류비 비교', barmode='group', height=400)
    st.plotly_chart(fig6, use_container_width=True)
