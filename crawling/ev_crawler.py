from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time


options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

url = "https://ev.or.kr/nportal/partcptn/initFaqAction.do"
driver.get(url)

wait = WebDriverWait(driver, 10)

data = []


def get_text(element):
    return driver.execute_script(
        "return arguments[0].innerText;",
        element
    ).strip()


def collect_current_page(page_no):

    wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div.board_faq")
        )
    )

    time.sleep(1)

    faq_items = driver.find_elements(
        By.CSS_SELECTOR,
        "div.board_faq"
    )

    print(f"{page_no}페이지 FAQ 개수:", len(faq_items))

    for item in faq_items:

        try:
            title_area = item.find_element(
                By.CSS_SELECTOR,
                "div.faq_title"
            )

            category = title_area.find_element(
                By.CSS_SELECTOR,
                "div:nth-child(2)"
            )

            title = title_area.find_element(
                By.CSS_SELECTOR,
                "div.title"
            )

            content = item.find_element(
                By.CSS_SELECTOR,
                "div.faq_con"
            )

            data.append({
                "page": page_no,
                "category": get_text(category),
                "title": get_text(title),
                "content": get_text(content)
            })

        except Exception as e:
            print("수집 실패:", e)


# 1~4페이지 수집
for page_no in range(1, 5):

    if page_no == 1:
        collect_current_page(page_no)

    else:
        # 페이지 이동
        driver.execute_script(
            f"goPage('statsList','10',{page_no});"
        )

        time.sleep(2)

        collect_current_page(page_no)


df = pd.DataFrame(data)



df = df[
    [
        "title",
        "content",
        "page",
        "category"
    ]
]

df.to_csv(
    "ev_faq_data.csv",
    encoding="utf-8-sig",
    index=False
)

