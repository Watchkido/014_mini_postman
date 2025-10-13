#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrapping.py - Web Scraping Utilities
=====================================
Verschiedene Web Scraping Funktionen
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_hockey_table(url_or_html):
    """
    🏒 Minimal kommentierter Hockey-Tabellen-Scraper
    
    Scrapt eine HTML-Tabelle mit Hockey-Team-Statistiken
    
    Args:
        url_or_html (str): URL der Webseite oder HTML-String
        
    Returns:
        pandas.DataFrame: Gescrapte Team-Daten
    """
    
    # 1. Content laden (URL oder HTML-String)
    if url_or_html.startswith('http'):
        # Von URL laden
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url_or_html, headers=headers)
        html_content = response.content
    else:
        # Direkter HTML-String
        html_content = url_or_html
    
    # 2. HTML parsen und Tabelle finden
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', class_='table')
    
    if not table:
        raise ValueError("❌ Keine Tabelle mit class='table' gefunden!")
    
    # 3. Header extrahieren (erste Zeile mit <th>)
    headers = [th.get_text().strip() for th in table.find('tr').find_all('th')]
    
    # 4. Team-Daten extrahieren (Zeilen mit class="team")
    data_rows = []
    for row in table.find_all('tr', class_='team'):
        # Alle <td> Zellen extrahieren
        row_data = [td.get_text().strip() or None for td in row.find_all('td')]
        data_rows.append(row_data)
    
    # 5. DataFrame erstellen
    df = pd.DataFrame(data_rows, columns=headers)
    
    # 6. Numerische Spalten konvertieren
    numeric_cols = ['Year', 'Wins', 'Losses', 'Goals For (GF)', 'Goals Against (GA)', 'Win %', '+ / -']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print(f"✅ {len(df)} Teams erfolgreich gescrapt!")
    return df

def scrape_all_hockey_pages(base_url="https://www.scrapethissite.com/pages/forms/", max_pages=24, delay=1.5):
    """
    🏒 Scrapt alle Seiten der Hockey-Statistiken
    
    Args:
        base_url (str): Basis-URL der Seite
        max_pages (int): Maximale Anzahl Seiten (Standard: 24)
        delay (float): Verzögerung zwischen Requests in Sekunden
        
    Returns:
        pandas.DataFrame: Alle gescrapten Team-Daten
    """
    
    import time
    
    print(f"🚀 Scrape {max_pages} Seiten Hockey-Daten...")
    all_data = []
    
    for page in range(1, max_pages + 1):
        url = f"{base_url}?page_num={page}"
        print(f"📡 Seite {page}/24: {url}")
        
        try:
            # Request senden
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # HTML parsen
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', class_='table')
            
            if table:
                # Header (nur bei Seite 1)
                if page == 1:
                    headers_list = [th.get_text().strip() for th in table.find('tr').find_all('th')]
                
                # Team-Daten extrahieren
                team_rows = table.find_all('tr', class_='team')
                
                for row in team_rows:
                    row_data = [td.get_text().strip() or None for td in row.find_all('td')]
                    if len(row_data) == len(headers_list):
                        all_data.append(row_data)
                
                print(f"   ✅ {len(team_rows)} Teams von Seite {page}")
            else:
                print(f"   ⚠️  Keine Tabelle auf Seite {page}")
            
            # Höfliche Verzögerung
            if page < max_pages:
                time.sleep(delay)
                
        except Exception as e:
            print(f"   ❌ Fehler auf Seite {page}: {e}")
    
    # DataFrame erstellen
    if all_data:
        df = pd.DataFrame(all_data, columns=headers_list)
        
        # Datentypen optimieren
        numeric_cols = ['Year', 'Wins', 'Losses', 'Goals For (GF)', 'Goals Against (GA)', '+ / -']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        if 'Win %' in df.columns:
            df['Win %'] = pd.to_numeric(df['Win %'], errors='coerce')
        
        print(f"✅ Gesamt: {len(df)} Teams von {max_pages} Seiten gescrapt!")
        return df
    else:
        print("❌ Keine Daten gefunden!")
        return pd.DataFrame()

# Beispiel-Verwendung:
if __name__ == "__main__":
    # Multi-Page Scraping
    df_all = scrape_all_hockey_pages()
    
    if not df_all.empty:
        # Statistiken anzeigen
        print(f"\n📊 ERGEBNISSE:")
        print(f"Teams gesamt: {len(df_all)}")
        print(f"Jahre: {df_all['Year'].min()} - {df_all['Year'].max()}")
        print(f"Verschiedene Teams: {df_all['Team Name'].nunique()}")
        
        # Speichern
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hockey_all_pages_{timestamp}.csv"
        df_all.to_csv(filename, index=False)
        print(f"💾 Gespeichert als: {filename}")
        
        # Top 5 Teams
        print(f"\n🏆 TOP 5 TEAMS (meiste Siege):")
        top5 = df_all.nlargest(5, 'Wins')[['Team Name', 'Year', 'Wins', 'Losses']]
        print(top5.to_string(index=False))