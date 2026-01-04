import json

def clean_text(text):
    if not text: return "N/A"
    return str(text).replace('\n', ' ').strip()

def main():
    print("Reading MASTER_CHILDCARE_DB.json...")
    
    try:
        with open("MASTER_CHILDCARE_DB.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: Could not find MASTER_CHILDCARE_DB.json")
        return

    output_file = "AI_KNOWLEDGE_BASE.txt"
    
    print(f"Converting {len(data)} records to full-text format...")
    
    with open(output_file, "w", encoding="utf-8") as f:
        for p in data:
            # --- HEADER ---
            name = clean_text(p.get('provider_name', 'Unknown Name'))
            address = clean_text(p.get('address', 'Unknown Address'))
            phone = clean_text(p.get('phone', 'N/A'))
            
            f.write(f"==================================================\n")
            f.write(f"PROVIDER: {name}\n")
            f.write(f"ADDRESS: {address}\n")
            f.write(f"PHONE: {phone}\n")
            
            # --- FINANCIALS (CRITICAL) ---
            fin = p.get('financials', {})
            if isinstance(fin, dict):
                amount = fin.get('Amounts Sum', 0)
                vendor = fin.get('matched_on_name', 'N/A')
                confidence = fin.get('match_confidence', 0)
                f.write(f"FINANCIAL_TOTAL_STATE_PAYMENTS: ${amount:,.2f}\n")
                f.write(f"FINANCIAL_VENDOR_NAME: {vendor} (Match Confidence: {confidence}%)\n")
            else:
                f.write(f"FINANCIAL_TOTAL_STATE_PAYMENTS: $0.00\n")
                f.write(f"FINANCIAL_VENDOR_NAME: Not Found\n")

            # --- KEY DETAILS ---
            details = p.get('details', {})
            capacity = clean_text(details.get('Licensed Capacity', 'N/A'))
            slots = clean_text(details.get('Total Available Slots', 'N/A'))
            ages = clean_text(details.get('Ages', 'N/A'))
            lic_status = clean_text(details.get('License Status', 'N/A'))
            
            f.write(f"LICENSE_CAPACITY: {capacity}\n")
            f.write(f"OPEN_SLOTS: {slots}\n")
            f.write(f"AGES_SERVED: {ages}\n")
            f.write(f"STATUS: {lic_status}\n")

            # --- COMPLAINTS (THE "VIOLATIONS" SECTION) ---
            complaints = p.get('complaints', [])
            if complaints:
                f.write("\n--- COMPLAINTS & VIOLATIONS ---\n")
                for c in complaints:
                    # Adjust keys based on what your scraper actually found
                    # Usually "Complaint Date" or "Date"
                    date = clean_text(c.get('Complaint Date', c.get('Date', 'Unknown Date')))
                    desc = clean_text(c.get('Description', c.get('Complaint/Violation', 'See report')))
                    status = clean_text(c.get('Status', c.get('Outcome', '')))
                    f.write(f" • DATE: {date} | STATUS: {status} | DETAILS: {desc}\n")
            else:
                f.write("\n--- COMPLAINTS & VIOLATIONS ---\n")
                f.write(" • No complaints recorded in this dataset.\n")

            # --- INSPECTIONS ---
            inspections = p.get('inspections', [])
            if inspections:
                f.write("\n--- INSPECTION HISTORY ---\n")
                for i in inspections:
                    date = clean_text(i.get('Inspections Date', 'Unknown Date'))
                    type_ = clean_text(i.get('Inspection Type', 'Regular'))
                    link = clean_text(i.get('document_url', 'No Link'))
                    f.write(f" • {date} [{type_}] -> REPORT LINK: {link}\n")
            else:
                f.write("\n--- INSPECTION HISTORY ---\n")
                f.write(" • No inspections found.\n")

            f.write("\n") # Spacer between providers

    print(f"Success! Created {output_file} with full details.")
    print("Upload this file to your OpenAI Assistant to fix the data retrieval issues.")

if __name__ == "__main__":
    main()