# =============================================
# 탭1 - 종합 트렌드
# =============================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from db_queries import load_oil_data, load_registration_data, load_region_list


def render_tab1(oil_fuel, oil_fuel_code, group_mode):
    regions = load_region_list()
    selected_region = st.selectbox("지역 선택", regions, key='tab1_region')

    oil_df = load_oil_data(selected_region, oil_fuel_code)
    reg_df = load_registration_data(selected_region)

    if reg_df.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없어요.")
        return

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
        fig.update_yaxes(
            title_text="유가 (원/리터)",
            secondary_y=True,
            range=[oil_filtered['평균유가'].min() * 0.95,
                   oil_filtered['평균유가'].max() * 1.05]
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("연료별 신규등록 비율")
    total_by_fuel = reg_df.groupby('연료')['등록대수'].sum().reset_index()
    fig2 = px.pie(total_by_fuel, values='등록대수', names='연료', hole=0.4,
                  color_discrete_sequence=px.colors.qualitative.Set3)
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)
