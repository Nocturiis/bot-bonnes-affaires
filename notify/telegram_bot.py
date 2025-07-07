import requests
import os

def send_telegram_message(message):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("Le jeton du bot Telegram ou l'ID de chat ne sont pas définis dans les variables d'environnement.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML" # Utiliser HTML pour le gras, les liens, etc.
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Message Telegram envoyé avec succès.")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'envoi du message Telegram : {e}")

if __name__ == '__main__':
    # Exemple d'utilisation
    sample_message = """
    <b>🚘 Nouvelle affaire notée 5/5 !</b>
    <a href="https://example.com/ad-link">VW Golf 7, 2017, 130 000 km – 7 500€</a>
    IA : “Bonne affaire, prix bas pour ce modèle.”
    """
    send_telegram_message(sample_message)