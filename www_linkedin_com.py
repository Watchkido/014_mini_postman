"""
o_linkedin.py
nutzt .env und env_config.py
zugriff auf linkedin api
🔄 Python lädt die env_config.py
🔍 Sie sucht nach einer .env Datei
📥 Sie lädt alle Umgebungsvariablen
⚙️ Alle Config-Klassen werden initialisiert

Wichtige Hinweise für API-Aufrufe
Versionierung: 
Viele APIs erfordern die Angabe einer Versionszeichenkette (z.B. "202212"). 
Ohne diese schlagen manche Anfragen fehl .
Pfadkeys: 
Wenn deine Resource Path Keys enthält (z.B. /adAccounts/{id}), 
musst du diese im path_keys-Parameter als Dictionary angeben .
Header: 
Für manche Endpunkte, wie den Profile API, muss der Header 
X-RestLi-Protocol-Version:2.0.0 gesetzt werden . 
Die Python-Bibliothek übernimmt dies in der Regel automatisch.
Datenformate: 
LinkedIn erwartet standardmäßig JSON. Die Python-Bibliothek sendet Anfragen 
automatisch im korrekten JSON-Format .
"""
from env_config import APIConfig, DatabaseConfig

# Die Klasse lädt automatisch aus .env
api_key = APIConfig.LIBRETRANSLATE_API_KEY  # "abc123xyz789_ihr_echter_key"
db_pass = DatabaseConfig.PASSWORD  


# grundlegender api abruf

from linkedin_api.clients.restli.client import RestliClient

restli_client = RestliClient()

try:
    response = restli_client.get(
        resource_path="/me",  # Endpunkt für das eigene Profil
        access_token="DEIN_ACCESS_TOKEN"  # Hier deinen Token einfügen
    )
    print("Profil abgerufen:")
    print(response.entity)
except Exception as e:
    print(f"Fehler beim Abrufen des Profils: {e}")



# 2. Erweiterte Suche mit dem FINDER-Endpunkt
try:
    response = restli_client.finder(
        resource_path="/adAccounts",
        finder_name="search",  # Name des "Finders"
        query_params={
            "search": {
                "status": {
                    "values": ["ACTIVE", "DRAFT"]
                },
                "test": False
            }
        },
        access_token="DEIN_ACCESS_TOKEN",
        version_string="202212"  # API-Version im Format JJJJMM
    )
    print("Gefundene Werbekonten:")
    for account in response.elements:
        print(account)
except Exception as e:
    print(f"Fehler bei der Suche: {e}")




# automatische aktualisierung des tokens alle 60 tage




"""
Beiträge veröffentlichen: Du kannst Textbeiträge, Bilder und Artikel auf deiner 
persönlichen Profilseite posten. Dafür benötigst du die Berechtigung w_member_social.

"Sign In with LinkedIn" nutzen: Du kannst die Anmeldung über LinkedIn in deinen
 eigenen Apps integrieren, um grundlegende Profilinformationen 
 (Name, Überschrift, Profilbild) und die E-Mail-Adresse eines Nutzers abzurufen. 
 Dies geschieht über die Berechtigungen openid, profile und email.
"""




# beitrag posten

import requests
import os

# Verwende deine Konfigurationsklasse aus der env_config.py
from env_config import APIConfig

def post_to_linkedin(commentary_text):
    """
    Veröffentlicht einen Textbeitrag auf LinkedIn.
    """
    access_token = APIConfig.LINKEDIN_ACCESS_TOKEN  # Dein Access Token
    author_urn = APIConfig.LINKEDIN_AUTHOR_URN      # z.B. "urn:li:person:123456"
    
    api_url = "https://api.linkedin.com/v2/ugcPosts"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    post_data = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": commentary_text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    response = requests.post(api_url, headers=headers, json=post_data)
    
    if response.status_code == 201:
        print("✅ Beitrag erfolgreich veröffentlicht!")
        return response.json()
    else:
        print(f"❌ Fehler beim Posten: {response.status_code} - {response.text}")
        return None

# Beispielaufruf
if __name__ == "__main__":
    mein_post_text = "Hallo LinkedIn! Dies ist mein erster Beitrag, der mit der Python-API automatisiert wurde. #Python #Automation"
    post_to_linkedin(mein_post_text)