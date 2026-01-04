import json
import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# 1. THE PARSER (Extracts data from HTML)
# ==========================================
class ChildCareParser:
    def clean_text(self, text):
        if not text: return ""
        return " ".join(text.split())

    def parse(self, html_content, source_url):
        soup = BeautifulSoup(html_content, 'html.parser')
        data = {
            "source_url": source_url,
            "provider_name": "Unknown",
            "address": "",
            "phone": "",
            "details": {},
            "inspections": [],
            "complaints": [],
            "license_history": []
        }

        # Extract Header (Name)
        try:
            data["provider_name"] = self.clean_text(soup.find("div", class_="panel-heading").find("h1").text)
        except: pass

        # Extract Contact (Address/Phone)
        try:
            panel_body = soup.find("div", class_="panel-body")
            contact_col = panel_body.find("div", class_="col-xs-4")
            paragraphs = contact_col.find_all("p")
            data["address"] = self.clean_text(paragraphs[0].get_text(separator=" "))
            if len(paragraphs) > 1:
                data["phone"] = self.clean_text(paragraphs[1].text)
        except: pass

        # Extract Key/Value Details
        for group in soup.find_all("div", class_="form-group"):
            label = group.find("label")
            val_div = group.find("p", class_="form-control-static")
            if label and val_div:
                key = self.clean_text(label.text).replace(":", "")
                val = self.clean_text(val_div.text)
                if key and val: data["details"][key] = val

        # Extract Tables
        data["inspections"] = self._parse_table(soup, "inspections")
        data["complaints"] = self._parse_table(soup, "complaints")
        data["license_history"] = self._parse_table(soup, "license_history")
        
        return data

    def _parse_table(self, soup, div_id):
        results = []
        tab_div = soup.find("div", id=div_id)
        if not tab_div: return results
        
        table = tab_div.find("table")
        if not table: return results

        headers = [self.clean_text(th.text) for th in table.find_all("th")]
        tbody = table.find("tbody")
        
        if tbody:
            for row in tbody.find_all("tr"):
                cells = row.find_all("td")
                if not cells: continue
                
                row_data = {}
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        row_data[headers[i]] = self.clean_text(cell.text)
                        # Capture PDF Links
                        link = cell.find("a", href=True)
                        if link:
                            row_data["document_url"] = link['href']
                results.append(row_data)
        return results

# ==========================================
# 2. THE MAIN LOOP
# ==========================================
def main():
    # --- CONFIGURATION ---
    input_file = "childcare_links_full.txt"  # The file with your 3000 links
    output_file = "childcare_data_final.jsonl" # Where we save the result
    # ---------------------

    # 1. Setup Selenium (Headless is faster)
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--log-level=3") # Suppress logs
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    parser = ChildCareParser()

    # 2. Read URLs
    try:
        with open(input_file, "r") as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}")
        return

    # 3. Check for existing progress (Resume feature)
    processed_count = 0
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            processed_count = sum(1 for line in f)
    
    print(f"Found {len(urls)} URLs.")
    if processed_count > 0:
        print(f"Resuming... skipping first {processed_count} already processed.")

    # 4. Loop
    with open(output_file, "a", encoding="utf-8") as f_out:
        for i, url in enumerate(urls):
            # Skip if already done
            if i < processed_count:
                continue
            
            print(f"[{i+1}/{len(urls)}] Scraping: {url} ...", end="\r")

            try:
                # Load Page
                driver.get(url)
                
                # Wait briefly for JS to render tabs (adjust if connection is slow)
                # time.sleep(0.5) 
                
                # Parse
                html = driver.page_source
                record = parser.parse(html, url)
                
                # Save immediately (JSON Lines format)
                f_out.write(json.dumps(record) + "\n")
                f_out.flush() # Ensure it writes to disk

            except Exception as e:
                print(f"\nError on {url}: {e}")
                # Optional: write to an error log so you can retry failed ones later

    print(f"\n\nDone! All data saved to {output_file}")
    driver.quit()

if __name__ == "__main__":
    main()