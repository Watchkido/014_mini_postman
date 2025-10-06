# Datei: mini_postman_gui.py
import streamlit as st
import requests
import json
from config import URL_PRESETS
import os
import subprocess

st.title("🧰 Mini Postman (Python Edition)")

method = st.selectbox("HTTP-Methode", ["GET", "POST", "PUT", "DELETE"])

# URL-Auswahl mit vordefinierten Optionen
url_preset = st.selectbox("URL-Vorlage wählen", list(URL_PRESETS.keys()))
selected_url = URL_PRESETS[url_preset]

# URL-Eingabefeld (wird automatisch mit ausgewählter Vorlage gefüllt)
url = st.text_input("URL", value=selected_url, help="Wählen Sie eine Vorlage aus oder geben Sie eine benutzerdefinierte URL ein")

headers_input = st.text_area("Headers (JSON)", '{"Content-Type": "application/json"}')
params_input = st.text_area("Params (JSON)", "{}")
data_input = st.text_area("Body (JSON oder Text)", "")

if st.button("Send Request"):
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

    st.subheader("Status Code")
    st.write(response.status_code)

    st.subheader("Headers")
    st.json(dict(response.headers))

    st.subheader("Body")
    response_text = ""
    try:
        response_data = response.json()
        st.json(response_data)
        # Konvertiere JSON zu String für Übersetzung
        response_text = json.dumps(response_data, indent=2, ensure_ascii=False)
    except:
        response_text = response.text
        st.text(response_text)
    
    # Übersetzung immer anbieten wenn Response vorhanden
    if response_text and response_text.strip():
        st.subheader("🌐 Deutsche Übersetzung")
        
        # Erst Sprache erkennen, dann nur bei Englisch übersetzen
        try:
            # Schritt 1: Sprache erkennen
            detect_payload = {
                'q': response_text,
                'api_key': ''
            }
            
            detect_response = requests.post(
                "http://192.168.178.185:5000/detect", 
                json=detect_payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if detect_response.status_code == 200:
                detect_result = detect_response.json()
                if detect_result and len(detect_result) > 0:
                    detected_language = detect_result[0].get('language', '')
                    confidence = detect_result[0].get('confidence', 0)
                    
                    st.info(f"🔍 Erkannte Sprache: **{detected_language}** (Konfidenz: {confidence}%)")
                    
                    # Nur übersetzen wenn Englisch erkannt wurde
                    if detected_language == 'en':
                        # Schritt 2: Übersetzen
                        translate_payload = {
                            'q': response_text,
                            'source': 'en',
                            'target': 'de',
                            'format': 'text',
                            'alternatives': 3,
                            'api_key': ''
                        }
                        
                        translate_response = requests.post(
                            "http://192.168.178.185:5000/translate", 
                            json=translate_payload,
                            headers={'Content-Type': 'application/json'},
                            timeout=60
                        )
                        
                        if translate_response.status_code == 200:
                            result = translate_response.json()
                            st.json(result)  # Zeige die komplette Antwort von LibreTranslate
                        else:
                            st.error(f"❌ Übersetzungsfehler: HTTP {translate_response.status_code}")
                    else:
                        st.info(f"ℹ️ Text ist nicht auf Englisch - keine Übersetzung nötig")
                else:
                    st.warning("⚠️ Sprache konnte nicht erkannt werden")
            else:
                st.error(f"❌ Spracherkennung fehlgeschlagen: HTTP {detect_response.status_code}")
                
        except requests.exceptions.Timeout:
            st.warning("⚠️ Zeitüberschreitung - Server antwortet nicht")
        except requests.exceptions.ConnectionError:
            st.error("🚫 Verbindung fehlgeschlagen - Server nicht erreichbar")
        except Exception as e:
            st.error(f"❌ Fehler: {str(e)}")

def list_python_files():
    """Listet alle Python-Dateien, die mit 'm' und einer Zahl beginnen."""
    base_path = os.path.dirname(__file__) if '__file__' in globals() else os.getcwd()
    return [f for f in os.listdir(base_path) if f.startswith('m') and f.endswith('.py')]

# Auswahlfeld für Python-Dateien
python_files = list_python_files()
selected_file = st.selectbox("Wählen Sie eine Datei aus:", python_files, key="file_selector")

if st.button("Datei ausführen"):
    if selected_file:
        file_path = os.path.join(os.path.dirname(__file__), selected_file)
        try:
            # Übergabe der URL an die Datei
            result = subprocess.run(["python", file_path, "--url", url], capture_output=True, text=True)
            st.text_area("Ausgabe der Datei:", result.stdout + result.stderr, key="file_output")
        except Exception as e:
            st.error(f"Fehler beim Ausführen der Datei: {e}")


# streamlit run mini_postman_gui.py
# streamlit run e:/dev/projekt_python_venv/014_Mini_Postman/src/014_Mini_Postman/modul4.py

# Terminal-Befehle:

# cd e:/dev/projekt_python_venv/014_Mini_Postman/src/mini_postman
# streamlit run mini_postman_gui.py
# streamlit run "e:\dev\projekt_python_venv\014_Mini_Postman\src\mini_postman\mini_postman_gui.py"
# Local URL: http://localhost:8501
