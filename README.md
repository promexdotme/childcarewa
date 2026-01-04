# Washington State Childcare & Financial Data Pipeline

This repository contains a full-scale data engineering pipeline designed to aggregate, clean, and merge Washington State childcare provider data with state financial records. 

By combining web scraping with fuzzy string matching, this project creates a unified **Knowledge Base** that links provider licensing details (capacity, violations, inspections) with state payment data for transparency and analysis.

## 🚀 Overview

The pipeline operates in four distinct stages:
1. **Link Extraction:** Scrapes thousands of provider profile URLs from the WA DCYF portal using Selenium.
2. **Deep Scraping:** Extracts granular data (Contact info, License status, Full Complaint history, and Inspection reports).
3. **Financial Merging:** Uses Fuzzy Logic to link provider names to a separate State Financial CSV, accounting for naming variations (e.g., "Jane Doe LLC" vs "Doe, Jane").
4. **AI Knowledge Base Generation:** Converts the final database into a structured text format optimized for RAG (Retrieval-Augmented Generation) in AI models like OpenAI Assistants.

---

## 📂 Project Structure

| File | Function |
| :--- | :--- |
| `childcare.py` | Handles infinite scrolling on the search portal to collect all provider URLs. |
| `jsonchildcare.py` | Scrapes detailed data from individual provider pages (includes resume-on-fail logic). |
| `merge_data.py` | Merges scraped JSON records with financial CSV data using `thefuzz`. |
| `jsontocsv.py` | Formats the final data into a clean text file (`AI_KNOWLEDGE_BASE.txt`) for LLM use. |
| `VendorPayments2527_simplified.csv` | Input: The raw financial payment data from the state. |
| `MASTER_CHILDCARE_DB.json` | Output: The complete, merged dataset in JSON format. |
| `AI_KNOWLEDGE_BASE.txt` | Output: The human-readable and AI-searchable text version of the data. |

---

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/promexdotme/childcarewa.git
   cd wa-childcare-pipeline
   ```

2. **Install required libraries:**
   ```bash
   pip install selenium beautifulsoup4 pandas thefuzz python-Levenshtein webdriver-manager
   ```

---

## 📑 Execution Steps

### 1. Extract Provider URLs
This script will open a browser and scroll to the bottom of the King County search results to capture all listing links.
```bash
python childcare.py
```

### 2. Scrape Detailed Data
This script iterates through the extracted links. It is designed to be "interruption-proof"—if it stops, rerunning it will automatically resume where it left off.
```bash
python jsonchildcare.py
```

### 3. Merge with Financials
Ensure your financial CSV is in the root folder. This script performs a fuzzy merge to connect providers with their state payment totals.
```bash
python merge_data.py
```

### 4. Export for AI/Research
Generate the final text-based report for use in data analysis or AI knowledge retrieval.
```bash
python jsontocsv.py
```

---

## 📊 Data Features
The final merged output provides a 360-degree view of each provider:
*   **Identification:** Name, Physical Address, and Phone.
*   **Licensing:** Capacity, age groups served, and current license status.
*   **Safety History:** Complete list of complaints, violations, and links to PDF inspection reports.
*   **Financials:** Total state payments received and the confidence score of the name match.

---

## ⚖️ Disclaimer
This project is for informational and educational purposes only. Users are responsible for ensuring compliance with the Terms of Service of the data sources and for the ethical use of public records.
