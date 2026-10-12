import os
import requests
from bs4 import BeautifulSoup

target_url = os.getenv(
    "TARGET_URL",
    "https://www.amrita.edu/aums/"
)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

try:
    print(f"\nScraping: {target_url}\n")

    response = requests.get(
        target_url,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Find headings
    titles = soup.find_all(["h1", "h2"])

    if not titles:
        print("No H1 or H2 headings found.")
    else:
        print(f"Found {len(titles)} headings:\n")

        for i, title in enumerate(titles, start=1):
            text = title.get_text(" ", strip=True)

            if text:
                print(f"{i}. {text}")

except requests.exceptions.Timeout:
    print("Error: Request timed out.")

except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")

except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: {e}")

except requests.exceptions.RequestException as e:
    print(f"Request Error: {e}")

except Exception as e:
    print(f"Error parsing webpage: {e}")