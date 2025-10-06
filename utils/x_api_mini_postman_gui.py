# Datei: mini_postman_gui.py
import streamlit as st
import requests
import json
import os
import subprocess
import sys
import psutil

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
        response_text = json.dumps(response_data, indent=2, ensure_ascii=False)
    except:
        response_text = response.text
        st.text(response_text)

if __name__ == "__main__":
    # Überprüfen, ob Streamlit bereits läuft
    streamlit_running = False
    for process in psutil.process_iter(['name', 'cmdline']):
        if "streamlit" in process.info['name'] or (process.info['cmdline'] and "streamlit" in " ".join(process.info['cmdline'])):
            print("Streamlit läuft bereits. Kein erneuter Start erforderlich.")
            streamlit_running = True
            break

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
