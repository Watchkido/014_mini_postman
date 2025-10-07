import requests
import pandas as pd

def fetch_uv_index():
    """
    Ruft den maximalen täglichen UV-Index für Berlin ab und gibt die Daten als Pandas DataFrame zurück.
    """
    # Koordinaten für Berlin
    latitude = 49.34
    longitude = 8.15

    # Open-Meteo API URL
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=uv_index_max&timezone=Europe/Berlin"

    try:
        # API-Anfrage senden
        response = requests.get(url)
        response.raise_for_status()  # Fehler bei HTTP-Statuscodes erkennen

        # JSON-Daten extrahieren
        data = response.json()

        # Relevante Daten extrahieren
        dates = data['daily']['time']
        uv_indices = data['daily']['uv_index_max']

        # Daten in DataFrame umwandeln
        df = pd.DataFrame({
            'Datum': dates,
            'Maximaler UV-Index': uv_indices
        })

        print("✅ UV-Index-Daten erfolgreich abgerufen!")
        return df

    except requests.exceptions.RequestException as e:
        print(f"❌ Fehler beim Abrufen der UV-Index-Daten: {e}")
        return None

if __name__ == "__main__":
    df_uv_index = fetch_uv_index()
    if df_uv_index is not None:
        print(df_uv_index)