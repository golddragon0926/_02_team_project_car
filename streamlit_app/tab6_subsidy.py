#-------------------------------------
# Streamlit GUI 코드
#-------------------------------------

import streamlit as st
import pandas as pd
import plotly.express as px
from db_queries import load_subsidy_csv


def render_tab6():
    st.title("🚗 전기차 보조금 조회 시스템")
    st.markdown("---")

    # ① 데이터 불러오기 (db_queries.py의 영문 컬럼 버전 사용)
    df = load_subsidy_csv()

    # ② 조회결과 요약
    st.subheader("📊 1. 조회결과 요약")

    # 2025년
    st.markdown("**📅 2025년**")
    df_2025 = df[df["year"] == 2025]
    col1, col2, col3 = st.columns(3)
    if len(df_2025) > 0:
        col1.metric("평균 보조금", f"{int(df_2025['total_subsidy'].mean())}만원")
        col2.metric("최대 보조금", f"{int(df_2025['total_subsidy'].max())}만원")
        col3.metric("최소 보조금", f"{int(df_2025['total_subsidy'].min())}만원")
    else:
        st.info("2025년 데이터가 없어요.")

    st.markdown("")

    # 2026년
    st.markdown("**📅 2026년**")
    df_2026 = df[df["year"] == 2026]
    col4, col5, col6 = st.columns(3)
    if len(df_2026) > 0:
        col4.metric("평균 보조금", f"{int(df_2026['total_subsidy'].mean())}만원")
        col5.metric("최대 보조금", f"{int(df_2026['total_subsidy'].max())}만원")
        col6.metric("최소 보조금", f"{int(df_2026['total_subsidy'].min())}만원")
    else:
        st.info("2026년 데이터가 없어요.")

    st.markdown("---")

    # ③ 시도별 평균 보조금 비교
    st.subheader("🗺️ 2. 시도별 평균 보조금 비교")
    sido_chart = df.groupby(["sido", "year"])["total_subsidy"].mean().reset_index()
    sido_chart.columns = ["시도", "연도", "평균보조금"]
    sido_chart["평균보조금"] = sido_chart["평균보조금"].round(0).astype(int)
    sido_chart["연도"] = sido_chart["연도"].astype(str)
    sido_chart = sido_chart.sort_values("평균보조금", ascending=False)
    fig1 = px.bar(
        sido_chart,
        x="시도",
        y="평균보조금",
        color="연도",
        barmode="group",
        title="시도별 평균 보조금 비교",
        color_discrete_map={"2025": "#3b82f6", "2026": "#ef4444"}
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    # ④ 제조사별 평균 보조금 비교
    st.subheader("🏭 3. 제조사별 평균 보조금 비교")
    top10_makers = df.groupby("manufacturer")["total_subsidy"].mean().nlargest(10).index.tolist()
    maker_chart = df.groupby(["manufacturer", "year"])["total_subsidy"].mean().reset_index()
    maker_chart.columns = ["제조사", "연도", "평균보조금"]
    maker_chart["평균보조금"] = maker_chart["평균보조금"].round(0).astype(int)
    maker_chart["연도"] = maker_chart["연도"].astype(str)
    maker_chart = maker_chart[maker_chart["제조사"].isin(top10_makers)]
    maker_chart = maker_chart.sort_values("평균보조금", ascending=False)
    fig2 = px.bar(
        maker_chart,
        x="제조사",
        y="평균보조금",
        color="연도",
        barmode="group",
        title="제조사별 평균 보조금 비교 TOP 10",
        color_discrete_map={"2025": "#3b82f6", "2026": "#ef4444"}
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ⑤ 검색 필터
    st.subheader("🔍 4. 검색 필터")
    f0, f1, f2, f3, f4 = st.columns(5)

    with f0:
        year_list = ["전체"] + sorted(df["year"].astype(str).unique().tolist())
        selected_year = st.selectbox("📅 연도 선택", year_list)

    if selected_year != "전체":
        df_filtered = df[df["year"] == int(selected_year)]
    else:
        df_filtered = df.copy()

    with f1:
        sido_list = ["전체"] + sorted(df_filtered["sido"].unique().tolist())
        selected_sido = st.selectbox("📍 시도 선택", sido_list)

    with f2:
        if selected_sido != "전체":
            sigungu_list = ["전체"] + sorted(
                df_filtered[df_filtered["sido"] == selected_sido]["sigungu"].unique().tolist()
            )
        else:
            sigungu_list = ["전체"] + sorted(df_filtered["sigungu"].unique().tolist())
        selected_sigungu = st.selectbox("📍 시군구 선택", sigungu_list)

    with f3:
        maker_list = ["전체"] + sorted(df_filtered["manufacturer"].unique().tolist())
        selected_maker = st.selectbox("🏭 제조사 선택", maker_list)

    with f4:
        if selected_maker != "전체":
            model_list = ["전체"] + sorted(
                df_filtered[df_filtered["manufacturer"] == selected_maker]["model_name"].unique().tolist()
            )
        else:
            model_list = ["전체"] + sorted(df_filtered["model_name"].unique().tolist())
        selected_model = st.selectbox("🚘 모델명 선택", model_list)

    # ⑥ 필터 적용
    filtered_df = df_filtered.copy()
    if selected_sido != "전체":
        filtered_df = filtered_df[filtered_df["sido"] == selected_sido]
    if selected_sigungu != "전체":
        filtered_df = filtered_df[filtered_df["sigungu"] == selected_sigungu]
    if selected_maker != "전체":
        filtered_df = filtered_df[filtered_df["manufacturer"] == selected_maker]
    if selected_model != "전체":
        filtered_df = filtered_df[filtered_df["model_name"] == selected_model]

    # ⑦ 모델 선택시 상세 카드
    if selected_model != "전체" and len(filtered_df) > 0:
        st.markdown("---")
        st.subheader(f"💰 {selected_model} 보조금 상세")
        row = filtered_df.iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("🏛️ 국비",   f"{int(row['national_subsidy'])}만원")
        c2.metric("🏙️ 지방비", f"{int(row['local_subsidy'])}만원")
        c3.metric("💰 합계",   f"{int(row['total_subsidy'])}만원")

    st.markdown("---")

    # ⑧ 상세 데이터
    st.subheader("📋 5. 상세 데이터")
    if len(filtered_df) > 0:
        display_df = filtered_df[
            ["year", "sido", "sigungu", "vehicle_type", "manufacturer", "model_name",
             "national_subsidy", "local_subsidy", "total_subsidy"]
        ].rename(columns={
            "year": "연도", "sido": "시도", "sigungu": "시군구", "vehicle_type": "차종",
            "manufacturer": "제조사", "model_name": "모델명",
            "national_subsidy": "국비", "local_subsidy": "지방비", "total_subsidy": "보조금"
        })
        st.dataframe(display_df, use_container_width=True)
    else:
        st.warning("조회 결과가 없어요! 필터를 변경해보세요 😊")

    st.caption("데이터 출처: 환경부 무공해차 통합누리집 (ev.or.kr) 2025~2026년 기준")