import os
import json
from dotenv import load_dotenv

from ai.evaluate import evaluate_car_ad
from notify.telegram_bot import send_telegram_message
from scraper.scrape_2ememain import scrape_2ememain_honda_civic

# Charger les variables d'environnement du fichier .env (pour les tests locaux)
load_dotenv()

# Chemin pour stocker les annonces vues
SEEN_ADS_FILE = 'data/annonces_vues.json'

def load_seen_ads():
    if os.path.exists(SEEN_ADS_FILE):
        with open(SEEN_ADS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_seen_ads(ads):
    with open(SEEN_ADS_FILE, 'w', encoding='utf-8') as f:
        json.dump(ads, f, indent=4, ensure_ascii=False)

def main():
    print("Démarrage du bot de détection de bonnes affaires automobiles...")
    seen_ads = load_seen_ads()
    new_ads_count = 0

    # 1. Scraping
    print("Scraping des Honda Civic sur 2ememain.be...")
    raw_listings = scrape_2ememain_honda_civic() # Appel à la nouvelle fonction
    print(f"Trouvé {len(raw_listings)} annonces de Honda Civic.")

    for listing in raw_listings:
        ad_url = listing.get('url')
        if not ad_url or ad_url in [ad['url'] for ad in seen_ads]:
            print(f"Ignorons l'annonce déjà vue ou invalide : {listing.get('title', 'N/A')}")
            continue

        new_ads_count += 1
        print(f"Traitement de la nouvelle annonce : {listing.get('title', 'N/A')} à {ad_url}")

        # Les détails sont déjà dans 'listing' grâce au scraper amélioré,
        # donc pas besoin d'appeler scrape_single_ad_details ici.

        # Pré-traitement/normalisation
        title = listing.get('title', 'N/A')
        description = listing.get('description', 'N/A')
        price = listing.get('price', 'N/A') # Le nettoyage du prix est déjà fait dans le scraper
        mileage = listing.get('mileage', 'N/A') # Nettoyé dans le scraper
        year = listing.get('year', 'N/A') # Nettoyé dans le scraper
        brand = listing.get('brand', 'Honda') # Vient du scraper
        model = listing.get('model', 'Civic') # Vient du scraper
        city = listing.get('city', 'N/A') # Si pas scrapé sur la liste, reste N/A

        # Nouvelles données extraites:
        fuel_type = listing.get('fuel_type', 'N/A')
        transmission = listing.get('transmission', 'N/A')
        body_type = listing.get('body_type', 'N/A')


        # 3. Analyse IA
        print(f"Analyse de l'annonce avec l'IA : {title}")
        ai_result = evaluate_car_ad(
            title,
            description,
            price,
            mileage,
            year,
            model,
            brand,
            fuel_type=fuel_type, # Passer les nouvelles informations à l'IA
            transmission=transmission,
            body_type=body_type
        )
        note = ai_result.get('note', 0)
        comment = ai_result.get('commentaire', 'Pas de commentaire IA.')

        print(f"Note IA : {note}, Commentaire : {comment}")

        # Ajouter les résultats IA à l'annonce
        listing['ai_note'] = note
        listing['ai_comment'] = comment

        # 4. Notification
        if note >= 4:
            message = f"""
            <b>🚘 Nouvelle affaire notée {note}/5 !</b>
            <b>{title}</b>
            Prix: {listing.get('price', 'N/A')} | Km: {listing.get('mileage', 'N/A')} | Année: {listing.get('year', 'N/A')}
            Carburant: {fuel_type} | Transmission: {transmission} | Carrosserie: {body_type}
            ➤ Voir l'annonce : <a href="{ad_url}">Lien</a>
            IA : “{comment}”
            """
            send_telegram_message(message)
            print("Notification envoyée !")

        # Add the processed ad to seen_ads to avoid reprocessing
        seen_ads.append(listing)
        save_seen_ads(seen_ads) # Save after each new ad to prevent data loss on crash

    if new_ads_count == 0:
        print("Aucune nouvelle annonce à traiter.")
    else:
        print(f"Terminé le traitement de {new_ads_count} nouvelles annonces.")


if __name__ == "__main__":
    main()
