import os
import json
from dotenv import load_dotenv
import time
import random

from ai.evaluate import evaluate_car_ad
from notify.telegram_bot import send_telegram_message
from scraper.scrape_2ememain import scrape_2ememain 

# Charger les variables d'environnement depuis .env (pour les tests locaux)
load_dotenv()

# Chemin du fichier pour stocker les annonces déjà vues
SEEN_ADS_FILE = 'data/annonces_vues.json'

def load_seen_ads():
    if os.path.exists(SEEN_ADS_FILE):
        try:
            with open(SEEN_ADS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Attention: Le fichier {SEEN_ADS_FILE} est corrompu ou vide. Création d'une nouvelle liste.")
            return []
    return []

def save_seen_ads(ads):
    # Assurez-vous que le répertoire 'data/' existe
    os.makedirs(os.path.dirname(SEEN_ADS_FILE), exist_ok=True)
    with open(SEEN_ADS_FILE, 'w', encoding='utf-8') as f:
        json.dump(ads, f, indent=4, ensure_ascii=False)

def main():
    print("Démarrage du bot de détection de bonnes affaires automobiles...")
    seen_ads = load_seen_ads()
    new_ads_count = 0

    # --- LISTE DES URLS DE BASE À SCRAPER ---
    # Pour chaque URL dans cette liste, le bot tentera de scraper les 10 premières pages.
    # Assurez-vous que ces URLs sont les URLs de la *première page* de votre recherche.
    # Exemple: "https://www.2ememain.be/l/autos/honda/f/civic/811/" pour la Civic,
    # ou "https://www.2ememain.be/l/autos/" pour toutes les voitures.

    base_urls_to_monitor = [

        # Seulement les récentes pour éviter le ban Github:

        "https://www.2ememain.be/l/autos/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        "https://www.2ememain.be/l/autos/#f:10882|Language:all-languages|PriceCentsTo:300000|sortBy:SORT_INDEX|sortOrder:DECREASING",
        "https://www.2ememain.be/l/autos/#f:10882|Language:all-languages|PriceCentsTo:300000|mileageTo:100001|sortBy:SORT_INDEX|sortOrder:DECREASING",
        "https://www.2ememain.be/l/autos/f/essence/473/#f:10882,13838|Language:all-languages|PriceCentsTo:300000|mileageTo:100001|sortBy:SORT_INDEX|sortOrder:DECREASING"


        # "https://www.2ememain.be/l/autos/", # All Autos (Pas récents)

        # # Prix
        # "https://www.2ememain.be/l/autos/#f:10882|Language:all-languages|PriceCentsTo:700000|sortBy:SORT_INDEX|sortOrder:DECREASING", # All autos <= 7000€
        # "https://www.2ememain.be/l/autos/f/essence/473/#f:10882|Language:all-languages|PriceCentsTo:700000|sortBy:SORT_INDEX|sortOrder:DECREASING", # All autos <= 7000€ Essence
        # "https://www.2ememain.be/l/autos/#f:10882|Language:all-languages|PriceCentsTo:500000|sortBy:SORT_INDEX|sortOrder:DECREASING", # All autos <= 5000€
        # "https://www.2ememain.be/l/autos/f/essence/473/#f:10882|Language:all-languages|PriceCentsTo:500000|sortBy:SORT_INDEX|sortOrder:DECREASING", # All autos <= 5000€ Essence
        # "https://www.2ememain.be/l/autos/#f:10882|Language:all-languages|PriceCentsTo:400000|sortBy:SORT_INDEX|sortOrder:DECREASING", # All autos <= 4000€
        # "https://www.2ememain.be/l/autos/f/essence/473/#f:10882|Language:all-languages|PriceCentsTo:400000|sortBy:SORT_INDEX|sortOrder:DECREASING", # All autos <= 4000€ Essence

        # # All Autos
        # "https://www.2ememain.be/l/autos/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/f/essence/473/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/f/essence/473/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/f/essence/473/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/f/essence/473/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/f/hybride-electrique-essence/13838/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/f/hybride-electrique-essence/13838/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/f/hybride-electrique-essence/13838/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/f/hybride-electrique-essence/13838/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",

        # # Dacia
        # "https://www.2ememain.be/l/autos/dacia/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/dacia/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/dacia/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/dacia/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/dacia/f/essence/473/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/dacia/f/essence/473/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/dacia/f/essence/473/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/dacia/f/essence/473/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/dacia/f/hybride-electrique-essence/13838/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/dacia/f/hybride-electrique-essence/13838/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/dacia/f/hybride-electrique-essence/13838/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/dacia/f/hybride-electrique-essence/13838/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",

        # # Honda
        # "https://www.2ememain.be/l/autos/honda/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/honda/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/honda/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/honda/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/honda/f/essence/473/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/honda/f/essence/473/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/honda/f/essence/473/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/honda/f/essence/473/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/honda/f/hybride-electrique-essence/13838/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/honda/f/hybride-electrique-essence/13838/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/honda/f/hybride-electrique-essence/13838/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/honda/f/hybride-electrique-essence/13838/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        
        # # Renault
        # "https://www.2ememain.be/l/autos/renault/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/renault/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/renault/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/renault/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/renault/f/essence/473/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/renault/f/essence/473/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/renault/f/essence/473/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/renault/f/essence/473/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/renault/f/hybride-electrique-essence/13838/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/renault/f/hybride-electrique-essence/13838/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/renault/f/hybride-electrique-essence/13838/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/renault/f/hybride-electrique-essence/13838/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",

        # # Toyota
        # "https://www.2ememain.be/l/autos/toyota/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/toyota/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/toyota/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/toyota/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/toyota/f/essence/473/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/toyota/f/essence/473/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/toyota/f/essence/473/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/toyota/f/essence/473/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/toyota/f/hybride-electrique-essence/13838/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/toyota/f/hybride-electrique-essence/13838/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/toyota/f/hybride-electrique-essence/13838/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/toyota/f/hybride-electrique-essence/13838/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        
        # # VW
        # "https://www.2ememain.be/l/autos/volkswagen/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/volkswagen/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/volkswagen/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/volkswagen/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/volkswagen/f/essence/473/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/volkswagen/f/essence/473/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/volkswagen/f/essence/473/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/volkswagen/f/essence/473/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/volkswagen/f/hybride-electrique-essence/13838/#f:10882|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/volkswagen/f/hybride-electrique-essence/13838/#f:10882|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/volkswagen/f/hybride-electrique-essence/13838/#f:10882|mileageTo:100001|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",
        # "https://www.2ememain.be/l/autos/volkswagen/f/hybride-electrique-essence/13838/#f:10882|mileageTo:100001|constructionYearFrom:2015|Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING",

        # # Modèles:
        # "https://www.2ememain.be/l/autos/honda/f/civic/811/", # Honda Civic (Pas récents)
        # "https://www.2ememain.be/l/autos/honda/f/civic/811/#Language:all-languages|sortBy:SORT_INDEX|sortOrder:DECREASING0", # Honda Civic (Pas récents)

    ]

    # Nombre de pages à scraper pour chaque URL de base
    num_pages_per_base_url = 10 

    all_specific_page_urls = []

    # Générer toutes les URLs de pages spécifiques à partir des URLs de base
    print(f"Génération des URLs de pages spécifiques (max {num_pages_per_base_url} pages par base URL)...")
    for base_url in base_urls_to_monitor:
        # Extraire le hash suffixe si présent dans l'URL de base pour le réappliquer à toutes les pages
        url_parts = base_url.split('#', 1)
        clean_base_url = url_parts[0] # URL sans le hash
        hash_suffix = '#' + url_parts[1] if len(url_parts) > 1 else ''

        for page_num in range(1, num_pages_per_base_url + 1):
            if page_num == 1:
                # La première page est l'URL de base + le hash
                full_page_url = clean_base_url + hash_suffix
            else:
                # Les pages suivantes utilisent le format /p/X/
                # Il faut s'assurer que l'URL ne se termine pas déjà par '/' avant d'ajouter 'p/X/'
                # et que le hash est ajouté à la fin.
                effective_base = clean_base_url
                if not effective_base.endswith('/'):
                    effective_base += '/'
                
                full_page_url = f"{effective_base}p/{page_num}/{hash_suffix}"
            
            all_specific_page_urls.append(full_page_url)
    
    print(f"Total de {len(all_specific_page_urls)} URLs de pages générées à scraper.")
    # --- FIN DE LA GÉNÉRATION DES URLS ---

    all_raw_listings = []

    print("\nDémarrage du scraping des annonces sur 2ememain.be...")

    for url_to_scrape in all_specific_page_urls:
        print(f"Scraping de la page : {url_to_scrape}")
        current_page_listings = scrape_2ememain(url_to_scrape)
        all_raw_listings.extend(current_page_listings)
        # Pause entre le scraping de différentes URLs (pages)
        time.sleep(random.uniform(1, 3)) 
    
    print(f"\nTrouvé un total de {len(all_raw_listings)} annonces brutes sur toutes les pages consultées.")

    for listing in all_raw_listings:
        ad_url = listing.get('url')
        if not ad_url:
            print(f"Ignorons l'annonce sans URL : {listing.get('title', 'N/A')}")
            continue
        
        seen_urls_list = [ad.get('url') for ad in seen_ads if ad.get('url')]
        if ad_url in seen_urls_list:
            print(f"Ignorons l'annonce déjà vue : {listing.get('title', 'N/A')}")
            continue

        new_ads_count += 1
        print(f"Traitement de la nouvelle annonce : {listing.get('title', 'N/A')} à {ad_url}")

        print("\n--- Informations extraites de l'annonce ---")
        print(f"  Titre: {listing.get('title', 'N/A')}")
        print(f"  URL: {listing.get('url', 'N/A')}")
        print(f"  Prix: {listing.get('price', 'N/A')}")
        print(f"  Kilométrage: {listing.get('mileage', 'N/A')} km")
        print(f"  Année: {listing.get('year', 'N/A')}")
        print(f"  Carburant: {listing.get('fuel_type', 'N/A')}")
        print(f"  Transmission: {listing.get('transmission', 'N/A')}")
        print(f"  Carrosserie: {listing.get('body_type', 'N/A')}")
        print(f"  Marque: {listing.get('brand', 'N/A')}")
        print(f"  Modèle: {listing.get('model', 'N/A')}")
        print(f"  Description: {listing.get('description', 'N/A')[:200]}...")  
        print("----------------------------------------\n")

        title = listing.get('title', 'N/A')
        description = listing.get('description', 'N/A')
        price = listing.get('price', 'N/A')
        mileage = listing.get('mileage', 'N/A')
        year = listing.get('year', 'N/A')
        brand = listing.get('brand', 'N/A')
        model = listing.get('model', 'N/A')
        city = listing.get('city', 'N/A') 

        fuel_type = listing.get('fuel_type', 'N/A')
        transmission = listing.get('transmission', 'N/A')
        body_type = listing.get('body_type', 'N/A')

        print(f"Analyse de l'annonce avec l'IA : {title}")
        ai_result = evaluate_car_ad(
            title,
            description,
            price,
            mileage,
            year,
            model,
            brand,
            fuel_type=fuel_type,
            transmission=transmission,
            body_type=body_type
        )
        
        note = ai_result.get('note', 0)
        try:
            note = int(note)
        except (ValueError, TypeError):
            print(f"Avertissement: Impossible de convertir la note '{note}' en entier. Utilisation de 0 par défaut.")
            note = 0
        
        comment = ai_result.get('commentaire', 'Pas de commentaire IA.')

        print(f"Note IA : {note}, Commentaire : {comment}")

        listing['ai_note'] = note
        listing['ai_comment'] = comment

        time.sleep(2) # Pause après chaque appel à l'IA

        if note >= 4:
            message = f"""
            <b>🚘 Nouvelle affaire notée {note}/5 !</b>
            <b>{title}</b>
            Marque: {brand} | Modèle: {model}
            Prix: {listing.get('price', 'N/A')} | Km: {listing.get('mileage', 'N/A')} | Année: {listing.get('year', 'N/A')}
            Carburant: {fuel_type} | Transmission: {transmission} | Carrosserie: {body_type}
            ➤ Voir l'annonce : <a href="{ad_url}">Lien</a>
            IA : “{comment}”
            """
            send_telegram_message(message)
            print("Notification envoyée !")

        seen_ads.append(listing)
        save_seen_ads(seen_ads) 

    if new_ads_count == 0:
        print("Aucune nouvelle annonce à traiter.")
    else:
        print(f"Terminé le traitement de {new_ads_count} nouvelles annonces.")


if __name__ == "__main__":
    main()