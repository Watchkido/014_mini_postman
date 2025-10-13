#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Test: Multi-Page Hockey Scraper
====================================
Testet das Multi-Page Scraping mit nur 3 Seiten
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def quick_test_multipage():
    """
    Schneller Test mit nur 3 Seiten
    """
    
    print("🧪 QUICK TEST: Multi-Page Scraping (erste 3 Seiten)")
    print("="*60)
    
    base_url = "https://www.scrapethissite.com/pages/forms/"
    all_data = []
    headers_list = []
    
    for page in range(1, 4):  # Nur erste 3 Seiten
        url = f"{base_url}?page_num={page}"
        print(f"📡 Scrape Seite {page}: {url}")
        
        try:
            # Request
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', class_='table')
            
            if table:
                # Header nur bei Seite 1
                if page == 1:
                    headers_list = [th.get_text().strip() for th in table.find('tr').find_all('th')]
                    print(f"   📋 Header: {headers_list}")
                
                # Teams scrapen
                team_rows = table.find_all('tr', class_='team')
                page_data = []
                
                for row in team_rows:
                    row_data = [td.get_text().strip() or None for td in row.find_all('td')]
                    if len(row_data) == len(headers_list):
                        all_data.append(row_data)
                        page_data.append(row_data)
                
                print(f"   ✅ {len(page_data)} Teams gefunden")
                
                # Beispiel-Team von dieser Seite
                if page_data:
                    example_team = page_data[0]
                    print(f"   🏒 Beispiel: {example_team[0]} ({example_team[1]}) - {example_team[2]} Siege")
            
            # Kurze Pause
            if page < 3:
                time.sleep(1)
                
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
    
    # DataFrame erstellen
    if all_data and headers_list:
        df = pd.DataFrame(all_data, columns=headers_list)
        
        # Datentypen optimieren
        numeric_cols = ['Year', 'Wins', 'Losses']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print(f"\n📊 ERGEBNISSE:")
        print(f"   Total Teams: {len(df)}")
        print(f"   Spalten: {list(df.columns)}")
        
        # Top 3 anzeigen
        print(f"\n🏆 TOP 3 TEAMS (aus den ersten 3 Seiten):")
        if 'Wins' in df.columns:
            top3 = df.nlargest(3, 'Wins')[['Team Name', 'Year', 'Wins', 'Losses']]
            print(top3.to_string(index=False))
        
        # Erste 5 Datensätze
        print(f"\n📋 ERSTE 5 DATENSÄTZE:")
        print(df.head().to_string(index=False))
        
        # Speichern
        df.to_csv('hockey_quick_test.csv', index=False)
        print(f"\n💾 Daten gespeichert als: hockey_quick_test.csv")
        
        return df
    else:
        print("❌ Keine Daten gesammelt!")
        return pd.DataFrame()

if __name__ == "__main__":
    quick_test_multipage()