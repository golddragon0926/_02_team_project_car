from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os

# ① 백그라운드 실행
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

def clean(text):
    return re.sub(r'\s+', ' ', text).strip()

all_data = []

# ② BMW FAQ 페이지 접속
print("BMW FAQ 페이지 접속 중...")
driver.get("https://faq.bmw.co.kr/s/?language=ko")
time.sleep(5)
print("접속 성공! ✅")

# ③ 도움말 더 보기 버튼 반복 클릭
print("\n도움말 더 보기 버튼 클릭 중...")
click_count = 0

while True:
    try:
        more_btn = driver.find_element(
            By.XPATH,
            "//*[contains(text(),'도움말 더 보기') or contains(text(),'더 보기') or contains(text(),'Load More') or contains(text(),'more')]"
        )
        if more_btn.is_displayed():
            driver.execute_script("arguments[0].click();", more_btn)
            click_count += 1
            print(f"  {click_count}번째 클릭 ✅")
            time.sleep(2)
        else:
            print("버튼 안 보임 → 종료")
            break
    except:
        print(f"더 이상 버튼 없음 → 종료 (총 {click_count}번 클릭)")
        break

# ④ 전체 내용 읽기
print("\nFAQ 내용 수집 중...")
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# ⑤ FAQ 항목 추출 - 방법 1
articles = soup.find_all("article")
print(f"article 태그 수: {len(articles)}개")

for article in articles:
    title_tag = article.find(["h1","h2","h3","h4","h5","strong"])
    if title_tag:
        title = clean(title_tag.get_text())
        content = clean(article.get_text().replace(title, ""))
        if title and len(content) > 10:
            all_data.append({
                "title"  : title,
                "content": content
            })

# 방법 2 - 클래스로 찾기
if len(all_data) == 0:
    print("다른 방법으로 시도 중...")
    items = soup.find_all(class_=lambda x: x and any(
        k in str(x).lower() for k in ["faq", "article", "item", "result", "question"]
    ))
    print(f"항목 수: {len(items)}개")

    for item in items:
        title_tag = item.find(["h1","h2","h3","h4","h5","a","strong"])
        if title_tag:
            title = clean(title_tag.get_text())
            content = clean(item.get_text().replace(title, ""))
            if title and len(content) > 10:
                all_data.append({
                    "title"  : title,
                    "content": content
                })

# ⑥ 결과 확인
print(f"\n총 {len(all_data)}개 FAQ 수집 완료!")

if len(all_data) > 0:
    df = pd.DataFrame(all_data)
    df = df.drop_duplicates()
    print(df.head(5))

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_path = os.path.join(BASE_DIR, "data", "bmw_faq_data.csv")
    df.to_csv(save_path, index=False, encoding="utf-8-sig")
    print(f"\nbmw_faq_data.csv 저장 완료! ✅ ({len(df)}개)")
else:
    print("\n=== 페이지 구조 확인 ===")
    print(soup.get_text()[:2000])

driver.quit()