# 🤖 Bot de Bonnes Affaires Automobiles (2ememain.be)

## 🌟 Aperçu du Projet

Ce dépôt contient un bot Python intelligent conçu pour détecter les "bonnes affaires" sur le site d'annonces automobiles belge **2ememain.be** (ou d'autres plateformes configurées). Il se concentre actuellement sur la **Honda Civic**.

Le bot fonctionne en trois étapes principales :

1.  **Scraping Web** : Il parcourt les annonces sur 2ememain.be pour les Honda Civic.
2.  **Analyse IA** : Il utilise l'API de **Mistral AI** pour évaluer chaque annonce, en lui attribuant une note de 1 à 5 et un commentaire justificatif.
3.  **Notification Telegram** : Si une annonce est jugée "bonne affaire" (note de 4/5 ou plus), le bot envoie une notification détaillée via un bot Telegram.

Le bot est conçu pour être exécuté régulièrement (par exemple, via une tâche planifiée ou GitHub Actions) afin de surveiller les nouvelles annonces et d'alerter l'utilisateur en temps réel.

## ✨ Fonctionnalités

  * **Scraping ciblé** des annonces de Honda Civic sur 2ememain.be.
  * **Intégration de l'IA** (Mistral AI) pour l'évaluation intelligente des prix, de la clarté de l'annonce, et du risque d'arnaque.
  * **Système de notation** des annonces (1 à 5).
  * **Notifications personnalisables** via Telegram pour les annonces à haute valeur.
  * **Gestion des annonces déjà vues** pour éviter les doublons et les notifications répétées.
  * **Gestion du "Rate Limiting"** pour une utilisation respectueuse de l'API Mistral AI.

## 🚀 Démarrage Rapide

Suivez ces étapes pour configurer et lancer le bot sur votre machine locale ou un serveur.

### Prérequis

  * Python 3.8 ou supérieur
  * Un compte Mistral AI et une **clé API** valide.
  * Un bot Telegram et un **chat ID** où les notifications seront envoyées.

### 1\. Cloner le Dépôt

```bash
git clone https://github.com/votre_utilisateur/votre_repo.git
cd votre_repo
```

### 2\. Créer l'Environnement Virtuel (Recommandé)

```bash
python -m venv .venv
source .venv/bin/activate  # Sur Linux/macOS
# ou
.venv\Scripts\activate     # Sur Windows
```

### 3\. Installer les Dépendances

```bash
pip install -r requirements.txt
```

### 4\. Configuration des Variables d'Environnement

Créez un fichier `.env` à la racine de votre projet avec les informations suivantes :

```
MISTRAL_API_KEY="votre_cle_api_mistral_ai"
TELEGRAM_BOT_TOKEN="votre_token_de_bot_telegram"
TELEGRAM_CHAT_ID="votre_id_de_chat_telegram"
```

  * **`MISTRAL_API_KEY`**: Votre clé API Mistral AI (obtenue sur `console.mistral.ai`).
  * **`TELEGRAM_BOT_TOKEN`**: Le token de votre bot Telegram (obtenu via BotFather).
  * **`TELEGRAM_CHAT_ID`**: L'ID du chat ou du groupe Telegram où le bot enverra les messages. Pour obtenir votre `chat_id`, vous pouvez envoyer un message à votre bot, puis ouvrir `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` dans votre navigateur. Cherchez l'objet `"chat"` et son `"id"`.

### 5\. Préparation du Dossier des Données

Le bot enregistre les annonces déjà vues pour éviter de les retraiter. Créez le dossier `data` :

```bash
mkdir data
```

### 6\. Lancer le Bot

```bash
python main.py
```

Le bot va alors commencer à scraper, analyser et envoyer des notifications si des bonnes affaires sont trouvées.

## ⚙️ Structure du Projet

```
.
├── main.py                     # Point d'entrée principal du bot
├── requirements.txt            # Liste des dépendances Python
├── .env.example                # Exemple de fichier .env
├── README.md                   # Ce fichier
├── ai/
│   └── evaluate.py             # Logique d'intégration avec l'API Mistral AI pour l'évaluation
├── notify/
│   └── telegram_bot.py         # Fonctions pour envoyer des messages via Telegram
├── scraper/
│   └── scrape_2ememain.py      # Logique de scraping pour 2ememain.be
└── data/
    └── annonces_vues.json      # Fichier JSON pour stocker les annonces déjà traitées
```

## 🧠 Comment l'IA évalue les annonces ?

Le fichier `ai/evaluate.py` contient la logique qui construit un **prompt détaillé** pour l'API de chat de Mistral AI. Ce prompt inclut toutes les informations extraites de l'annonce (titre, description, prix, kilométrage, année, etc.).

Mistral AI est ensuite chargée de :

  * Évaluer le **prix** par rapport au marché (selon ses connaissances générales et le prompt).
  * Juger la **clarté et la complétude** de l'annonce.
  * Identifier d'éventuels **risques d'arnaque**.
  * Déterminer l'**intérêt global** de l'affaire.

L'IA renvoie une note numérique (de 1 à 5) et un commentaire concis, qui sont ensuite utilisés par le bot.

## ⚠️ Avertissements et Limitations

  * **Changements du site web (2ememain.be)** : Le scraping est sensible aux modifications de la structure HTML du site cible. Si 2ememain.be met à jour son design, le scraper pourrait nécessiter des ajustements.
  * **Limites d'API Mistral AI** : Des erreurs `429 Too Many Requests` peuvent survenir si vous dépassez les quotas de l'API. Le `time.sleep(2)` est intégré pour mitiger cela, mais si les erreurs persistent, le délai pourrait devoir être augmenté.
  * **Coût de l'API Mistral AI** : L'utilisation de l'API Mistral AI (en particulier des modèles plus grands comme `mistral-large-latest`) engendre des coûts. Surveillez votre consommation sur votre tableau de bord Mistral AI.
  * **Fiabilité de l'IA** : L'évaluation de l'IA est basée sur son entraînement et le prompt fourni. Elle n'est pas infaillible et ne remplace pas une vérification humaine approfondie de l'annonce.

## 🤝 Contribution

Les contributions sont les bienvenues \! Si vous souhaitez améliorer le bot, corriger des bugs ou ajouter de nouvelles fonctionnalités :

1.  Faites un "fork" du dépôt.
2.  Créez une nouvelle branche (`git checkout -b feature/nouvelle-fonctionnalite`).
3.  Effectuez vos modifications et testez-les.
4.  Commitez vos changements (`git commit -m 'feat: ajoute une nouvelle fonctionnalité'`).
5.  Poussez vers votre branche (`git push origin feature/nouvelle-fonctionnalite`).
6.  Ouvrez une "pull request".

-----

## Licence

Ce projet est sous licence MIT.

-----
