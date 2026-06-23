import urllib.request

url = 'https://www.amfiindia.com/spages/NAVAll.txt'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    content = response.read().decode('utf-8')

lines = content.split('\n')

direct_growth_funds = []
current_category = None
current_fund_house = None

for idx, line in enumerate(lines):
    line_stripped = line.strip()
    if not line_stripped:
        continue
    
    if ';' not in line_stripped:
        if line_stripped.startswith("Open Ended Schemes") or line_stripped.startswith("Close Ended Schemes") or line_stripped.startswith("Interval Fund"):
            current_category = line_stripped
        else:
            current_fund_house = line_stripped
    else:
        if current_category == "Open Ended Schemes(Other Scheme - Index Funds)":
            parts = line_stripped.split(';')
            if len(parts) >= 5:
                scheme_code = parts[0]
                scheme_name = parts[3]
                nav = parts[4]
                
                # Filter for Direct and Growth (case insensitive)
                name_lower = scheme_name.lower()
                if "direct" in name_lower and "growth" in name_lower and "idcw" not in name_lower and "dividend" not in name_lower:
                    direct_growth_funds.append({
                        "scheme_code": scheme_code,
                        "scheme_name": scheme_name,
                        "nav": nav,
                        "fund_house": current_fund_house
                    })

print(f"Total Direct Growth Index Funds found: {len(direct_growth_funds)}")
print("Sample Direct Growth index funds:")
for f in direct_growth_funds[:20]:
    print(f"{f['scheme_code']} - {f['scheme_name']} ({f['fund_house']})")
