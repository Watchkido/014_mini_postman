# 🧰 Mini Postman - Comprehensive API Testing Suite

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Eine umfassende Python-basierte API-Testing-Suite als Alternative zu Postman**

[🚀 Quick Start](#-quick-start) • [📖 Features](#-features) • [🛠️ Installation](#-installation) • [📚 Documentation](#-documentation)

</div>

---

## 📋 Inhaltsverzeichnis

- [🎯 Überblick](#-überblick)
- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [🛠️ Installation](#-installation)
- [💻 Verwendung](#-verwendung)
- [🧪 Testing](#-testing)
- [🐳 Docker](#-docker)
- [🔧 Konfiguration](#-konfiguration)
- [📊 Status Codes](#-status-codes)
- [🌐 Übersetzungen](#-übersetzungen)
- [🔒 Sicherheit](#-sicherheit)
- [📚 API Documentation](#-api-documentation)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🎯 Überblick

**Mini Postman** ist eine leistungsstarke, Python-basierte API-Testing-Suite, die als Alternative zu Postman entwickelt wurde. Das Tool bietet sowohl eine benutzerfreundliche **Streamlit GUI** als auch mächtige **Kommandozeilen-Tools** für umfassende API-Tests, Health Checks und Performance-Monitoring.

### 🌟 Warum Mini Postman?

- ✅ **Open Source** - Vollständig kostenfrei und erweiterbar
- ✅ **Benutzerfreundlich** - Moderne Web-GUI mit intuitiver Bedienung  
- ✅ **Mehrsprachig** - Deutsche und englische Unterstützung
- ✅ **Umfassend** - 11 verschiedene Test-Kategorien
- ✅ **Professionell** - Enterprise-ready mit Docker-Support
- ✅ **Erweiterbar** - Modulare Architektur für Custom-Features

---

## ✨ Features

### 🖥️ **Streamlit GUI Interface**
<div align="center">
<img src="https://via.placeholder.com/800x400/FF4B4B/FFFFFF?text=Streamlit+GUI+Interface" alt="GUI Interface" />
</div>

- **🎨 Moderne Web-Oberfläche** für API-Tests
- **📋 Vordefinierte URL-Vorlagen** für schnelle Tests
- **🔄 Alle HTTP-Methoden** (GET, POST, PUT, DELETE, PATCH)
- **📝 JSON-Editor** für Headers, Parameter und Request-Body
- **🌐 Automatische Übersetzung** von API-Responses (EN → DE)
- **🔍 Intelligente Spracherkennung** für optimale Übersetzung
- **⚡ Integrierte Tool-Ausführung** direkt aus der GUI

### 🏥 **Health Check Tool** (`m005_gesundheitschecker.py`)

```python
# Beispiel-Verwendung
python m005_gesundheitschecker.py --url https://api.example.com
```

- **📊 11 Verschiedene Test-Kategorien:**
  1. 🔗 Basis Connectivity Check
  2. 🌐 HTTP-Methoden Tests (GET, POST, PUT, DELETE)
  3. ⚡ Performance Benchmarking 
  4. 📄 Content-Validierung (JSON, HTML, Dateigröße)
  5. 💾 System-Ressourcen Monitoring (CPU, RAM, Disk)
  6. 🔒 SSL/TLS Certificate Validation
  7. 📱 Response Headers Analysis
  8. 🎯 Custom Endpoint Testing
  9. 📈 Load Testing Simulation
  10. 🔍 Error Detection & Analysis
  11. 📋 Comprehensive Reporting

- **🎨 Features:**
  - **Unicode-Support** für Windows-Konsolen
  - **Domain-basierte Log-Dateien** (`m005_example_com_20251006_143544.log`)
  - **Anfängerfreundliche Erklärungen** für jeden Test
  - **Farbkodierte Ausgabe** mit Emoji-Support
  - **Detaillierte Performance-Metriken**

### 🔍 **API Checker** (`m004_api_checker.py`)

- **📦 Batch-API-Testing** für mehrere Endpoints
- **⏱️ Präzise Response-Zeit-Messung** (Millisekunden-Genauigkeit)
- **🛡️ Umfassendes Error-Handling**
- **📊 JSON-Export** der Testergebnisse
- **📈 Performance-Trends** und Statistiken

### 🧪 **Modulare Test-Suite** (`m001.py` - `m003.py`)

- **🧩 Modular aufgebaute Scripts** für spezifische Use Cases
- **⚙️ Flexible Parameter-Übergabe** über CLI
- **📝 Integrierte Logging-Funktionalität**
- **🔧 Einfache Erweiterung** für Custom-Tests

---

## 🚀 Quick Start

### 1️⃣ **Sofort starten (3 Befehle)**

```bash
git clone https://github.com/Watchkido/014_mini_postman.git
cd 014_mini_postman
pip install -r requirements.txt
```

### 2️⃣ **GUI starten**

```bash
streamlit run api_mini_postman_gui.py
```

🎉 **Fertig!** Die GUI öffnet automatisch unter `http://localhost:8501`

### 3️⃣ **Health Check testen**

```bash
python m005_gesundheitschecker.py --url https://jsonplaceholder.typicode.com/posts/1
```

---

## 🛠️ Installation

### 📋 **Systemanforderungen**

| Komponente | Minimum | Empfohlen |
|------------|---------|-----------|
| **Python** | 3.8+ | 3.11+ |
| **RAM** | 4 GB | 8 GB+ |
| **Storage** | 100 MB | 1 GB |
| **OS** | Windows 10, Linux, macOS | Beliebig |

### 🐍 **Python Installation**

#### **Option 1: Mit Virtual Environment (Empfohlen)**

```bash
# Repository klonen
git clone https://github.com/Watchkido/014_mini_postman.git
cd 014_mini_postman

# Virtual Environment erstellen
python -m venv venv

# Virtual Environment aktivieren
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

#### **Option 2: System-wide Installation**

```bash
pip install streamlit requests psutil python-dotenv pandas
```

### 🔧 **Konfiguration**

```bash
# Environment-Datei erstellen
cp .env.example .env

# .env editieren (Optional)
notepad .env  # Windows
vim .env      # Linux/Mac
```

**Beispiel `.env` Konfiguration:**

```env
# Entwicklung
DEBUG=true
ENVIRONMENT=development

# Performance
PERFORMANCE_WARNING_MS=1000
PERFORMANCE_ERROR_MS=3000
MAX_REQUESTS_PER_MINUTE=60

# LibreTranslate (Optional)
LIBRETRANSLATE_BASE_URL=http://localhost:5000
LIBRETRANSLATE_API_KEY=your_api_key_here

# Notifications (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

---

## 💻 Verwendung

### 🖥️ **GUI Interface**

#### **1. Streamlit GUI starten**

```bash
streamlit run api_mini_postman_gui.py
```

#### **2. Features der GUI**

<table>
<tr>
<td width="50%">

**🎯 HTTP-Request Testing:**
- URL-Vorlagen auswählen
- HTTP-Methode wählen
- Headers & Parameter setzen
- Request Body definieren
- Response analysieren

</td>
<td width="50%">

**🌐 Übersetzungsfeatures:**
- Automatische Spracherkennung
- EN → DE Übersetzung
- API-Response Lokalisierung
- Mehrsprachige Status Codes

</td>
</tr>
</table>

#### **3. Vordefinierte URL-Vorlagen**

Die GUI bietet sofort verwendbare API-Endpoints:

```python
URL_PRESETS = {
    "JSONPlaceholder Posts": "https://jsonplaceholder.typicode.com/posts",
    "JSONPlaceholder Users": "https://jsonplaceholder.typicode.com/users", 
    "HTTPBin GET": "https://httpbin.org/get",
    "HTTPBin POST": "https://httpbin.org/post",
    "GitHub API": "https://api.github.com/users/octocat",
    "Custom URL": ""
}
```

### 🏥 **Health Check Tool**

#### **Basis-Verwendung:**

```bash
python m005_gesundheitschecker.py --url https://example.com
```

#### **Erweiterte Optionen:**

```bash
# Mit spezifischen Tests
python m005_gesundheitschecker.py --url https://api.example.com --tests connectivity,performance,ssl

# Mit Custom Timeout
python m005_gesundheitschecker.py --url https://slow-api.com --timeout 30

# Verbose Output
python m005_gesundheitschecker.py --url https://example.com --verbose
```

#### **Output-Beispiel:**

```
🏥 COMPREHENSIVE SINGLE URL HEALTH CHECK FOR: https://jsonplaceholder.typicode.com/posts/1
======================================================================

🔗 BASIS CONNECTIVITY CHECK
• Prüft, ob die Webseite überhaupt erreichbar ist
• Misst die Antwortzeit für einen einfachen GET-Request
----------------------------------------
✅ Verbindung erfolgreich - Status Code: 200
⚡ Response Zeit: 145.32ms
📊 Rating: EXCELLENT (< 200ms)

🌐 HTTP METHODS TESTS  
• Testet verschiedene HTTP-Methoden (GET, POST, PUT, DELETE)
• Prüft, welche Methoden der Server unterstützt
----------------------------------------
✅ GET: Unterstützt (200)
❌ POST: Nicht unterstützt (405)
❌ PUT: Nicht unterstützt (405) 
❌ DELETE: Nicht unterstützt (405)

⚡ PERFORMANCE BENCHMARKING
• Führt mehrere Requests durch und berechnet Statistiken
• Misst Durchschnitt, Minimum und Maximum der Response-Zeiten
----------------------------------------
📊 Performance Tests (3 Durchläufe):
   • Durchschnitt: 142.15ms
   • Minimum: 134.21ms  
   • Maximum: 156.78ms
   • Rating: EXCELLENT

===============================
📋 COMPREHENSIVE HEALTH REPORT
===============================
🎯 Ziel: https://jsonplaceholder.typicode.com/posts/1
⏰ Datum: 2025-10-06 14:35:44
✅ Success Rate: 85.7% (6/7 Tests erfolgreich)
📊 Gesamtbewertung: GOOD
```

### 📊 **Batch API Testing**

```bash
# API Checker für multiple Endpoints
python m004_api_checker.py --config endpoints.json
```

**endpoints.json Beispiel:**

```json
{
  "endpoints": [
    {
      "name": "User API",
      "url": "https://jsonplaceholder.typicode.com/users/1",
      "method": "GET",
      "expected_status": 200
    },
    {
      "name": "Posts API", 
      "url": "https://jsonplaceholder.typicode.com/posts",
      "method": "POST",
      "data": {"title": "Test Post", "body": "Test Body"},
      "expected_status": 201
    }
  ]
}
```

---

## 🧪 Testing

### 🔬 **Test-Framework**

Das Projekt verwendet **pytest** für umfassende Tests:

```bash
# Alle Tests ausführen
pytest

# Mit Coverage Report
pytest --cov=. --cov-report=html

# Nur Unit Tests
pytest tests/test_*.py -v

# Performance Tests
pytest tests/performance/ -v
```

### 📊 **Test-Kategorien**

<table>
<tr>
<th>Kategorie</th>
<th>Beschreibung</th>
<th>Ausführung</th>
</tr>
<tr>
<td>🧪 <strong>Unit Tests</strong></td>
<td>Einzelne Funktionen & Klassen</td>
<td><code>pytest tests/test_*.py</code></td>
</tr>
<tr>
<td>🔗 <strong>Integration Tests</strong></td>
<td>API-Interaktionen & Services</td>
<td><code>pytest tests/integration/</code></td>
</tr>
<tr>
<td>⚡ <strong>Performance Tests</strong></td>
<td>Load Testing & Benchmarks</td>
<td><code>pytest tests/performance/</code></td>
</tr>
<tr>
<td>🎭 <strong>End-to-End Tests</strong></td>
<td>GUI & Workflow Testing</td>
<td><code>pytest tests/e2e/</code></td>
</tr>
</table>

### 🎯 **Load Testing mit Locust**

```bash
# Einfacher Load Test
locust -f tests/performance/test_load.py --host=https://httpbin.org

# Headless mit Parameters
locust -f tests/performance/test_load.py \
    --host=https://httpbin.org \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --headless
```

---

## 🐳 Docker

### 🚀 **Quick Start mit Docker**

#### **Option 1: Docker Compose (Empfohlen)**

```bash
# Full Stack starten (Mini Postman + LibreTranslate + PostgreSQL)
docker-compose up -d

# Nur Mini Postman
docker-compose up mini-postman
```

#### **Option 2: Single Container**

```bash
# Image bauen
docker build -t mini-postman .

# Container starten
docker run -p 8501:8501 --env-file .env mini-postman
```

### 🏗️ **Docker-Architektur**

```yaml
# docker-compose.yml
version: '3.8'
services:
  mini-postman:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DEBUG=false
      - LIBRETRANSLATE_BASE_URL=http://libretranslate:5000
    depends_on:
      - libretranslate
      
  libretranslate:
    image: libretranslate/libretranslate:latest
    ports:
      - "5000:5000"
    environment:
      - LT_API_KEYS=true
      
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=mini_postman_db
      - POSTGRES_USER=minipostman
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 🔧 **Docker Commands**

```bash
# Logs ansehen
docker-compose logs -f mini-postman

# Container Status
docker-compose ps

# In Container einsteigen
docker-compose exec mini-postman bash

# Services neustarten
docker-compose restart mini-postman

# Alles stoppen & löschen
docker-compose down -v
```

---

## 🔧 Konfiguration

### ⚙️ **Environment Configuration**

Die Konfiguration erfolgt über die zentrale `env_config.py`:

```python
# Konfiguration laden
from env_config import APIConfig, AppConfig, NotificationConfig

# API-Keys abrufen
translate_key = APIConfig.LIBRETRANSLATE_API_KEY
openai_key = APIConfig.OPENAI_API_KEY

# App-Settings
debug_mode = AppConfig.DEBUG
max_requests = AppConfig.MAX_REQUESTS_PER_MINUTE

# Konfiguration validieren
from env_config import validate_required_config, print_config_summary
validate_required_config()
print_config_summary()
```

### 📊 **Konfiguration testen**

```bash
# Aktuelle Konfiguration anzeigen
python env_config.py
```

**Output:**

```
============================================================
MINI POSTMAN - KONFIGURATION
============================================================
Environment: development
Debug Mode: True
Log Level: INFO

API Konfiguration:
  LibreTranslate URL: http://192.168.178.185:5000
  LibreTranslate API Key: ✓ Konfiguriert
  OpenAI API Key: ✗ Nicht konfiguriert

Performance Settings:
  Warning Threshold: 1000ms
  Error Threshold: 5000ms
  Max Requests/Min: 60

Benachrichtigungen:
  E-Mail: ✗ Nicht konfiguriert
  Slack: ✗ Nicht konfiguriert

Sicherheit:
  JWT: ✗ Nicht konfiguriert
============================================================
```

---

## 📊 Status Codes

### 🎨 **Zweisprachige Status Code-Anzeige**

Mini Postman bietet **vollständige deutsche Übersetzungen** für alle HTTP Status Codes:

| Code | Englisch | Deutsch | Anzeige |
|------|----------|---------|---------|
| 200 | Success - OK | In Ordnung | ✅ 200 - Success - OK (In Ordnung) |
| 404 | Client Error - Not Found | Nicht gefunden | ⚠️ 404 - Client Error - Not Found (Nicht gefunden) |
| 500 | Server Error - Internal Server Error | Interner Serverfehler | ❌ 500 - Server Error - Internal Server Error (Interner Serverfehler) |

### 📋 **Status Code-Kategorien**

<div align="center">
<table>
<tr>
<th>Kategorie</th>
<th>Codes</th>
<th>Icon</th>
<th>Farbe</th>
<th>Bedeutung</th>
</tr>
<tr>
<td><strong>1xx Informational</strong></td>
<td>100-103</td>
<td>ℹ️</td>
<td>🔵 Blau</td>
<td>Informative Nachrichten</td>
</tr>
<tr>
<td><strong>2xx Success</strong></td>
<td>200-226</td>
<td>✅</td>
<td>🟢 Grün</td>
<td>Erfolgreiche Anfragen</td>
</tr>
<tr>
<td><strong>3xx Redirection</strong></td>
<td>300-308</td>
<td>🔄</td>
<td>🔵 Blau</td>
<td>Weiterleitungen</td>
</tr>
<tr>
<td><strong>4xx Client Error</strong></td>
<td>400-451</td>
<td>⚠️</td>
<td>🟡 Gelb</td>
<td>Client-Fehler</td>
</tr>
<tr>
<td><strong>5xx Server Error</strong></td>
<td>500-511</td>
<td>❌</td>
<td>🔴 Rot</td>
<td>Server-Fehler</td>
</tr>
</table>
</div>

### 🎯 **Besondere Status Codes**

- **418** - `I'm a teapot (Ich bin eine Teekanne)` 🫖 - Der berühmte April-Scherz-Status
- **429** - `Too Many Requests (Zu viele Anfragen)` - Rate Limiting
- **451** - `Unavailable For Legal Reasons (Aus rechtlichen Gründen nicht verfügbar)` - Zensur

---

## 🌐 Übersetzungen  

### 🔄 **LibreTranslate Integration**

Mini Postman bietet **automatische Übersetzung** von API-Responses:

```python
# Automatische Spracherkennung
detected_language = detect_language(api_response)

# Intelligente Übersetzung (nur bei Bedarf)
if detected_language == 'en':
    german_translation = translate_text(api_response, 'en', 'de')
```

### 🎯 **Translation Features**

- **🔍 Intelligente Spracherkennung** - Erkennt automatisch die Sprache
- **⚡ Effiziente Übersetzung** - Übersetzt nur englische Inhalte
- **📊 Konfidenz-Score** - Zeigt Genauigkeit der Spracherkennung
- **🔄 Batch-Translation** - Übersetzt große JSON-Responses
- **⚙️ Konfigurierbar** - Unterstützt verschiedene Translation-APIs

### 🛠️ **Unterstützte Translation-APIs**

| Service | Status | Konfiguration |
|---------|--------|---------------|
| **LibreTranslate** | ✅ Aktiv | `LIBRETRANSLATE_BASE_URL` |
| **Google Translate** | 🔧 Optional | `GOOGLE_TRANSLATE_API_KEY` |
| **Azure Translator** | 🔧 Optional | `AZURE_TRANSLATOR_KEY` |
| **OpenAI GPT** | 🔧 Optional | `OPENAI_API_KEY` |

---

## 🔒 Sicherheit

### 🛡️ **Security Features**

Mini Postman implementiert **Enterprise-grade Security**:

#### **🔐 API-Key Management**

```python
from env_config import SecureAPIKeyManager

# API-Keys verschlüsseln
key_manager = SecureAPIKeyManager()
encrypted_key = key_manager.encrypt_api_key("sk-1234567890")

# Zur Laufzeit entschlüsseln
decrypted_key = key_manager.decrypt_api_key(encrypted_key)
```

#### **🚫 .gitignore Protection**

```gitignore
# Sensitive Files
.env
*.log
.crypto_key
**/*_secret*
**/*_private*

# API Keys & Tokens
**/api_keys/
**/tokens/
**/.secrets/
```

#### **⚠️ Security Best Practices**

- ✅ **Environment Variables** für alle Secrets
- ✅ **Verschlüsselte API-Key Storage** 
- ✅ **Rate Limiting** für API-Requests
- ✅ **Input Validation** für alle User-Inputs
- ✅ **Secure Headers** in HTTP-Requests
- ✅ **No Secrets in Code** - Alle sensiblen Daten über .env

### 🔍 **Security Audit**

```bash
# Security Check ausführen
python -m safety check
python -m bandit -r .

# Dependencies auf Vulnerabilities prüfen  
pip-audit
```

---

## 📚 API Documentation

### 🎯 **Programmierbare APIs**

Mini Postman bietet **umfassende APIs** für Integration in eigene Projekte:

#### **Health Check API**

```python
from m005_gesundheitschecker import ComprehensiveHealthChecker

# Health Check erstellen
checker = ComprehensiveHealthChecker("https://api.example.com")

# Comprehensive Check ausführen
results = checker.run_comprehensive_check()

# Spezifische Tests
connectivity = checker.check_basic_connectivity()
performance = checker.check_performance()
ssl_info = checker.check_ssl_certificate()
```

#### **Async API Testing**

```python
import asyncio
import aiohttp
from typing import List, Dict

class AsyncAPITester:
    async def test_endpoints(self, endpoints: List[str]) -> List[Dict]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.test_single_endpoint(session, url) for url in endpoints]
            return await asyncio.gather(*tasks)
    
    async def test_single_endpoint(self, session, url):
        async with session.get(url) as response:
            return {
                'url': url,
                'status': response.status,
                'response_time': response.headers.get('X-Response-Time'),
                'success': 200 <= response.status < 400
            }

# Verwendung
tester = AsyncAPITester()
results = await tester.test_endpoints([
    'https://api1.example.com',
    'https://api2.example.com', 
    'https://api3.example.com'
])
```

#### **Translation API**

```python
from env_config import APIConfig

class TranslationAPI:
    def __init__(self):
        self.base_url = APIConfig.LIBRETRANSLATE_BASE_URL
        self.api_key = APIConfig.LIBRETRANSLATE_API_KEY
    
    def translate_api_response(self, response_text: str) -> dict:
        # 1. Sprache erkennen
        detected = self.detect_language(response_text)
        
        # 2. Bei Bedarf übersetzen
        if detected['language'] == 'en':
            return self.translate_text(response_text, 'en', 'de')
        
        return {'translated': False, 'reason': 'Not English'}
```

### 📖 **Vollständige API-Dokumentation**

Siehe [`API_DOCS.md`](API_DOCS.md) für detaillierte API-Referenz mit:

- 🔧 Environment Setup & Konfiguration
- 🏥 Health Check API mit Code-Beispielen
- 🧪 API Testing Framework
- 🌐 Translation API Integration
- 📊 Performance Monitoring & Alerts
- 🔄 Scheduled Health Checks
- 🔐 Authentication Helpers
- 📈 Analytics & Reporting

---

## 🤝 Contributing

### 🎯 **Beitragen ist willkommen!**

Wir freuen uns über **jede Art von Beitrag**:

#### **🐛 Bug Reports**
```bash
# Issue Template verwenden:
# - Detaillierte Beschreibung
# - Reproduktionsschritte  
# - Environment-Info
# - Erwartetes vs. tatsächliches Verhalten
```

#### **✨ Feature Requests**
```bash
# Feature Request Template:
# - Use Case beschreiben
# - Lösungsvorschlag
# - Alternativen erwähnen
# - Mockups/Beispiele anhängen
```

#### **🔧 Pull Requests**

```bash
# Development Setup
git clone https://github.com/Watchkido/014_mini_postman.git
cd 014_mini_postman
git checkout -b feature/your-feature-name

# Änderungen machen
# ...

# Tests ausführen
pytest
flake8 .
black .

# Pull Request erstellen
git push origin feature/your-feature-name
```

#### **📋 Contribution Guidelines**

1. **🧪 Tests schreiben** für neue Features
2. **📚 Dokumentation aktualisieren**
3. **🎨 Code-Style** befolgen (PEP 8, Black)
4. **🔍 Type Hints** verwenden
5. **📝 Commit Messages** aussagekräftig gestalten

### 🏆 **Contributors**

<div align="center">

![Contributors](https://contrib.rocks/image?repo=Watchkido/014_mini_postman)

**Vielen Dank an alle Contributor! 🙏**

</div>

---

## 📄 License

### 📜 **MIT License**

```
MIT License

Copyright (c) 2025 Watchkido

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Support & Community

<div align="center">

### 🌟 **Star das Projekt auf GitHub!** 

[![GitHub stars](https://img.shields.io/github/stars/Watchkido/014_mini_postman?style=social)](https://github.com/Watchkido/014_mini_postman/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Watchkido/014_mini_postman?style=social)](https://github.com/Watchkido/014_mini_postman/network/members)
[![GitHub issues](https://img.shields.io/github/issues/Watchkido/014_mini_postman)](https://github.com/Watchkido/014_mini_postman/issues)

### 📬 **Kontakt & Support**

| Kanal | Link | Beschreibung |
|-------|------|--------------|
| 🐛 **Issues** | [GitHub Issues](https://github.com/Watchkido/014_mini_postman/issues) | Bug Reports & Feature Requests |
| 💬 **Discussions** | [GitHub Discussions](https://github.com/Watchkido/014_mini_postman/discussions) | Community Q&A |
| 📧 **E-Mail** | [watchkido@example.com](mailto:watchkido@example.com) | Direkte Unterstützung |
| 📖 **Wiki** | [GitHub Wiki](https://github.com/Watchkido/014_mini_postman/wiki) | Erweiterte Dokumentation |

</div>

---

<div align="center">

### 🎉 **Vielen Dank für die Nutzung von Mini Postman!**

**Entwickelt mit ❤️ von [Watchkido](https://github.com/Watchkido)**

*"Making API testing simple, powerful, and accessible for everyone"*

---

**⭐ Vergiss nicht, das Projekt zu sternen, wenn es dir gefällt! ⭐**

</div>