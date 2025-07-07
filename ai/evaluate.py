from mistralai.client import Mistral
# importez seulement ce dont vous avez besoin : pas de ChatMessage explicitement
import os
import json

def evaluate_car_ad(title, description, price, mileage, year, model, brand, fuel_type='N/A', transmission='N/A', body_type='N/A'):
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("La variable d'environnement MISTRAL_API_KEY n'est pas définie.")

    client = Mistral(api_key=api_key)

    # Nettoyer et préparer les entrées pour le prompt
    description_clean = description if description else "Aucune description fournie."
    mileage_clean = f"{mileage} km" if mileage and mileage != 'N/A' else "Kilométrage non spécifié."
    year_clean = f"Année: {year}" if year and year != 'N/A' else "Année non spécifiée."
    price_clean = f"Prix: {price}" if price and price != 'N/A' else "Prix non spécifié."
    model_brand_clean = f"Modèle: {model}, Marque: {brand}" if model and brand else ""

    # Nouvelles informations pour le prompt
    fuel_type_clean = f"Type de carburant: {fuel_type}" if fuel_type != 'N/A' else ""
    transmission_clean = f"Transmission: {transmission}" if transmission != 'N/A' else ""
    body_type_clean = f"Type de carrosserie: {body_type}" if body_type != 'N/A' else ""


    prompt = f"""
    Voici une annonce de vente de voiture d'occasion. Évalue-la selon ces critères :
    - Prix par rapport au marché pour une Honda Civic (est-il bas, normal, élevé pour ce type de véhicule et ses caractéristiques ?)
    - Clarté et complétude de l’annonce (informations manquantes, description vague ?)
    - Risque d’arnaque (mots-clés suspects, prix irréaliste, demande urgente ?)
    - Intérêt de l’affaire (potentielle bonne affaire, affaire moyenne, mauvaise affaire ?)

    Informations de l'annonce :
    Titre: {title}
    Description: {description_clean}
    {price_clean}
    {mileage_clean}
    {year_clean}
    {model_brand_clean}
    {fuel_type_clean}
    {transmission_clean}
    {body_type_clean}

    Note de 1 (arnaque probable / très mauvaise affaire) à 5 (excellente affaire / coup de fusil), puis justifie en 2 lignes.
    Retourne la réponse au format JSON strict :
    ```json
    {{
      "note": [1-5],
      "commentaire": "Justification en 2 lignes."
    }}
    ```
    """

    messages = [
        # Utilisation d'un dictionnaire simple pour le message
        {"role": "user", "content": prompt}
    ]

    try:
        chat_response = client.chat.complete( # Utilisez client.chat.complete() comme dans la doc
            model="mistral-large-latest",
            response_format={"type": "json_object"},
            messages=messages
        )
        content = chat_response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API Mistral : {e}")
        return {"note": 0, "commentaire": "Erreur lors de l'analyse IA."}

if __name__ == '__main__':
    # ... (Votre exemple d'utilisation reste le même, il appelle juste la fonction evaluate_car_ad)
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
        example_ad['fuel_type'],
        example_ad['transmission'],
        example_ad['body_type']
    )
    print(ai_result)