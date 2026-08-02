import requests
from bs4 import BeautifulSoup

url = 'https://www.made-in-china.com/productdirectory.do?word=plastic+packaging&file=&subaction=hunt&style=b&mode=and&code=0&comProvince=nolimit&order=0&isOpenCorrection=1&page=1'
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(res.text, 'html.parser')
for i, extra in enumerate(soup.select('.pro-extra')[:3], 1):
    print('=== ITEM', i, '===')
    print('company:', extra.select_one('.company-name-txt a').get_text(strip=True) if extra.select_one('.company-name-txt a') else None)
    product_tags = extra.select('.product-name')
    print('product-name count:', len(product_tags))
    for tag in product_tags:
        print('PRODUCT TAG:', tag.name, tag.get('class'), repr(tag.get_text(' ', strip=True)))
    print('---')
    print('raw text snippet:', repr(extra.get_text(' ', strip=True)[:500]))
    print('---')
