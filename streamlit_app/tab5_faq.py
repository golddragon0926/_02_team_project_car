import streamlit as st
import pandas as pd
import os

def render_tab5():
    st.subheader("🚗 자동차 통합 FAQ 및 지원 플랫폼")
    st.caption("현대자동차, 기아자동차, 오피넷, BMW, KGM 등 흩어져 있는 자동차 관련 핵심 FAQ를 이곳에서 한방에 검색하세요!")

    base_path = os.getcwd()
    faq_path = os.path.join(base_path, "data", "faq.csv")

    if not os.path.exists(faq_path):
        st.error("⚠️ FAQ 데이터 파일(data/faq.csv)을 찾을 수 없어요. export_csv.py를 먼저 실행해주세요.")
        return

    df = pd.read_csv(faq_path, encoding="utf-8-sig")

    st.write("### 🔍 내 입맛대로 필터링")

    # 모든 브랜드가 기본으로 체크되도록 초기화
    all_filters = sorted(df["brand"].unique().tolist())
    selected_filters = st.multiselect(
        "📝 조회할 기관 및 브랜드를 선택하세요 (중복 선택 가능)",
        options=all_filters,
    )

    # 통합 키워드 검색창
    search_query = st.text_input("💡 검색어를 입력하세요 (질문이나 답변 내용 전체 검색 가능)", "")

    # 선택된 브랜드로 필터링
    active_filters = selected_filters if selected_filters else all_filters
    filtered_df = df[df["brand"].isin(active_filters)].copy()

    # 키워드 검색 필터 적용
    if search_query:
        filtered_df = filtered_df[
            filtered_df["title"].str.contains(search_query, case=False, na=False) |
            filtered_df["content"].str.contains(search_query, case=False, na=False)
        ]

    st.write("---")

    # 검색 결과 중 상위 50개만 출력
    limited_df = filtered_df.head(50)

    if len(filtered_df) > 50:
        st.write(f"📊 검색 조건에 맞는 FAQ 총 {len(filtered_df)}건 중 **상위 50건**을 출력합니다.")
    else:
        st.write(f"📊 조건에 딱 맞는 FAQ를 총 **{len(limited_df)}**건 찾았습니다!")

    if not limited_df.empty:
        for idx, row in limited_df.iterrows():
            extra_info = ""
            if pd.notna(row.get("category")):
                extra_info = f" | {row['category']}"

            with st.expander(f"📌 [{row['brand']}{extra_info}] {row['title']}"):
                st.write(row['content'])
    else:
        st.info("선택하신 필터나 검색어에 맞는 FAQ가 없어요. 다른 키워드를 입력해 보세요!")