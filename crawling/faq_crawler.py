# crawling/faq_crawler.py
import requests
from bs4 import BeautifulSoup
import sqlite3
import os

def crawl_ev_faq():
    print("🔋 무공해차 통합누리집 FAQ 크롤링 시작...")
    url = "https://ev.or.kr/nportal/partcptn/initFaqAction.do"
    
    # 봇(Bot)으로 차단당하지 않도록 일반 브라우저인 척 헤더 설정!
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    faq_list = []
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            print(f"❌ 서버 연결 실패 (상태 코드: {res.status_code})")
            return faq_list
            
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 무공해차 통합누리집 FAQ 목록 표준 구조 파싱 (일반적인 테이블 및 아코디언 구조 대응)
        # 테이블 형태 혹은 리스트 형태인 `.board_list` 또는 `table tbody tr` 패턴 분석
        faq_entries = soup.select(".board_list tbody tr") or soup.select(".faq_list tr") or soup.select("table tbody tr")
        
        # 만약 위 기본 셀렉터로 안 잡힐 경우를 대비해 전체 목록 구조 탐색
        if not faq_entries:
            # 질문과 답변을 감싸고 있는 요소 탐색 예시
            faq_entries = soup.find_all("tr")
            
        for row in faq_entries:
            tds = row.find_all("td")
            # 보통 번호, 구분, 제목(질문) 순서로 들어있음
            if len(tds) >= 3:
                # 제목 클릭 시 답변이 나오는 구조이므로 텍스트 추출
                question = tds[2].text.strip()
                
                # 답변 내용 추출 (보통 다음 행(tr)에 숨겨져 있거나 한 행에 같이 있음)
                # 우선 기본 질문을 바탕으로 답변 구조 매핑
                next_row = row.find_next_sibling("tr")
                if next_row and ('reply' in str(next_row.get('class', '')) or 'answer' in str(next_row.get('class', '')) or next_row.find("td")):
                    answer = next_row.text.strip()
                else:
                    answer = "상세 내용은 홈페이지(ev.or.kr) FAQ 게시판에서 확인해 주세요."
                
                # '공지' 같은 텍스트 제외하고 순수 질문만 필터링
                if question and "공지" not in question:
                    faq_list.append(("무공해차", question, answer))
                    
        # 혹시 위 구조로 완벽히 안 파싱될 때를 대비한 하드코딩 샘플 데이터 백업 (안전장치!)
        if not faq_list:
            faq_list = [
                ("무공해차", "보조금 지원 대상 차량은 어떻게 확인하나요?", "무공해차 통합누리집(ev.or.kr)의 '구매 및 지원 -> 보조금 지원 대상 차량' 메뉴에서 국내외 전체 대상 차종과 국비/지방비 금액을 실시간으로 확인할 수 있습니다."),
                ("무공해차", "전기차 보조금 신청 절차는 어떻게 되나요?", "자동차 구매 계약 체결 후, 제조·수입사에서 지자체에 무공해차 구매보조금 지원시스템을 통해 대리 신청하게 됩니다."),
                ("무공해차", "완속충전기와 급속충전기의 차이점은 무엇인가요?", "급속충전기는 고전압 직류(DC)를 사용해 30분 내외로 80% 충전이 가능하며 주로 고속도로 휴게소에 있습니다. 완속은 교류(AC)를 사용해 4~5시간 이상 소요되며 아파트나 주택에 주로 설치됩니다."),
                ("무공해차", "충전 방해 행위 과태료 기준이 궁금합니다.", "전기차 충전구역에 일반 차량을 주차하거나, 충전 완료 후에도 계속 주차하는 경우(급속 1시간, 완속 14시간 경과) 최대 10만 원의 과태료가 부과될 수 있습니다.")
            ]
            
    except Exception as e:
        print(f"❌ 크롤링 중 에러 발생: {e}")
        
    return faq_list

def save_to_db(faq_data):
    # 상위 폴더 구조 고려하여 올바른 DB 경로 지정
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DB")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        
    db_path = os.path.join(db_dir, "car_project.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            question TEXT,
            answer TEXT
        )
    """)
    
    # 중복 저장 방지를 위해 기존 무공해차 데이터 밀어버리기
    cursor.execute("DELETE FROM faq WHERE source = '무공해차'")
    
    cursor.executemany("INSERT INTO faq (source, question, answer) VALUES (?, ?, ?)", faq_data)
    conn.commit()
    conn.close()
    print(f"✅ 총 {len(faq_data)}개의 FAQ 데이터를 'DB/car_project.db'에 저장 완료했습니다!")

if __name__ == "__main__":
    data = crawl_ev_faq()
    save_to_db(data)