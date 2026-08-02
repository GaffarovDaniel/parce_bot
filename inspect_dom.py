import requests
from bs4 import BeautifulSoup

url = 'https://www.made-in-china.com/productdirectory.do?word=plastic+packaging&file=&subaction=hunt&style=b&mode=and&code=0&comProvince=nolimit&order=0&isOpenCorrection=1&page=1'
headers = {'User-Agent': 'Mozilla/5.0'}
r = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(r.text, 'html.parser')
extra = soup.select_one('.pro-extra')
if not extra:
    print('no pro-extra found')
    raise SystemExit(1)

parent = extra.parent
print('extra parent tag', parent.name, 'classes', parent.get('class'))
print('parent children tags:')
for i, child in enumerate(parent.find_all(recursive=False), 1):
    print(i, child.name, child.get('class'))

print('--- parent text snippet ---')
print(parent.get_text(' ', strip=True)[:800])

print('--- siblings ---')
for sib in parent.next_siblings:
    if getattr(sib, 'name', None):
        print('sib', sib.name, sib.get('class'))
        print('text', sib.get_text(' ', strip=True)[:200])
        break

print('--- searching within parent for product-like classes ---')
for tag in parent.find_all(True):
    cls = tag.get('class') or []
    txt = tag.get_text(' ', strip=True)
    if any(k in cls for k in ['product', 'prod', 'goods', 'item']) or any('product' in c for c in cls):
        print('tag', tag.name, cls, 'text', repr(txt[:150]))
print('--- done ---')
