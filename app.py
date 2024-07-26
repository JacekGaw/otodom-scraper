import requests
from bs4 import BeautifulSoup
import re
import time

start_time = time.time()

def extract_prices_from_otodom(url, page=1):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    if page > 1:
        url += f"&page={page}"

    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html5lib')
        
        # Find all price elements with the specific class
        price_elements = soup.find_all('span', class_='css-2bt9f1')
        
        prices = []
        for element in price_elements:
            price_text = element.text.strip()
            # Extract numeric value from price text
            price_value = re.search(r'([\d\s]+)', price_text)
            if price_value:
                # Clean the price text by removing non-numeric characters
                clean_price = price_value.group(0).replace('\xa0', '').replace(' ', '')
                if(clean_price):
                    price_int = int(clean_price)
                    prices.append(price_int)
                else:
                    continue
        
        if prices:
            return {
                'prices': prices,
                'offerCount': len(prices)
            }
        else:
            print("No prices found on the page.")
            return None
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None

# Use the function
base_url = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/dolnoslaskie/wroclaw/wroclaw/wroclaw?ownerTypeSingleSelect=ALL&by=DEFAULT&direction=DESC&viewType=listing"

# Scrape first 3 pages

for page in range(1, 3):
    
    print(f"\nScraping page {page}:")
    price_info = extract_prices_from_otodom(base_url, page)

    if price_info:
        print(f"Number of offers: {price_info['offerCount']}")
        print("\nIndividual offer prices:")
        sum = 0
        for price in price_info['prices']:
            sum += price
            print(f"{price} PLN")
        
        print(f"Avg = {sum / price_info['offerCount']} ")
    else:
        print("Failed to extract price information.")

print(f"{round(time.time() - start_time, 2)}s")
