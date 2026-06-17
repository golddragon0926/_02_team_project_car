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
from tab5_faq import run_faq_tab

st.set_page_config(
    page_title="유가 변동 & 자동차 등록 현황",
    page_icon="🚗",
    layout="wide"
)

# GeoJSON 로드
GEOJSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'korea.geojson')
with open(GEOJSON_PATH, encoding='utf-8') as f:
    korea_geojson = json.load(f)

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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 종합 트렌드",
    "🗺️ 지역별 비교",
    "📰 뉴스 & 이벤트",
    "💰 유류비 시뮬레이터",
    "FAQ"
])

with tab1:
    render_tab1(oil_fuel, oil_fuel_code, group_mode)

with tab2:
    render_tab2(korea_geojson)

with tab3:
    render_tab3()

with tab4:
    render_tab4()

with tab5:
    run_faq_tab()
