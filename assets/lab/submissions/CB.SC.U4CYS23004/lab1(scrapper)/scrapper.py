import os
import urllib.request
from bs4 import BeautifulSoup
from http.server import BaseHTTPRequestHandler, HTTPServer

def run_scraper():
    url = os.environ.get("TARGET_URL", "https://news.ycombinator.com")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            soup = BeautifulSoup(response.read(), 'html.parser')
        
        items = soup.select("span.titleline > a") if "news.ycombinator.com" in url else soup.find_all(['h1', 'h2'])
        titles = [i.get_text(strip=True) for i in items if i.get_text(strip=True)]

        list_items = "".join(f"<li>{t}</li>" for t in titles) or "<li>No items found.</li>"
        return f"<html><body><h1>Scraping: {url}</h1><p>Found {len(titles)} items.</p><ol>{list_items}</ol></body></html>"
    except Exception as e:
        return f"<html><body><h1>Error</h1><p>{e}</p></body></html>"

class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(run_scraper().encode('utf-8'))

if __name__ == "__main__":
    print("Server running on port 8080...")
    HTTPServer(('0.0.0.0', 8080), WebHandler).serve_forever()