# =============================================
# 탭3 - 뉴스 & 이벤트
# =============================================

import streamlit as st
import plotly.graph_objects as go
import re
from db_queries import load_oil_surge_data, get_news_by_date


def render_tab3():
    st.subheader("📰 유가 급등 시점 & 관련 뉴스")

    surge_df = load_oil_surge_data()

    fig_news = go.Figure()

    fig_news.add_trace(go.Scatter(
        x=surge_df['월'],
        y=surge_df['평균유가'],
        mode='lines+markers',
        name='휘발유 평균가격',
        line=dict(color='#FF4B4B', width=3)
    ))

    surge_only = surge_df[surge_df['급등여부']]
    fig_news.add_trace(go.Scatter(
        x=surge_only['월'],
        y=surge_only['평균유가'],
        mode='markers+text',
        name='급등 시점',
        marker=dict(color='orange', size=15, symbol='star'),
        text=[f"+{v:.1f}%" for v in surge_only['전월대비']],
        textposition='top center'
    ))

    fig_news.update_layout(
        title='유가 추이 & 급등 시점 (⭐: 전월 대비 3% 이상 상승)',
        height=450,
        yaxis=dict(
            range=[surge_df['평균유가'].min() * 0.95,
                   surge_df['평균유가'].max() * 1.05]
        )
    )
    st.plotly_chart(fig_news, use_container_width=True)

    st.markdown("---")

    surge_months = surge_df[surge_df['급등여부']]['월'].tolist()

    if surge_months:
        st.subheader("📅 급등 시점 뉴스 조회")

        col1, col2 = st.columns([1, 2])

        with col1:
            selected_month = st.selectbox(
                "급등 시점 선택",
                surge_months,
                format_func=lambda x: f"{x} (+{surge_df[surge_df['월']==x]['전월대비'].values[0]:.1f}%)"
            )

            keyword = st.selectbox(
                "검색 키워드",
                ['유가 상승', '기름값', '휘발유 가격', '고유가', '전기차']
            )

            selected_data = surge_df[surge_df['월'] == selected_month]
            if not selected_data.empty:
                st.metric(
                    f"{selected_month} 평균 유가",
                    f"{selected_data['평균유가'].values[0]:,.0f} 원/리터",
                    delta=f"+{selected_data['전월대비'].values[0]:.1f}%"
                )

        with col2:
            st.subheader(f"🗞️ {selected_month} 관련 뉴스")

            search_keyword = f"{keyword} {selected_month[:4]}년 {selected_month[5:]}월"
            news_items = get_news_by_date(search_keyword, display=10)

            if news_items:
                for item in news_items:
                    title = re.sub(r'<[^>]+>', '', item['title'])
                    date  = item['pubDate'][:16]
                    url   = item['link']
                    st.markdown(f"**[{title}]({url})**")
                    st.caption(f"📅 {date}")
                    st.divider()
            else:
                st.warning("관련 뉴스를 찾을 수 없어요.")
    else:
        st.info("급등 시점이 감지되지 않았어요.")
