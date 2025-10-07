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

# API URLs
url = "https://jsonplaceholder.typicode.com/users"
url_post = "https://jsonplaceholder.typicode.com/posts"

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

def fetch_posts():
    """Holt alle Posts von der JSONPlaceholder API"""
    try:
        print(f"🔍 Lade Posts von: {url_post}")
        response = requests.get(url_post, timeout=10)
        response.raise_for_status()
        
        posts = response.json()
        print(f"✅ Erfolgreich {len(posts)} Posts geladen!")
        print()
        
        return posts
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Fehler beim Laden der Posts: {e}")
        return None

def format_post_data(post, unicode_support=True):
    """Formatiert Post-Daten in einer schönen, lesbaren Form"""
    
    # Header für den Post
    print_separator(unicode_support)
    if unicode_support:
        print(f"📝 POST #{post['id']}: {post['title'][:50]}{'...' if len(post['title']) > 50 else ''}")
    else:
        print(f"POST #{post['id']}: {post['title'][:50]}{'...' if len(post['title']) > 50 else ''}")
    print_separator(unicode_support)
    
    # Post-Daten
    print(f"👤 Benutzer-ID : {post['userId']}")
    print(f"📋 Titel      : {post['title']}")
    print(f"📄 Inhalt     : {post['body']}")
    print()

def create_post():
    """Erstellt einen neuen Post über die JSONPlaceholder API"""
    
    print("📝 NEUEN POST ERSTELLEN:")
    print_separator(True, 40)
    
    # Eingaben vom Benutzer
    try:
        user_id = int(input("👤 Benutzer-ID (1-10): "))
        if user_id < 1 or user_id > 10:
            print("❌ Benutzer-ID muss zwischen 1 und 10 liegen!")
            return None
            
        title = input("📋 Titel des Posts: ").strip()
        if not title:
            print("❌ Titel darf nicht leer sein!")
            return None
            
        body = input("📄 Inhalt des Posts: ").strip()
        if not body:
            print("❌ Inhalt darf nicht leer sein!")
            return None
            
    except ValueError:
        print("❌ Ungültige Benutzer-ID!")
        return None
    
    # Post-Daten vorbereiten
    post_data = {
        'title': title,
        'body': body,
        'userId': user_id
    }
    
    try:
        print(f"\n🚀 Sende POST-Request an: {url_post}")
        response = requests.post(url_post, json=post_data, timeout=10)
        response.raise_for_status()
        
        created_post = response.json()
        
        print("✅ Post erfolgreich erstellt!")
        print_separator(True)
        print(f"📝 POST ID: {created_post['id']}")
        print(f"👤 Benutzer-ID: {created_post['userId']}")
        print(f"📋 Titel: {created_post['title']}")
        print(f"📄 Inhalt: {created_post['body']}")
        print_separator(True)
        
        return created_post
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Fehler beim Erstellen des Posts: {e}")
        return None

def create_posts_dataframe(posts):
    """Erstellt ein pandas DataFrame mit den wichtigsten Post-Daten"""
    
    data = []
    for post in posts:
        # Kürze Titel und Inhalt für bessere Darstellung
        title_short = post['title'][:30] + '...' if len(post['title']) > 30 else post['title']
        body_short = post['body'][:40] + '...' if len(post['body']) > 40 else post['body']
        
        data.append({
            'ID': post['id'],
            'Benutzer-ID': post['userId'],
            'Titel': title_short,
            'Inhalt': body_short
        })
    
    return pd.DataFrame(data)

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
        print("📋 HAUPTMENÜ:")
        print("=" * 50)
        print("👤 BENUTZER:")
        print("1. Alle Benutzer in Tabellenform anzeigen")
        print("2. Einzelnen Benutzer detailliert anzeigen")
        print("3. Alle Benutzer detailliert anzeigen")
        print()
        print("📝 POSTS:")
        print("4. Alle Posts in Tabellenform anzeigen")
        print("5. Einzelnen Post detailliert anzeigen")
        print("6. Alle Posts detailliert anzeigen")
        print("7. Neuen Post erstellen")
        print()
        print("📄 DATEN:")
        print("8. JSON-Rohdaten (Benutzer) anzeigen")
        print("9. JSON-Rohdaten (Posts) anzeigen")
        print()
        print("0. Beenden")
        print("=" * 50)
        
        choice = input("Wählen Sie eine Option (0-9): ").strip()
        print()
        
        if choice == "1":
            # Benutzer-Tabelle anzeigen
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
            # Posts-Tabelle anzeigen
            posts = fetch_posts()
            if posts:
                df = create_posts_dataframe(posts)
                print("📊 POSTS-ÜBERSICHT:")
                print(df.to_string(index=False))
                print()
            
        elif choice == "5":
            # Einzelnen Post anzeigen
            posts = fetch_posts()
            if posts:
                print("Verfügbare Posts (erste 10):")
                for post in posts[:10]:
                    print(f"  {post['id']}: {post['title'][:40]}{'...' if len(post['title']) > 40 else ''}")
                print()
                
                try:
                    post_id = int(input("Post-ID eingeben: "))
                    post = next((p for p in posts if p['id'] == post_id), None)
                    
                    if post:
                        format_post_data(post, unicode_support)
                    else:
                        print("❌ Post nicht gefunden!")
                        
                except ValueError:
                    print("❌ Ungültige ID!")
                print()
            
        elif choice == "6":
            # Alle Posts detailliert (erste 10)
            posts = fetch_posts()
            if posts:
                print("📝 Zeige die ersten 10 Posts:")
                for post in posts[:10]:
                    format_post_data(post, unicode_support)
            
        elif choice == "7":
            # Neuen Post erstellen
            created_post = create_post()
            if created_post:
                print("✨ Der erstellte Post:")
                format_post_data(created_post, unicode_support)
            
        elif choice == "8":
            # JSON-Rohdaten Benutzer
            print("📄 JSON-ROHDATEN (BENUTZER):")
            print(json.dumps(users, indent=2, ensure_ascii=False))
            print()
            
        elif choice == "9":
            # JSON-Rohdaten Posts
            posts = fetch_posts()
            if posts:
                print("📄 JSON-ROHDATEN (POSTS - erste 5):")
                print(json.dumps(posts[:5], indent=2, ensure_ascii=False))
                print()
            
        elif choice == "0":
            print("👋 Programm beendet. Auf Wiedersehen!")
            break
            
        else:
            print("❌ Ungültige Auswahl!")
            print()

if __name__ == "__main__":
    main()
