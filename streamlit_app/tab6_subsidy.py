#-------------------------------------
#Streamlit GUI 코드
#-------------------------------------
from config.db_config import DB_CONFIG

import streamlit as st
import pymysql
import pandas as pd
import plotly.express as px


@st.cache_data
def get_data():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subsidy")
    rows = cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    conn.close()
    return pd.DataFrame(rows, columns=cols)

# ② 페이지 설정
st.set_page_config(
    page_title="전기차 보조금 조회 시스템",
    page_icon="🚗",
    layout="wide"
)

# ③ 사이드바 메뉴만
st.sidebar.title("📋 메뉴")
menu = st.sidebar.selectbox(
    "메뉴 선택",["🚗 2026년 전기차 보조금 확인"]
)

# ④ 데이터 불러오기
df = get_data()

# ===============================
# 홈 화면
# ===============================
if menu == "🏠 홈":
    st.title("🚗 전기차 보조금 조회 시스템")
    st.markdown("---")
    st.markdown("""
    ### 👋 안녕하세요!
    이 시스템은 **2026년 전국 전기차 보조금**을 쉽게 조회할 수 있는 서비스예요.

    #### 📌 주요 기능
    - 🔍 **시도 / 제조사 / 모델명** 필터 검색
    - 📊 **차트**로 보조금 비교
    - 📋 **테이블**로 상세 데이터 확인
    """)

    col1, col2, col3 = st.columns(3)
    col1.metric("총 데이터 수", f"{len(df)}개")
    col2.metric("지역 수",      f"{df['시도'].nunique()}개 시도")
    col3.metric("제조사 수",    f"{df['제조사'].nunique()}개")

    st.markdown("---")
    st.info("👈 왼쪽 메뉴에서 **2026년 전기차 보조금 확인** 을 선택하세요!")

# ===============================
# 보조금 확인 화면
# ===============================
elif menu == "🚗 2026년 전기차 보조금 확인":
    st.title("🚗 2026년 전기차 보조금 확인")
    st.markdown("---")

    # ===============================
    # 1. 조회결과 요약
    # ===============================
    st.subheader("📊 1. 조회결과 요약")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("평균 보조금", f"{int(df['보조금'].mean())}만원")
    col2.metric("최대 보조금", f"{int(df['보조금'].max())}만원")
    col3.metric("최소 보조금", f"{int(df['보조금'].min())}만원")

    st.markdown("---")

    # ===============================
    # 2. 시도별 평균 보조금
    # ===============================
    st.subheader("🗺️ 2. 시도별 평균 보조금")
    sido_chart = df.groupby("시도")["보조금"].mean().reset_index()
    sido_chart.columns = ["시도", "평균보조금"]
    sido_chart["평균보조금"] = sido_chart["평균보조금"].round(0).astype(int)
    sido_chart = sido_chart.sort_values("평균보조금", ascending=False)
    fig1 = px.bar(
        sido_chart,
        x="시도",
        y="평균보조금",
        color="평균보조금",
        color_continuous_scale="blues",
        title="시도별 평균 보조금 (만원)"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    # ===============================
    # 3. 제조사별 평균 보조금
    # ===============================
    st.subheader("🏭 3. 제조사별 평균 보조금")
    maker_chart = df.groupby("제조사")["보조금"].mean().reset_index()
    maker_chart.columns = ["제조사", "평균보조금"]
    maker_chart["평균보조금"] = maker_chart["평균보조금"].round(0).astype(int)
    maker_chart = maker_chart.sort_values("평균보조금", ascending=False).head(10)
    fig2 = px.bar(
        maker_chart,
        x="제조사",
        y="평균보조금",
        color="평균보조금",
        color_continuous_scale="reds",
        title="제조사별 평균 보조금 TOP 10 (만원)"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ===============================
    # 4. 검색 필터 (본문 안에!)
    # ===============================
    st.subheader("🔍 4. 검색 필터")

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        sido_list = ["전체"] + sorted(df["시도"].unique().tolist())
        selected_sido = st.selectbox("📍 시도 선택", sido_list)

    with f2:
        if selected_sido != "전체":
            sigungu_list = ["전체"] + sorted(
                df[df["시도"] == selected_sido]["시군구"].unique().tolist()
            )
        else:
            sigungu_list = ["전체"] + sorted(df["시군구"].unique().tolist())
        selected_sigungu = st.selectbox("📍 시군구 선택", sigungu_list)

    with f3:
        maker_list = ["전체"] + sorted(df["제조사"].unique().tolist())
        selected_maker = st.selectbox("🏭 제조사 선택", maker_list)

    with f4:
        if selected_maker != "전체":
            model_list = ["전체"] + sorted(
                df[df["제조사"] == selected_maker]["모델명"].unique().tolist()
            )
        else:
            model_list = ["전체"] + sorted(df["모델명"].unique().tolist())
        selected_model = st.selectbox("🚘 모델명 선택", model_list)

    # ⑤ 필터 적용
    filtered_df = df.copy()
    if selected_sido != "전체":
        filtered_df = filtered_df[filtered_df["시도"] == selected_sido]
    if selected_sigungu != "전체":
        filtered_df = filtered_df[filtered_df["시군구"] == selected_sigungu]
    if selected_maker != "전체":
        filtered_df = filtered_df[filtered_df["제조사"] == selected_maker]
    if selected_model != "전체":
        filtered_df = filtered_df[filtered_df["모델명"] == selected_model]

    # 모델 선택시 상세 카드
    if selected_model != "전체" and len(filtered_df) > 0:
        st.markdown("---")
        st.subheader(f"💰 {selected_model} 보조금 상세")
        row = filtered_df.iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("🏛️ 국비",   f"{int(row['국비'])}만원")
        c2.metric("🏙️ 지방비", f"{int(row['지방비'])}만원")
        c3.metric("💰 합계",   f"{int(row['보조금'])}만원")

    st.markdown("---")

    # ===============================
    # 5. 상세 데이터
    # ===============================
    st.subheader("📋 5. 상세 데이터")
    if len(filtered_df) > 0:
        st.dataframe(
            filtered_df[["시도", "시군구", "차종", "제조사", "모델명", "국비", "지방비", "보조금"]],
            use_container_width=True
        )
    else:
        st.warning("조회 결과가 없어요! 필터를 변경해보세요 😊")

    st.caption("데이터 출처: 환경부 무공해차 통합누리집 (ev.or.kr) 2026년 기준")