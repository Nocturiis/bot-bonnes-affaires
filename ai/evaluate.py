import os
import json
# --- CORRECTION ICI : Aligner avec le Quickstart ---
from mistralai import Mistral # Importation de la classe Mistral directement
# Plus besoin d'importer ChatMessage explicitement si on utilise des dictionnaires pour les messages
# from mistralai.models.chat import ChatMessage # <-- Ligne à SUPPRIMER

def evaluate_car_ad(title, description, price, mileage, year, model, brand, fuel_type='N/A', transmission='N/A', body_type='N/A'):
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("La variable d'environnement MISTRAL_API_KEY n'est pas définie.")

    # --- CORRECTION ICI : Initialisation du client comme dans le Quickstart ---
    client = Mistral(api_key=api_key)

    # Nettoyer et préparer les entrées pour le prompt
    description_clean = description if description else "Aucune description fournie."
    mileage_clean = f"{mileage} km" if mileage and str(mileage).strip() != 'N/A' else "Kilométrage non spécifié."
    year_clean = f"Année: {year}" if year and str(year).strip() != 'N/A' else "Année non spécifiée."
    price_clean = f"Prix: {price}" if price and str(price).strip() != 'N/A' else "Prix non spécifié."
    model_brand_clean = f"Modèle: {model}, Marque: {brand}" if model and brand else ""

    fuel_type_clean = f"Type de carburant: {fuel_type}" if fuel_type and str(fuel_type).strip() != 'N/A' else ""
    transmission_clean = f"Transmission: {transmission}" if transmission and str(transmission).strip() != 'N/A' else ""
    body_type_clean = f"Type de carrosserie: {body_type}" if body_type and str(body_type).strip() != 'N/A' else ""

    prompt = f"""
Voici une annonce de vente de voiture d'occasion. Évalue-la de manière rigoureuse selon ces critères :

1. **Prix par rapport au marché** : Est-il **nettement inférieur**, **dans la moyenne**, ou **trop élevé** pour un véhicule de ce type (marque, modèle, année, kilométrage, état apparent) ? Compare implicitement au prix du marché local.
2. **Clarté et complétude de l’annonce** : L’annonce fournit-elle **toutes les infos essentielles** (entretien, nombre de propriétaires, CT, état mécanique, options, défauts éventuels) ? Y a-t-il des éléments **vagues ou absents** ?
3. **Risque d’arnaque** : Détecte les signaux d’alerte : **prix trop beau pour être vrai**, **langage manipulateur**, **formule urgente**, **vendeur peu transparent**, **infos incohérentes**, **photos douteuses ou absentes**, etc.
4. **Attractivité de l’affaire** : En combinant les trois critères ci-dessus, juge si c’est :
   - une **arnaque claire** (1)
   - une **affaire douteuse ou risquée** (2)
   - une **offre banale ou moyenne** (3)
   - une **bonne affaire avec légers doutes** (4)
   - une **affaire en or, sans risque visible, sous-cotée** (5)

### Notation

Attribue une note de 1 à 5 selon cette grille stricte :

- **1 = Arnaque probable**, incohérences ou prix irréaliste, très mauvaise affaire.
- **2 = Affaire risquée ou mauvaise**, prix trop élevé ou annonce douteuse.
- **3 = Offre neutre ou moyenne**, prix dans la norme, pas d'intérêt particulier.
- **4 = Bonne affaire**, légère sous-cote ou bonne transparence.
- **5 = Affaire en or**, vendue **nettement sous le prix du marché**, **aucun signe d’arnaque**, **revente possible avec profit immédiat**.

### Instructions

Ne sois **pas indulgent**. **Note sévèrement** si tu n’as pas assez d'infos. **Méfie-toi par défaut**, la prudence prévaut sur l’optimisme.

Annonce à évaluer :
Titre: {title}
Description: {description_clean}
{price_clean}
{mileage_clean}
{year_clean}
{model_brand_clean}
{fuel_type_clean}
{transmission_clean}
{body_type_clean}

Retourne la réponse **au format JSON strict** uniquement, sans aucune explication additionnelle :
```json
{{
  "note": [1-5],
  "commentaire": "Justification en 2 lignes."
}}


    messages = [
        # --- CORRECTION ICI : Utilisation d'un dictionnaire simple pour le message ---
        {"role": "user", "content": prompt}
    ]

    try:
        # --- CORRECTION ICI : Appel de l'API comme dans le Quickstart ---
        chat_response = client.chat.complete(
            model="mistral-tiny",
            response_format={"type": "json_object"}, # Cette option devrait fonctionner avec cette API
            messages=messages
        )

        content = chat_response.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Erreur lors de l'appel à l'API Mistral : {e}")
        return {"note": 0, "commentaire": "Erreur lors de l'analyse IA ou de la réponse JSON."}

if __name__ == '__main__':
    example_ad = {
        "title": "Honda Civic 1.8 i-VTEC Sport, boîte auto",
        "description": "Belle Civic à vendre, faible consommation, carnet d'entretien complet. Quelques petites rayures.",
        "price": "8500€",
        "mileage": "110000",
        "year": "2015",
        "model": "Civic",
        "brand": "Honda",
        "fuel_type": "Essence",
        "transmission": "Automatique",
        "body_type": "Berline"
    }
    ai_result = evaluate_car_ad(
        example_ad['title'],
        example_ad['description'],
        example_ad['price'],
        example_ad['mileage'],
        example_ad['year'],
        example_ad['model'],
        example_ad['brand'],
        fuel_type=example_ad['fuel_type'],
        transmission=example_ad['transmission'],
        body_type=example_ad['body_type']
    )
    print(ai_result)