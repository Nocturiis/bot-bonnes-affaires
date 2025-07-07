import requests
from bs4 import BeautifulSoup
import time
import random
import re # Pour les expressions régulières afin de nettoyer les données

def scrape_2ememain_honda_civic(url="https://www.2ememain.be/l/autos/honda/f/civic/811/#f:10882"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7', # Préférer le contenu en français
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Referer': 'https://www.2ememain.be/',
        'Connection': 'keep-alive'
    }
    listings = []
    seen_urls = set() # Pour éviter les doublons au cas où la même annonce apparaîtrait

    print(f"Démarrage du scraping des Honda Civic sur 2ememain.be depuis : {url}")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Lève une erreur HTTP pour les mauvaises réponses (4xx ou 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Trouver tous les conteneurs d'annonces
        # Basé sur votre structure HTML, il semble que chaque annonce soit dans un élément
        # qui contient les classes comme "hz-Listing-group" ou similaire.
        # Nous allons chercher les liens des annonces car ils contiennent l'URL de l'annonce.
        # Le lien principal pour chaque annonce est <a class="hz-Link hz-Link--block hz-Card-link" href="...">
        car_ad_links = soup.find_all('a', class_='hz-Link hz-Link--block hz-Card-link')

        if not car_ad_links:
            print("Aucun lien d'annonce trouvé avec le sélecteur 'a.hz-Link.hz-Link--block.hz-Card-link'. Vérifiez le sélecteur.")
            # Tentons de trouver les éléments div qui contiennent les infos, si les liens ne sont pas trouvés directement
            car_ad_containers = soup.find_all('div', class_='hz-Listing-group')
            print(f"Tentative de trouver des conteneurs d'annonces : {len(car_ad_containers)} trouvés.")
            if not car_ad_containers:
                print("Aucun conteneur d'annonce trouvé avec le sélecteur 'div.hz-Listing-group'. Le site a peut-être changé sa structure.")

        for ad_link in car_ad_links:
            link_href = ad_link.get('href')
            if not link_href or not link_href.startswith('/a/'): # S'assurer que c'est un lien d'annonce valide
                 continue
            full_url = "https://www.2ememain.be" + link_href

            if full_url in seen_urls:
                continue # Skip if already processed

            seen_urls.add(full_url) # Add to seen_urls set

            # Extraire les infos directement du bloc d'annonce sur la page de liste
            # La plupart des informations sont contenues DANS le 'a.hz-Link' lui-même ou ses enfants directs
            title_tag = ad_link.find('h3', class_='hz-Listing-title')
            title = title_tag.get_text(strip=True) if title_tag else 'N/A'

            price_tag = ad_link.find('span', class_='hz-Title--title4') # Ou 'hz-Listing-price-value' selon le contexte précis
            price = price_tag.get_text(strip=True) if price_tag else 'N/A'

            description_tag = ad_link.find('p', class_='hz-Listing-description')
            description = description_tag.get_text(strip=True) if description_tag else 'N/A'

            # Pour les attributs (année, kilométrage, carburant, transmission, carrosserie)
            attributes = ad_link.find_all('span', class_='hz-Attribute')
            year = 'N/A'
            mileage = 'N/A'
            fuel_type = 'N/A'
            transmission = 'N/A'
            body_type = 'N/A'

            for attr in attributes:
                icon_class = attr.find('i')
                if icon_class:
                    if 'hz-SvgIconCarConstructionYear' in icon_class.get('class', []):
                        year = attr.get_text(strip=True).replace(' ', '') # Nettoyer l'espace après l'année
                    elif 'hz-SvgIconCarMileage' in icon_class.get('class', []):
                        mileage = attr.get_text(strip=True).replace('km', '').replace('.', '').replace(',', '').strip()
                    elif 'hz-SvgIconCarFuel' in icon_class.get('class', []):
                        fuel_type = attr.get_text(strip=True)
                    elif 'hz-SvgIconCarTransmission' in icon_class.get('class', []):
                        transmission = attr.get_text(strip=True)
                    elif 'hz-SvgIconCarBody' in icon_class.get('class', []):
                        body_type = attr.get_text(strip=True)


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
                'brand': 'Honda', # Fixé car on cible les Honda Civic
                'model': 'Civic', # Fixé car on cible les Honda Civic
                'city': 'N/A' # La ville n'est généralement pas sur la page de liste, il faudrait visiter l'annonce
            })
            time.sleep(random.uniform(0.1, 0.5)) # Petits délais entre chaque annonce pour la politesse

    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau ou HTTP lors du scraping : {e}")
    except Exception as e:
        print(f"Une erreur inattendue est survenue lors du scraping : {e}")

    print(f"Scraping terminé. {len(listings)} annonces de Honda Civic trouvées.")
    return listings

# La fonction scrape_single_ad_details n'est plus strictement nécessaire pour les champs de base,
# car nous extrayons déjà pas mal d'informations de la page de liste.
# Cependant, elle peut être utile si vous avez besoin d'informations plus profondes
# qui ne sont disponibles que sur la page individuelle (ex: plus de photos, options détaillées, nom du vendeur).
# Pour l'instant, on la met de côté pour la simplicité et la performance.
# Si vous avez besoin de la ville ou d'autres détails non présents sur la liste, il faudra la réintégrer.

# def scrape_single_ad_details(ad_url, headers):
#     # ... (code précédent de scrape_single_ad_details si vous en avez toujours besoin)
#     pass


if __name__ == '__main__':
    print("Démarrage du scraper 2ememain.be pour Honda Civic...")
    honda_civic_listings = scrape_2ememain_honda_civic()
    for listing in honda_civic_listings[:3]: # Afficher les 3 premières annonces pour les tests
        print(json.dumps(listing, indent=2, ensure_ascii=False)) # Afficher joliment le JSON

    print(f"\nScraping de {len(honda_civic_listings)} annonces de Honda Civic effectué.")