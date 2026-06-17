import requests
from bs4 import BeautifulSoup

url = "https://ev.or.kr/nportal/partcptn/initFaqAction.do"

headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "Chrome/120.0.0.0 Safari/537.36"
}


response = requests.get(
    url,
    headers=headers
)


print(response.status_code)

html = response.text


soup = BeautifulSoup(
    html,
    "html.parser"
)

print(soup.prettify()[:2000])