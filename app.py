import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
import time

async def fetch(session, url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    async with session.get(url, headers=headers) as response:
        if response.status != 200:
            print(f"Not recived status 200. Retrying...")
            return await fetch(session, url)
        print(f"Status Code: {response.status}")
        return await response.text()
    
async def get_number_of_pages(session, url):
    response_text = await fetch(session, url)
    soup = BeautifulSoup(response_text, 'html5lib')
    pages = soup.find_all('li', class_='css-1lclt1h')[-1]
    pages_count = int(pages.text.strip())
    print(f"Ilosc stron: {pages_count}")
    if(pages_count):
        return pages_count
    return None

async def extract_prices_from_otodom(session, url, page=1):
    if page > 1:
        url += f"&page={page}"

    response_text = await fetch(session, url)
    soup = BeautifulSoup(response_text, 'html5lib')
    
    price_elements = []
    for div in soup.find_all('div', attrs={'data-cy': 'search.listing.organic'}):
        price_elements.extend(div.find_all('span', class_='css-2bt9f1'))
        price_elements.extend(div.find_all('span', class_='css-1s0utmm'))    # price_elements = soup.find_all('span', class_='css-2bt9f1')
    
    prices = []
    for element in price_elements:
        price_text = element.text.strip()
        # Extract numeric value from price text
        price_value = re.search(r'([\d\s]+)', price_text)
        if price_value:
            # Clean the price text by removing non-numeric characters
            clean_price = price_value.group(0).replace('\xa0', '').replace(' ', '')
            if clean_price:
                price_int = int(clean_price)
                prices.append(price_int)
    
    if prices:
        return {
            'prices': prices,
            'offerCount': len(prices)
        }
    else:
        print("No prices found on the page.")
        return None

async def main():
    start_time = time.time()
    
    base_url = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/dolnoslaskie/wroclaw/wroclaw/wroclaw?viewType=listing%3Fpage%3D345&by=PRICE&direction=ASC"
    
    # pages_to_scrap = 400
    tasks = []
    
    
    async with aiohttp.ClientSession() as session:
        pages_to_scrap = await get_number_of_pages(session, base_url)
        for page in range(1, pages_to_scrap + 1):
            print(f"\nScraping page {page}:")
            task = asyncio.create_task(extract_prices_from_otodom(session, base_url, page))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        sum = 0
        number = 0
        pages_to_check = ""
        for i, price_info in enumerate(results):
            if price_info:
                print(f"\nPage {i+1} - Number of offers: {price_info['offerCount']}")
                print("Individual offer prices:")
                number += price_info['offerCount']
                sum_prices = 0
                for price in price_info['prices']:
                    print(f"{price}zł")
                    sum += price
                    sum_prices += price
                
                print(f"Avg = {round(sum_prices / price_info['offerCount'], 2)}zł")
            else:
                pages_to_check = f"{pages_to_check}, {i+1}"
                print(f"Failed to extract price information from page {i+1}.")
    
    print(f"Items with price: {number}")
    print(f"Pages to check: {pages_to_check}")
    print(f"Scraped {pages_to_scrap} pages in: {round(time.time() - start_time, 2)}s. The average price is: {round(sum / number, 2)}zł")

# Run the main function
asyncio.run(main())
