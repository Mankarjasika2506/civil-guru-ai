import requests
from bs4 import BeautifulSoup
import json
import time

print("🚀 PIB English Article Downloader started...")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

BASE_URL = "https://pib.gov.in/newsite/erelcontent.aspx?relid="

# ── UPSC relevant keywords ──
UPSC_KEYWORDS = [
    "economy", "gdp", "inflation", "budget", "fiscal", "monetary",
    "rbi", "agriculture", "environment", "climate", "constitution",
    "parliament", "policy", "scheme", "ministry", "government",
    "health", "education", "defence", "science", "technology",
    "infrastructure", "welfare", "development", "reform", "act",
    "committee", "bilateral", "international", "trade", "finance",
    "election", "court", "tribunal", "commission", "award"
]

def is_upsc_relevant(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in UPSC_KEYWORDS)

def extract_article(relid):
    url = BASE_URL + str(relid)
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)

        # ── Skip empty/deleted articles immediately ──
        if len(response.content) <= 5500:
            return None

        soup = BeautifulSoup(response.content, "lxml")
        text = soup.get_text(separator=" ", strip=True)

        if len(text) < 200 or "JavaScript must be enabled" in text:
            return None

        ministry = "General"
        lines = text.split("\n")
        for line in lines[:5]:
            if "Ministry" in line or "Department" in line or "Office" in line:
                ministry = line.strip()
                break

        text = " ".join(text.split())

        if "English Releases" in text:
            text = text[text.find("English Releases") + 16:]

        return {
            "id": relid,
            "ministry": ministry,
            "url": url,
            "text": text[:3000]
        }

    except Exception as e:
        print(f"⚠️ Skipping {relid}: {e}")
        return None

# ── Resume from where we stopped ──
START_ID = 201155
END_ID   = 202000

# Load existing articles first
try:
    with open("pib_articles.json", "r", encoding="utf-8") as f:
        articles = json.load(f)
    print(f"✅ Loaded {len(articles)} existing articles")
except:
    articles = []
    print("Starting fresh...")

skipped = 0

print(f"Resuming from ID {START_ID} to {END_ID}...")
print("Please wait.\n")

for relid in range(START_ID, END_ID + 1):
    article = extract_article(relid)

    if article and is_upsc_relevant(article["text"]):
        articles.append(article)
        print(f"✅ {relid} | Total: {len(articles)}")
    else:
        skipped += 1

    # Save every 100 articles
    if len(articles) % 100 == 0 and len(articles) > 0:
        with open("pib_articles.json", "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(articles)} articles so far...")

    time.sleep(0.3)

# Final save
with open("pib_articles.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, indent=2, ensure_ascii=False)

print(f"\n🎯 Done!")
print(f"✅ Relevant articles saved : {len(articles)}")
print(f"⏭️  Skipped                : {skipped}")
print(f"📁 Saved to pib_articles.json")