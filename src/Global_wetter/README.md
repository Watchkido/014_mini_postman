# Weltwetter Projekt

Right data. Smart use. Better weather. Bang!

## Projektbeschreibung
Das Weltwetter-Projekt ist eine interaktive 3D-Visualisierung der Wetterdaten von Städten weltweit. Es kombiniert moderne Webtechnologien mit Python-Backend, um eine immersive Benutzererfahrung zu bieten.

## Hauptfunktionen
- **3D-Globus**: Darstellung der Erde mit realistischer Textur.
- **Live-Wetterdaten**: Integration von Wetter-APIs zur Anzeige aktueller Wetterinformationen.
- **Interaktive Steuerung**: Drehen und Zoomen des Globus mit Maus oder Touch.
- **Stadtmarkierungen**: Synchronisierte Marker, die sich mit der Erdrotation bewegen.
- **CSV-Datenmanagement**: Städteinformationen werden aus einer CSV-Datei geladen.
- **Externe CSS-Datei**: Verbesserte Wartbarkeit durch Auslagerung der Stile.

## Technologien
- **Backend**: Python Flask mit ThreadPoolExecutor für parallele API-Aufrufe.
- **Frontend**: Three.js für die 3D-Visualisierung.
- **Datenmanagement**: CSV-Dateien für Städteinformationen.
- **Styling**: Externe CSS-Datei für responsives Design.
- **API**: Open-Meteo API für Wetterdaten.

## Projektstruktur
```
Global_wetter/
├── simple_server.py       # Flask-Server für Backend-Logik
├── weltwetter.html        # Haupt-HTML-Datei für die 3D-Visualisierung
├── weltwetter.css         # Externe CSS-Datei für Stile
├── world_cities.csv       # CSV-Datei mit Städteinformationen
├── utils/                 # Hilfsfunktionen und Konstanten
└── README.md              # Projektbeschreibung
```

## Installation
1. **Python-Umgebung einrichten**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Für Windows: venv\Scripts\activate
   ```
2. **Abhängigkeiten installieren**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Server starten**:
   ```bash
   python simple_server.py
   ```

## Nutzung
- Öffnen Sie die Datei `weltwetter.html` in einem Browser, um die 3D-Visualisierung zu starten.
- Drehen Sie den Globus mit der Maus und klicken Sie auf Marker, um Wetterinformationen anzuzeigen.

## API-Integration

Das Weltwetter-Projekt nutzt die Open-Meteo API, um aktuelle Wetterdaten für die auf dem Globus dargestellten Städte abzurufen. Die API wird im Backend durch parallele Anfragen effizient genutzt, um die Ladezeiten zu minimieren.

### Verwendete Endpunkte
- **/api/cities**: Liefert eine Liste aller Städte aus der CSV-Datei, einschließlich Name, Land, Breitengrad und Längengrad.
- **/api/weather**: Ruft die aktuellen Wetterdaten für eine bestimmte Stadt ab. Die Anfrage erfolgt mit den Parametern `latitude` und `longitude`.

### Beispielanfragen
#### Städte abrufen
```bash
curl http://localhost:5000/api/cities
```
Antwort:
```json
[
  {
    "name": "Berlin",
    "country": "Deutschland",
    "latitude": 52.52,
    "longitude": 13.405
  },
  {
    "name": "Paris",
    "country": "Frankreich",
    "latitude": 48.8566,
    "longitude": 2.3522
  }
]
```

#### Wetterdaten abrufen
```bash
curl "http://localhost:5000/api/weather?latitude=52.52&longitude=13.405"
```
Antwort:
```json
{
  "temperature": 15.3,
  "humidity": 72,
  "wind_speed": 5.4
}
```

### API-Optimierung
- **Parallele Anfragen**: Mithilfe von `ThreadPoolExecutor` werden bis zu 20 gleichzeitige Anfragen an die Open-Meteo API gesendet, um die Ladezeiten zu reduzieren.
- **Caching**: Häufig angefragte Daten werden zwischengespeichert, um die Anzahl der API-Aufrufe zu minimieren.
- **Fehlerbehandlung**: Das Backend behandelt API-Fehler robust und liefert entsprechende Fehlermeldungen an den Client.

### Vorteile der API-Integration
- Echtzeit-Wetterdaten für alle Städte auf dem Globus.
- Schnelle Ladezeiten durch parallele Verarbeitung.
- Erweiterbarkeit für zusätzliche Wetterparameter.

## To-Do
- [ ] Erweiterung der Städteanzahl.
- [ ] Optimierung der Ladezeiten.
- [ ] Hinzufügen weiterer Wetterparameter.

## Lizenz
Dieses Projekt steht unter der MIT-Lizenz.

---

**Entwickelt mit ❤️ von Frank: Right data. Smart use. Better weather. Bang!**