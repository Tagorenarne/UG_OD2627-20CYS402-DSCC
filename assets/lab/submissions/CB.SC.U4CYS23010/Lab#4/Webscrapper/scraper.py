import os
import requests
from bs4 import BeautifulSoup

target_url = os.environ.get("TARGET_URL", "https://news.ycombinator.com")

try:

    response = requests.get(target_url)
    response.raise_for_status() 
    soup = BeautifulSoup(response.text, 'html.parser')
    
    headings = soup.find_all(['h1', 'h2'])

    print(f"\nScraping: {target_url}\n")
    print("-" * 40)
    
    for i, heading in enumerate(headings, 1):
        title = heading.get_text(strip=True)
        if title:  # Only print if the title isn't blank
            print(f"{i}. [{heading.name.upper()}] {title}")

except Exception as e:
    print(f"Error fetching or parsing the URL: {e}")
