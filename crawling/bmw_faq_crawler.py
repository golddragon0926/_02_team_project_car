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
    text = re.sub(r'\s+', ' ', text).strip()
    # 앞에 붙은 숫자 제거 (560347 등)
    text = re.sub(r'^\d+', '', text).strip()
    # 이모티콘 제거
    text = re.sub(r'[^\w\s\.,?!()·\-/:%]', '', text)
    # 불필요한 텍스트 제거
    for remove in ["도움이 되었습니까", "모델 & 옵션",
                   "Skip to", "닫기", "전체 도움말 보기"]:
        text = text.replace(remove, "")
    return text.strip()

all_data = []

print("BMW FAQ 페이지 접속 중...")
driver.get("https://faq.bmw.co.kr/s/?language=ko")
time.sleep(5)
print("접속 성공! ✅")

# ① 도움말 더 보기 버튼 반복 클릭
print("\n도움말 더 보기 버튼 클릭 중...")
click_count = 0
while True:
    try:
        more_btn = driver.find_element(By.XPATH,
            "//*[contains(text(),'도움말 더 보기')]"
        )
        if more_btn.is_displayed():
            driver.execute_script("arguments[0].click();", more_btn)
            click_count += 1
            print(f"  {click_count}번째 클릭 ✅")
            time.sleep(2)
        else:
            break
    except:
        print(f"더 이상 버튼 없음 (총 {click_count}번 클릭)")
        break

# ② 전체 도움말 보기 버튼 전부 클릭
print("\n전체 도움말 보기 버튼 클릭 중...")
while True:
    try:
        full_btns = driver.find_elements(By.XPATH,
            "//*[contains(text(),'전체 도움말 보기')]"
        )
        if not full_btns:
            break
        clicked = 0
        for btn in full_btns:
            try:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    clicked += 1
                    time.sleep(1)
            except:
                pass
        print(f"  {clicked}개 클릭 ✅")
        if clicked == 0:
            break
        time.sleep(2)
    except:
        break

print("\nFAQ 내용 수집 중...")
time.sleep(2)
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# ③ article-list-item 클래스로 FAQ 추출
items = soup.find_all(class_="article-list-item")
print(f"FAQ 항목 수: {len(items)}개")

for item in items:
    try:
        # 제목
        title_tag = item.find(class_="article-headline")
        if not title_tag:
            title_tag = item.find(["h1","h2","h3","h4","h5","a"])

        if not title_tag:
            continue

        title = clean(title_tag.get_text())

        # 내용
        body_tag = item.find(class_="article-body")
        if not body_tag:
            body_tag = item.find(class_="article-preview")
        if not body_tag:
            body_tag = item

        content = clean(body_tag.get_text().replace(title_tag.get_text(), ""))

        # 카테고리
        cat_tag = item.find(class_="article-category")
        category = clean(cat_tag.get_text()) if cat_tag else ""

        if title and len(content) > 10 and title != category:
            all_data.append({
                "title"   : title,
                "content" : content,
                "category": category
            })

    except Exception as e:
        continue

# ④ 결과 확인
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
    print("데이터 없음 ❌")

driver.quit()