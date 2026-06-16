# =============================================
# 탭4 - 유류비 시뮬레이터
# =============================================

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from db_queries import get_current_gas_price


def render_tab4():
    st.subheader("💰 휘발유 vs 전기차 연간 유류비 시뮬레이터")

    current_gas_price, price_date = get_current_gas_price()

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
        '급속충전 (민간)':   (380, "GS칼텍스, 테슬라, SK 등 민간 급속충전기 (50kW 이상) | 쇼핑몰, 주차장 등 | 약 30분~1시간 충전"),
        '완속충전 (한전)':   (200, "한국전력공사 운영 완속충전기 (7kW 이하) | 아파트, 공공주차장 등 | 약 4~8시간 충전"),
        '아파트 완속충전':   (130, "아파트 전기요금 기반 완속충전 (7kW 이하) | 자택 주차장 야간 충전 | 가장 저렴한 방식"),
    }

    if charge_type == '직접 입력':
        electric_cost = st.slider("전기차 충전 단가 (원/kWh)", 100, 500, 250, 10)
        st.info("💡 급속충전 평균 약 347원/kWh, 완속충전 약 200원/kWh, 아파트 완속 약 130원/kWh")
    else:
        electric_cost, description = charge_info[charge_type]
        desc_parts = description.split(' | ')
        st.info(f"""
        💡 **{charge_type}**
        - 설명: {desc_parts[0]}
        - 위치: {desc_parts[1]}
        - 충전시간: {desc_parts[2]}
        - 적용 단가: **{electric_cost}원/kWh**
        """)

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
