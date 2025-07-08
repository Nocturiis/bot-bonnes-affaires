import requests
from bs4 import BeautifulSoup
import re
import unicodedata # Ajouté pour la fonction slugify
from urllib.parse import urlparse # Ajouté pour une meilleure analyse d'URL

# Fonction utilitaire pour "slugifier" le texte (le rendre compatible URL)
def slugify(text):
    """
    Convertit une chaîne de caractères en un slug adapté aux URL.
    Gère les accents et les caractères spéciaux.
    """
    if not isinstance(text, str):
        return ""
    # Normalise les caractères Unicode (ex: é -> e) et encode/décode en ASCII pour les ignorer
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    # Remplace les caractères non alphanumériques (sauf tirets/espaces) par rien
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    # Remplace les séquences d'espaces ou de tirets par un seul tiret
    text = re.sub(r'[-\s]+', '-', text)
    return text

def scrape_2ememain(url):
    print(f"Starting scraping from: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lance une erreur HTTP pour les mauvaises réponses (4xx ou 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    listings = []

    # Trouver tous les éléments de liste d'annonces
    listing_elements = soup.find_all('li', class_='hz-Listing--list-item-cars')

    # Tenter d'extraire une marque de l'URL de la page actuelle pour une reconstruction potentielle de l'URL
    parsed_url = urlparse(url)
    path_segments = [s for s in parsed_url.path.split('/') if s]
    
    detected_brand_for_reconstruction = None
    if 'autos' in path_segments:
        autos_index = path_segments.index('autos')
        if autos_index + 1 < len(path_segments):
            # Le segment après 'autos' pourrait être la marque (ex: 'honda')
            potential_brand_segment = path_segments[autos_index + 1]
            # Exclure les segments comme 'f' (pour le carburant) ou 'p' (pour la pagination)
            if potential_brand_segment not in ['f', 'p']: 
                 detected_brand_for_reconstruction = potential_brand_segment
    
    # Si une marque a été détectée, préparez son segment pour le chemin de l'URL
    brand_path_segment_for_reconstruction = f"{detected_brand_for_reconstruction}/" if detected_brand_for_reconstruction else ''

    for listing_element in listing_elements:
        listing_data = {}
        ad_url = None

        # --- 1. Tenter d'obtenir l'URL directement depuis la balise d'ancrage principale ---
        main_link_tag = listing_element.find('a', class_='hz-Link hz-Link--block hz-Listing-coverLink')
        if main_link_tag:
            ad_url = main_link_tag.get('href')

        # --- 2. Si l'URL est manquante, tenter de la reconstruire ---
        if not ad_url:
            title_tag = listing_element.find('h3', class_='hz-Listing-title')
            if title_tag:
                # Extraire l'ID de l'annonce de l'attribut 'id' de la balise h3
                listing_id_match = re.search(r'Listing-title-(m\d+)', title_tag.get('id', ''))
                # Extraire le texte du titre
                title_text = title_tag.get_text(strip=True)

                if listing_id_match and title_text and brand_path_segment_for_reconstruction:
                    listing_id = listing_id_match.group(1)
                    title_slug = slugify(title_text)
                    
                    # Construction de l'URL basée sur le pattern observé sur 2ememain.be
                    # Ex: /v/autos/honda/m1234567890-honda-civic-vtec
                    ad_url = f"/v/autos/{brand_path_segment_for_reconstruction}{listing_id}-{title_slug}"
                    
                    # Assurez-vous que l'URL est absolue
                    if ad_url and not ad_url.startswith('http'):
                        ad_url = f"https://www.2ememain.be{ad_url}"
                    print(f"  > Reconstructed URL for '{title_text[:30]}...': {ad_url}")
                else:
                    # Message si la reconstruction n'est pas possible (ex: ID ou titre manquant)
                    print(f"  > Warning: Lien d'annonce trouvé sans 'href' et impossible de reconstruire l'URL (infos ID/titre/marque manquantes). Ignoré. (HTML partiel: {listing_element})")
                    continue # Passer à l'annonce suivante
            else:
                # Message si la balise h3 elle-même est manquante
                print(f"  > Warning: Lien d'annonce trouvé sans 'href' et pas de balise h3 de titre. Ignoré. (HTML partiel: {listing_element})")
                continue # Passer à l'annonce suivante
        
        # --- Finalisation de l'URL si elle n'est pas encore absolue ---
        if ad_url and not ad_url.startswith('http'):
            ad_url = f"https://www.2ememain.be{ad_url}"

        # --- Vérification finale avant de traiter l'annonce ---
        if not ad_url: 
            print(f"  > Warning: Échec de l'obtention ou de la reconstruction de l'URL de l'annonce. Ignoré. (HTML partiel: {listing_element})")
            continue # Passer à l'annonce suivante

        listing_data['url'] = ad_url

        # --- Extraction des autres détails de l'annonce (logique inchangée) ---
        title_tag = listing_element.find('h3', class_='hz-Listing-title')
        listing_data['title'] = title_tag.get_text(strip=True) if title_tag else 'N/A'

        price_tag = listing_element.find('span', class_='hz-Price-amount')
        listing_data['price'] = price_tag.get_text(strip=True) if price_tag else 'N/A'
        
        attributes = listing_element.find_all('div', class_='hz-Listing-attribute')
        for attr in attributes:
            label_tag = attr.find('div', class_='hz-Listing-attribute-label')
            value_tag = attr.find('div', class_='hz-Listing-attribute-value')
            if label_tag and value_tag:
                label = label_tag.get_text(strip=True)
                value = value_tag.get_text(strip=True)

                if 'Kilométrage' in label:
                    listing_data['mileage'] = value
                elif 'Année' in label:
                    listing_data['year'] = value
                elif 'Carburant' in label:
                    listing_data['fuel_type'] = value
                elif 'Transmission' in label:
                    listing_data['transmission'] = value
                elif 'Carrosserie' in label:
                    listing_data['body_type'] = value
                elif 'Marque' in label: 
                    listing_data['brand'] = value
                elif 'Modèle' in label:
                    listing_data['model'] = value
        
        # Définir des valeurs par défaut si les attributs n'ont pas été trouvés
        listing_data.setdefault('mileage', 'N/A')
        listing_data.setdefault('year', 'N/A')
        listing_data.setdefault('fuel_type', 'N/A')
        listing_data.setdefault('transmission', 'N/A')
        listing_data.setdefault('body_type', 'N/A')
        listing_data.setdefault('brand', 'N/A')
        listing_data.setdefault('model', 'N/A')

        city_tag = listing_element.find('div', class_='hz-Listing-location')
        if city_tag:
            city_span = city_tag.find('span', class_='u-colorTextSecondary')
            listing_data['city'] = city_span.get_text(strip=True) if city_span else 'N/A'
        else:
            listing_data['city'] = 'N/A'

        # La description complète n'est généralement pas sur la page de liste
        listing_data['description'] = 'N/A (description complète sur la page de l\'annonce)'

        listings.append(listing_data)

    print(f"Scraping finished. Found {len(listings)} listings on this page.")
    return listings