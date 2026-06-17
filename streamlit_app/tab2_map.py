# =============================================
# 탭2 - 지역별 비교 (지도)
# =============================================

import streamlit as st
import plotly.express as px
from db_queries import load_region_map_data, load_registration_data


def render_tab2(korea_geojson):
    map_data = load_region_map_data()

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

        clicked_region = '전체'
        if selected_map and selected_map.get('selection') and selected_map['selection'].get('points'):
            clicked_region = selected_map['selection']['points'][0].get('location', '전체')

        st.info(f"선택된 지역: **{clicked_region}**")

        if clicked_region != '전체':
            region_info = map_data[map_data['지역'] == clicked_region]
            if not region_info.empty:
                st.metric("평균 휘발유 가격", f"{region_info['평균유가'].values[0]:,.0f} 원/리터")
                st.metric("친환경차 선택 비율", f"{region_info['친환경비율'].values[0]:.1f} %")

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
