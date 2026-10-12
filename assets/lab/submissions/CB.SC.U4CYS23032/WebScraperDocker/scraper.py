import os
import requests
from bs4 import BeautifulSoup

# Read URL from environment variable
target_url = os.getenv("TARGET_URL", "https://www.geeksforgeeks.org/")

try:
    response = requests.get(target_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Get all h1 and h2 headings
    titles = soup.find_all(["h1", "h2"])

    # If no h1/h2 headings are found, scrape Hacker News article titles
    if not titles:
        titles = soup.select(".titleline > a")

    print(f"\nScraping: {target_url}\n")

    if titles:
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title.get_text(strip=True)}")
    else:
        print("No headings or article titles found.")

except Exception as e:
    print(f"Error fetching or parsing the URL: {e}")