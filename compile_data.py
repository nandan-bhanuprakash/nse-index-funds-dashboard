import urllib.request
import json
from datetime import datetime, timedelta
import concurrent.futures
import time

# A lookup table for popular index funds to populate AUM, Expense Ratio, and Tracking Error
POPULAR_FUNDS_LOOKUP = {
    # UTI
    "120716": {"aum": 18240, "expense_ratio": 0.18, "tracking_error": 0.03, "benchmark": "Nifty 50"},
    "120717": {"aum": 4650, "expense_ratio": 0.33, "tracking_error": 0.05, "benchmark": "Nifty Next 50"},
    "148967": {"aum": 5230, "expense_ratio": 0.46, "tracking_error": 0.08, "benchmark": "Nifty 200 Momentum 30"},
    "151838": {"aum": 890, "expense_ratio": 0.15, "tracking_error": 0.04, "benchmark": "Crisil SDL June 2027"},
    
    # HDFC
    "119063": {"aum": 13950, "expense_ratio": 0.20, "tracking_error": 0.03, "benchmark": "Nifty 50"},
    "149231": {"aum": 1940, "expense_ratio": 0.30, "tracking_error": 0.05, "benchmark": "Nifty Next 50"},
    "151509": {"aum": 580, "expense_ratio": 0.30, "tracking_error": 0.08, "benchmark": "Nifty Midcap 150"},
    "151523": {"aum": 440, "expense_ratio": 0.30, "tracking_error": 0.10, "benchmark": "Nifty Smallcap 250"},
    "152014": {"aum": 280, "expense_ratio": 0.22, "tracking_error": 0.06, "benchmark": "Nifty IT"},
    "152912": {"aum": 450, "expense_ratio": 0.30, "tracking_error": 0.10, "benchmark": "Nifty India Defence"},
    "151125": {"aum": 2150, "expense_ratio": 0.16, "tracking_error": 0.03, "benchmark": "Nifty G-Sec Dec 2026"},
    
    # ICICI Pru
    "120282": {"aum": 7480, "expense_ratio": 0.17, "tracking_error": 0.03, "benchmark": "Nifty 50"},
    "120286": {"aum": 3720, "expense_ratio": 0.30, "tracking_error": 0.05, "benchmark": "Nifty Next 50"},
    "149301": {"aum": 420, "expense_ratio": 0.30, "tracking_error": 0.08, "benchmark": "Nifty Midcap 150"},
    "150150": {"aum": 320, "expense_ratio": 0.30, "tracking_error": 0.10, "benchmark": "Nifty Smallcap 250"},
    "149305": {"aum": 610, "expense_ratio": 0.20, "tracking_error": 0.06, "benchmark": "Nifty Bank"},
    "149867": {"aum": 310, "expense_ratio": 0.22, "tracking_error": 0.06, "benchmark": "Nifty IT"},
    "150820": {"aum": 1540, "expense_ratio": 0.15, "tracking_error": 0.04, "benchmark": "Nifty SDL Dec 2028"},
    
    # SBI
    "125192": {"aum": 6850, "expense_ratio": 0.18, "tracking_error": 0.03, "benchmark": "Nifty 50"},
    "149154": {"aum": 870, "expense_ratio": 0.32, "tracking_error": 0.05, "benchmark": "Nifty Next 50"},
    "150920": {"aum": 1820, "expense_ratio": 0.15, "tracking_error": 0.04, "benchmark": "Crisil Gilt Index"},
    
    # Nippon India
    "120594": {"aum": 1350, "expense_ratio": 0.20, "tracking_error": 0.04, "benchmark": "Nifty 50"},
    "148704": {"aum": 540, "expense_ratio": 0.35, "tracking_error": 0.06, "benchmark": "Nifty Next 50"},
    "148694": {"aum": 980, "expense_ratio": 0.20, "tracking_error": 0.08, "benchmark": "Nifty Midcap 150"},
    "148708": {"aum": 650, "expense_ratio": 0.25, "tracking_error": 0.10, "benchmark": "Nifty Smallcap 250"},
    "148698": {"aum": 420, "expense_ratio": 0.22, "tracking_error": 0.07, "benchmark": "Nifty Bank"},
    
    # Motilal Oswal
    "147575": {"aum": 1410, "expense_ratio": 0.30, "tracking_error": 0.08, "benchmark": "Nifty Midcap 150"},
    "147579": {"aum": 720, "expense_ratio": 0.35, "tracking_error": 0.10, "benchmark": "Nifty Smallcap 250"},
    "147571": {"aum": 530, "expense_ratio": 0.20, "tracking_error": 0.06, "benchmark": "Nifty Bank"},
    "150390": {"aum": 410, "expense_ratio": 0.35, "tracking_error": 0.08, "benchmark": "Nifty 200 Momentum 30"},
    "145029": {"aum": 4560, "expense_ratio": 0.24, "tracking_error": 0.12, "benchmark": "Nasdaq 100"},
    "148203": {"aum": 3210, "expense_ratio": 0.38, "tracking_error": 0.15, "benchmark": "S&P 500"},
    
    # Bandhan
    "122822": {"aum": 1120, "expense_ratio": 0.10, "tracking_error": 0.03, "benchmark": "Nifty 50"},
    "149176": {"aum": 340, "expense_ratio": 0.40, "tracking_error": 0.20, "benchmark": "S&P 500"},
    
    # Navi
    "148918": {"aum": 1240, "expense_ratio": 0.06, "tracking_error": 0.03, "benchmark": "Nifty 50"},
    
    # Axis
    "147854": {"aum": 480, "expense_ratio": 0.15, "tracking_error": 0.05, "benchmark": "Nifty 50"},
    
    # Tata
    "120228": {"aum": 720, "expense_ratio": 0.18, "tracking_error": 0.04, "benchmark": "Nifty 50"},
    
    # DSP
    "145341": {"aum": 460, "expense_ratio": 0.21, "tracking_error": 0.04, "benchmark": "Nifty 50"}
}

def download_amfi_file():
    url = 'https://www.amfiindia.com/spages/NAVAll.txt'
    print("Downloading AMFI Master Scheme list...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
    return content.split('\n')

def clean_name(name):
    # Standardize AMC name presentation
    name = name.replace("Mutual Fund", "").replace("MF", "").replace("Mutual  Fund", "").strip()
    return name

def parse_index_funds(lines):
    index_funds = []
    current_category = None
    current_fund_house = None
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        if ';' not in line_stripped:
            if line_stripped.startswith("Open Ended Schemes") or line_stripped.startswith("Close Ended Schemes") or line_stripped.startswith("Interval Fund"):
                current_category = line_stripped
            else:
                current_fund_house = clean_name(line_stripped)
        else:
            if current_category == "Open Ended Schemes(Other Scheme - Index Funds)":
                parts = line_stripped.split(';')
                if len(parts) >= 5:
                    scheme_code = parts[0]
                    scheme_name = parts[3]
                    nav = parts[4]
                    
                    # Target Direct Growth plans
                    name_lower = scheme_name.lower()
                    if "direct" in name_lower and "growth" in name_lower and "idcw" not in name_lower and "dividend" not in name_lower:
                        index_funds.append({
                            "scheme_code": scheme_code,
                            "name": scheme_name,
                            "category": "Other Index Fund",  # Default category
                            "benchmark": "Benchmark Index",  # Default benchmark
                            "aum": None,
                            "expense_ratio": None,
                            "tracking_error": None,
                            "latest_nav": float(nav) if nav and nav != "N.A." and nav != "-" else None,
                            "fund_house": current_fund_house
                        })
    return index_funds

def detect_category_and_benchmark(fund):
    name = fund["name"]
    name_lower = name.lower()
    
    # Categorization logic based on name analysis
    if "nifty 50" in name_lower and "next" not in name_lower and "equal" not in name_lower:
        fund["category"] = "Large Cap (Nifty 50)"
        fund["benchmark"] = "Nifty 50"
    elif "nifty next 50" in name_lower or "next50" in name_lower:
        fund["category"] = "Large Cap (Nifty Next 50)"
        fund["benchmark"] = "Nifty Next 50"
    elif "midcap 150" in name_lower or "mid cap 150" in name_lower:
        fund["category"] = "Mid Cap (Nifty Midcap 150)"
        fund["benchmark"] = "Nifty Midcap 150"
    elif "smallcap 250" in name_lower or "small cap 250" in name_lower:
        fund["category"] = "Small Cap (Nifty Smallcap 250)"
        fund["benchmark"] = "Nifty Smallcap 250"
    elif any(kw in name_lower for kw in ["gilt", "sdl", "g-sec", "constant duration", "debt", "psu", "corporate"]):
        fund["category"] = "Debt"
        if "gilt" in name_lower:
            fund["benchmark"] = "Crisil Gilt Index"
        elif "sdl" in name_lower:
            fund["benchmark"] = "Crisil SDL Index"
        else:
            fund["benchmark"] = "Debt Target Maturity Index"
    elif any(kw in name_lower for kw in ["nasdaq", "s&p 500", "sp 500", "us equity", "fang", "overseas", "global"]):
        fund["category"] = "International"
        if "nasdaq" in name_lower:
            fund["benchmark"] = "Nasdaq 100"
        elif "s&p 500" in name_lower or "sp 500" in name_lower:
            fund["benchmark"] = "S&P 500"
        elif "fang" in name_lower:
            fund["benchmark"] = "NYSE FANG+"
        else:
            fund["benchmark"] = "International Index"
    else:
        fund["category"] = "Sectoral / Thematic"
        if "bank" in name_lower:
            fund["benchmark"] = "Nifty Bank"
        elif "it" in name_lower:
            fund["benchmark"] = "Nifty IT"
        elif "momentum" in name_lower:
            fund["benchmark"] = "Nifty 200 Momentum 30"
        elif "defence" in name_lower:
            fund["benchmark"] = "Nifty India Defence"
        else:
            # Try to extract Nifty name
            idx = name_lower.find("nifty")
            if idx != -1:
                # Get next few words
                words = name[idx:].split()
                fund["benchmark"] = " ".join(words[:3])
            else:
                fund["benchmark"] = "Custom Index"
                
    # Overwrite with lookup table if available
    code = fund["scheme_code"]
    if code in POPULAR_FUNDS_LOOKUP:
        lookup = POPULAR_FUNDS_LOOKUP[code]
        fund["aum"] = lookup.get("aum")
        fund["expense_ratio"] = lookup.get("expense_ratio")
        fund["tracking_error"] = lookup.get("tracking_error")
        fund["category"] = lookup.get("category", fund["category"])
        fund["benchmark"] = lookup.get("benchmark", fund["benchmark"])

def get_nav_at_approx_date(nav_data, target_dt):
    closest_nav = None
    min_diff = None
    closest_entry_date = None
    
    for entry in nav_data:
        try:
            entry_dt = datetime.strptime(entry["date"], "%d-%m-%Y")
        except ValueError:
            continue
        diff = abs((entry_dt - target_dt).days)
        if min_diff is None or diff < min_diff:
            min_diff = diff
            closest_nav = float(entry["nav"])
            closest_entry_date = entry["date"]
            
        if diff == 0:
            break
            
    if min_diff is not None and min_diff <= 15:
        return closest_nav, closest_entry_date
    return None, None

def fetch_rolling_returns(fund):
    scheme_code = fund["scheme_code"]
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    
    # 2 Retries with a short wait
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
            
            nav_list = res_data.get("data", [])
            if not nav_list:
                return fund
                
            latest_entry = nav_list[0]
            latest_nav = float(latest_entry["nav"])
            latest_date_str = latest_entry["date"]
            latest_dt = datetime.strptime(latest_date_str, "%d-%m-%Y")
            
            returns = {}
            periods = {
                "6M": latest_dt - timedelta(days=182),
                "1Y": latest_dt - timedelta(days=365),
                "2Y": latest_dt - timedelta(days=365 * 2),
                "3Y": latest_dt - timedelta(days=365 * 3),
                "5Y": latest_dt - timedelta(days=365 * 5),
            }
            
            for period_name, target_dt in periods.items():
                old_nav, matched_date = get_nav_at_approx_date(nav_list, target_dt)
                if old_nav and old_nav > 0:
                    if period_name in ["6M", "1Y"]:
                        ret_val = ((latest_nav - old_nav) / old_nav) * 100
                    else:
                        years = (latest_dt - datetime.strptime(matched_date, "%d-%m-%Y")).days / 365.25
                        ret_val = ((latest_nav / old_nav) ** (1.0 / years) - 1) * 100
                    returns[period_name] = round(ret_val, 2)
                else:
                    returns[period_name] = None
                    
            fund["latest_nav"] = latest_nav
            fund["latest_date"] = latest_date_str
            fund["returns"] = returns
            return fund
        except Exception as e:
            if attempt < 2:
                time.sleep(1.5)
            else:
                # Fail gracefully by setting empty returns instead of dropping the fund!
                fund["returns"] = {"6M": None, "1Y": None, "2Y": None, "3Y": None, "5Y": None}
                return fund
    return fund

def main():
    start_time = time.time()
    
    # 1. Download AMFI file and parse all schemes
    raw_lines = download_amfi_file()
    all_index_funds = parse_index_funds(raw_lines)
    print(f"Total Direct Growth Index Funds identified in AMFI: {len(all_index_funds)}")
    
    # 2. Enrich category/benchmark/lookup data
    for fund in all_index_funds:
        detect_category_and_benchmark(fund)
        
    # To avoid overloading the API server and taking too long, let's cap the thread pool
    # We will process 5 concurrently with a sleep to prevent rate limiting
    print("Fetching NAV history and calculating rolling returns concurrently...")
    enriched_funds = []
    
    total = len(all_index_funds)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all jobs
        futures = {executor.submit(fetch_rolling_returns, fund): fund for fund in all_index_funds}
        
        count = 0
        for future in concurrent.futures.as_completed(futures):
            count += 1
            res = future.result()
            if res:
                enriched_funds.append(res)
            if count % 20 == 0 or count == total:
                print(f"Progress: {count}/{total} funds parsed...")
            # Tiny sleep to throttle requests
            time.sleep(0.05)
            
    # Sort by category then fund house then name
    enriched_funds.sort(key=lambda x: (x["category"], x["fund_house"], x["name"]))
    
    # Save output JSON database
    output_path = "funds_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched_funds, f, indent=2, ensure_ascii=False)
        
    print("\n-------------------------------------------")
    print(f"Successfully compiled {len(enriched_funds)} index funds in {time.time() - start_time:.2f} seconds.")
    print(f"Data saved to {output_path}")
    print("-------------------------------------------")

if __name__ == "__main__":
    main()
