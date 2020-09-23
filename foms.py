import requests
from bs4 import BeautifulSoup

URL = "http://aofoms.ru/index.php?c=availPolicy"


with requests.Session() as s:
    s.headers={"User-Agent":"Mozilla/5.0"}
    res = s.get(URL)
    soup = BeautifulSoup(res.text, "lxml")
    payload = {item['name']:item.get('value', '') for item in soup.select("input[name]")}
    # print(payload)
    # payload['__EVENTTARGET'] = 'polisYesEnp'
    payload['polis'] = 'enp'
    payload['npolEnp'] = '2847040848000286'
    payload['spol'] = ''
    payload['npol'] = ''
    payload['npolVrem'] = ''
    payload['npolBlank'] = ''
    payload['polisYesEnp'] = 'Найти'

    data = {'polis': 'enp', 'npolEnp': '2847040848000286', 'spol': '', 'npol': '', 'npolVrem': '', 'npolBlank': '', 'polisYesEnp': 'Найти'}

    req = s.post(URL, data=data, headers={"User-Agent":"Mozilla/5.0"})
    soup_obj = BeautifulSoup(req.text, "lxml")
    # print(soup_obj.text)
    res = []
    for items in soup_obj.select("div.content_in > h2"):
        res.append(items.get_text())
    print(res)
        # for i in items.parent.contents:
        #     print(i.string.strip())
    #     data = [item.get_text(strip=True) for item in items.select("div")]
    #     print(data)