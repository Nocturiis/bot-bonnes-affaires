import requests
from bs4 import BeautifulSoup
import time
import random
import re

def scrape_2ememain_honda_civic(url="https://www.2ememain.be/l/autos/honda/f/civic/811/#f:10882"):
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

    print(f"Démarrage du scraping des Honda Civic sur 2ememain.be depuis : {url}")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        car_ad_links = soup.find_all('a', class_='hz-Listing-coverLink')

        if not car_ad_links:
            print("Aucun lien d'annonce trouvé avec le sélecteur 'a.hz-Link.hz-Link--block.hz-Listing-coverLink'.")
            print("Le site a peut-être changé sa structure HTML. Veuillez inspecter la page à nouveau.")
            return []

        for ad_link in car_ad_links:
            full_url = "https://www.2ememain.be" + ad_link.get('href')

            if full_url in seen_urls:
                continue

            seen_urls.add(full_url)

            title_tag = ad_link.find('h3', class_='hz-Listing-title')
            title = title_tag.get_text(strip=True) if title_tag else 'N/A'

            price_tag = ad_link.find('span', class_='hz-Title--title4')
            price = price_tag.get_text(strip=True) if price_tag else 'N/A'
            if price != 'N/A':
                price = re.sub(r'[€.,-]', '', price).strip()

            description_tag = ad_link.find('p', class_='hz-Listing-description')
            description = description_tag.get_text(strip=True) if description_tag else 'N/A'

            attributes_container = ad_link.find('div', class_='hz-Listing-attributes')
            year = 'N/A'
            mileage = 'N/A'
            fuel_type = 'N/A'
            transmission = 'N/A' # Initialiser à 'N/A'
            body_type = 'N/A'

            if attributes_container:
                attributes = attributes_container.find_all('span', class_='hz-Attribute')
                for attr in attributes:
                    icon_class = attr.find('i')
                    if icon_class:
                        icon_classes = icon_class.get('class', [])
                        attr_text_raw = attr.get_text(strip=True) # Récupérer le texte brut
                        attr_text = attr_text_raw if attr_text_raw else 'N/A' # S'assurer qu'il n'est pas vide ou None

                        if 'hz-SvgIconCarConstructionYear' in icon_classes:
                            year = attr_text
                        elif 'hz-SvgIconCarMileage' in icon_classes:
                            # Utiliser attr_text qui est garanti non-None
                            mileage = attr_text.replace('km', '').replace('.', '').replace(',', '').strip()
                        elif 'hz-SvgIconCarFuel' in icon_classes:
                            fuel_type = attr_text
                        elif 'hz-SvgIconCarTransmission' in icon_classes:
                            transmission = attr_text
                        elif 'hz-SvgIconCarBody' in icon_classes:
                            body_type = attr_text

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
                'brand': 'Honda',
                'model': 'Civic',
                'city': 'N/A'
            })
            time.sleep(random.uniform(0.1, 0.5))

    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau ou HTTP lors du scraping : {e}")
    except Exception as e:
        print(f"Une erreur inattendue est survenue lors du scraping : {e}")
        import traceback
        traceback.print_exc()
        return []

    print(f"Scraping terminé. {len(listings)} annonces de Honda Civic trouvées.")
    return listings