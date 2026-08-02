import random
import time
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.made-in-china.com/productdirectory.do"


def scrape_made_in_china(keyword: str, pages: int) -> list[dict[str, str]]:
    encoded_keyword = quote(keyword)
    suppliers: list[dict[str, str]] = []

    for page in range(1, pages + 1):
        if page > 1:
            time.sleep(round(random.uniform(3, 6), 2))

        url = (
            f"{BASE_URL}?word={encoded_keyword}&file=&subaction=hunt&style=b&mode=and"
            f"&code=0&comProvince=nolimit&order=0&isOpenCorrection=1&page={page}"
        )
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
        except requests.RequestException:
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        for company_heading in soup.select("h2.company-name"):
            company_name = company_heading.get_text(" ", strip=True)
            if not company_name:
                continue

            card = company_heading.find_parent(["div", "li", "article", "section"])
            if card is None:
                card = company_heading.parent

            product_block = card.select_one("div.product-list") if card else None
            products_text = product_block.get_text(" ", strip=True) if product_block else ""

            profile_link = ""
            for link in card.find_all("a", href=True) if card else []:
                href = link.get("href", "")
                if href.startswith("http"):
                    profile_link = href
                    break
                if "/company/" in href or "/company" in href:
                    profile_link = urljoin(url, href)
                    break

            suppliers.append(
                {
                    "company_name": company_name,
                    "profile_link": profile_link,
                    "products_text": products_text,
                }
            )

    return suppliers
