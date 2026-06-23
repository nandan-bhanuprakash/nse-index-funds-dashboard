import urllib.request
import json

scheme_code = "119648"
url = f"https://api.mfapi.in/mf/{scheme_code}"
print(f"Fetching {url}...")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        
    print("Keys in response:", data.keys())
    print("Meta section:")
    print(json.dumps(data.get("meta", {}), indent=2))
    print("First 5 NAV points:")
    print(json.dumps(data.get("data", [])[:5], indent=2))
except Exception as e:
    print("Error:", e)
