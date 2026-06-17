#----------------------------------
#보조금 스크래핑 코드
#----------------------------------

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

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

def close_popups():
    close_list = [
        "//button[contains(text(),'닫기')]",
        "//a[contains(text(),'닫기')]",
        "//*[@class='close']",
        "//*[@class='btn_close']",
        "//*[@class='popup_close']",
        "//button[contains(text(),'오늘 하루')]",
    ]
    for attempt in range(5):
        closed = 0
        for xpath in close_list:
            try:
                btns = driver.find_elements(By.XPATH, xpath)
                for btn in btns:
                    if btn.is_displayed():
                        btn.click()
                        closed += 1
                        time.sleep(0.5)
            except:
                pass
        if closed == 0:
            break
        time.sleep(1)

all_data = []

print("========== 2026년 시작 ==========")

# ② 페이지 접속
driver.get("https://ev.or.kr/nportal/buySupprt/initPsLocalCarPirceAction.do")
time.sleep(5)
close_popups()

# ③ 2026년 선택
Select(driver.find_element(By.NAME, "year1")).select_by_visible_text("2026")
time.sleep(2)
print("2026년 선택 완료 ✅")

# ④ 조회 버튼 클릭
all_btns = driver.find_elements(By.XPATH, "//button")
for btn in all_btns:
    if "조회" in btn.text and btn.is_displayed():
        driver.execute_script("arguments[0].click();", btn)
        print("조회 완료 ✅")
        time.sleep(5)
        break

# ⑤ 메인 창 핸들 저장
main_window = driver.current_window_handle

# ⑥ 조회 버튼 찾기
buttons = driver.find_elements(
    By.XPATH,
    "/html/body/div[6]/div[2]/div/div[2]/table/tbody/tr/td[3]/a"
)
print(f"조회 버튼 총 {len(buttons)}개 발견")

# ⑦ 전체 클릭 ← 5 → 전체로 변경!
for i in range(len(buttons)):
    try:
        buttons = driver.find_elements(
            By.XPATH,
            "/html/body/div[6]/div[2]/div/div[2]/table/tbody/tr/td[3]/a"
        )

        row  = buttons[i].find_element(By.XPATH, "./ancestor::tr")
        cols = row.find_elements(By.TAG_NAME, "td")
        sido    = clean(cols[0].text)
        sigungu = clean(cols[1].text)

        print(f"  {i+1}. {sido} {sigungu} 클릭...")

        driver.execute_script("arguments[0].click();", buttons[i])
        time.sleep(3)

        # ⑧ 새 창 전환
        all_windows = driver.window_handles
        popup_window = None
        for window in all_windows:
            if window != main_window:
                popup_window = window
                break

        if not popup_window:
            print(f"    새 창 없음 ❌")
            continue

        driver.switch_to.window(popup_window)
        time.sleep(2)

        # ⑨ 팝업 스크래핑
        popup_soup = BeautifulSoup(driver.page_source, "html.parser")
        popup_tables = popup_soup.find_all("table")

        for table in popup_tables:
            headers = [clean(th.text) for th in table.find_all("th")]
            for pop_row in table.find_all("tr"):
                tds = pop_row.find_all("td")
                if len(tds) >= 2:
                    row_data = {
                        "연도"   : "2026",
                        "시도"   : sido,
                        "시군구" : sigungu,
                    }
                    for j, td in enumerate(tds):
                        col_name = headers[j] if j < len(headers) else f"컬럼{j+1}"
                        row_data[col_name] = clean(td.text)
                    all_data.append(row_data)

        # ⑩ 팝업 닫고 복귀
        driver.close()
        driver.switch_to.window(main_window)
        print(f"    완료 ✅")
        time.sleep(1)

    except Exception as e:
        print(f"  {i+1}번 오류: {e}")
        try:
            driver.switch_to.window(main_window)
        except:
            pass
        continue

# ⑪ 저장
df = pd.DataFrame(all_data)
print(f"\n총 {len(df)}개 데이터 수집 완료!")
print(df.head(20))

if len(df) > 0:
    df.to_csv("보조금데이터.csv", index=False, encoding="utf-8-sig")
    print("\n보조금데이터.csv 저장 완료! ✅")
else:
    print("데이터 없음 ❌")

driver.quit()