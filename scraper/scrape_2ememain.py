import requests
from bs4 import BeautifulSoup
import time
import random
import re

# Renamed the function to be more generic
def scrape_2ememain(url): 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Referer': 'https://www.2ememain.be/',
        'Connection': 'keep-alive'
    }
    listings = []
    seen_urls = set()

    print(f"Starting scraping from: {url}")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        car_ad_links = soup.find_all('a', class_='hz-Listing-coverLink')

        if not car_ad_links:
            print("No ad links found with selector 'a.hz-Link.hz-Link--block.hz-Listing-coverLink'.")
            print("The website structure might have changed. Please inspect the page again.")
            return []

        for ad_link in car_ad_links:
            href = ad_link.get('href')
            if not href:
                print(f"Warning: Ad link found without 'href' attribute. Skipping. (Partial HTML: {ad_link.prettify()[:200]}...)")
                continue

            full_url = "https://www.2ememain.be" + href

            if full_url in seen_urls:
                continue

            seen_urls.add(full_url)

            title_tag = ad_link.find('h3', class_='hz-Listing-title')
            title = title_tag.get_text(strip=True) if title_tag else 'N/A'

            price_tag = ad_link.find('span', class_='hz-Title--title4')
            price = price_tag.get_text(strip=True) if price_tag else 'N/A'
            if price != 'N/A':
                # Remove currency symbols, dots, commas, and strip whitespace
                price = re.sub(r'[€.,-]', '', price).strip()

            description_tag = ad_link.find('p', class_='hz-Listing-description')
            description = description_tag.get_text(strip=True) if description_tag else 'N/A'

            attributes_container = ad_link.find('div', class_='hz-Listing-attributes')
            year = 'N/A'
            mileage = 'N/A'
            fuel_type = 'N/A'
            transmission = 'N/A'
            body_type = 'N/A'

            if attributes_container:
                attributes = attributes_container.find_all('span', class_='hz-Attribute')
                for attr in attributes:
                    icon_class = attr.find('i')
                    if icon_class:
                        icon_classes = icon_class.get('class', [])
                        attr_text_raw = attr.get_text(strip=True)
                        attr_text = attr_text_raw if attr_text_raw else 'N/A'

                        if 'hz-SvgIconCarConstructionYear' in icon_classes:
                            year = attr_text
                        elif 'hz-SvgIconCarMileage' in icon_classes:
                            # Remove 'km', dots, commas, and strip whitespace
                            mileage = attr_text.replace('km', '').replace('.', '').replace(',', '').strip()
                        elif 'hz-SvgIconCarFuel' in icon_classes:
                            fuel_type = attr_text
                        elif 'hz-SvgIconCarTransmission' in icon_classes:
                            transmission = attr_text
                        elif 'hz-SvgIconCarBody' in icon_classes:
                            body_type = attr_text

            # Attempt to extract brand and model from the title as a fallback
            # This is a basic approach and might need refinement for accuracy
            brand = 'N/A'
            model = 'N/A'
            if title and title != 'N/A':
                title_lower = title.lower()
                # Simple attempt to find common brands and then models
                known_brands = {
                    'honda': ['civic', 'cr-v', 'jazz', 'accord'],
                    'volkswagen': ['golf', 'passat', 'polo'],
                    'bmw': ['serie 3', 'serie 5', 'x3'],
                    'mercedes': ['c-klasse', 'e-klasse', 'a-klasse'],
                    'audi': ['a3', 'a4', 'a6'],
                    # Add more brands and their common models here
                }
                
                found_brand = False
                for b, models_list in known_brands.items():
                    if b in title_lower:
                        brand = b.capitalize()
                        found_brand = True
                        for m in models_list:
                            if m in title_lower:
                                model = m.capitalize()
                                break
                        break
                
                # Fallback if no specific brand/model found from known list
                if not found_brand and len(title.split()) > 1:
                    # Take the first word as brand, second as model (very simplistic)
                    brand = title.split()[0]
                    model = title.split()[1]


            listings.append({
                'title': title,
                'price': price,
                'url': full_url,
                'description': description,
                'year': year,
                'mileage': mileage,
                'fuel_type': fuel_type,
                'transmission': transmission,
                'body_type': body_type,
                'brand': brand,
                'model': model,
                'city': 'N/A' # 2ememain.be doesn't usually provide city on listing cards
            })
            time.sleep(random.uniform(0.1, 0.5)) # Small random delay between ad extractions

    except requests.exceptions.RequestException as e:
        print(f"Network or HTTP error during scraping: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during scraping: {e}")
        import traceback
        traceback.print_exc()
        return []

    print(f"Scraping finished. Found {len(listings)} listings on this page.")
    return listings

if __name__ == '__main__':
    import json
    # Example usage for testing the generic scraper
    print("Local test of 2ememain.be scraper...")
    # Use the general auto URL for testing
    test_url = "https://www.2ememain.be/l/autos/#f:10882" 
    general_listings = scrape_2ememain(test_url)
    for listing in general_listings[:5]:
        print(json.dumps(listing, indent=2, ensure_ascii=False))

    print(f"\nScraping of {len(general_listings)} listings completed.")