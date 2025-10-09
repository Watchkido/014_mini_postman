import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime

#https://nominatim.openstreetmap.org/ui/reverse.html



class WeatherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wetter API - Koordinaten Abfrage")
        self.root.geometry("800x600")
        
        # Beispiel-Koordinaten für große Städte
        self.city_examples = {
            "Neustadt":(49.3473, 8.1624),
            "Berlin": (52.5200, 13.4050),
            "Hamburg": (53.5511, 9.9937),
            "München": (48.1351, 11.5820),
            "Köln": (50.9375, 6.9603),
            "Frankfurt": (50.1109, 8.6821),
            "Stuttgart": (48.7758, 9.1829),
            "Düsseldorf": (51.2277, 6.7735),
            "Dortmund": (51.5136, 7.4653),
            "Essen": (51.4556, 7.0116),
            "Leipzig": (51.3397, 12.3731),
            "Bremen": (53.0793, 8.8017),
            "Dresden": (51.0504, 13.7373),
            "Hannover": (52.3759, 9.7320),
            "Nürnberg": (49.4521, 11.0767),
            "Wien": (48.2082, 16.3738),
            "Zürich": (47.3769, 8.5417),
            "London": (51.5074, -0.1278),
            "Paris": (48.8566, 2.3522),
            "Rom": (41.9028, 12.4964),
            "Madrid": (40.4168, -3.7038),
            "Amsterdam": (52.3676, 4.9041),
            "Prag": (50.0755, 14.4378),
            "Warschau": (52.2297, 21.0122),
            "Stockholm": (59.3293, 18.0686),
            "Kopenhagen": (55.6761, 12.5683),
            "Oslo": (59.9139, 10.7522),
            "Helsinki": (60.1699, 24.9384),
            "Budapest": (47.4979, 19.0402),
            "Bukarest": (44.4268, 26.1025),
            "Sofia": (42.6977, 23.3219),
            "Athen": (37.9755, 23.7348),
            "Lissabon": (38.7223, -9.1393),
            "Dublin": (53.3498, -6.2603),
            "Brüssel": (50.8503, 4.3517),
            "Luxemburg": (49.6117, 6.1319),
            "Bern": (46.9481, 7.4474),
            "Vaduz": (47.1410, 9.5209),
            "Monaco": (43.7384, 7.4246),
            "San Marino": (43.9424, 12.4578)
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titel
        title_label = ttk.Label(main_frame, text="Wetter API - Koordinaten Eingabe", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Stadtauswahl
        city_frame = ttk.LabelFrame(main_frame, text="Stadt auswählen (optional)", padding="10")
        city_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(city_frame, text="Stadt:").grid(row=0, column=0, sticky=tk.W)
        self.city_var = tk.StringVar()
        city_combo = ttk.Combobox(city_frame, textvariable=self.city_var, 
                                 values=list(self.city_examples.keys()), width=30)
        city_combo.grid(row=0, column=1, padx=(10, 0))
        city_combo.bind('<<ComboboxSelected>>', self.on_city_selected)
        
        # Koordinaten-Eingabe
        coord_frame = ttk.LabelFrame(main_frame, text="Koordinaten eingeben", padding="10")
        coord_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Breitengrad
        ttk.Label(coord_frame, text="Breitengrad (Latitude):").grid(row=0, column=0, sticky=tk.W)
        self.lat_var = tk.StringVar(value="52.52")
        lat_entry = ttk.Entry(coord_frame, textvariable=self.lat_var, width=15)
        lat_entry.grid(row=0, column=1, padx=(10, 0))
        
        ttk.Label(coord_frame, text="Beispiel: 52.52 (Berlin)").grid(row=0, column=2, padx=(10, 0), sticky=tk.W)
        
        # Längengrad
        ttk.Label(coord_frame, text="Längengrad (Longitude):").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.lon_var = tk.StringVar(value="13.41")
        lon_entry = ttk.Entry(coord_frame, textvariable=self.lon_var, width=15)
        lon_entry.grid(row=1, column=1, padx=(10, 0), pady=(10, 0))
        
        ttk.Label(coord_frame, text="Beispiel: 13.41 (Berlin)").grid(row=1, column=2, padx=(10, 0), pady=(10, 0), sticky=tk.W)
        
        # Button für Wetterdaten abrufen
        get_weather_btn = ttk.Button(main_frame, text="Wetterdaten abrufen", 
                                   command=self.get_weather_data, style="Accent.TButton")
        get_weather_btn.grid(row=3, column=0, columnspan=3, pady=20)
        
        # Ergebnis-Anzeige
        result_frame = ttk.LabelFrame(main_frame, text="Wetterdaten", padding="10")
        result_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Scrollbarer Text für Ergebnisse
        text_frame = ttk.Frame(result_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.result_text = tk.Text(text_frame, wrap=tk.WORD, height=20, width=80)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Gewichtung für Responsive Design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
    def on_city_selected(self, event):
        """Wird aufgerufen, wenn eine Stadt aus der Dropdown-Liste ausgewählt wird"""
        selected_city = self.city_var.get()
        if selected_city in self.city_examples:
            lat, lon = self.city_examples[selected_city]
            self.lat_var.set(str(lat))
            self.lon_var.set(str(lon))
            
    def validate_coordinates(self):
        """Validiert die eingegebenen Koordinaten"""
        try:
            lat = float(self.lat_var.get())
            lon = float(self.lon_var.get())
            
            if not (-90 <= lat <= 90):
                raise ValueError("Breitengrad muss zwischen -90 und 90 liegen")
            if not (-180 <= lon <= 180):
                raise ValueError("Längengrad muss zwischen -180 und 180 liegen")
                
            return lat, lon
        except ValueError as e:
            messagebox.showerror("Ungültige Koordinaten", str(e))
            return None, None
            
    def get_weather_data(self):
        """Ruft die Wetterdaten von der API ab und zeigt sie an"""
        lat, lon = self.validate_coordinates()
        if lat is None or lon is None:
            return
            
        try:
            # API-Aufruf
            base_url = "https://api.open-meteo.com/"
            endpoint = f"v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            
            # Lade-Cursor anzeigen
            self.root.config(cursor="wait")
            self.root.update()
            
            response = requests.get(base_url + endpoint, timeout=10)
            
            if response.status_code == 200:
                weather_data = response.json()
                self.display_weather_data(weather_data)
            else:
                messagebox.showerror("API Fehler", 
                                   f"Fehler beim Abrufen der Wetterdaten!\n"
                                   f"Status Code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Verbindungsfehler", 
                               f"Fehler bei der Verbindung zur API:\n{str(e)}")
        finally:
            # Normal-Cursor wiederherstellen
            self.root.config(cursor="")
            
    def display_weather_data(self, data):
        """Zeigt die Wetterdaten in formatierter Form an"""
        self.result_text.delete(1.0, tk.END)
        
        # Header mit Standortinformationen
        header = f"""
=== WETTERDATEN ===
Abgerufen am: {datetime.now().strftime('%d.%m.%Y um %H:%M:%S')}

STANDORT INFORMATIONEN:
• Breitengrad: {data.get('latitude', 'N/A')}°
• Längengrad: {data.get('longitude', 'N/A')}°
• Höhe über Meeresspiegel: {data.get('elevation', 'N/A')} m
• Zeitzone: {data.get('timezone', 'N/A')} ({data.get('timezone_abbreviation', 'N/A')})
• UTC Offset: {data.get('utc_offset_seconds', 'N/A')} Sekunden

"""
        
        self.result_text.insert(tk.END, header)
        
        # Aktuelle Wetterdaten
        if 'current_weather' in data:
            current = data['current_weather']
            units = data.get('current_weather_units', {})
            
            # Wettercode zu Text konvertieren
            weather_description = self.get_weather_description(current.get('weathercode', 0))
            
            # Tag/Nacht Status
            is_day = "Tag" if current.get('is_day', 0) == 1 else "Nacht"
            
            weather_info = f"""AKTUELLE WETTERBEDINGUNGEN:
• Zeit: {current.get('time', 'N/A')}
• Temperatur: {current.get('temperature', 'N/A')} {units.get('temperature', '°C')}
• Wetterbedingungen: {weather_description} (Code: {current.get('weathercode', 'N/A')})
• Tag/Nacht: {is_day}
• Windgeschwindigkeit: {current.get('windspeed', 'N/A')} {units.get('windspeed', 'km/h')}
• Windrichtung: {current.get('winddirection', 'N/A')} {units.get('winddirection', '°')}
• Messintervall: {current.get('interval', 'N/A')} {units.get('interval', 'Sekunden')}

"""
            
            self.result_text.insert(tk.END, weather_info)
            
        # API-Informationen
        api_info = f"""API INFORMATIONEN:
• Generierungszeit: {data.get('generationtime_ms', 'N/A')} ms

"""
        
        self.result_text.insert(tk.END, api_info)
        
        # Vollständige JSON-Antwort (formatiert)
        json_data = f"""VOLLSTÄNDIGE API-ANTWORT (JSON):
{json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)}
"""
        
        self.result_text.insert(tk.END, json_data)
        
    def get_weather_description(self, code):
        """Konvertiert WMO-Wettercode in deutsche Beschreibung"""
        weather_codes = {
            0: "Klarer Himmel",
            1: "Hauptsächlich klar", 
            2: "Teilweise bewölkt",
            3: "Bedeckt",
            45: "Nebel",
            48: "Nebel mit Reifablagerung",
            51: "Leichter Sprühregen",
            53: "Mäßiger Sprühregen", 
            55: "Dichter Sprühregen",
            56: "Leichter gefrierender Sprühregen",
            57: "Dichter gefrierender Sprühregen",
            61: "Leichter Regen",
            63: "Mäßiger Regen",
            65: "Starker Regen",
            66: "Leichter gefrierender Regen",
            67: "Starker gefrierender Regen",
            71: "Leichter Schneefall",
            73: "Mäßiger Schneefall",
            75: "Starker Schneefall",
            77: "Schneekörner",
            80: "Leichte Regenschauer",
            81: "Mäßige Regenschauer",
            82: "Heftige Regenschauer",
            85: "Leichte Schneeschauer",
            86: "Heftige Schneeschauer",
            95: "Gewitter",
            96: "Gewitter mit leichtem Hagel",
            99: "Gewitter mit schwerem Hagel"
        }
        
        return weather_codes.get(code, f"Unbekannt (Code: {code})")

def main():
    """Hauptfunktion zum Starten der GUI"""
    root = tk.Tk()
    
    # Versuche ein modernes Theme zu setzen
    try:
        style = ttk.Style()
        # Verfügbare Themes anzeigen (optional)
        # print("Verfügbare Themes:", style.theme_names())
        
        # Versuche ein modernes Theme zu setzen
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        elif 'alt' in style.theme_names():
            style.theme_use('alt')
    except:
        pass  # Fallback auf Standard-Theme
    
    app = WeatherGUI(root)
    
    # Zentriere das Fenster auf dem Bildschirm
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()