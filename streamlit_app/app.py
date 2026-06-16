# =============================================
# 유가 변동에 따른 자동차 현황 파악 대시보드
# =============================================

import streamlit as st
import pymysql
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db_config import DB_CONFIG, OPINET_API_KEY

st.set_page_config(
    page_title="유가 변동 & 자동차 등록 현황",
    page_icon="🚗",
    layout="wide"
)

# GeoJSON 로드
GEOJSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'korea.geojson')
with open(GEOJSON_PATH, encoding='utf-8') as f:
    korea_geojson = json.load(f)

# GeoJSON name → DB region_name 매핑
REGION_NAME_MAP = {
    '서울특별시': '서울특별시', '부산광역시': '부산광역시', '대구광역시': '대구광역시',
    '인천광역시': '인천광역시', '광주광역시': '광주광역시', '대전광역시': '대전광역시',
    '울산광역시': '울산광역시', '세종특별자치시': '세종특별자치시', '경기도': '경기도',
    '강원도': '강원도', '충청북도': '충청북도', '충청남도': '충청남도',
    '전라북도': '전라북도', '전라남도': '전라남도', '경상북도': '경상북도',
    '경상남도': '경상남도', '제주특별자치도': '제주특별자치도'
}

# =============================================
# DB 함수
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
def load_region_map_data():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 지역별 평균 유가
    cursor.execute("""
        SELECT r.region_name, AVG(o.price) AS 평균유가
        FROM oil_price o JOIN region r ON o.region_id = r.region_id
        WHERE o.fuel_code = 'GAS' AND r.region_id != 0
        GROUP BY r.region_name
    """)
    oil_df = pd.DataFrame(cursor.fetchall(), columns=['지역', '평균유가'])
    oil_df['평균유가'] = oil_df['평균유가'].astype(float)

    # 지역별 친환경차 비율
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
    import requests
    from datetime import datetime
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


# =============================================
# 사이드바
# =============================================
st.sidebar.title("🔧 필터")
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
# TAB 1 - 종합 트렌드
# =============================================
with tab1:
    regions = load_region_list()
    selected_region = st.selectbox("지역 선택", regions, key='tab1_region')

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
                title=f'유가 추이 & 신규 등록 대수 (월별) - {selected_region}',
                barmode='stack', height=500,
                legend=dict(orientation='h', y=-0.2),
            )
            fig.update_yaxes(title_text="등록 대수", secondary_y=False)
            fig.update_yaxes(title_text="유가 (원/리터)", secondary_y=True)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("연료별 신규등록 비율")
        total_by_fuel = reg_df.groupby('연료')['등록대수'].sum().reset_index()
        fig2 = px.pie(total_by_fuel, values='등록대수', names='연료', hole=0.4,
                      color_discrete_sequence=px.colors.qualitative.Set3)
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)


# =============================================
# TAB 2 - 지역별 비교 (지도)
# =============================================
with tab2:
    map_data = load_region_map_data()

    # 지도 표시 데이터 선택
    map_metric = st.radio(
        "지도에 표시할 데이터",
        ['친환경차 비율 (%)', '평균 휘발유 가격 (원)'],
        horizontal=True
    )

    metric_col = '친환경비율' if map_metric == '친환경차 비율 (%)' else '평균유가'
    color_scale = 'Greens' if metric_col == '친환경비율' else 'Reds'
    label = '친환경차 비율(%)' if metric_col == '친환경비율' else '평균유가(원)'

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.subheader("🗺️ 지역 클릭해서 상세 조회")

        fig_map = px.choropleth_mapbox(
            map_data,
            geojson=korea_geojson,
            locations='지역',
            featureidkey='properties.name',
            color=metric_col,
            color_continuous_scale=color_scale,
            mapbox_style='carto-positron',
            zoom=5.5,
            center={"lat": 36.5, "lon": 127.5},
            opacity=0.7,
            labels={metric_col: label},
            hover_data={'지역': True, '친환경비율': True, '평균유가': True}
        )
        fig_map.update_layout(height=550, margin={"r":0,"t":0,"l":0,"b":0})
        selected_map = st.plotly_chart(fig_map, use_container_width=True, on_select='rerun')

    with col2:
        st.subheader("📊 지역 상세 데이터")

        # 클릭한 지역 감지
        clicked_region = '전체'
        if selected_map and selected_map.get('selection') and selected_map['selection'].get('points'):
            clicked_region = selected_map['selection']['points'][0].get('location', '전체')

        st.info(f"선택된 지역: **{clicked_region}**")

        # 선택 지역 데이터 표시
        if clicked_region != '전체':
            region_info = map_data[map_data['지역'] == clicked_region]
            if not region_info.empty:
                st.metric("평균 휘발유 가격", f"{region_info['평균유가'].values[0]:,.0f} 원/리터")
                st.metric("친환경차 선택 비율", f"{region_info['친환경비율'].values[0]:.1f} %")

        # 선택 지역 등록 데이터
        reg_detail = load_registration_data(clicked_region)
        if not reg_detail.empty:
            total_by_fuel = reg_detail.groupby('연료')['등록대수'].sum().reset_index()
            fig_detail = px.pie(
                total_by_fuel, values='등록대수', names='연료',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_detail.update_layout(height=350, showlegend=True)
            st.plotly_chart(fig_detail, use_container_width=True)

    # 지역별 비교 바차트
    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        fig3 = px.bar(map_data.sort_values('평균유가'), x='평균유가', y='지역',
                      orientation='h', title='지역별 평균 휘발유 가격',
                      color='평균유가', color_continuous_scale='Reds')
        fig3.update_layout(height=500)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = px.bar(map_data.sort_values('친환경비율'), x='친환경비율', y='지역',
                      orientation='h', title='지역별 친환경차 선택 비율 (%)',
                      color='친환경비율', color_continuous_scale='Greens')
        fig4.update_layout(height=500)
        st.plotly_chart(fig4, use_container_width=True)

    # 상관관계 산점도
    fig5 = px.scatter(map_data, x='평균유가', y='친환경비율', text='지역',
                      title='유가 vs 친환경차 선택 비율 상관관계', trendline='ols',
                      color_discrete_sequence=['#00CC96'])
    fig5.update_traces(textposition='top center')
    fig5.update_layout(height=450)
    st.plotly_chart(fig5, use_container_width=True)


# =============================================
# TAB 3 - 유류비 시뮬레이터
# =============================================
with tab3:
    st.subheader("💰 휘발유 vs 전기차 연간 유류비 시뮬레이터")

    current_gas_price, price_date = get_current_gas_price()

    # 유가 조절 옵션
    price_mode = st.radio(
        "휘발유 가격 기준",
        ['실시간 자동 적용', '직접 입력'],
        horizontal=True
    )

    if price_mode == '실시간 자동 적용':
        st.metric(f"전국 실시간 휘발유 가격 ({price_date} 기준)", f"{current_gas_price:,.0f} 원/리터")
        gas_price = current_gas_price
    else:
        gas_price = st.slider(
            "휘발유 가격 직접 입력 (원/리터)",
            min_value=1000,
            max_value=3000,
            value=int(current_gas_price),
            step=10
        )
        st.info(f"💡 현재 실시간 가격: {current_gas_price:,.0f} 원/리터")

    st.markdown("---")

    st.subheader("⚡ 충전 방식 선택")
    charge_type = st.radio(
        "주로 사용하는 충전 방식",
        ['급속충전 (환경부)', '급속충전 (민간)', '완속충전 (한전)', '아파트 완속충전', '직접 입력'],
        horizontal=True
    )

    charge_info = {
        '급속충전 (환경부)': (347, "환경부에서 운영하는 공공 급속충전기 (50kW 이상) | 고속도로 휴게소, 공공시설 등 | 약 30분~1시간 충전"),
        '급속충전 (민간)': (380, "GS칼텍스, 테슬라, SK 등 민간 급속충전기 (50kW 이상) | 쇼핑몰, 주차장 등 | 약 30분~1시간 충전"),
        '완속충전 (한전)': (200, "한국전력공사 운영 완속충전기 (7kW 이하) | 아파트, 공공주차장 등 | 약 4~8시간 충전"),
        '아파트 완속충전': (130, "아파트 전기요금 기반 완속충전 (7kW 이하) | 자택 주차장 야간 충전 | 가장 저렴한 방식"),
    }

    if charge_type != '직접 입력':
        electric_cost, description = charge_info[charge_type]
        desc_parts = description.split(' | ')
        st.info(f"""
        💡 **{charge_type}**
        - 설명: {desc_parts[0]}
        - 위치: {desc_parts[1]}
        - 충전시간: {desc_parts[2]}
        - 적용 단가: **{electric_cost}원/kWh**
        """)
    else:
        electric_cost, description = charge_info[charge_type]
        st.info(f"💡 {description} → **{electric_cost}원/kWh** 적용")

    st.markdown("---")

    annual_km       = st.slider("연간 주행거리 (km)", 5000, 50000, 15000, 1000)
    gas_efficiency  = st.slider("휘발유차 연비 (km/L)", 8, 20, 12, 1)
    elec_efficiency = st.slider("전기차 전비 (km/kWh)", 4, 8, 6, 1)

    gas_cost  = (annual_km / gas_efficiency) * gas_price
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

    # 충전 방식별 비교표
    st.subheader("📊 충전 방식별 연간 비용 비교")
    compare_data = []
    for name, (cost, desc) in charge_info.items():
        annual = (annual_km / elec_efficiency) * cost
        compare_data.append({
            '충전 방식': name,
            '단가 (원/kWh)': cost,
            '연간 충전비': f"{annual:,.0f} 원",
            '휘발유 대비 절감': f"{gas_cost - annual:,.0f} 원",
            '설명': desc
        })
    st.dataframe(pd.DataFrame(compare_data), use_container_width=True, hide_index=True)