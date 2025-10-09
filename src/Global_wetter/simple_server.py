#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# E:\dev\projekt_python_venv\014_mini_postman\src\Global_wetter python simple_server.py
"""
Optimierter Wetter-Server für die HTML-Weltkugel
CSV-basierte Städte-Datenbank für bessere Wartbarkeit

Autor: Frank Albrecht  
Datum: 9. Oktober 2025
Version: 2.0 - CSV-Optimiert

Changelog:
- [2025-10-09] CSV-Datei für Städte-Koordinaten ausgelagert
- [2025-10-09] Performance-Optimierungen mit Caching
- [2025-10-09] Modulare Code-Struktur implementiert
- [2025-10-09] Erweiterte Fehlerbehandlung und Logging
"""

from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import webbrowser
import time
import os
import csv
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import logging
from functools import lru_cache
from typing import Dict, List, Tuple, Optional

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask-App erstellen
app = Flask(__name__)
CORS(app)  # CORS aktivieren

# Globale Variablen für Caching
_city_coords_cache: Dict = {}
_cache_loaded: bool = False

# === UTILITY FUNCTIONS ===

@lru_cache(maxsize=1)
def load_city_coordinates() -> Dict[str, Dict[str, any]]:
    """
    Lädt Städte-Koordinaten aus CSV-Datei mit Caching.
    
    :returns: Dictionary mit Städte-Koordinaten
    :rtype: Dict[str, Dict[str, any]]
    :raises FileNotFoundError: Wenn CSV-Datei nicht gefunden wird
    
    Beispiel:
        >>> coords = load_city_coordinates()
        >>> coords['Berlin']
        {'lat': 52.52, 'lon': 13.405, 'country': 'Deutschland', 'continent': 'Europa'}
    """
    global _city_coords_cache, _cache_loaded
    
    if _cache_loaded and _city_coords_cache:
        logger.info(f"✅ Cache Hit: {len(_city_coords_cache)} Städte aus Cache geladen")
        return _city_coords_cache
    
    csv_path = os.path.join(os.path.dirname(__file__), 'world_cities.csv')
    
    try:
        logger.info(f"📂 Lade Städte aus CSV-Datei: {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                city_name = row['city']
                _city_coords_cache[city_name] = {
                    'lat': float(row['lat']),
                    'lon': float(row['lon']),
                    'country': row['country'],
                    'continent': row['continent']
                }
        
        _cache_loaded = True
        logger.info(f"✅ {len(_city_coords_cache)} Städte erfolgreich aus CSV geladen")
        return _city_coords_cache
        
    except FileNotFoundError:
        logger.error(f"❌ CSV-Datei nicht gefunden: {csv_path}")
        # Fallback auf Basic-Städte
        return get_fallback_cities()
    
    except Exception as e:
        logger.error(f"❌ Fehler beim Laden der CSV: {str(e)}")
        return get_fallback_cities()

def get_fallback_cities() -> Dict[str, Dict[str, any]]:
    """
    Fallback-Städte für den Fall, dass die CSV-Datei nicht verfügbar ist.
    
    :returns: Dictionary mit Basis-Städten
    :rtype: Dict[str, Dict[str, any]]
    """
    logger.warning("⚠️ Verwende Fallback-Städte")
    
    return {
        'Berlin': {'lat': 52.5200, 'lon': 13.4050, 'country': 'Deutschland', 'continent': 'Europa'},
        'Paris': {'lat': 48.8566, 'lon': 2.3522, 'country': 'Frankreich', 'continent': 'Europa'},
        'London': {'lat': 51.5074, 'lon': -0.1278, 'country': 'Großbritannien', 'continent': 'Europa'},
        'Rom': {'lat': 41.9028, 'lon': 12.4964, 'country': 'Italien', 'continent': 'Europa'},
        'Madrid': {'lat': 40.4168, 'lon': -3.7038, 'country': 'Spanien', 'continent': 'Europa'},
        'Wien': {'lat': 48.2082, 'lon': 16.3738, 'country': 'Österreich', 'continent': 'Europa'},
        'Tokio': {'lat': 35.6762, 'lon': 139.6503, 'country': 'Japan', 'continent': 'Asien'},
        'Washington D.C.': {'lat': 38.9072, 'lon': -77.0369, 'country': 'USA', 'continent': 'Nordamerika'},
        'Canberra': {'lat': -35.2809, 'lon': 149.1300, 'country': 'Australien', 'continent': 'Ozeanien'}
    }

def get_weather_description(weather_code: int) -> str:
    """
    Wandelt Wetter-Codes in deutschen Text um.
    
    :param weather_code: Numerischer Wetter-Code von Open-Meteo API
    :type weather_code: int
    :returns: Deutsche Beschreibung des Wetters
    :rtype: str
    """
    weather_descriptions = {
        0: "Klar", 1: "Überwiegend klar", 2: "Teilweise bewölkt", 3: "Bedeckt",
        45: "Nebel", 48: "Eisnebel",
        51: "Leichter Nieselregen", 53: "Nieselregen", 55: "Starker Nieselregen",
        61: "Leichter Regen", 63: "Regen", 65: "Starker Regen",
        71: "Leichter Schnee", 73: "Schnee", 75: "Starker Schnee",
        80: "Regenschauer", 81: "Starke Regenschauer", 82: "Heftige Regenschauer",
        95: "Gewitter", 96: "Gewitter mit Hagel", 99: "Starkes Gewitter"
    }
    
    return weather_descriptions.get(weather_code, f"Code {weather_code}")

# === ROUTE HANDLERS ===
@app.route('/')
def index():
    """Zeigt die HTML-Weltkugel an"""
    # HTML-Datei im selben Verzeichnis suchen
    html_path = os.path.join(os.path.dirname(__file__), 'weltwetter.html')
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>❌ weltwetter.html nicht gefunden</h1>
        <p>Bitte stellen Sie sicher, dass weltwetter.html im selben Verzeichnis liegt.</p>
        """

@app.route('/test_globe.html')
def test_globe():
    """Test-Seite für 3D-Debugging"""
    html_path = os.path.join(os.path.dirname(__file__), 'test_globe.html')
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>❌ test_globe.html nicht gefunden</h1>"

@app.route('/einfach')
def einfach():
    """Einfache CSS-Version ohne Three.js"""
    html_path = os.path.join(os.path.dirname(__file__), 'weltwetter_einfach.html')
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>❌ weltwetter_einfach.html nicht gefunden</h1>"

@app.route('/weltwetter.css')
def serve_css():
    """CSS-Datei für das Wetter-Interface servieren"""
    css_path = os.path.join(os.path.dirname(__file__), 'weltwetter.css')
    
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            from flask import Response
            return Response(f.read(), mimetype='text/css')
    except FileNotFoundError:
        return "/* CSS-Datei nicht gefunden */", 404

@app.route('/api/weather/<city>')
def get_weather(city: str):
    """
    Gibt Live-Wetterdaten von Open-Meteo API für eine einzelne Stadt zurück.
    
    :param city: Name der Stadt
    :type city: str
    :returns: JSON mit Wetterdaten oder Fehlermeldung
    :rtype: dict
    :raises: 404 wenn Stadt nicht gefunden wird
    
    Beispiel:
        GET /api/weather/Berlin
        Returns: {"temperature": 15.2, "description": "Bedeckt", ...}
    """
    city_coords = load_city_coordinates()
    
    if city not in city_coords:
        logger.warning(f"⚠️ Stadt nicht gefunden: {city}")
        return jsonify({
            "error": f"Stadt {city} nicht gefunden",
            "available_cities": list(city_coords.keys())[:10],  # Erste 10 als Beispiel
            "total_cities": len(city_coords),
            "status": "error"
        }), 404
    
    coords = city_coords[city]
    
    try:
        # Open-Meteo API aufrufen
        weather_data = fetch_city_weather_data(city, coords)
        return jsonify(weather_data)
        
    except Exception as e:
        logger.error(f"❌ Serverfehler für {city}: {str(e)}")
        return jsonify({
            "error": f"Serverfehler: {str(e)}",
            "status": "error"
        }), 500

# Hilfsfunktion für parallele API-Aufrufe
def fetch_city_weather_data(city_name, coords):
    """Lädt Wetterdaten für eine einzelne Stadt - threadsafe"""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': coords['lat'],
            'longitude': coords['lon'],
            'current_weather': True,
            'timezone': 'auto',
            'hourly': 'temperature_2m,relativehumidity_2m,windspeed_10m'
        }
        
        # Schnellerer Timeout für bessere Performance
        response = requests.get(url, params=params, timeout=2)
        
        if response.ok:
            data = response.json()
            current = data['current_weather']
            
            # Wetter-Code in deutschen Text umwandeln
            weather_descriptions = {
                0: "Klar", 1: "Überwiegend klar", 2: "Teilweise bewölkt", 3: "Bedeckt",
                45: "Nebel", 48: "Eisnebel",
                51: "Leichter Nieselregen", 53: "Nieselregen", 55: "Starker Nieselregen",
                61: "Leichter Regen", 63: "Regen", 65: "Starker Regen",
                71: "Leichter Schnee", 73: "Schnee", 75: "Starker Schnee",
                80: "Regenschauer", 81: "Starke Regenschauer", 82: "Heftige Regenschauer",
                95: "Gewitter", 96: "Gewitter mit Hagel", 99: "Starkes Gewitter"
            }
            
            description = weather_descriptions.get(current['weathercode'], f"Code {current['weathercode']}")
            
            from datetime import datetime
            abrufzeit = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            
            return {
                "city": city_name,
                "country": coords['country'],
                "temperature": round(current['temperature'], 1),
                "description": description,
                "windspeed": current['windspeed'],
                "winddirection": current['winddirection'],
                "is_day": current['is_day'] == 1,
                "coordinates": {
                    "lat": coords['lat'],
                    "lon": coords['lon']
                },
                "abrufzeit": abrufzeit,
                "status": "success"
            }
        else:
            raise Exception(f"API Error: {response.status_code}")
            
    except Exception as e:
        from datetime import datetime
        return {
            "city": city_name,
            "country": coords['country'],
            "temperature": 20,
            "description": "Daten nicht verfügbar (Timeout/Offline)",
            "windspeed": 0,
            "winddirection": 0,
            "is_day": True,
            "coordinates": coords,
            "abrufzeit": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "status": "fallback",
            "error": str(e)
        }

# TURBO: API für alle Städte parallel - CSV-optimiert
@app.route('/api/weather/all')
@cross_origin()
def get_all_weather_fast():
    """Gibt Wetterdaten für alle Städte zurück - PARALLEL und SCHNELL mit CSV-Daten!"""
    start_time = time.time()
    city_coords = load_city_coordinates()
    
    if not city_coords:
        fallback_cities = get_fallback_cities()
        city_coords = fallback_cities
        logger.warning("⚠️ Verwende Fallback-Städte für /all Endpoint")
    
    logger.info(f"🚀 Turbo-Abruf aller {len(city_coords)} Städte startet")
    
    # Fallback-Koordinaten falls CSV nicht geladen werden kann (wird aber nicht mehr benötigt)
    fallback_coords = {
        # Europa
        'Berlin': {'lat': 52.5200, 'lon': 13.4050, 'country': 'Deutschland'},
        'Paris': {'lat': 48.8566, 'lon': 2.3522, 'country': 'Frankreich'},
        'London': {'lat': 51.5074, 'lon': -0.1278, 'country': 'Großbritannien'},
        'Rom': {'lat': 41.9028, 'lon': 12.4964, 'country': 'Italien'},
        'Madrid': {'lat': 40.4168, 'lon': -3.7038, 'country': 'Spanien'},
        'Wien': {'lat': 48.2082, 'lon': 16.3738, 'country': 'Österreich'},
        'Bern': {'lat': 46.9480, 'lon': 7.4474, 'country': 'Schweiz'},
        'Warschau': {'lat': 52.2297, 'lon': 21.0122, 'country': 'Polen'},
        'Prag': {'lat': 50.0755, 'lon': 14.4378, 'country': 'Tschechien'},
        'Budapest': {'lat': 47.4979, 'lon': 19.0402, 'country': 'Ungarn'},
        'Amsterdam': {'lat': 52.3676, 'lon': 4.9041, 'country': 'Niederlande'},
        'Stockholm': {'lat': 59.3293, 'lon': 18.0686, 'country': 'Schweden'},
        'Kopenhagen': {'lat': 55.6761, 'lon': 12.5683, 'country': 'Dänemark'},
        'Oslo': {'lat': 59.9139, 'lon': 10.7522, 'country': 'Norwegen'},
        'Helsinki': {'lat': 60.1699, 'lon': 24.9384, 'country': 'Finnland'},
        'Reykjavik': {'lat': 64.1466, 'lon': -21.9426, 'country': 'Island'},
        'Dublin': {'lat': 53.3498, 'lon': -6.2603, 'country': 'Irland'},
        'Lissabon': {'lat': 38.7223, 'lon': -9.1393, 'country': 'Portugal'},
        'Athen': {'lat': 37.9755, 'lon': 23.7348, 'country': 'Griechenland'},
        'Bukarest': {'lat': 44.4268, 'lon': 26.1025, 'country': 'Rumänien'},
        'Sofia': {'lat': 42.6977, 'lon': 23.3219, 'country': 'Bulgarien'},
        'Zagreb': {'lat': 45.8150, 'lon': 15.9819, 'country': 'Kroatien'},
        'Belgrad': {'lat': 44.7866, 'lon': 20.4489, 'country': 'Serbien'},
        'Ljubljana': {'lat': 46.0569, 'lon': 14.5058, 'country': 'Slowenien'},
        'Bratislava': {'lat': 48.1486, 'lon': 17.1077, 'country': 'Slowakei'},
        'Vilnius': {'lat': 54.6872, 'lon': 25.2797, 'country': 'Litauen'},
        'Riga': {'lat': 56.9496, 'lon': 24.1052, 'country': 'Lettland'},
        'Tallinn': {'lat': 59.4370, 'lon': 24.7536, 'country': 'Estland'},
        'Minsk': {'lat': 53.9006, 'lon': 27.5590, 'country': 'Belarus'},
        'Kiew': {'lat': 50.4501, 'lon': 30.5234, 'country': 'Ukraine'},
        'Moskau': {'lat': 55.7558, 'lon': 37.6176, 'country': 'Russland'},
        
        # Asien
        'Tokio': {'lat': 35.6762, 'lon': 139.6503, 'country': 'Japan'},
        'Peking': {'lat': 39.9042, 'lon': 116.4074, 'country': 'China'},
        'Seoul': {'lat': 37.5665, 'lon': 126.9780, 'country': 'Südkorea'},
        'Neu-Delhi': {'lat': 28.6139, 'lon': 77.2090, 'country': 'Indien'},
        'Bangkok': {'lat': 13.7563, 'lon': 100.5018, 'country': 'Thailand'},
        'Hanoi': {'lat': 21.0285, 'lon': 105.8542, 'country': 'Vietnam'},
        'Manila': {'lat': 14.5995, 'lon': 120.9842, 'country': 'Philippinen'},
        'Jakarta': {'lat': -6.2088, 'lon': 106.8456, 'country': 'Indonesien'},
        'Kuala Lumpur': {'lat': 3.1390, 'lon': 101.6869, 'country': 'Malaysia'},
        'Singapur': {'lat': 1.3521, 'lon': 103.8198, 'country': 'Singapur'},
        'Islamabad': {'lat': 33.6844, 'lon': 73.0479, 'country': 'Pakistan'},
        'Kabul': {'lat': 34.5553, 'lon': 69.2075, 'country': 'Afghanistan'},
        'Teheran': {'lat': 35.6892, 'lon': 51.3890, 'country': 'Iran'},
        'Bagdad': {'lat': 33.3128, 'lon': 44.3615, 'country': 'Irak'},
        'Ankara': {'lat': 39.9334, 'lon': 32.8597, 'country': 'Türkei'},
        
        # Afrika
        'Kairo': {'lat': 30.0444, 'lon': 31.2357, 'country': 'Ägypten'},
        'Lagos': {'lat': 6.5244, 'lon': 3.3792, 'country': 'Nigeria'},
        'Kapstadt': {'lat': -33.9249, 'lon': 18.4241, 'country': 'Südafrika'},
        'Nairobi': {'lat': -1.2921, 'lon': 36.8219, 'country': 'Kenia'},
        'Addis Abeba': {'lat': 9.1450, 'lon': 40.4897, 'country': 'Äthiopien'},
        'Rabat': {'lat': 34.0209, 'lon': -6.8417, 'country': 'Marokko'},
        'Tunis': {'lat': 36.8065, 'lon': 10.1815, 'country': 'Tunesien'},
        'Algier': {'lat': 36.7538, 'lon': 3.0588, 'country': 'Algerien'},
        'Tripolis': {'lat': 32.8872, 'lon': 13.1913, 'country': 'Libyen'},
        'Accra': {'lat': 5.6037, 'lon': -0.1870, 'country': 'Ghana'},
        
        # Nord-/Südamerika
        'Washington D.C.': {'lat': 38.9072, 'lon': -77.0369, 'country': 'USA'},
        'Ottawa': {'lat': 45.4215, 'lon': -75.6972, 'country': 'Kanada'},
        'Mexiko-Stadt': {'lat': 19.4326, 'lon': -99.1332, 'country': 'Mexiko'},
        'Guatemala-Stadt': {'lat': 14.6349, 'lon': -90.5069, 'country': 'Guatemala'},
        'Havanna': {'lat': 23.1136, 'lon': -82.3666, 'country': 'Kuba'},
        'Brasília': {'lat': -15.8267, 'lon': -47.9218, 'country': 'Brasilien'},
        'Buenos Aires': {'lat': -34.6118, 'lon': -58.3960, 'country': 'Argentinien'},
        'Santiago': {'lat': -33.4489, 'lon': -70.6693, 'country': 'Chile'},
        'Lima': {'lat': -12.0464, 'lon': -77.0428, 'country': 'Peru'},
        'Bogotá': {'lat': 4.7110, 'lon': -74.0721, 'country': 'Kolumbien'},
        'Caracas': {'lat': 10.4806, 'lon': -66.9036, 'country': 'Venezuela'},
        'Quito': {'lat': -0.1807, 'lon': -78.4678, 'country': 'Ecuador'},
        'La Paz': {'lat': -16.5000, 'lon': -68.1193, 'country': 'Bolivien'},
        'Asunción': {'lat': -25.2637, 'lon': -57.5759, 'country': 'Paraguay'},
        'Montevideo': {'lat': -34.9011, 'lon': -56.1645, 'country': 'Uruguay'},
        
        # Weitere wichtige Städte Asien
        'Riad': {'lat': 24.7136, 'lon': 46.6753, 'country': 'Saudi-Arabien'},
        'Kuwait-Stadt': {'lat': 29.3759, 'lon': 47.9774, 'country': 'Kuwait'},
        'Doha': {'lat': 25.2760, 'lon': 51.5200, 'country': 'Katar'},
        'Abu Dhabi': {'lat': 24.2992, 'lon': 54.6972, 'country': 'VAE'},
        'Muskat': {'lat': 23.5880, 'lon': 58.3829, 'country': 'Oman'},
        'Sanaa': {'lat': 15.3549, 'lon': 44.2066, 'country': 'Jemen'},
        'Damaskus': {'lat': 33.5138, 'lon': 36.2765, 'country': 'Syrien'},
        'Beirut': {'lat': 33.8938, 'lon': 35.5018, 'country': 'Libanon'},
        'Amman': {'lat': 31.9454, 'lon': 35.9284, 'country': 'Jordanien'},
        'Jerusalem': {'lat': 31.7683, 'lon': 35.2137, 'country': 'Israel'},
        'Dhaka': {'lat': 23.8103, 'lon': 90.4125, 'country': 'Bangladesch'},
        'Colombo': {'lat': 6.9271, 'lon': 79.8612, 'country': 'Sri Lanka'},
        'Kathmandu': {'lat': 27.7172, 'lon': 85.3240, 'country': 'Nepal'},
        'Thimphu': {'lat': 27.4728, 'lon': 89.6390, 'country': 'Bhutan'},
        'Male': {'lat': 4.1755, 'lon': 73.5093, 'country': 'Malediven'},
        'Ulaanbaatar': {'lat': 47.8864, 'lon': 106.9057, 'country': 'Mongolei'},
        'Pjöngjang': {'lat': 39.0392, 'lon': 125.7625, 'country': 'Nordkorea'},
        'Vientiane': {'lat': 17.9757, 'lon': 102.6331, 'country': 'Laos'},
        'Phnom Penh': {'lat': 11.5449, 'lon': 104.8922, 'country': 'Kambodscha'},
        'Bandar Seri Begawan': {'lat': 4.9031, 'lon': 114.9398, 'country': 'Brunei'},
        'Dili': {'lat': -8.5569, 'lon': 125.5603, 'country': 'Osttimor'},
        
        # Weitere Städte Afrika
        'Kinshasa': {'lat': -4.4419, 'lon': 15.2663, 'country': 'DR Kongo'},
        'Luanda': {'lat': -8.8390, 'lon': 13.2894, 'country': 'Angola'},
        'Maputo': {'lat': -25.9692, 'lon': 32.5732, 'country': 'Mosambik'},
        'Harare': {'lat': -17.8216, 'lon': 31.0492, 'country': 'Simbabwe'},
        'Gaborone': {'lat': -24.6282, 'lon': 25.9231, 'country': 'Botswana'},
        'Windhoek': {'lat': -22.5609, 'lon': 17.0658, 'country': 'Namibia'},
        'Maseru': {'lat': -29.3151, 'lon': 27.4869, 'country': 'Lesotho'},
        'Mbabane': {'lat': -26.3054, 'lon': 31.1367, 'country': 'Eswatini'},
        'Antananarivo': {'lat': -18.8792, 'lon': 47.5079, 'country': 'Madagaskar'},
        'Port Louis': {'lat': -20.1609, 'lon': 57.5012, 'country': 'Mauritius'},
        'Victoria': {'lat': -4.6196, 'lon': 55.4513, 'country': 'Seychellen'},
        'Moroni': {'lat': -11.7022, 'lon': 43.2551, 'country': 'Komoren'},
        'Yamoussoukro': {'lat': 6.8276, 'lon': -5.2893, 'country': 'Elfenbeinküste'},
        'Ouagadougou': {'lat': 12.3714, 'lon': -1.5197, 'country': 'Burkina Faso'},
        'Bamako': {'lat': 12.6392, 'lon': -8.0029, 'country': 'Mali'},
        'Niamey': {'lat': 13.5116, 'lon': 2.1254, 'country': 'Niger'},
        'N\'Djamena': {'lat': 12.1348, 'lon': 15.0557, 'country': 'Tschad'},
        'Bangui': {'lat': 4.3947, 'lon': 18.5582, 'country': 'Zentralafrikanische Republik'},
        'Libreville': {'lat': 0.4162, 'lon': 9.4673, 'country': 'Gabun'},
        'Malabo': {'lat': 3.7504, 'lon': 8.7371, 'country': 'Äquatorialguinea'},
        'São Tomé': {'lat': 0.1864, 'lon': 6.6131, 'country': 'São Tomé und Príncipe'},
        'Praia': {'lat': 14.9177, 'lon': -23.5092, 'country': 'Kap Verde'},
        'Bissau': {'lat': 11.8817, 'lon': -15.6178, 'country': 'Guinea-Bissau'},
        'Conakry': {'lat': 9.6412, 'lon': -13.5784, 'country': 'Guinea'},
        'Freetown': {'lat': 8.4657, 'lon': -13.2317, 'country': 'Sierra Leone'},
        'Monrovia': {'lat': 6.2907, 'lon': -10.7605, 'country': 'Liberia'},
        'Abuja': {'lat': 9.0765, 'lon': 7.3986, 'country': 'Nigeria'},
        'Lomé': {'lat': 6.1228, 'lon': 1.2255, 'country': 'Togo'},
        'Porto-Novo': {'lat': 6.4969, 'lon': 2.6283, 'country': 'Benin'},
        'Kampala': {'lat': 0.3476, 'lon': 32.5825, 'country': 'Uganda'},
        'Kigali': {'lat': -1.9403, 'lon': 30.0644, 'country': 'Ruanda'},
        'Bujumbura': {'lat': -3.3614, 'lon': 29.3599, 'country': 'Burundi'},
        'Dodoma': {'lat': -6.1630, 'lon': 35.7516, 'country': 'Tansania'},
        'Lusaka': {'lat': -15.3875, 'lon': 28.3228, 'country': 'Sambia'},
        'Lilongwe': {'lat': -13.9626, 'lon': 33.7741, 'country': 'Malawi'},
        'Moroni': {'lat': -11.7172, 'lon': 43.2473, 'country': 'Komoren'},
        'Dschibuti': {'lat': 11.8251, 'lon': 42.5903, 'country': 'Dschibuti'},
        'Asmara': {'lat': 15.3229, 'lon': 38.9251, 'country': 'Eritrea'},
        'Mogadischu': {'lat': 2.0469, 'lon': 45.3182, 'country': 'Somalia'},
        
        # Weitere Städte Amerika
        'Belize City': {'lat': 17.5045, 'lon': -88.1962, 'country': 'Belize'},
        'San Salvador': {'lat': 13.6929, 'lon': -89.2182, 'country': 'El Salvador'},
        'Tegucigalpa': {'lat': 14.0723, 'lon': -87.1921, 'country': 'Honduras'},
        'Managua': {'lat': 12.1150, 'lon': -86.2362, 'country': 'Nicaragua'},
        'San José': {'lat': 9.9281, 'lon': -84.0907, 'country': 'Costa Rica'},
        'Panama-Stadt': {'lat': 8.5380, 'lon': -80.7821, 'country': 'Panama'},
        'Kingston': {'lat': 17.9970, 'lon': -76.7936, 'country': 'Jamaika'},
        'Port-au-Prince': {'lat': 18.5944, 'lon': -72.3074, 'country': 'Haiti'},
        'Santo Domingo': {'lat': 18.4861, 'lon': -69.9312, 'country': 'Dominikanische Republik'},
        'San Juan': {'lat': 18.4655, 'lon': -66.1057, 'country': 'Puerto Rico'},
        'Georgetown': {'lat': 6.8013, 'lon': -58.1551, 'country': 'Guyana'},
        'Paramaribo': {'lat': 5.8520, 'lon': -55.2038, 'country': 'Suriname'},
        'Cayenne': {'lat': 4.9337, 'lon': -52.3281, 'country': 'Französisch-Guayana'},
        
        # Ozeanien
        'Canberra': {'lat': -35.2809, 'lon': 149.1300, 'country': 'Australien'},
        'Wellington': {'lat': -41.2865, 'lon': 174.7762, 'country': 'Neuseeland'},
        'Suva': {'lat': -18.1248, 'lon': 178.4501, 'country': 'Fidschi'},
        'Port Moresby': {'lat': -9.4438, 'lon': 147.1803, 'country': 'Papua-Neuguinea'},
        'Nuku\'alofa': {'lat': -21.1789, 'lon': -175.1982, 'country': 'Tonga'},
        'Apia': {'lat': -13.8506, 'lon': -171.7513, 'country': 'Samoa'},
        'Port Vila': {'lat': -17.7334, 'lon': 168.3273, 'country': 'Vanuatu'},
        'Honiara': {'lat': -9.4280, 'lon': 159.9498, 'country': 'Salomonen'},
        'Tarawa': {'lat': 1.3278, 'lon': 172.9797, 'country': 'Kiribati'},
        'Majuro': {'lat': 7.1315, 'lon': 171.1845, 'country': 'Marshallinseln'},
        'Palikir': {'lat': 6.9147, 'lon': 158.1611, 'country': 'Mikronesien'},
        'Ngerulmud': {'lat': 7.5006, 'lon': 134.6242, 'country': 'Palau'},
        'Funafuti': {'lat': -8.5243, 'lon': 179.1942, 'country': 'Tuvalu'},
        'Yaren': {'lat': -0.5477, 'lon': 166.9209, 'country': 'Nauru'}
    }
    
    start_time = time.time()
    weather_data = {}
    
    # PARALLEL: Alle API-Calls gleichzeitig mit ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=20) as executor:
        # Alle Future-Tasks starten
        future_to_city = {
            executor.submit(fetch_city_weather_data, city, coords): city 
            for city, coords in city_coords.items()
        }
        
        # Ergebnisse sammeln, sobald sie fertig sind
        for future in as_completed(future_to_city):
            city = future_to_city[future]
            try:
                result = future.result()
                weather_data[city] = result
            except Exception as exc:
                print(f'⚠️ {city} generierte Exception: {exc}')
                weather_data[city] = {
                    "error": str(exc), 
                    "status": "error",
                    "city": city
                }
    
    end_time = time.time()
    duration = round(end_time - start_time, 2)
    
    from datetime import datetime
    return jsonify({
        "cities": weather_data,
        "city_coords": city_coords,  # Koordinaten hinzufügen
        "abrufzeit": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "anzahl_staedte": len(weather_data),
        "dauer_sekunden": duration,
        "performance": f"⚡ {len(weather_data)} Städte in {duration}s geladen",
        "status": "success"
    })

# Alternative: Einzelne Stadt (optimiert)
@app.route('/api/weather/fast/<city>')
def get_weather_fast(city):
    """Optimierte Version für einzelne Städte"""
    city_coords = {
        'Berlin': {'lat': 52.5200, 'lon': 13.4050, 'country': 'Deutschland'},
        'Paris': {'lat': 48.8566, 'lon': 2.3522, 'country': 'Frankreich'},
        'London': {'lat': 51.5074, 'lon': -0.1278, 'country': 'Großbritannien'},
        'Rom': {'lat': 41.9028, 'lon': 12.4964, 'country': 'Italien'},
        'Madrid': {'lat': 40.4168, 'lon': -3.7038, 'country': 'Spanien'},
        'Wien': {'lat': 48.2082, 'lon': 16.3738, 'country': 'Österreich'},
        'Bern': {'lat': 46.9480, 'lon': 7.4474, 'country': 'Schweiz'},
        'Warschau': {'lat': 52.2297, 'lon': 21.0122, 'country': 'Polen'},
        'Prag': {'lat': 50.0755, 'lon': 14.4378, 'country': 'Tschechien'},
        'Budapest': {'lat': 47.4979, 'lon': 19.0402, 'country': 'Ungarn'}
    }
    
    if city not in city_coords:
        return jsonify({"error": f"Stadt {city} nicht gefunden", "status": "error"}), 404
    
    start_time = time.time()
    result = fetch_city_weather_data(city, city_coords[city])
    duration = round(time.time() - start_time, 2)
    
    result["performance"] = f"⚡ Geladen in {duration}s"
    return jsonify(result)

@app.route('/api/cities')
def get_cities():
    """Gibt alle verfügbaren Städte mit Koordinaten zurück"""
    return jsonify({
        "cities": city_coords,
        "total": len(city_coords),
        "status": "success"
    })

@app.route('/health')
def health():
    """Server-Status"""
    return jsonify({"status": "ok", "message": "Server läuft!"})

def main():
    """Startet den kompletten Server"""
    print("� Weltwetter-Server")
    print("=" * 40)
    print("� Server startet...")
    print("🌐 URL: http://localhost:5000")
    print("⏹️  Strg+C zum Beenden")
    print("=" * 40)
    
    # Browser öffnen
    def open_browser():
        time.sleep(2)
        try:
            webbrowser.open('http://localhost:5000')
            print("✅ Browser geöffnet!")
        except:
            print("⚠️ Browser konnte nicht geöffnet werden")
    
    import threading
    threading.Timer(2, open_browser).start()
    
    # Server starten
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        use_reloader=False
    )

if __name__ == "__main__":
    main()