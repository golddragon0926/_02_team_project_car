import requests

key = 'a1b725c91c2ff7bd7c58a8f6dd1bde049366c3de014b6a57f36bb440a0ca9155'

url = 'http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList'

params = {
    'serviceKey' : key,
    'pageNo'     : '1',
    'numOfRows'  : '10',
    'type'       : 'json'
}

r = requests.get(url, params=params)
print("상태코드:", r.status_code)
print("응답내용:", r.text[:200])