from bs4 import BeautifulSoup
import requests

SEARCH_URL = "https://www.amazon.com/s?k=kitchen+organization"
ASIN_FILE = "asins.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def get_asins(url):
    """Fetches an Amazon search page and returns the ASINs found on it."""
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Each search result stores its ASIN in the data-asin attribute.
        products = soup.select(
            '[data-component-type="s-search-result"][data-asin]'
        )

        return [
            product.get("data-asin")
            for product in products
            if product.get("data-asin")
        ]

    except requests.RequestException as error:
        print(f"Request failed: {error}")
        return []


def load_existing_asins():
    """Loads previously collected ASINs to avoid adding duplicates."""
    try:
        with open(ASIN_FILE, "r", encoding="utf-8") as file:
            return {
                line.strip()
                for line in file
                if line.strip()
            }

    except FileNotFoundError:
        return set()


def save_new_asins(asins):
    """Appends only new ASINs to the local ASIN file."""
    existing_asins = load_existing_asins()

    new_asins = [
        asin
        for asin in asins
        if asin not in existing_asins
    ]

    # Append mode keeps the existing ASIN pool and adds only new entries.
    with open(ASIN_FILE, "a", encoding="utf-8") as file:
        for asin in new_asins:
            file.write(asin + "\n")

    return new_asins


def main():
    asins = get_asins(SEARCH_URL)

    if not asins:
        print("No ASINs found.")
        return

    new_asins = save_new_asins(asins)

    print(f"{len(asins)} ASIN found.")
    print(f"{len(new_asins)} new ASIN added.\n")

    for asin in new_asins:
        print(asin)


if __name__ == "__main__":
    main()
