import json
import pandas as pd
import re
from thefuzz import fuzz
from thefuzz import process

def clean_vendor_name(name):
    """
    Gentle Cleaning: Removes symbols (#*.) but KEEPS numbers 
    so 'ABC 1' and 'ABC 2' stay separate.
    """
    if not isinstance(name, str): return ""
    
    # 1. Upper case
    name = name.upper()
    
    # 2. Remove ONLY leading symbols and whitespace (keep digits!)
    # Regex: Match #, *, ., -, or space at the start
    name = re.sub(r'^[#\*\-\.\s]+', '', name)
    
    # 3. Remove common legal suffixes (optional)
    remove_list = [' LLC', ' INC', ' DBA', ' FAMILY CHILD CARE', ' ADULT FAMILY HOME']
    for word in remove_list:
        name = name.replace(word, '')
        
    return name.strip()

def clean_scraper_name(name):
    """
    Cleans the Scraper names.
    Input: "Abatiyow Mulki Omar (Abatiyow Family Childcare)"
    Output: Returns a list of potential names
    """
    if not name: return []
    
    name = name.upper()
    potential_names = []
    
    # Check if there is a parenthesis structure: "Owner (Business)"
    match = re.search(r'(.*)\((.*)\)', name)
    if match:
        potential_names.append(clean_vendor_name(match.group(1))) # Owner part
        potential_names.append(clean_vendor_name(match.group(2))) # Business part
    else:
        potential_names.append(clean_vendor_name(name))
        
    return potential_names

def main():
    print("Loading data...")
    
    # --- CONFIGURATION: EXACT CSV HEADERS ---
    csv_file = "VendorPayments2527_simplified.csv"
    col_vendor = "Vendor"
    col_amount = "Amounts Sum"
    col_months = "Months (C/FMonth list)" # <--- THIS WAS THE FIX
    # ----------------------------------------

    # 1. Load CSV (Financial Data)
    try:
        df_csv = pd.read_csv(csv_file, on_bad_lines='skip')
    except FileNotFoundError:
        print(f"Error: Could not find {csv_file}")
        return

    # Clean the names
    df_csv['clean_vendor'] = df_csv[col_vendor].apply(clean_vendor_name)
    
    # Ensure amounts are numbers (replace errors with 0)
    df_csv[col_amount] = pd.to_numeric(df_csv[col_amount], errors='coerce').fillna(0)

    # --- THE SAFE GROUPING ---
    print("Grouping duplicate vendors...")
    
    # We aggregate using the variable names we defined above
    df_grouped = df_csv.groupby('clean_vendor', as_index=False).agg({
        col_vendor: 'first',             # Keep original name
        col_amount: 'sum',               # Sum money
        col_months: lambda x: ' | '.join(x.astype(str)) # Track months
    })

    # Convert to dictionary
    financial_db = df_grouped[df_grouped['clean_vendor'].str.len() > 2].set_index('clean_vendor').to_dict(orient='index')
    
    vendor_names_list = list(financial_db.keys())
    print(f"Database loaded. {len(vendor_names_list)} unique vendors ready for matching.")

    # 2. Load JSONL (Scraper Data)
    merged_data = []
    
    print("Processing scraper data and linking records...")
    
    try:
        with open("childcare_data_final.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                provider = json.loads(line)
                provider_raw_name = provider.get("provider_name", "")
                
                search_names = clean_scraper_name(provider_raw_name)
                
                best_match = None
                best_score = 0
                
                # Try to match scraper name against the CSV list
                if search_names and vendor_names_list:
                    for search_name in search_names:
                        if len(search_name) < 3: continue 
                        
                        # Fuzzy Match
                        match, score = process.extractOne(search_name, vendor_names_list, scorer=fuzz.token_sort_ratio)
                        
                        if score > best_score:
                            best_score = score
                            best_match = match
                
                # DECISION THRESHOLD (> 85% match)
                financial_data = None
                if best_score > 85:
                    financial_data = financial_db.get(best_match)
                    # Add match metadata
                    financial_data['match_confidence'] = best_score
                    financial_data['matched_on_name'] = best_match
                
                # 3. Merge
                provider['financials'] = financial_data if financial_data else "Not Found"
                merged_data.append(provider)

    except FileNotFoundError:
        print("Error: Could not find 'childcare_data_final.jsonl'. Make sure you ran the scraper first.")
        return

    # 4. Save the Master File
    output_filename = "MASTER_CHILDCARE_DB.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, indent=4)
        
    print(f"Done! Merged {len(merged_data)} records.")
    print(f"Saved to {output_filename}")

if __name__ == "__main__":
    main()