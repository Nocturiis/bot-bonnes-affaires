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
Voici une annonce de vente de voiture (neuve ou d'occasion). Évalue-la avec un maximum de rigueur selon les critères suivants. L'objectif est de **déterminer si la voiture peut être revendue rapidement avec bénéfice**, ou si l'annonce cache des pièges.

---

### 1. **Prix vs marché local**
Le prix demandé est-il :
- **objectivement bien en-dessous** du prix du marché actuel (au moins 10–15% sous-coté) ?
- **dans la norme** ?
- **trop élevé ou surestimé**, même en cas de bon état ?
Fais une estimation **implicite**, comme un humain expérimenté en occasion.

### 2. **Qualité de l’annonce**
Contient-elle **tous les éléments cruciaux** :
- historique (propriétaires, entretiens, CT, accidents)
- options et équipements
- état réel et défauts signalés
- photos nombreuses et claires
Toute **absence d'information critique** doit être **pénalisée sévèrement**.

### 3. **Signes de risque ou d’arnaque**
Repère les signaux suivants :
- prix trop bas pour être vrai
- vendeur flou ou formulation vague ("comme neuf", "à voir", "urgent", etc.)
- incohérences (ex : voiture neuve avec plaque étrangère)
- données techniques imprécises ou masquées
- import douteux ou voiture invendable localement

**Ne donne jamais la note maximale si un doute subsiste.**

---

### 4. **Synthèse – attractivité de l’affaire**
Classe l’annonce dans cette grille **ultra stricte** :

- **1 = Arnaque probable ou prix aberrant**
- **2 = Offre peu intéressante ou risquée**
- **3 = Offre banale, sans gain espéré à la revente**
- **4 = Bonne affaire possible, avec réserve**
- **5 = Exception rare : revente quasi immédiate possible avec bénéfice (>= 10%), aucune faille détectée, vendeur clair et complet)**

**⚠️ Par défaut, sois méfiant et pessimiste. Le niveau 5 doit être exceptionnel.** N’accorde cette note **que si toutes les conditions sont réunies** (prix nettement bas + infos complètes + modèle recherché + aucun risque détecté).

---

### Format de réponse :

Retourne la réponse au **format JSON strict**, sans explication additionnelle :

```json
{{
  "note": [1-5],
  "commentaire": "Synthèse en 2 phrases max. Justifie la note en restant neutre et critique."
}}
"""

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
