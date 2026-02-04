import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import warnings
import re

warnings.filterwarnings("ignore")

WA_PHONE_ID = os.getenv("WA_PHONE_ID")
WA_TOKEN = os.getenv("WA_TOKEN")
RECIPIENT_PHONE = os.getenv("RECIPIENT_PHONE")

if not all([WA_PHONE_ID, WA_TOKEN, RECIPIENT_PHONE]):
    raise ValueError("Erreur : Variables d'environnement manquantes !")

def get_menu_final():
    url = "https://www.crous-bfc.fr/restaurant/resto-u-montmuzard/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(separator="\n", strip=True)
        
        jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        now = datetime.now()
        day_name = jours[now.weekday()]
        day_num = now.day
        
        day_pattern = rf"{day_name}\s+{day_num}"
        next_day_num = day_num + 1
        next_day_name = jours[(now.weekday() + 1) % 7]
        next_day_pattern = rf"{next_day_name}\s+{next_day_num}"
        
        regex = rf"{day_pattern}.*?(?={next_day_pattern}|$)"
        match = re.search(regex, page_text, re.DOTALL | re.IGNORECASE)
        
        if not match:
            return f"⚠️ Menu du {day_name} {day_num} introuvable."
            
        day_content = match.group(0)
        current_hour = now.hour
        parts = re.split(r"(Dîner)", day_content, flags=re.IGNORECASE)
        dejeuner_text = parts[0]
        diner_text = parts[1] + parts[2] if len(parts) > 2 else ""
        
        if current_hour < 14:
            target_text = dejeuner_text
            header = "🌞 *DÉJEUNER - MONTMUZARD*"
        else:
            target_text = diner_text
            header = "🌙 *DÎNER - MONTMUZARD*"

        raw_lines = target_text.split('\n')
        formatted_menu = [f"🍽️ {header} - {now.strftime('%d/%m')}"]
        
        for line in raw_lines:
            l = line.strip()
            if not l or len(l) < 3 or "Menu du" in l or day_pattern in l.lower(): continue
            if "Déjeuner" in l or "Dîner" in l: continue
            elif "Plats" in l or "étage" in l: formatted_menu.append(f"\n📍 _{l}_")
            elif "garnitures" in l.lower(): formatted_menu.append("🥗 _Garnitures :_")
            elif "MENU CONSEIL" in l: continue
            else:
                formatted_menu.append(f"• {l}")

        return "\n".join(formatted_menu)
    except Exception as e:
        return f"❌ Erreur : {str(e)}"

def send_whatsapp(message):
    url = f"https://graph.facebook.com/v18.0/{WA_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WA_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT_PHONE,
        "type": "text",
        "text": {"body": message}
    }
    return requests.post(url, headers=headers, json=payload).json()

if __name__ == "__main__":
    content = get_menu_final()
    print(send_whatsapp(content))
