"""
JSONPlaceholder User Data Fetcher
==================================
Kleines Programm zum Abrufen und Anzeigen von Benutzerdaten
von der JSONPlaceholder API in einer schönen, übersichtlichen Form.

Autor: Frank Albrecht
Datum: 2025-10-07
"""

import requests
import pandas as pd
import json
import sys
from datetime import datetime
from env_config import APIConfig

def check_unicode_support():
    """Prüft, ob die Konsole Unicode-Zeichen unterstützt"""
    try:
        sys.stdout.write("✓")
        sys.stdout.flush()
        return True
    except UnicodeEncodeError:
        return False

def get_icon(success=True, unicode_support=True):
    """Gibt das passende Icon zurück - Unicode oder ASCII"""
    if unicode_support:
        return "✅" if success else "❌"
    else:
        return "OK" if success else "FEHLER"

def print_separator(unicode_support=True, length=80):
    """Druckt eine schöne Trennlinie"""
    if unicode_support:
        print("═" * length)
    else:
        print("=" * length)

def format_user_data(user, unicode_support=True):
    """Formatiert Benutzerdaten in einer schönen, lesbaren Form"""
    
    # Header für den Benutzer
    print_separator(unicode_support)
    if unicode_support:
        print(f"👤 BENUTZER #{user['id']}: {user['name']}")
    else:
        print(f"BENUTZER #{user['id']}: {user['name']}")
    print_separator(unicode_support)
    
    # Grunddaten
    print(f"📋 Username    : {user['username']}")
    print(f"📧 E-Mail      : {user['email']}")
    print(f"📞 Telefon     : {user['phone']}")
    print(f"🌐 Website     : {user['website']}")
    print()
    
    # Adresse
    address = user['address']
    print("🏠 ADRESSE:")
    print(f"   Straße     : {address['street']} {address['suite']}")
    print(f"   Stadt      : {address['city']}")
    print(f"   PLZ        : {address['zipcode']}")
    print(f"   Koordinaten: {address['geo']['lat']}, {address['geo']['lng']}")
    print()
    
    # Firma
    company = user['company']
    print("🏢 FIRMA:")
    print(f"   Name       : {company['name']}")
    print(f"   Slogan     : {company['catchPhrase']}")
    print(f"   Geschäft   : {company['bs']}")
    print()

def fetch_users():
    """Holt alle Benutzer von der JSONPlaceholder API"""
    url = "https://jsonplaceholder.typicode.com/users"
    
    try:
        print(f"🔍 Lade Benutzerdaten von: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        users = response.json()
        print(f"✅ Erfolgreich {len(users)} Benutzer geladen!")
        print()
        
        return users
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Fehler beim Laden der Daten: {e}")
        return None

def create_users_dataframe(users):
    """Erstellt ein pandas DataFrame mit den wichtigsten Benutzerdaten"""
    
    data = []
    for user in users:
        data.append({
            'ID': user['id'],
            'Name': user['name'],
            'Username': user['username'],
            'Email': user['email'],
            'Stadt': user['address']['city'],
            'Firma': user['company']['name'],
            'Website': user['website']
        })
    
    return pd.DataFrame(data)

def main():
    """Hauptfunktion des Programms"""
    
    # Unicode-Unterstützung prüfen
    unicode_support = check_unicode_support()
    
    # Programmstart
    print_separator(unicode_support, 60)
    if unicode_support:
        print("🌐 JSONPlaceholder User Data Viewer")
    else:
        print("JSONPlaceholder User Data Viewer")
    print(f"Zeitstempel: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator(unicode_support, 60)
    print()
    
    # Benutzer laden
    users = fetch_users()
    if not users:
        print("❌ Programm beendet - keine Daten erhalten.")
        return
    
    # Menü anzeigen
    while True:
        print("📋 OPTIONEN:")
        print("1. Alle Benutzer in Tabellenform anzeigen")
        print("2. Einzelnen Benutzer detailliert anzeigen")
        print("3. Alle Benutzer detailliert anzeigen")
        print("4. JSON-Rohdaten anzeigen")
        print("5. Beenden")
        print()
        
        choice = input("Wählen Sie eine Option (1-5): ").strip()
        print()
        
        if choice == "1":
            # Tabelle anzeigen
            df = create_users_dataframe(users)
            print("📊 BENUTZER-ÜBERSICHT:")
            print(df.to_string(index=False))
            print()
            
        elif choice == "2":
            # Einzelnen Benutzer anzeigen
            print("Verfügbare Benutzer:")
            for user in users:
                print(f"  {user['id']}: {user['name']}")
            print()
            
            try:
                user_id = int(input("Benutzer-ID eingeben: "))
                user = next((u for u in users if u['id'] == user_id), None)
                
                if user:
                    format_user_data(user, unicode_support)
                else:
                    print("❌ Benutzer nicht gefunden!")
                    
            except ValueError:
                print("❌ Ungültige ID!")
            print()
            
        elif choice == "3":
            # Alle Benutzer detailliert
            for user in users:
                format_user_data(user, unicode_support)
            
        elif choice == "4":
            # JSON-Rohdaten
            print("📄 JSON-ROHDATEN:")
            print(json.dumps(users, indent=2, ensure_ascii=False))
            print()
            
        elif choice == "5":
            print("👋 Programm beendet. Auf Wiedersehen!")
            break
            
        else:
            print("❌ Ungültige Auswahl!")
            print()

if __name__ == "__main__":
    main()
