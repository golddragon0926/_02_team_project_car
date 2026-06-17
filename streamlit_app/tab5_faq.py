# streamlit_app/tab5_faq.py
import streamlit as st
import sqlite3
import os

def get_faq_data(search_query="", source_filter="전체"):
    # DB 파일 절대 경로 계산 (streamlit_app 폴더 기준으로 한 칸 위 DB 폴더 내부)
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DB", "car_project.db")
    
    if not os.path.exists(db_path):
        return []
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 만약 테이블이 없으면 빈 배열 반환
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='faq'")
    if not cursor.fetchone():
        conn.close()
        return []
        
    sql = "SELECT source, question, answer FROM faq WHERE 1=1"
    params = []
    
    if source_filter != "전체":
        sql += " AND source = ?"
        params.append(source_filter)
        
    if search_query:
        sql += " AND (question LIKE ? OR answer LIKE ?)"
        params.append(f"%{search_query}%")
        params.append(f"%{search_query}%")
        
    cursor.execute(sql, params)
    results = cursor.fetchall()
    conn.close()
    return results

def render_tab5():
    st.title("📋 자동차 및 무공해차 FAQ 게시판")
    st.write("오피넷 및 무공해차 통합누리집에서 수집한 핵심 질문들을 모아둔 공간입니다.")
    st.markdown("---")
    
    # 필터 및 검색창 영역
    col1, col2 = st.columns([1, 2])
    with col1:
        source_filter = st.selectbox("📌 출처 필터", ["전체", "무공해차", "오피넷"])
    with col2:
        search_query = st.text_input("🔍 궁금한 키워드를 검색하세요 (예: 보조금, 충전, 과태료)", "")
        
    # DB에서 검색 데이터 추출
    faqs = get_faq_data(search_query, source_filter)
    
    if not faqs:
        st.info("💡 검색 결과가 없어요! 다른 키워드로 검색하거나 크롤러를 먼저 작동시켜 주세요.")
    else:
        st.success(f"총 {len(faqs)}개의 질문을 찾았습니다!")
        
        # 아코디언 게시판 형태로 표출
        for source, question, answer in faqs:
            badge = "⚡ [무공해차]" if source == "무공해차" else "⛽ [오피넷]"
            with st.expander(f"{badge} {question}"):
                st.write(answer)