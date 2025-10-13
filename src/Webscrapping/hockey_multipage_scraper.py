#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Page Hockey Statistics Scraper
====================================
Scrapt alle 24 Seiten der Hockey-Statistiken von scrapethissite.com
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from datetime import datetime

def scrape_single_page(page_num):
    """
    Scrapt eine einzelne Seite der Hockey-Statistiken
    
    Args:
        page_num (int): Seitennummer (1-24)
        
    Returns:
        pandas.DataFrame: DataFrame mit den Team-Daten dieser Seite
    """
    
    # URL für die spezifische Seite
    url = f"https://www.scrapethissite.com/pages/forms/?page_num={page_num}"
    
    print(f"📡 Scrape Seite {page_num}: {url}")
    
    # Request mit User-Agent Header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # HTML parsen
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tabelle finden
        table = soup.find('table', class_='table')
        if not table:
            print(f"⚠️  Keine Tabelle auf Seite {page_num} gefunden!")
            return pd.DataFrame()
        
        # Header extrahieren (nur bei der ersten Seite)
        headers_list = []
        header_row = table.find('tr')
        if header_row:
            for th in header_row.find_all('th'):
                headers_list.append(th.get_text().strip())
        
        # Team-Daten extrahieren
        data_rows = []
        team_rows = table.find_all('tr', class_='team')
        
        print(f"   🏒 {len(team_rows)} Teams gefunden")
        
        for row in team_rows:
            cells = row.find_all('td')
            if len(cells) >= len(headers_list):  # Sicherheitscheck
                row_data = []
                for cell in cells:
                    text = cell.get_text().strip()
                    row_data.append(text if text else None)
                data_rows.append(row_data)
        
        # DataFrame erstellen
        if data_rows and headers_list:
            df = pd.DataFrame(data_rows, columns=headers_list)
            return df
        else:
            return pd.DataFrame()
            
    except requests.RequestException as e:
        print(f"❌ Fehler beim Laden von Seite {page_num}: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Unerwarteter Fehler auf Seite {page_num}: {e}")
        return pd.DataFrame()

def scrape_all_pages(max_pages=24, delay=1.0):
    """
    Scrapt alle Seiten der Hockey-Statistiken
    
    Args:
        max_pages (int): Maximale Anzahl der Seiten (Standard: 24)
        delay (float): Verzögerung zwischen Requests in Sekunden
        
    Returns:
        pandas.DataFrame: Kombinierter DataFrame mit allen Daten
    """
    
    print(f"🚀 Starte Multi-Page Scraping (1-{max_pages} Seiten)")
    print(f"⏱️  Verzögerung zwischen Requests: {delay}s")
    
    all_dataframes = []
    successful_pages = 0
    failed_pages = []
    
    for page_num in range(1, max_pages + 1):
        # Einzelne Seite scrapen
        df = scrape_single_page(page_num)
        
        if not df.empty:
            all_dataframes.append(df)
            successful_pages += 1
            print(f"   ✅ Seite {page_num}: {len(df)} Teams gesammelt")
        else:
            failed_pages.append(page_num)
            print(f"   ❌ Seite {page_num}: Keine Daten")
        
        # Verzögerung zwischen Requests (höflich gegenüber dem Server)
        if page_num < max_pages:
            time.sleep(delay)
    
    # Alle DataFrames kombinieren
    if all_dataframes:
        print(f"\n📊 Kombiniere Daten von {successful_pages} Seiten...")
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Datentypen optimieren
        combined_df = optimize_datatypes(combined_df)
        
        print(f"✅ Erfolgreich {len(combined_df)} Teams von {successful_pages} Seiten gescrapt!")
        
        if failed_pages:
            print(f"⚠️  Fehlgeschlagene Seiten: {failed_pages}")
        
        return combined_df
    else:
        print("❌ Keine Daten gesammelt!")
        return pd.DataFrame()

def optimize_datatypes(df):
    """
    Optimiert die Datentypen des DataFrames
    
    Args:
        df (pandas.DataFrame): Original DataFrame
        
    Returns:
        pandas.DataFrame: Optimierter DataFrame
    """
    
    print("🔧 Optimiere Datentypen...")
    
    # Numerische Spalten definieren
    numeric_columns = {
        'Year': 'int',
        'Wins': 'int',
        'Losses': 'int',
        'OT Losses': 'int',
        'Goals For (GF)': 'int',
        'Goals Against (GA)': 'int',
        '+ / -': 'int'
    }
    
    float_columns = ['Win %']
    
    # Numerische Spalten konvertieren
    for col, dtype in numeric_columns.items():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if dtype == 'int':
                df[col] = df[col].fillna(0).astype('int32')
    
    # Float-Spalten konvertieren
    for col in float_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def save_results(df, base_filename='hockey_all_pages'):
    """
    Speichert die Ergebnisse in verschiedenen Formaten
    
    Args:
        df (pandas.DataFrame): DataFrame mit allen Daten
        base_filename (str): Basis-Dateiname
    """
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # CSV speichern
    csv_file = f"{base_filename}_{timestamp}.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"💾 Daten gespeichert als: {csv_file}")
    
    # Excel speichern (optional)
    try:
        excel_file = f"{base_filename}_{timestamp}.xlsx"
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Alle Daten
            df.to_excel(writer, sheet_name='Alle Teams', index=False)
            
            # Nach Jahren gruppiert (falls gewünscht)
            if 'Year' in df.columns:
                years = sorted(df['Year'].unique())
                for year in years:
                    if pd.notna(year):  # NaN-Werte überspringen
                        year_data = df[df['Year'] == year]
                        sheet_name = f'Jahr_{int(year)}'
                        if len(sheet_name) <= 31:  # Excel Blattname-Limit
                            year_data.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"📗 Excel-Datei erstellt: {excel_file}")
    except ImportError:
        print("⚠️  Excel-Export nicht verfügbar (openpyxl installieren mit: pip install openpyxl)")
    except Exception as e:
        print(f"⚠️  Excel-Export fehlgeschlagen: {e}")

def show_statistics(df):
    """
    Zeigt grundlegende Statistiken der gescrapten Daten
    
    Args:
        df (pandas.DataFrame): DataFrame mit den Daten
    """
    
    print(f"\n📈 DATEN-STATISTIKEN:")
    print(f"{'='*50}")
    print(f"📊 Gesamtanzahl Teams: {len(df)}")
    
    if 'Year' in df.columns:
        years = df['Year'].dropna()
        if not years.empty:
            print(f"📅 Jahre: {int(years.min())} - {int(years.max())}")
            print(f"📅 Anzahl verschiedene Jahre: {years.nunique()}")
    
    if 'Team Name' in df.columns:
        teams = df['Team Name'].nunique()
        print(f"🏒 Anzahl verschiedene Teams: {teams}")
    
    print(f"📋 Spalten: {list(df.columns)}")
    
    # Top 5 Teams nach Wins (falls verfügbar)
    if 'Wins' in df.columns and 'Team Name' in df.columns:
        print(f"\n🏆 TOP 5 TEAMS (meiste Siege):")
        top_teams = df.nlargest(5, 'Wins')[['Team Name', 'Year', 'Wins', 'Losses']]
        print(top_teams.to_string(index=False))

def main():
    """
    Hauptfunktion
    """
    
    print("🏒 HOCKEY STATISTICS MULTI-PAGE SCRAPER")
    print("="*50)
    
    # Alle Seiten scrapen
    df = scrape_all_pages(max_pages=24, delay=1.5)  # 1.5s Verzögerung
    
    if not df.empty:
        # Statistiken anzeigen
        show_statistics(df)
        
        # Ergebnisse speichern
        save_results(df)
        
        # Erste 10 Zeilen anzeigen
        print(f"\n📋 ERSTE 10 DATENSÄTZE:")
        print(df.head(10).to_string(index=False))
        
    else:
        print("❌ Keine Daten zum Speichern verfügbar!")

if __name__ == "__main__":
    main()