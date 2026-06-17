import streamlit as st
import pandas as pd
import os
import re

def render_tab5():
    st.subheader("🚗 자동차 통합 FAQ 및 지원 플랫폼")
    st.caption("현대자동차, 기아자동차, 오피넷, BMW, KGM 등 흩어져 있는 자동차 관련 핵심 FAQ를 이곳에서 한방에 검색하세요!")

    base_path = os.getcwd()

    # 1. s분리된 개별 CSV 파일 경로 매핑
    FAQ_SOURCES = {
        "현대자동차": os.path.join(base_path, "data", "hyundai_faq_data.csv"),
        "기아자동차": os.path.join(base_path, "data", "kia_faq_data.csv"),
        "오피넷": os.path.join(base_path, "data", "opinet_faq_data.csv"),
        "BMW": os.path.join(base_path, "data", "bmw_faq_data.csv"),
        "KGM": os.path.join(base_path, "data", "kgm_faq_data.csv")
        # "무공해차": os.path.join("data", "ev_faq_data.csv")
    }

    st.write("### 🔍 내 입맛대로 필터링")

    # 2. 모든 필터가 기본으로 체크되도록 초기화
    all_filters = list(FAQ_SOURCES.keys())
    selected_filters = st.multiselect(
        "📝 조회할 기관 및 브랜드를 선택하세요 (중복 선택 가능)",
        options=all_filters
    )

    # 통합 키워드 검색창
    search_query = st.text_input("💡 검색어를 입력하세요 (질문이나 답변 내용 전체 검색 가능)", "")

    # 3. 선택된 필터에 맞게 CSV 파일들을 실시간 병합
    active_filters = selected_filters if selected_filters else all_filters
    combined_list = []

    for filter_name in active_filters:
        file_path = FAQ_SOURCES[filter_name]

        if os.path.exists(file_path):
            try:
                # 한글 깨짐 및 파싱 줄바꿈 에러 방지용 안전 로드
                temp_df = pd.read_csv(
                    file_path,
                    encoding="utf-8-sig",
                    on_bad_lines='skip'  # 깨진 줄이 있어도 튕기지 않고 패스
                )

                if not temp_df.empty:
                    # 컬럼명 표준화 규칙 (질문 -> title, 답변 -> content)
                    rename_dict = {}
                    for col in temp_df.columns:
                        if col in ['질문', '질문(Question)', 'Title']:
                            rename_dict[col] = 'title'
                        elif col in ['답변', '답변(Answer)', 'Content']:
                            rename_dict[col] = 'content'

                    if rename_dict:
                        temp_df = temp_df.rename(columns=rename_dict)

                    # 데이터 내부의 무분별한 공백과 줄바꿈 실시간 청소🧼
                    def clear_spaces(text):
                        if pd.isna(text):
                            return ""
                        return re.sub(r'\s+', ' ', str(text)).strip()

                    temp_df['title'] = temp_df['title'].apply(clear_spaces)
                    temp_df['content'] = temp_df['content'].apply(clear_spaces)

                    # 출처 태그 부여 후 리스트에 적재
                    temp_df["source"] = filter_name
                    combined_list.append(temp_df)
            except Exception as e:
                st.warning(f"⚠️ {filter_name} 데이터 로드 실패 (사유: {e})")
        else:
            if filter_name == "무공해차":
                st.caption(f"ℹ️ {filter_name} FAQ 데이터는 현재 열심히 준비 중이에요! (파일 대기 중)")

    st.write("---")

    # 4. 종합 믹스 데이터 필터링 및 화면 출력
    if combined_list:
        # 부가 정보 열(분류, 작성일 등)이 달라도 판다스가 유연하게 하나로 묶어줍니다.
        df = pd.concat(combined_list, ignore_index=True, sort=False).drop_duplicates(subset=['title'])

        # 키워드 검색 필터 적용
        if search_query:
            df = df[
                df["title"].str.contains(search_query, case=False, na=False) |
                df["content"].str.contains(search_query, case=False, na=False)
                ]

        # 🎯 [핵심 수정] 검색 결과 중 상위 50개만 슬라이싱하여 제한합니다.
        limited_df = df.head(50)

        # 전체 검색 개수와 화면 표시 개수 상태 파악 후 안내 멘트 분기
        if len(df) > 50:
            st.write(f"📊 검색 조건에 맞는 FAQ 총 {len(df)}건 중 **상위 50건**을 출력합니다.")
        else:
            st.write(f"📊 조건에 딱 맞는 FAQ를 총 **{len(limited_df)}**건 찾았습니다!")

        if not limited_df.empty:
            # 50개로 제한된 데이터프레임(limited_df)만 순회하며 아코디언 출력
            for idx, row in limited_df.iterrows():
                # 부가 정보가 존재하는 경우 라벨 텍스트 동적 생성
                extra_info = ""
                if '분류' in row and pd.notna(row['분류']):
                    extra_info += f" | {row['분류']}"
                if '작성일' in row and pd.notna(row['작성일']):
                    extra_info += f" | {row['작성일']}"

                with st.expander(f"📌 [{row['source']}{extra_info}] {row['title']}"):
                    st.write(row['content'])
        else:
            st.info("선택하신 필터나 검색어에 맞는 FAQ가 없어요. 다른 키워드를 입력해 보세요!")
    else:
        st.info("현재 화면에 불러올 수 있는 FAQ 데이터 파일이 하나도 없습니다.")