"""
✅ Testet die API-Verbindung
✅ Ermittelt automatisch deine Profil-URN
✅ Postet einen Test-Beitrag auf deinem Profil
✅ Verwendet die aktuelle LinkedIn Posts API
✅ Enthält vollständige Fehlerbehandlun

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

Postman kann den Prozess erheblich vereinfachen:

Automatisierung: In den Collection-Authorization-Einstellungen kannst du "OAuth 2.0" auswählen.
Konfiguration: Fülle die Felder mit diesen Werten:
Grant Type: Authorization Code
Callback URL: https://oauth.pstmn.io/v1/browser-callback
Auth URL: https://www.linkedin.com/oauth/v2/authorization
Access Token URL: https://www.linkedin.com/oauth/v2/accessToken
Client ID & Secret: Deine Anmeldedaten
Scope: Die gewünschten Berechtigungen (z. B. r_liteprofile r_emailaddress)
Client Authentication: Send as Basic Auth Header oder Send client credentials in body
Postman leitet dich dann durch die Anmeldung bei LinkedIn an und verwaltet den Token für dich.

"""
from env_config import APIConfig, DatabaseConfig

# Die Klasse lädt automatisch aus .env
api_key = APIConfig.LIBRETRANSLATE_API_KEY  # "abc123xyz789_ihr_echter_key"
db_pass = DatabaseConfig.PASSWORD  

import requests
from linkedin_api.clients.restli.client import RestliClient
from env_config import APIConfig, EnvConfig
import json

def setup_linkedin_client():
    """Initialisiert den LinkedIn Client mit dem Access Token"""
    access_token = APIConfig.LINKEDIN_ACCESS_TOKEN
    
    if not access_token or access_token == "DEIN_ACCESS_TOKEN":
        print("❌ Bitte setze deinen Access Token in der .env Datei")
        print(f"🔑 Dein Token: {access_token}")
        return None, None
    
    restli_client = RestliClient()
    return restli_client, access_token

def get_user_profile(restli_client, access_token):
    """Ermittelt das eigene Profil und die URN über userinfo"""
    try:
        print("📝 Rufe Profilinformationen ab...")
        # Rufe die userinfo auf
        response = restli_client.get(
            resource_path="/userinfo",  # Geänderter Endpunkt
            access_token=access_token
        )
        profile_data = response.entity
        
        # Die Profil-ID wird aus dem 'sub'-Feld der Antwort entnommen
        profile_id = profile_data['sub']  # 'sub' steht für Subject Identifier
        author_urn = f"urn:li:person:{profile_id}"
        
        print(f"✅ Profil-URN ermittelt: {author_urn}")
        # Anzeige des Namens (falls in der Antwort vorhanden)
        print(f"👤 Name: {profile_data.get('name', 'N/A')}")
        return author_urn
    except Exception as e:
        print(f"❌ Fehler beim Profil-Abruf: {e}")
        return None

def post_to_linkedin(commentary_text, access_token, author_urn):
    """Veröffentlicht einen Textbeitrag auf LinkedIn mit der neuen Posts API"""
    api_url = "https://api.linkedin.com/rest/posts"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": EnvConfig.get("LINKEDIN_API_VERSION", "202509"),  # Unterstützte Version angepasst
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    post_data = {
        "author": author_urn,
        "commentary": commentary_text,
        "visibility": "PUBLIC",
        "lifecycleState": "PUBLISHED",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        }
    }
    
    print("📤 Poste Beitrag auf LinkedIn...")
    response = requests.post(api_url, headers=headers, json=post_data)
    
    if response.status_code == 201:
        post_id = response.headers.get('x-restli-id')
        print("✅ Beitrag erfolgreich veröffentlicht!")
        print(f"📎 Post-ID: {post_id}")
        return post_id
    else:
        print(f"❌ Fehler beim Posten: {response.status_code}")
        print(f"🔍 Fehlerdetails: {response.text}")
        return None

def test_api_connection(restli_client, access_token):
    """Testet die API-Verbindung mit dem userinfo Endpunkt"""
    try:
        print("🔗 Teste API-Verbindung...")
        # Verwende /userinfo anstelle von /me
        response = restli_client.get(
            resource_path="/userinfo",  # Geänderter Endpunkt
            access_token=access_token
        )
        print("✅ API-Verbindung erfolgreich!")
        return True
    except Exception as e:
        print(f"❌ API-Verbindungsfehler: {e}")
        return False


def main():
    """Hauptfunktion - Führt den kompletten LinkedIn Flow aus"""
    print("🚀 Starte LinkedIn API Integration...")
    
    # 1. Client initialisieren
    restli_client, access_token = setup_linkedin_client()
    if not restli_client:
        return
    
    # 2. API-Verbindung testen
    if not test_api_connection(restli_client, access_token):
        return
    
    # 3. Profil-URN ermitteln
    author_urn = get_user_profile(restli_client, access_token)
    if not author_urn:
        return
    
    # 4. Beitrag posten
    test_text = (
        "Hallo LinkedIn-Community! 👋\n\n"
        "Dies ist mein erster Beitrag, der vollständig über die LinkedIn API mit Python automatisiert wurde. "
        "Frank Albrecht - Data Analyst am 10.02.26 - Right data. Smart use. More money. BAM!! 💻\n\n"
        "#Python #Automation #Datenanalyst #Neustadt #API #LinkedInAPI #DigitalMarketing"
    )
    
    post_to_linkedin(test_text, access_token, author_urn)

if __name__ == "__main__":
    main()