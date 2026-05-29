import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Check bills page
url = "https://prsindia.org/billtrack"
response = requests.get(url, headers=HEADERS, timeout=10)
soup = BeautifulSoup(response.content, "lxml")

# Find all bill links
print("📋 Bills found:\n")
links = soup.find_all("a", href=True)

bills = []
for a in links:
    href = a["href"]
    text = a.get_text(strip=True)
    if "/bills/" in href or "/billtrack/" in href:
        full_url = "https://prsindia.org" + href if href.startswith("/") else href
        print(f"✅ {text[:60]} → {full_url}")
        bills.append(full_url)

print(f"\nTotal bill links: {len(bills)}")