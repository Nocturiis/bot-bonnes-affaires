import os
import json
from mistralai.client import MistralClient
from mistralai.types.chat_completion import ChatMessage

def evaluate_car_ad(title, description, price, mileage, year, model, brand, fuel_type='N/A', transmission='N/A', body_type='N/A'):
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("La variable d'environnement MISTRAL_API_KEY n'est pas définie.")

    client = MistralClient(api_key=api_key) # Initialisation du client

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
    Retourne la réponse au format JSON strict (ne mets rien d'autre que le JSON):
    ```json
    {{
      "note": [1-5],
      "commentaire": "Justification en 2 lignes."
    }}
    ```
    """

    messages = [
        # Utilisation de ChatMessage pour plus de robustesse avec les nouvelles versions
        ChatMessage(role="user", content=prompt)
    ]

    try:
        # Revenir à client.chat.completions pour les nouvelles versions
        chat_response = client.chat.completions.create( # Nouvelle méthode pour les versions > 0.5
            model="mistral-tiny",
            response_format={"type": "json_object"}, # Cette option devrait fonctionner maintenant
            messages=messages
        )

        content = chat_response.choices[0].message.content
        # La bibliothèque est censée déjà valider le JSON avec response_format={"type": "json_object"}
        # Mais on garde le json.loads() au cas où et pour avoir un dict.
        return json.loads(content)

    # La gestion des exceptions est plus fine avec les nouvelles versions de la lib
    except Exception as e:
        # Pour le débogage, imprimez l'erreur complète
        import traceback
        traceback.print_exc() 
        print(f"Erreur lors de l'appel à l'API Mistral : {e}")
        return {"note": 0, "commentaire": "Erreur lors de l'analyse IA ou de la réponse JSON."}

if __name__ == '__main__':
    # ... (Votre bloc de test local reste inchangé) ...
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