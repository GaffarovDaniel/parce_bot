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
        for product_card in soup.select("div.prod-info"):
            product_name_tag = product_card.select_one("h2.product-name")
            company_link_tag = product_card.select_one(".company-name-txt a")
            product_detail_tag = product_card.select_one("a.product-detail")

            company_name = company_link_tag.get_text(" ", strip=True) if company_link_tag else ""
            if not company_name:
                continue

            products_text_parts = []
            if product_name_tag:
                products_text_parts.append(product_name_tag.get_text(" ", strip=True))
            if product_detail_tag:
                products_text_parts.append(product_detail_tag.get_text(" ", strip=True))
            products_text = " | ".join(p for p in products_text_parts if p)

            profile_link = ""
            if company_link_tag and company_link_tag.get("href"):
                profile_link = company_link_tag["href"].strip()

            suppliers.append(
                {
                    "company_name": company_name,
                    "profile_link": profile_link,
                    "products_text": products_text,
                }
            )

    return suppliers
