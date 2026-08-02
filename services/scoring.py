def calculate_supplier_score(company_name: str, products_text: str, keyword: str) -> int:
    score = 50.0
    company_name = company_name or ""
    products_text = products_text or ""
    keyword = keyword or ""

    if keyword.lower() in products_text.lower():
        score += 20

    manufacturer_indicators = ["manufacturer", "factory", "industry", "co., ltd", "co ltd", "ltd", "limited"]
    if any(indicator in company_name.lower() for indicator in manufacturer_indicators):
        score += 20

    trading_indicators = ["trading", "trade", "import", "export"]
    if any(indicator in company_name.lower() for indicator in trading_indicators):
        score -= 30

    if len(products_text.strip()) > 30:
        score += 10

    return max(0, min(100, int(score)))
