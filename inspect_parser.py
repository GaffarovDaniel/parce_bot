import requests
from bs4 import BeautifulSoup

url = 'https://www.made-in-china.com/productdirectory.do?word=plastic+packaging&file=&subaction=hunt&style=b&mode=and&code=0&comProvince=nolimit&order=0&isOpenCorrection=1&page=1'
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, headers=headers, timeout=30)
print('status', res.status_code)
print('len', len(res.text))
soup = BeautifulSoup(res.text, 'html.parser')
print('pro-extra', len(soup.select('.pro-extra')))
print('compnay-name-li', len(soup.select('.compnay-name-li')))
print('company-name-txt a', len(soup.select('.company-name-txt a')))
print('product-name', len(soup.select('.product-name')))
print('company-name-wrapper', len(soup.select('.company-name-wrapper')))
print('company-name', len(soup.select('.company-name')))
print('company-link href examples:')
for a in soup.select('.company-name-txt a')[:10]:
    print('-', a.get('href'), repr(a.get_text(strip=True)))
print('---- first pro-extra snippets ----')
for extra in soup.select('.pro-extra')[:3]:
    print('SNIPPET:', extra.get_text(' ', strip=True)[:300])
    print('---')
