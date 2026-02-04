import os
import requests
from datetime import datetime

RESTO_ID = "602" 
WA_PHONE_ID = os.getenv("WA_PHONE_ID")
WA_TOKEN = os.getenv("WA_TOKEN")
RECIPIENT_PHONE = os.getenv("RECIPIENT_PHONE")





def get_crous_menu():
    url = f"https://api.croustillant.menu/v1/restaurants/{RESTO_ID}/menu"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        today_str = datetime.now().strftime("%Y-%m-%d")
        daily_menu = next((m for m in data if m['date'] == today_str), None)
        if not daily_menu:
            return "⚠️ Pas de menu communiqué pour aujourd'hui."
        header = f"🍽️ *MENU DU JOUR - {daily_menu.get('restaurant_name', 'Resto U')}*"
        sections = []
        for meal in daily_menu.get('meals', []):
            meal_type = meal.get('name', 'Menu')
            items = "\n".join([f"• {item['name']}" for item in meal.get('food_items', [])])
            sections.append(f"*{meal_type}*\n{items}")
        return f"{header}\n\n" + "\n\n".join(sections)
    except Exception as e:
        return f"❌ Erreur Data: Impossible de récupérer le menu ({e})"






def send_whatsapp_alert(message):
    url = f"https://graph.facebook.com/v18.0/{WA_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WA_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT_PHONE,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()





if __name__ == "__main__":
    menu = get_crous_menu()
    status = send_whatsapp_alert(menu)
    print(f"Status: {status}")
