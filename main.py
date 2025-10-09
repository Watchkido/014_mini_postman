# Importiere benötigte Bibliotheken für HTTP-Anfragen und JSON-Verarbeitung
import requests
import json

# Definiere Koordinaten für Berlin (Latitude/Longitude)
latitude = 52.52  # Breitengrad von Berlin
longitude = 13.41  # Längengrad von Berlin

# Basis-URL der Open-Meteo API für Wetterdaten
base_url = "https://api.open-meteo.com/"

# Erstelle den vollständigen Endpoint für aktuelle Wetterdaten
# Füge die Koordinaten als Parameter hinzu und aktiviere current_weather
endpoint_1 = f"v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"

# Sende HTTP GET-Anfrage an die API
response = requests.get(base_url + endpoint_1)

# Prüfe ob die Anfrage erfolgreich war (Status Code 200 = OK)
if response.status_code == 200:
    # Bei Erfolg: Formatiere die JSON-Antwort und gebe sie aus
    # indent=4 sorgt für schöne Einrückung, sort_keys=True sortiert die Schlüssel alphabetisch
    print(json.dumps(response.json(), indent=4, sort_keys=True))
else:
    # Bei Fehler: Gebe Fehlermeldung aus
    print("Fehler beim Abrufen der Wetterdaten!")
    