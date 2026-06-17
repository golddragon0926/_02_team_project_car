import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

url = "https://www.opinet.co.kr/user/cufaq/cufaqSelect.do"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# 1. FAQ 목록 가져오기
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
rows = soup.select("tbody tr")
data = []

for row in rows:

    cols = row.select("td")

    if len(cols) >= 4:
        question_tag = cols[2]
        onclick = question_tag.get("onclick")
        faq_id = None
        if onclick:
            faq_id = re.findall(
                r"\d+",
                onclick
            )[0]
        data.append({
            "id": faq_id,
            "분류":
                cols[1].get_text(strip=True),
            "title":
                cols[2].get_text(strip=True),
            "작성일":
                cols[3].get_text(strip=True)
        })

# 2. 답변 가져오는 함수
def get_answer(faq_id):

    detail_url = (
        "https://www.opinet.co.kr/user/cufaq/cufaqDetail.do"
    )
    payload = {
        "BORD_SN": faq_id,
        "TAB_CODE": "ALL"
    }

    res = requests.post(detail_url, data=payload, headers=headers)
    detail_soup = BeautifulSoup(res.text, "html.parser")

    # 일단 전체 텍스트에서 가져오기
    answer = detail_soup.select_one(".view_contents")
    if answer:
        return answer.get_text(
            " ",
            strip=True
        )
    return "답변 없음"

# # 3. 답변 붙이기

for item in data:
    print("수집중:", item["id"])
    item["content"] = get_answer(item["id"])


df = pd.DataFrame(data)
# 컬럼 순서 변경
new_order = [
    'title',
    'content',
    'id',
    '분류',
    '작성일'
]
df = df[new_order]

# 4. 저장
df.to_csv("opinet_faq_data.csv", encoding="utf-8-sig", index=False)
print("완료")