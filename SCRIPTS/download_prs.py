import requests
from bs4 import BeautifulSoup
import json
import time
import random

print("🚀 PRS Bill Downloader started...")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

BASE_URL = "https://prsindia.org"

def get_all_bill_links():
    url = "https://prsindia.org/billtrack"
    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.content, "lxml")

    bill_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/billtrack/" in href and href != "/billtrack":
            full_url = BASE_URL + href if href.startswith("/") else href
            if full_url not in bill_links:
                bill_links.append(full_url)

    return bill_links

def get_bill_content(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)

        if len(response.content) < 3000:
            return None

        soup = BeautifulSoup(response.content, "lxml")

        # Extract title
        title = ""
        title_tag = soup.find("h1") or soup.find("h2")
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Extract main content
        content = soup.get_text(separator=" ", strip=True)
        content = " ".join(content.split())

        if len(content) < 200:
            return None

        # Extract category
        category = "General"
        for a in soup.find_all("a", href=True):
            if "/billtrack/category/" in a["href"]:
                category = a.get_text(strip=True)
                break

        return {
            "title": title,
            "category": category,
            "url": url,
            "text": content[:3000]
        }

    except Exception as e:
        print(f"⚠️ Error: {e}")
        return None

# ── Get all bill links ──
print("📋 Fetching bill links...")
bill_links = get_all_bill_links()
print(f"✅ Found {len(bill_links)} bills\n")

articles = []

for i, url in enumerate(bill_links):
    bill = get_bill_content(url)

    if bill:
        articles.append(bill)
        print(f"✅ {i+1}/{len(bill_links)} | {bill['title'][:60]}...")
    else:
        print(f"⏭️  Skipped: {url}")

    # Save every 50 bills
    if len(articles) % 50 == 0 and len(articles) > 0:
        with open("prs_articles.json", "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(articles)} bills...")

    time.sleep(random.uniform(0.5, 1.0))

# Final save
with open("prs_articles.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, indent=2, ensure_ascii=False)

print(f"\n🎯 Done!")
print(f"✅ Bills saved : {len(articles)}")
print(f"📁 Saved to prs_articles.json")