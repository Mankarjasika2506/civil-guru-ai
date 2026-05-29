import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Test the stuck IDs specifically
stuck_ids = [201195, 201196, 201197, 201198, 201199, 201200]

for relid in stuck_ids:
    url = f"https://pib.gov.in/newsite/erelcontent.aspx?relid={relid}"
    print(f"\nTesting ID: {relid}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        
        print(f"Status code : {response.status_code}")
        print(f"Response time: {response.elapsed.total_seconds():.2f} sec")
        print(f"Content size: {len(response.content)} bytes")
        print(f"Preview: {response.text[:100]}")
        
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT — server not responding")
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR — server refused")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")