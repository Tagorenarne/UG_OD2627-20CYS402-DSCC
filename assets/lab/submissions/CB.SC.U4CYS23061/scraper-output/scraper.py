import os
import requests
from bs4 import BeautifulSoup

target_url = os.getenv("TARGET_URL", "https://example.com")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

try:
    response = requests.get(target_url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    titles = soup.find_all(["h1", "h2"])

    print(f"\nScraping: {target_url}\n")
    for i, title in enumerate(titles, 1):
        text = title.get_text(strip=True)
        if text:
            print(f"{i}. {text}")

except Exception as e:
    print(f"Error fetching or parsing the URL: {e}")