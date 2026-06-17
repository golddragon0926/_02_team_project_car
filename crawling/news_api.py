import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import urllib.parse
from email.utils import parsedate_to_datetime

# 핵심: 여기에 st.cache_data를 걸어두면 app.py에서 불러다 쓸 때도 캐싱이 적용됩니다!
@st.cache_data(ttl=3600)
def get_google_news(keyword, max_items=5):
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"

    response = requests.get(url)
    if response.status_code != 200:
        return None

    root = ET.fromstring(response.text)
    news_list = []

    for i, item in enumerate(root.findall('.//item')):
        if i >= max_items:
            break

        title = item.find('title').text
        link = item.find('link').text
        pubDate_raw = item.find('pubDate').text

        dt = parsedate_to_datetime(pubDate_raw)
        formatted_date = dt.strftime('%Y-%m-%d')

        news_list.append({
            'keyword': keyword,
            'date': formatted_date,
            'title': title,
            'link': link
        })

    return pd.DataFrame(news_list)


# ==========================================
# 🛠️ 테스트 실행 블록 (여기서부터 추가하세요)
# ==========================================
if __name__ == "__main__":
      # 1. 테스트할 키워드 설정
      test_keyword = "하이브리드"
      print(f"[{test_keyword}] 관련 최신 구글 뉴스 수집 테스트를 시작합니다...\n")

      # 2. 함수 실행 (기사 3개만 가져와보기)
      test_df = get_google_news(test_keyword, max_items=3)

      # 3. 결과 확인
      if test_df is not None and not test_df.empty:
          print("✅ 성공! 뉴스를 완벽하게 가져왔습니다.\n")

          # 보기 좋게 한 줄씩 출력
          for index, row in test_df.iterrows():
              print(f"📅 {row['date']}")
              print(f"📰 {row['title']}")
              print(f"🔗 {row['link']}")
              print("-" * 50)
      else:
          print("❌ 실패! 뉴스를 가져오지 못했습니다. 네트워크 상태나 코드를 확인해주세요.")

