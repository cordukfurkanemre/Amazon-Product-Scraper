from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import requests
import re

ASIN_FILE = "asins.txt"
BASE_URL = "https://www.amazon.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def read_asins():
    """Reads ASINs from the text file."""
    with open(ASIN_FILE, "r", encoding="utf-8") as file:
        return [
            line.strip()
            for line in file
            if line.strip()
        ]


def get_price(soup):
    """Extracts the main price or an available offer price."""

    # Standard product price
    price = soup.select_one(".a-price .a-offscreen")

    if price:
        return price.get_text(" ", strip=True)

    # Some products display their price under buying options/offers.
    for element in soup.select("span.a-color-base"):
        text = element.get_text(" ", strip=True)

        price_pattern = (
            r"^(?:[A-Z]{3}|[$€£¥₺₹₽])\s*\d[\d.,]*$"
            r"|^\d[\d.,]*\s*(?:[A-Z]{3}|[$€£¥₺₹₽])$"
        )

        if re.match(price_pattern, text):
            return text

    return None


def get_product(asin):
    """Fetches product details for a single ASIN."""

    url = f"{BASE_URL}/dp/{asin}"

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        title_element = soup.select_one("#productTitle")

        # Skip pages where a product title could not be found.
        if not title_element:
            return None

        review_element = soup.select_one(
            "#acrCustomerReviewText"
        )

        return {
            "asin": asin,
            "title": title_element.get_text(
                " ",
                strip=True
            ),
            "reviews": (
                review_element.get_text(
                    " ",
                    strip=True
                )
                if review_element
                else None
            ),
            "price": get_price(soup)
        }

    except requests.RequestException:
        return None


def main():
    asins = read_asins()

    print(f"{len(asins)} ASIN loaded.\n")

    # Processes multiple products concurrently.
    # Lower this value if requests become unstable or fail frequently.
    with ThreadPoolExecutor(max_workers=20) as executor:
        products = executor.map(
            get_product,
            asins
        )

        count = 0

        for product in products:
            if not product:
                continue

            count += 1

            print(f"[{count}]")
            print(f"ASIN: {product['asin']}")
            print(f"Title: {product['title']}")
            print(f"Reviews: {product['reviews']}")
            print(f"Price: {product['price']}")
            print("-" * 60)

    print(f"\n{count} products processed.")


if __name__ == "__main__":
    main()