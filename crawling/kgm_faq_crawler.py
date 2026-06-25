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

# ② 페이지 접속
print("KG모빌리티 FAQ 페이지 접속 중...")
driver.get("https://www.kg-mobility.com/sr/online-center/faq")
time.sleep(10)
print("접속 성공! ✅")

# ③ 한 페이지 스크래핑 함수
def scrape_current_page():
    time.sleep(2)
    page_data = []

    # FAQ 버튼 개수 확인
    faq_btns = driver.find_elements(By.CLASS_NAME, "cursor-zoom")
    print(f"    FAQ 버튼 수: {len(faq_btns)}개")

    for i in range(len(faq_btns)):
        try:
            # 매번 새로 찾기
            faq_btns = driver.find_elements(By.CLASS_NAME, "cursor-zoom")
            btn = faq_btns[i]

            # 제목 가져오기
            full_text = clean(btn.text)
            parts = full_text.split(" ", 1)
            category = parts[0] if len(parts) == 2 else ""
            title = parts[1] if len(parts) == 2 else full_text

            print(f"    {i+1}. {title[:40]}...")

            # ④ 버튼 클릭
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(2)

            # ⑤ accordion-body 에서 답변 가져오기
            faq_btns = driver.find_elements(By.CLASS_NAME, "cursor-zoom")
            btn = faq_btns[i]
            parent = btn.find_element(By.XPATH, "./parent::*")
            siblings = parent.find_elements(By.XPATH, "./following-sibling::*")

            content = ""
            for sib in siblings:
                cls = sib.get_attribute("class") or ""
                if "accordion-body" in cls or "body" in cls:
                    content = clean(sib.text)
                    break

            if title and len(content) > 10:
                page_data.append({
                    "title"   : title,
                    "content" : content,
                    "category": category
                })
                print(f"       답변: {content[:50]}...")
            else:
                print(f"       답변 없음 ❌")

            # ⑥ 다시 클릭해서 닫기
            faq_btns = driver.find_elements(By.CLASS_NAME, "cursor-zoom")
            driver.execute_script("arguments[0].click();", faq_btns[i])
            time.sleep(0.5)

        except Exception as e:
            print(f"    오류: {e}")
            continue

    return page_data

# ④ 전체 페이지 순회
page_num = 1

while True:
    print(f"\n=== 페이지 {page_num} 처리 중 ===")
    page_data = scrape_current_page()
    all_data.extend(page_data)
    print(f"    수집: {len(page_data)}개 / 누적: {len(all_data)}개")

    # 다음 페이지 이동
    try:
        next_page = page_num + 1

        # 5페이지마다 화살표 클릭
        if page_num % 5 == 0:
            print(f"\n    → 다음 페이지 화살표 클릭")
            next_arrow = driver.find_element(By.XPATH,
                "//button[contains(text(),'다음 페이지')]"
            )
            driver.execute_script("arguments[0].click();", next_arrow)
            time.sleep(2)
            page_num += 1
        else:
            next_btn = driver.find_element(By.XPATH,
                f"//button[text()='{next_page}'] | //a[text()='{next_page}']"
            )
            print(f"\n    → {next_page}페이지로 이동")
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(2)
            page_num += 1

    except:
        print(f"\n마지막 페이지 → 종료")
        break

# ⑤ 저장
print(f"\n총 {len(all_data)}개 FAQ 수집 완료!")

if len(all_data) > 0:
    df = pd.DataFrame(all_data)
    df = df.drop_duplicates()
    print(df.head(5))

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_path = os.path.join(BASE_DIR, "data", "kgm_faq_data.csv")
    df.to_csv(save_path, index=False, encoding="utf-8-sig")
    print(f"\nkgm_faq_data.csv 저장 완료! ✅ ({len(df)}개)")
else:
    print("데이터 없음 ❌")

driver.quit()