# 🧰 Mini Postman - Comprehensive API Testing Suite

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey.svg)](https://python.org)

Eine umfassende Python-basierte API-Testing-Suite, die als Alternative zu Postman entwickelt wurde. Das Tool bietet sowohl eine grafische Benutzeroberfläche als auch leistungsstarke Kommandozeilen-Tools für API-Tests, Health Checks und Performance-Monitoring.

## 🚀 Features

### 🖥️ GUI-Interface (Streamlit)
- **Benutzerfreundliche Web-Oberfläche** für API-Tests
- **Vordefinierte URL-Vorlagen** für schnelle Tests
- **Unterstützung aller HTTP-Methoden** (GET, POST, PUT, DELETE)
- **JSON-Editor** für Headers, Parameter und Request-Body
- **Automatische Übersetzung** von englischen API-Responses ins Deutsche
- **Spracherkennung** für intelligente Übersetzung
- **Integrierte Test-Tool-Ausführung** direkt aus der GUI

### 🏥 Health Check Tool (m005_gesundheitschecker.py)
- **Umfassende Website-Analyse** mit 11 verschiedenen Tests
- **Multi-HTTP-Methoden-Tests** (GET, HEAD, OPTIONS)
- **Performance-Benchmarking** mit mehreren Durchläufen
- **Content-Validierung** (JSON, HTML, Dateigröße)
- **System-Ressourcen-Monitoring** (CPU, RAM, Festplatte)
- **Intelligente Unicode-Unterstützung** für Windows-Konsolen
- **Domain-basierte Log-Dateien** mit vollständiger Ausgabe
- **Anfängerfreundliche Erklärungen** für alle Tests

### 🔍 API Checker (m004_api_checker.py)
- **Batch-API-Testing** für mehrere Endpoints
- **Response-Zeit-Messung** mit Millisekunden-Genauigkeit
- **Error-Handling** und detaillierte Fehlerprotokollierung
- **JSON-Export** der Testergebnisse

### 🧪 Test-Module (m001-m003)
- **Modular aufgebaute Test-Scripts** für spezifische Anwendungsfälle
- **Flexible Parameter-Übergabe** über Kommandozeile
- **Integrierte Logging-Funktionalität**

## 📋 Systemanforderungen

- **Python**: 3.8 oder höher
- **Betriebssystem**: Windows, Linux, macOS
- **RAM**: Mindestens 4 GB (optimal: 8 GB+)
- **Festplatte**: 100 MB freier Speicherplatz

## 🛠️ Installation

### 1. Repository klonen
```bash
git clone https://github.com/Watchkido/014_mini_postman.git
cd 014_mini_postman
```

### 2. Python Virtual Environment erstellen (empfohlen)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows
```

### 3. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 4. Konfiguration anpassen
Bearbeiten Sie `config.py` um URL-Vorlagen und andere Einstellungen anzupassen:
```python
URL_PRESETS = {
    'Ihre API': 'https://api.example.com/endpoint',
    # Weitere URLs hinzufügen...
}
```

## 🚀 Verwendung

### GUI-Interface starten
```bash
python api_mini_postman_gui.py
```
Die Streamlit-Oberfläche öffnet sich automatisch im Browser unter `http://localhost:8501`

### Health Check durchführen
```bash
python m005_gesundheitschecker.py --url https://example.com
```

**Parameter:**
- `--url`: Die zu testende URL (erforderlich)
- `--timeout`: Timeout in Sekunden (optional, Standard: 10)

**Beispiele:**
```bash
# Einfacher Health Check
python m005_gesundheitschecker.py --url https://jsonplaceholder.typicode.com/posts

# Mit benutzerdefiniertem Timeout
python m005_gesundheitschecker.py --url https://api.example.com --timeout 30
```

### API Checker verwenden
```bash
python m004_api_checker.py --urls https://api1.com https://api2.com
```

## 📊 Health Check Kategorien

Das Health Check Tool führt umfassende Tests in folgenden Bereichen durch:

### 🔗 BASIS CONNECTIVITY CHECK
- Prüft grundlegende Erreichbarkeit der Website
- Misst Antwortzeiten für GET-Requests
- Erkennt automatische Weiterleitungen

### 🌐 HTTP METHODEN CHECK  
- Testet GET, HEAD und OPTIONS Requests
- Identifiziert verwendete Server-Software
- Prüft HTTP-Status-Codes und Antwortzeiten

### ⚡ PERFORMANCE CHECK
- Führt 3 Performance-Tests durch
- Berechnet Durchschnittswerte und Statistiken
- Klassifiziert Geschwindigkeit (FAST/MED/SLOW)
- Erstellt Performance-Bewertungen (EXCELLENT/GOOD/AVERAGE/POOR)

### 📄 CONTENT VALIDATION
- Analysiert Content-Type Header
- Validiert JSON-Struktur und -Größe  
- Überprüft Datenintegrität

### 💻 SYSTEM RESOURCES
- Überwacht CPU-Auslastung
- Prüft Arbeitsspeicher-Verbrauch
- Kontrolliert verfügbaren Festplattenspeicher

## 📁 Log-Dateien

Health Check Ergebnisse werden automatisch in Log-Dateien gespeichert:

**Format:** `m005_{domain}_{YYYYMMDD_HHMMSS}.log`

**Beispiele:**
- `m005_jsonplaceholder_typicode_com_20251006_143544.log`
- `m005_httpbin_org_20251006_150259.log`
- `m005_www_google_com_20251006_145818.log`

### Log-Datei Struktur:
```
🏥 COMPREHENSIVE SINGLE URL HEALTH CHECK
============================================================
Ziel URL: https://example.com
Gestartet: 2025-10-06 15:02:59
============================================================

[Vollständige Terminal-Ausgabe mit allen Tests und Ergebnissen]

[2025-10-06 15:03:08] COMPREHENSIVE REPORT - Success Rate: 100.0%
[2025-10-06 15:03:08] PASS | Connectivity: Basic HTTP GET
[2025-10-06 15:03:08] PASS | HTTP Methods: GET Request
[Weitere technische Details...]
```

## 🎯 Performance-Bewertungen

Das System verwendet intelligente Bewertungskriterien:

### Antwortzeiten:
- **🚀 FAST**: < 200ms (sehr schnell)
- **⚡ MED**: 200-1000ms (normale Geschwindigkeit)  
- **🐌 SLOW**: > 1000ms (langsam - über 1s)

### Gesamt-Bewertungen:
- **✅ AUSGEZEICHNET (95-100%)**: Alle Funktionen arbeiten optimal
- **⚠️ GUT (80-94%)**: Kleinere Probleme, aber funktionsfähig
- **🔶 BEFRIEDIGEND (60-79%)**: Mehrere Probleme benötigen Aufmerksamkeit
- **🔴 MANGELHAFT (<60%)**: Schwerwiegende Probleme erkannt

## 🌐 Übersetzungsfeature

Die GUI bietet automatische Übersetzung von API-Responses:

### Voraussetzungen:
- LibreTranslate Server unter `http://192.168.178.185:5000`
- Oder andere LibreTranslate-Instanz (URL in Code anpassen)

### Funktionen:
- **Automatische Spracherkennung**
- **Übersetzung von Englisch zu Deutsch**
- **Mehrere Übersetzungsalternativen**
- **Konfidenz-Bewertung der Spracherkennung**

## 📁 Projektstruktur

```
014_mini_postman/
├── README.md                              # Diese Datei
├── requirements.txt                       # Python-Abhängigkeiten
├── config.py                             # Konfigurationsdatei
├── api_mini_postman_gui.py               # Streamlit GUI
├── m001_test.py                          # Test-Modul 1
├── m002_test.py                          # Test-Modul 2
├── m003_test.py                          # Test-Modul 3
├── m004_api_checker.py                   # API Batch Checker
├── m005_gesundheitschecker.py            # Health Check Tool
├── utils/                                # Hilfsfunktionen
│   ├── __init__.py
│   ├── helper.py
│   └── konstanten.py
└── logs/                                 # Log-Dateien (automatisch erstellt)
    ├── m005_example_com_20251006_143544.log
    └── ...
```

## 🔧 Konfiguration

### URL-Vorlagen anpassen (config.py):
```python
URL_PRESETS = {
    'Ihre API - GET': 'https://api.ihreapp.com/get',
    'Ihre API - POST': 'https://api.ihreapp.com/post',
    'Test API': 'https://httpbin.org/get',
    # Weitere URLs...
}
```

### Health Check Einstellungen:
```python
# In m005_gesundheitschecker.py
self.alert_threshold_ms = 1000  # Performance-Warnschwelle in ms
```

## 🐛 Fehlerbehebung

### Häufige Probleme:

**1. Unicode-Zeichen werden nicht angezeigt (Windows)**
- Das Tool erkennt automatisch Windows-Konsolen und nutzt ASCII-Fallbacks
- Emojis werden durch Text-Bezeichner ersetzt: `🏥` → `[HEALTH]`

**2. Streamlit startet nicht**
```bash
# Manuell starten:
streamlit run api_mini_postman_gui.py
```

**3. LibreTranslate nicht verfügbar**
- Server-URL in `api_mini_postman_gui.py` anpassen
- Oder Übersetzungsfeature deaktivieren

**4. Timeout-Fehler bei langsamen APIs**
```bash
# Timeout erhöhen:
python m005_gesundheitschecker.py --url https://slow-api.com --timeout 30
```

## 🤝 Beitragen

Wir freuen uns über Beiträge! So können Sie helfen:

1. **Fork** des Repositories erstellen
2. **Feature-Branch** erstellen (`git checkout -b feature/AmazingFeature`)
3. **Änderungen committen** (`git commit -m 'Add some AmazingFeature'`)
4. **Branch pushen** (`git push origin feature/AmazingFeature`)
5. **Pull Request** erstellen

### Development Setup:
```bash
# Repository klonen
git clone https://github.com/Watchkido/014_mini_postman.git
cd 014_mini_postman

# Virtual Environment erstellen
python -m venv dev-env
source dev-env/bin/activate  # Linux/Mac
dev-env\Scripts\activate     # Windows

# Development-Abhängigkeiten installieren  
pip install -r requirements-dev.txt

# Tests ausführen
python -m pytest tests/
```

## 📝 Changelog

### Version 1.0.0 (2025-10-06)
- ✅ Streamlit GUI für API-Testing
- ✅ Umfassendes Health Check Tool mit 11 Test-Kategorien
- ✅ Domain-basierte Log-Datei-Benennung
- ✅ Unicode-Unterstützung für Windows-Konsolen
- ✅ Automatische Übersetzung von API-Responses
- ✅ Performance-Benchmarking und -Bewertung
- ✅ System-Ressourcen-Monitoring
- ✅ Anfängerfreundliche Erklärungen aller Tests

### Geplante Features (v1.1):
- 🔄 REST API für Headless-Betrieb
- 📊 Grafische Performance-Diagramme
- 🔔 E-Mail/Slack-Benachrichtigungen bei Fehlern
- ⏰ Geplante/wiederkehrende Health Checks
- 🐳 Docker-Container für einfache Bereitstellung

## 📞 Support

- **GitHub Issues**: [Problem melden](https://github.com/Watchkido/014_mini_postman/issues)
- **Dokumentation**: Siehe dieses README und Code-Kommentare
- **E-Mail**: watchkido@example.com

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe [LICENSE](LICENSE) Datei für Details.

## 🙏 Danksagungen

- **Streamlit** für das fantastische Web-Framework
- **Requests** für die HTTP-Bibliothek
- **JSONPlaceholder** für die Test-API
- **HTTPBin** für HTTP-Testing-Utilities
- **LibreTranslate** für Open-Source-Übersetzungen

## 📈 Statistiken

- **Programmiersprache**: Python 3.8+
- **GUI-Framework**: Streamlit
- **HTTP-Library**: Requests
- **Test-Kategorien**: 11
- **Unterstützte HTTP-Methoden**: GET, POST, PUT, DELETE, HEAD, OPTIONS
- **Log-Format**: UTF-8 mit Unicode-Support
- **Performance-Tests**: 3 pro Health Check
- **Bewertungskategorien**: 4 (EXCELLENT, GOOD, AVERAGE, POOR)

---

**Entwickelt mit ❤️ von [Watchkido](https://github.com/Watchkido)**

*Letzte Aktualisierung: 6. Oktober 2025*