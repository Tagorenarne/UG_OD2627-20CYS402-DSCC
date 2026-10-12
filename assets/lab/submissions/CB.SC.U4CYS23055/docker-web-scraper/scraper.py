import os
import requests
from bs4 import BeautifulSoup

# Read URL from environment variable
target_url = os.getenv(
    "TARGET_URL",
    "https://news.ycombinator.com"
)

try:
    response = requests.get(target_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    titles = soup.find_all(["h1", "h2"])

    print(f"\nScraping: {target_url}\n")

    for i, title in enumerate(titles, 1):
        print(f"{i}. {title.get_text(strip=True)}")

except Exception as e:
    print(f"Error fetching or parsing the URL: {e}")