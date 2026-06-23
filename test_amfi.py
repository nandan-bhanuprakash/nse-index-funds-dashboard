import urllib.request

url = 'https://www.amfiindia.com/spages/NAVAll.txt'
print("Downloading...")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    content = response.read().decode('utf-8')

lines = content.split('\n')
print(f"Total lines: {len(lines)}")

# Let's inspect unique headers or category markers.
# AMFI text format:
# Schemes are grouped under categories. A category line usually doesn't have semicolons and is followed by headers.
# Let's print the first 200 lines to see the structure.
for i in range(200):
    if i < len(lines):
        print(f"{i}: {lines[i]}")
