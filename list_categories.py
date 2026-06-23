import urllib.request

url = 'https://www.amfiindia.com/spages/NAVAll.txt'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    content = response.read().decode('utf-8')

lines = content.split('\n')

categories = set()
current_category = None

# Let's parse the file.
# The structure is typically:
# Category Name (e.g. Open Ended Schemes ( Equity Scheme - Large Cap Fund ))
#   Fund House Name (e.g. Aditya Birla Sun Life Mutual Fund)
#     Scheme Code;ISIN Div Payout/ ISIN Growth;ISIN Div Reinvest;Scheme Name;Net Asset Value;Date
# A category line doesn't have semicolons, is not empty, and is before a fund house which is also not empty.
# Actually, let's see how they are structured.
# Let's print lines that do not contain semicolons and are not empty, and see if we can identify categories.

for idx, line in enumerate(lines):
    line_stripped = line.strip()
    if not line_stripped:
        continue
    if ';' not in line_stripped:
        # Check if it looks like a category or fund house
        # Let's print the first 100 such lines
        categories.add(line_stripped)

print(f"Total non-semicolon lines: {len(categories)}")
print("Sample of non-semicolon lines:")
for c in sorted(list(categories))[:100]:
    print(c)
