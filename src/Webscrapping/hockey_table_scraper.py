#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hockey Team Statistics Table Scraper
====================================
Minimaler Code zum Scrappen einer HTML-Tabelle mit Hockey-Team-Statistiken
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_hockey_table(url):
    """
    Scrapt Hockey-Team-Statistiken aus einer HTML-Tabelle
    
    Args:
        url (str): URL der Webseite mit der Tabelle
        
    Returns:
        pandas.DataFrame: DataFrame mit den gescrapten Daten
    """
    
    # 1. HTTP-Request zur Webseite senden
    print("📡 Sende Request zur Webseite...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Fehler werfen bei HTTP-Fehlern
    
    # 2. HTML-Content parsen
    print("🔍 Parse HTML-Content...")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 3. Tabelle finden (class="table")
    table = soup.find('table', class_='table')
    if not table:
        raise ValueError("❌ Keine Tabelle mit class='table' gefunden!")
    
    # 4. Header-Zeile extrahieren
    print("📋 Extrahiere Tabellen-Header...")
    headers = []
    header_row = table.find('tr')
    for th in header_row.find_all('th'):
        headers.append(th.get_text().strip())
    
    # 5. Datenzeilen extrahieren (nur Zeilen mit class="team")
    print("📊 Extrahiere Team-Daten...")
    data_rows = []
    
    # Alle Zeilen mit class="team" finden
    team_rows = table.find_all('tr', class_='team')
    
    for row in team_rows:
        # Alle Zellen in der Zeile extrahieren
        cells = row.find_all('td')
        row_data = []
        
        for cell in cells:
            # Text extrahieren und bereinigen
            text = cell.get_text().strip()
            # Leere Zellen als None behandeln
            row_data.append(text if text else None)
        
        data_rows.append(row_data)
    
    # 6. DataFrame erstellen
    print("🐼 Erstelle pandas DataFrame...")
    df = pd.DataFrame(data_rows, columns=headers)
    
    # 7. Datentypen optimieren
    print("🔧 Optimiere Datentypen...")
    
    # Numerische Spalten konvertieren
    numeric_columns = ['Year', 'Wins', 'Losses', 'Goals For (GF)', 'Goals Against (GA)']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Win % und +/- als float
    if 'Win %' in df.columns:
        df['Win %'] = pd.to_numeric(df['Win %'], errors='coerce')
    
    if '+ / -' in df.columns:
        df['+ / -'] = pd.to_numeric(df['+ / -'], errors='coerce')
    
    print(f"✅ Erfolgreich {len(df)} Teams gescrapt!")
    return df

def save_data(df, filename_prefix='hockey_stats'):
    """
    Speichert die Daten in verschiedenen Formaten
    
    Args:
        df (pandas.DataFrame): DataFrame mit den Daten
        filename_prefix (str): Prefix für die Dateinamen
    """
    
    # Als CSV speichern
    csv_file = f"{filename_prefix}.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"💾 Daten gespeichert als: {csv_file}")
    
    # Als Excel speichern (optional)
    try:
        excel_file = f"{filename_prefix}.xlsx"
        df.to_excel(excel_file, index=False)
        print(f"📗 Daten gespeichert als: {excel_file}")
    except ImportError:
        print("⚠️  Excel-Export nicht verfügbar (openpyxl nicht installiert)")

def main():
    """
    Hauptfunktion - Beispiel für die Verwendung
    """
    
    # URL der Webseite (hier müssen Sie die echte URL einsetzen)
    url = "https://example.com/hockey-stats"  # ⚠️ ECHTE URL EINSETZEN!
    
    try:
        # Tabelle scrappen
        df = scrape_hockey_table(url)
        
        # Erste 5 Zeilen anzeigen
        print("\n📈 Erste 5 Datensätze:")
        print(df.head())
        
        # Grundlegende Statistiken
        print(f"\n📊 Datensatz-Info:")
        print(f"   - Anzahl Teams: {len(df)}")
        print(f"   - Spalten: {list(df.columns)}")
        print(f"   - Jahre: {df['Year'].min()} - {df['Year'].max()}")
        
        # Daten speichern
        save_data(df)
        
    except Exception as e:
        print(f"❌ Fehler beim Scrapping: {e}")

# Alternative: Direktes Scrappen von HTML-String (für Testing)
def scrape_from_html_string(html_content):
    """
    Scrapt direkt aus einem HTML-String (für Tests)
    
    Args:
        html_content (str): HTML-String mit der Tabelle
        
    Returns:
        pandas.DataFrame: DataFrame mit den Daten
    """
    
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', class_='table')
    
    # Header extrahieren
    headers = []
    header_row = table.find('tr')
    for th in header_row.find_all('th'):
        headers.append(th.get_text().strip())
    
    # Daten extrahieren
    data_rows = []
    team_rows = table.find_all('tr', class_='team')
    
    for row in team_rows:
        cells = row.find_all('td')
        row_data = [cell.get_text().strip() or None for cell in cells]
        data_rows.append(row_data)
    
    return pd.DataFrame(data_rows, columns=headers)

if __name__ == "__main__":
    main()