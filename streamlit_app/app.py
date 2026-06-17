# =============================================
# 유가 변동에 따른 자동차 현황 파악 대시보드
# =============================================

import streamlit as st
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tab1_trend import render_tab1
from tab2_map   import render_tab2
from tab3_news  import render_tab3
from tab4_sim   import render_tab4
from tab5_faq   import render_tab5
from tab6_subsidy import render_tab6

st.set_page_config(
    page_title="유가 변동 & 자동차 등록 현황",
    page_icon="🚗",
    layout="wide"
)

st.markdown("""
<style>
/* 선택된 버튼 (Primary) - 하늘색 */
[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background-color: #5DADE2;
    color: white;
    border: none;
}

/* 기본 버튼 (Secondary) */
[data-testid="stSidebar"] .stButton button[kind="secondary"] {
    background-color: white;
    color: #2C3E50;
    border: 1px solid #AED6F1;
}
</style>
""", unsafe_allow_html=True)

# GeoJSON 로드
GEOJSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'korea.geojson')
with open(GEOJSON_PATH, encoding='utf-8') as f:
    korea_geojson = json.load(f)

# =============================================
# 세션 상태 초기화
# =============================================
if 'page' not in st.session_state:
    st.session_state.page = "📈 종합 트렌드"

# =============================================
# 사이드바
# =============================================
st.sidebar.title("🚗 유가 변동")
st.sidebar.caption("자동차 현황 대시보드")
st.sidebar.markdown("---")

menus = [
    "📈 종합 트렌드",
    "🗺️ 지역별 비교",
    "📰 뉴스 & 이벤트",
    "💰 유류비 시뮬레이터",
    "❓ FAQ",
    "❓ 전기차 보조금"
]

for menu in menus:
    if st.sidebar.button(
        menu,
        use_container_width=True,
        type="primary" if st.session_state.page == menu else "secondary"
    ):
        st.session_state.page = menu
        st.rerun()  # ← 즉시 반영

# =============================================
# 페이지 전환
# =============================================
if st.session_state.page == "📈 종합 트렌드":
    render_tab1()
elif st.session_state.page == "🗺️ 지역별 비교":
    render_tab2(korea_geojson)
elif st.session_state.page == "📰 뉴스 & 이벤트":
    render_tab3()
elif st.session_state.page == "💰 유류비 시뮬레이터":
    render_tab4()
elif st.session_state.page == "❓ FAQ":
    render_tab5()
elif st.session_state.page == "❓ 전기차 보조금":
    render_tab6()