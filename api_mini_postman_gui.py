# Datei: mini_postman_gui.py
import streamlit as st
import requests
import json
from config import URL_PRESETS

# Streamlit-Seitenkonfiguration für Wide Mode
st.set_page_config(
    page_title="🧰 Mini Postman",
    page_icon="🧰",
    layout="wide",  # Wide Mode aktiviert
    initial_sidebar_state="expanded"
)
import os
import subprocess
import sys
import psutil
import csv
import pandas as pd
from env_config import APIConfig, DatabaseConfig

# Die Klasse lädt automatisch aus .env
api_key = APIConfig.LIBRETRANSLATE_API_KEY  # "abc123xyz789_ihr_echter_key"
db_pass = DatabaseConfig.PASSWORD  



st.title("🧰 Mini Postman (Python Edition)")

# HTTP-Methode Auswahl
method = st.selectbox("HTTP-Methode", ["GET", "POST", "PUT", "DELETE"])

# URL-Auswahl mit vordefinierten Optionen
url_preset = st.selectbox("URL-Vorlage wählen", list(URL_PRESETS.keys()))
selected_url = URL_PRESETS[url_preset]

# URL-Eingabefeld (wird automatisch mit ausgewählter Vorlage gefüllt)
url = st.text_input("URL", value=selected_url, help="Wählen Sie eine Vorlage aus oder geben Sie eine benutzerdefinierte URL ein")

# Send Request Button
send_request = st.button("🚀 Send Request", type="primary")

# Platzhalter für Status Code (wird nach Request gefüllt)
status_placeholder = st.empty()

# Request-Konfiguration in Spalten
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📋 Headers (JSON)")
    headers_input = st.text_area("Headers", value='{"Content-Type": "application/json"}', height=200, key="headers", help="HTTP Headers im JSON-Format", label_visibility="collapsed")

with col2:
    st.subheader("🔧 Params (JSON)")
    params_input = st.text_area("Params", value="{}", height=200, key="params", help="URL-Parameter im JSON-Format", label_visibility="collapsed")

with col3:
    st.subheader("📝 Body (JSON oder Text)")
    data_input = st.text_area("Body", value="", height=200, key="body", help="Request Body - JSON oder Plain Text", label_visibility="collapsed")

if send_request:
    try:
        headers = json.loads(headers_input) if headers_input else {}
        params = json.loads(params_input) if params_input else {}
    except json.JSONDecodeError:
        st.error("Headers/Params müssen gültiges JSON sein.")
        st.stop()

    json_data = None
    data = None
    try:
        json_data = json.loads(data_input) if data_input else None
    except:
        data = data_input

    response = requests.request(method, url, headers=headers, params=params, json=json_data, data=data)

    # HTTP Status Codes aus CSV-Datei laden
    @st.cache_data
    def load_status_codes():
        """Lädt HTTP Status Codes aus CSV-Datei"""
        status_codes = {}
        csv_path = os.path.join(os.path.dirname(__file__), 'http_status_codes.csv')
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    status_codes[int(row['number'])] = row['text']
        except FileNotFoundError:
            st.warning("⚠️ http_status_codes.csv nicht gefunden - verwende Fallback-Codes")
            # Fallback für wichtigste Status Codes
            status_codes = {
                200: "Success - OK",
                201: "Success - Created", 
                400: "Client Error - Bad Request",
                401: "Client Error - Unauthorized",
                403: "Client Error - Forbidden",
                404: "Client Error - Not Found",
                500: "Server Error - Internal Server Error",
                502: "Server Error - Bad Gateway",
                503: "Server Error - Service Unavailable"
            }
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Status Codes: {e}")
            status_codes = {200: "Success - OK", 404: "Client Error - Not Found", 500: "Server Error - Internal Server Error"}
        
        return status_codes

    status_codes = load_status_codes()
    
    # Status Code anzeigen (nach URL-Feld, vor Headers)
    status_code = response.status_code
    status_explanation = status_codes.get(status_code, f"Unbekannter Status Code ({status_code})")
    
    # Status Code mit Farbkodierung in dem Platzhalter anzeigen
    with status_placeholder.container():
        st.subheader("📊 Response Status")
        if 200 <= status_code < 300:
            st.success(f"✅ {status_code} - {status_explanation}")
        elif 300 <= status_code < 400:
            st.info(f"🔄 {status_code} - {status_explanation}")
        elif 400 <= status_code < 500:
            st.warning(f"⚠️ {status_code} - {status_explanation}")
        elif status_code >= 500:
            st.error(f"❌ {status_code} - {status_explanation}")
        else:
            st.info(f"ℹ️ {status_code} - {status_explanation}")

    # Response-Anzeige in Spalten
    st.subheader("📡 Response Details")
    
    resp_col1, resp_col2 = st.columns(2)
    
    with resp_col1:
        st.subheader("🏷️ Response Headers")
        st.json(dict(response.headers))
    
    with resp_col2:
        st.subheader("📄 Response Body")
        response_text = ""
        try:
            response_data = response.json()
            st.json(response_data)
            # Konvertiere JSON zu String für Übersetzung
            response_text = json.dumps(response_data, indent=2, ensure_ascii=False)
        except:
            response_text = response.text
            st.text(response_text)
    
    # Trennlinie vor Übersetzungsbereich
    st.divider()
    
    # Übersetzung ganz unten anbieten wenn Response vorhanden
    if response_text and response_text.strip():
        st.subheader("🌐 Deutsche Übersetzung")
        
        # Übersetzungsoptionen in Spalten
        trans_col1, trans_col2 = st.columns([3, 1])
        
        with trans_col2:
            st.write("**Übersetzungsoptionen:**")
            auto_translate = st.checkbox("Automatisch übersetzen", value=True)
            source_lang = st.selectbox("Von Sprache:", ["auto", "en", "fr", "es", "it"], index=0)
            target_lang = st.selectbox("Zu Sprache:", ["de", "en", "fr", "es", "it"], index=0)
        
        with trans_col1:
            if auto_translate:
                # Erst Sprache erkennen, dann übersetzen
                try:
                    # Begrenze Text auf 1000 Zeichen für Übersetzung
                    text_to_translate = response_text[:1000] if len(response_text) > 1000 else response_text
                    
                    # Schritt 1: Sprache erkennen (nur wenn auto)
                    if source_lang == "auto":
                        detect_payload = {
                            'q': text_to_translate,
                            'api_key': ''
                        }
                        
                        with st.spinner("🔍 Erkenne Sprache..."):
                            detect_response = requests.post(
                                "http://192.168.178.185:5000/detect", 
                                json=detect_payload,
                                headers={'Content-Type': 'application/json'},
                                timeout=30
                            )
                        
                        if detect_response.status_code == 200:
                            detect_result = detect_response.json()
                            if detect_result and len(detect_result) > 0:
                                detected_language = detect_result[0].get('language', 'en')
                                confidence = detect_result[0].get('confidence', 0)
                                
                                st.info(f"🔍 Erkannte Sprache: **{detected_language}** (Konfidenz: {confidence:.1f}%)")
                                source_lang = detected_language
                            else:
                                st.warning("⚠️ Sprache konnte nicht erkannt werden - verwende Englisch")
                                source_lang = "en"
                        else:
                            st.error(f"❌ Spracherkennung fehlgeschlagen: HTTP {detect_response.status_code}")
                            source_lang = "en"
                    
                    # Schritt 2: Übersetzen (nur wenn Quellsprache != Zielsprache)
                    if source_lang != target_lang:
                        translate_payload = {
                            'q': text_to_translate,
                            'source': source_lang,
                            'target': target_lang,
                            'format': 'text',
                            'alternatives': 3,
                            'api_key': ''
                        }
                        
                        with st.spinner("🔄 Übersetze Text..."):
                            translate_response = requests.post(
                                "http://192.168.178.185:5000/translate", 
                                json=translate_payload,
                                headers={'Content-Type': 'application/json'},
                                timeout=60
                            )
                        
                        if translate_response.status_code == 200:
                            result = translate_response.json()
                            
                            # Zeige nur den übersetzten Text prominent an
                            if 'translatedText' in result:
                                st.success("✅ Übersetzung erfolgreich!")
                                st.text_area(
                                    f"📝 Übersetzter Text ({source_lang} → {target_lang}):",
                                    value=result['translatedText'],
                                    height=150,
                                    disabled=True
                                )
                                
                                # Optional: Zeige Alternativen wenn vorhanden
                                if 'alternatives' in result and result['alternatives']:
                                    with st.expander("🔀 Alternative Übersetzungen"):
                                        for i, alt in enumerate(result['alternatives'], 1):
                                            st.write(f"**Alternative {i}:** {alt}")
                                
                                # Optional: Zeige vollständige API-Antwort
                                with st.expander("🔧 Vollständige API-Antwort (Debug)"):
                                    st.json(result)
                            else:
                                st.error("❌ Kein übersetzter Text in der Antwort gefunden")
                                st.json(result)
                        else:
                            st.error(f"❌ Übersetzungsfehler: HTTP {translate_response.status_code}")
                    else:
                        st.info(f"ℹ️ Quell- und Zielsprache sind identisch ({source_lang}) - keine Übersetzung nötig")
                        
                except requests.exceptions.Timeout:
                    st.warning("⚠️ Zeitüberschreitung - Server antwortet nicht")
                except requests.exceptions.ConnectionError:
                    st.error("🚫 Verbindung fehlgeschlagen - Server nicht erreichbar auf http://192.168.178.185:5000")
                except Exception as e:
                    st.error(f"❌ Unerwarteter Fehler: {str(e)}")
            else:
                st.info("ℹ️ Automatische Übersetzung ist deaktiviert. Aktiviere die Checkbox oben um zu übersetzen.")

def list_python_files():
    """Listet alle Python-Dateien, die mit 'm' und einer Zahl beginnen."""
    try:
        # Versuche verschiedene Methoden um den Pfad zu finden
        if '__file__' in globals() and globals()['__file__']:
            base_path = os.path.dirname(os.path.abspath(__file__))
        else:
            # Fallback: Aktuelles Arbeitsverzeichnis
            base_path = os.getcwd()
        
        # Prüfe ob der Pfad existiert
        if not os.path.exists(base_path):
            base_path = os.getcwd()
        
        # Liste alle Python-Dateien die mit 'm' beginnen
        files = []
        for f in os.listdir(base_path):
            if f.startswith('m') and f.endswith('.py'):
                files.append(f)
        
        # Fallback: Wenn keine Dateien gefunden, füge Beispieldateien hinzu
        if not files:
            files = ['Keine m*.py Dateien gefunden']
        
        return files
        
    except Exception as e:
        # Wenn alles fehlschlägt, gib eine Fehlermeldung zurück
        return [f'Fehler beim Laden der Dateien: {str(e)}']

# Sicheres Laden der Python-Dateien
try:
    python_files = list_python_files()
except Exception as e:
    python_files = [f'Fehler: {str(e)}']

# Datei-Auswahl nur anzeigen wenn gültige Dateien vorhanden
if python_files and python_files[0] != 'Keine m*.py Dateien gefunden':
    st.divider()
    st.subheader("🔧 Datei-Ausführung")
    
    selected_file = st.selectbox(
        "Wählen Sie eine Datei aus, an die der Link zur Weiterverarbeitung übergeben werden soll:", 
        python_files, 
        key="file_selector"
    )
    
    if st.button("📄 Datei ausführen"):
        if selected_file and not selected_file.startswith('Fehler'):
            try:
                # Bestimme den korrekten Dateipfad
                if '__file__' in globals() and globals()['__file__']:
                    base_path = os.path.dirname(os.path.abspath(__file__))
                else:
                    base_path = os.getcwd()
                    
                file_path = os.path.join(base_path, selected_file)
                
                # Prüfe ob die Datei existiert
                if os.path.exists(file_path):
                    # Übergabe der URL an die Datei
                    with st.spinner(f"Führe {selected_file} aus..."):
                        result = subprocess.run(
                            ["python", file_path, "--url", url], 
                            capture_output=True, 
                            text=True,
                            cwd=base_path
                        )
                    
                    st.subheader("📊 Ausgabe der Datei:")
                    
                    if result.stdout:
                        st.text_area("✅ Erfolgreiche Ausgabe:", result.stdout, height=200)
                    
                    if result.stderr:
                        st.text_area("⚠️ Fehler/Warnungen:", result.stderr, height=100)
                    
                    if result.returncode == 0:
                        st.success("✅ Datei erfolgreich ausgeführt!")
                    else:
                        st.error(f"❌ Datei beendet mit Fehlercode: {result.returncode}")
                        
                else:
                    st.error(f"❌ Datei nicht gefunden: {file_path}")
                    
            except Exception as e:
                st.error(f"❌ Fehler beim Ausführen der Datei: {e}")
        else:
            st.warning("⚠️ Bitte wählen Sie eine gültige Datei aus.")
else:
    st.info("ℹ️ Keine ausführbaren m*.py Dateien im aktuellen Verzeichnis gefunden.")


# streamlit run mini_postman_gui.py
# streamlit run e:/dev/projekt_python_venv/014_Mini_Postman/src/014_Mini_Postman/modul4.py

# Terminal-Befehle:

# cd e:/dev/projekt_python_venv/014_Mini_Postman/src/mini_postman
# streamlit run mini_postman_gui.py
# streamlit run "e:\dev\projekt_python_venv\014_Mini_Postman\src\mini_postman\mini_postman_gui.py"
# Local URL: http://localhost:8501

if __name__ == "__main__":
       # Überprüfen, ob Streamlit bereits läuft
    streamlit_running = False
    for process in psutil.process_iter(['name', 'cmdline']):
        if "streamlit" in process.info['name'] or (process.info['cmdline'] and "streamlit" in " ".join(process.info['cmdline'])):
            print("Streamlit läuft bereits. Kein erneuter Start erforderlich.")
            streamlit_running = True
            break  # Schleife beenden, da Streamlit gefunden wurde

    if not streamlit_running:
        # Ermitteln des absoluten Pfads zur aktuellen Datei
        script_path = os.path.abspath(__file__)

        try:
            # Streamlit mit dem aktuellen Skript starten
            subprocess.run([sys.executable, "-m", "streamlit", "run", script_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Starten von Streamlit: {e}")
        except KeyboardInterrupt:
            print("Streamlit wurde manuell beendet.")
