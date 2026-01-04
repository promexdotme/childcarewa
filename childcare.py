import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def scrape_robust():
    # 1. Setup - We keep the browser visible to monitor progress
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Keep commented out to see the scroll happen
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    url = "https://www.findchildcarewa.org/PSS_Search?p=DEL%20Licensed&PSL-0030=Open&PSL-0026=King"
    base_url = "https://www.findchildcarewa.org"
    
    print(f"Opening {url}...")
    driver.get(url)
    time.sleep(5)  # Initial wait for the first batch to load

    # 2. Robust Infinite Scroll Loop
    print("Starting robust scroll process...")
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    retries = 0
    max_retries = 5  # How many times to try if the page seems stuck
    pause_time = 3.0 # Increased wait time to account for browser lag
    
    while True:
        # Scroll to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for load
        time.sleep(pause_time)
        
        # Calculate new height
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # Check if the page grew
        if new_height == last_height:
            retries += 1
            print(f"  > No new items loaded. Retry {retries}/{max_retries}...")
            
            # THE JIGGLE: Scroll up a bit and back down to trigger lazy loaders
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)
            
            # Check height again after jiggle
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height and retries >= max_retries:
                print("  > limit reached or network stopped sending data.")
                break
            elif new_height != last_height:
                print("  > Jiggle worked! Resuming scroll.")
                retries = 0 # Reset retries since we found more data
        else:
            retries = 0 # Reset retries since we found more data
            
        last_height = new_height
        
        # Optional: Print current item count roughly (just counting 'View Details' buttons)
        # This slows down the script slightly, so we only do it every few scrolls if you want, 
        # but here it helps debug.
        # buttons = driver.find_elements("class name", "waco-button_dcyfBlue")
        # print(f"  > Current Page Height: {last_height} | Approx items loaded: {len(buttons)}")
        print(f"  > Scrolled. New height: {last_height}")

    # 3. Parse content
    print("\nScroll finished. Parsing HTML content...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    driver.quit()

    # 4. Extract Links
    links = soup.find_all('a', class_='btn waco-button_dcyfBlue')
    
    extracted_urls = []
    print(f"Found {len(links)} total links. Extracting URLs...")

    for link in links:
        href = link.get('href')
        if href and "/PSS_Provider?id=" in href:
            full_url = base_url + href
            extracted_urls.append(full_url)

    # 5. Output
    output_filename = "childcare_links_full.txt"
    with open(output_filename, "w") as f:
        for url in extracted_urls:
            f.write(url + "\n")
            
    print(f"Success! Extracted {len(extracted_urls)} URLs.")
    print(f"Saved to {output_filename}")

if __name__ == "__main__":
    scrape_robust()