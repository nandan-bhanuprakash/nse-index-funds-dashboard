import urllib.request

url = 'https://www.amfiindia.com/spages/NAVAll.txt'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    content = response.read().decode('utf-8')

lines = content.split('\n')

index_funds = []
current_category = None
current_fund_house = None

for idx, line in enumerate(lines):
    line_stripped = line.strip()
    if not line_stripped:
        continue
    
    if ';' not in line_stripped:
        # It's either a category or a fund house.
        # How do we distinguish? Usually category names start with "Open Ended Schemes" or "Close Ended Schemes"
        if line_stripped.startswith("Open Ended Schemes") or line_stripped.startswith("Close Ended Schemes") or line_stripped.startswith("Interval Fund") or line_stripped.startswith("Sanctioned"):
            current_category = line_stripped
        else:
            current_fund_house = line_stripped
    else:
        # It's a scheme line: Scheme Code;ISIN Div Payout/ ISIN Growth;ISIN Div Reinvest;Scheme Name;Net Asset Value;Date
        if current_category == "Open Ended Schemes(Other Scheme - Index Funds)":
            parts = line_stripped.split(';')
            if len(parts) >= 5:
                scheme_code = parts[0]
                isin_growth = parts[1]
                isin_div = parts[2]
                scheme_name = parts[3]
                nav = parts[4]
                date = parts[5] if len(parts) > 5 else ""
                
                index_funds.append({
                    "scheme_code": scheme_code,
                    "isin_growth": isin_growth,
                    "isin_div": isin_div,
                    "scheme_name": scheme_name,
                    "nav": nav,
                    "date": date,
                    "fund_house": current_fund_house
                })

print(f"Total Index Funds found: {len(index_funds)}")
print("Sample index funds:")
for f in index_funds[:15]:
    print(f"{f['scheme_code']} - {f['scheme_name']} ({f['fund_house']}) - NAV: {f['nav']}")
