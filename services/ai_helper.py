import logging
import os

from google import genai

logger = logging.getLogger(__name__)


def categorize_products_with_gemini(products_text: str) -> str:
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        prompt = (
            "Analyze the factory's list of products and return strictly 1-2 words — "
            "the general product category in Russian (for example: Электроника, Упаковка, Пищевая продукция). "
            f"Product list: {products_text}"
        )
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        return (response.text or "Требует уточнения").strip() or "Требует уточнения"
    except Exception as exc:
        logger.exception("Gemini categorization failed: %s", exc)
        return "Требует уточнения"
