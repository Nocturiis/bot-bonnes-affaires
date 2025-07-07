import os
import json
from dotenv import load_dotenv
import time # Don't forget to import time for the sleep function

from ai.evaluate import evaluate_car_ad
from notify.telegram_bot import send_telegram_message
from scraper.scrape_2ememain import scrape_2ememain_honda_civic

# Load environment variables from .env file (for local tests)
load_dotenv()

# Path to store seen ads
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
    with open(SEEN_ADS_FILE, 'w', encoding='utf-8') as f:
        json.dump(ads, f, indent=4, ensure_ascii=False)

def main():
    print("Démarrage du bot de détection de bonnes affaires automobiles...")
    seen_ads = load_seen_ads()
    new_ads_count = 0

    # 1. Scraping
    print("Scraping des Honda Civic sur 2ememain.be...")
    raw_listings = scrape_2ememain_honda_civic()
    print(f"Trouvé {len(raw_listings)} annonces de Honda Civic.")

    for listing in raw_listings:
        ad_url = listing.get('url')
        if not ad_url:
            print(f"Ignorons l'annonce sans URL : {listing.get('title', 'N/A')}")
            continue
        
        # Check if the ad has already been seen by comparing the URL
        # We create a list of URLs of already seen ads for quick search
        seen_urls_list = [ad.get('url') for ad in seen_ads if ad.get('url')]
        if ad_url in seen_urls_list:
            print(f"Ignorons l'annonce déjà vue : {listing.get('title', 'N/A')}")
            continue

        new_ads_count += 1
        print(f"Traitement de la nouvelle annonce : {listing.get('title', 'N/A')} à {ad_url}")

        # --- NEW IMPLEMENTATION HERE: Display extracted information ---
        print("\n--- Informations extraites de l'annonce ---")
        print(f"  Titre: {listing.get('title', 'N/A')}")
        print(f"  URL: {listing.get('url', 'N/A')}")
        print(f"  Prix: {listing.get('price', 'N/A')}")
        print(f"  Kilométrage: {listing.get('mileage', 'N/A')} km")
        print(f"  Année: {listing.get('year', 'N/A')}")
        print(f"  Carburant: {listing.get('fuel_type', 'N/A')}")
        print(f"  Transmission: {listing.get('transmission', 'N/A')}")
        print(f"  Carrosserie: {listing.get('body_type', 'N/A')}")
        # Display only the first 200 characters of the description to avoid overloading logs
        print(f"  Description: {listing.get('description', 'N/A')[:200]}...") 
        print("----------------------------------------\n")
        # --- END OF NEW IMPLEMENTATION ---

        # Pre-processing/normalization - These variables are already extracted and cleaned by the scraper
        title = listing.get('title', 'N/A')
        description = listing.get('description', 'N/A')
        price = listing.get('price', 'N/A')
        mileage = listing.get('mileage', 'N/A')
        year = listing.get('year', 'N/A')
        brand = listing.get('brand', 'Honda')
        model = listing.get('model', 'Civic')
        city = listing.get('city', 'N/A')

        fuel_type = listing.get('fuel_type', 'N/A')
        transmission = listing.get('transmission', 'N/A')
        body_type = listing.get('body_type', 'N/A')

        # 3. AI Analysis
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
        # --- FIX: Convert 'note' to an integer ---
        try:
            note = int(note)
        except (ValueError, TypeError):
            print(f"Avertissement: Impossible de convertir la note '{note}' en entier. Utilisation de 0 par défaut.")
            note = 0
        # --- END FIX ---
        
        comment = ai_result.get('commentaire', 'Pas de commentaire IA.')

        print(f"Note IA : {note}, Commentaire : {comment}")

        # Add AI results to the listing
        listing['ai_note'] = note
        listing['ai_comment'] = comment

        # --- IMPORTANT: Add a delay to avoid rate limiting with the AI API ---
        import time # Ensure time is imported at the top of the file
        time.sleep(2) # Wait for 2 seconds after each AI call
        # --- END OF DELAY ---

        # 4. Notification
        if note >= 4: # Now, 'note' is an integer, comparison is possible
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
        save_seen_ads(seen_ads) # Save after each new ad to prevent data loss in case of a crash

    if new_ads_count == 0:
        print("Aucune nouvelle annonce à traiter.")
    else:
        print(f"Terminé le traitement de {new_ads_count} nouvelles annonces.")


if __name__ == "__main__":
    main()