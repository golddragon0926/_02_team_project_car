import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time


BASE_URL = "https://www.opinet.co.kr"

LIST_URL = BASE_URL + "/user/cufaq/cufaqSelect.do"
DETAIL_URL = BASE_URL + "/user/cufaq/cufaqDetail.do"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_answer(session, faq_id):
    payload = {
        "BORD_SN": faq_id,
        "TAB_CODE": "ALL"
    }

    res = session.post(
        DETAIL_URL,
        data=payload,
        headers=headers
    )

    soup = BeautifulSoup(res.text, "html.parser")

    answer = soup.select_one(".view_contents")

    if answer:
        return answer.get_text(" ", strip=True)

    return "답변 없음"


def get_faq_list_by_page(session, page_no):
    payload = {
        "pageIndex": page_no
    }

    res = session.post(
        LIST_URL,
        data=payload,
        headers=headers
    )

    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select("tbody tr")

    page_data = []

    for row in rows:
        cols = row.select("td")

        if len(cols) >= 4:
            onclick = cols[2].get("onclick")

            faq_id = None

            if onclick:
                faq_id = re.findall(r"\d+", onclick)[0]

            page_data.append({
                "id": faq_id,
                "분류": cols[1].get_text(strip=True),
                "title": cols[2].get_text(strip=True),
                "작성일": cols[3].get_text(strip=True)
            })

    return page_data


session = requests.Session()

all_data = []

# 현재 페이지가 1~4페이지라면
for page_no in range(1, 5):
    print(f"{page_no}페이지 수집중...")

    page_items = get_faq_list_by_page(session, page_no)

    for item in page_items:
        print("답변 수집중:", item["id"], item["title"])

        item["content"] = get_answer(session, item["id"])

        all_data.append(item)

        time.sleep(0.3)


# csv저장
df = pd.DataFrame(all_data)

df = df[
    [
        "title",
        "content",
        "id",
        "분류",
        "작성일"
    ]
]

df.to_csv(
    "opinet_faq_data.csv",
    encoding="utf-8-sig",
    index=False
)