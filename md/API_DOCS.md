# API Documentation - Mini Postman

## 📚 Übersicht

Mini Postman bietet sowohl eine GUI als auch programmierbare APIs für verschiedene Testing-Szenarien.

## 🔧 Environment Setup

### 1. Environment-Variablen laden
```python
from env_config import APIConfig, AppConfig, NotificationConfig

# API Keys abrufen
translate_key = APIConfig.LIBRETRANSLATE_API_KEY
openai_key = APIConfig.OPENAI_API_KEY

# App-Konfiguration
debug_mode = AppConfig.DEBUG
max_requests = AppConfig.MAX_REQUESTS_PER_MINUTE
```

### 2. Konfiguration validieren
```python
from env_config import validate_required_config, print_config_summary

# Konfiguration prüfen
validate_required_config()

# Übersicht anzeigen
print_config_summary()
```

## 🌐 Health Check API

### Grundlegende Verwendung
```python
from m005_gesundheitschecker import ComprehensiveHealthChecker

# Health Check erstellen
checker = ComprehensiveHealthChecker("https://api.example.com")

# Check durchführen
checker.run_comprehensive_check()

# Log-Datei: m005_api_example_com_20251006_143544.log
```

### Programmierbare API
```python
import requests
from datetime import datetime
import time

class HealthCheckAPI:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mini-Postman-API/1.0',
            'Authorization': f'Bearer {api_key}' if api_key else None
        }
    
    def connectivity_check(self) -> dict:
        """Basis-Connectivity Test"""
        try:
            start_time = time.time()
            response = requests.get(
                self.base_url, 
                headers=self.headers,
                timeout=10
            )
            response_time = (time.time() - start_time) * 1000
            
            return {
                'success': True,
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def performance_test(self, iterations: int = 3) -> dict:
        """Performance Benchmark"""
        times = []
        for i in range(iterations):
            start = time.time()
            try:
                response = requests.get(self.base_url, headers=self.headers)
                times.append((time.time() - start) * 1000)
            except:
                continue
            time.sleep(1)  # Pause zwischen Tests
        
        if times:
            return {
                'avg_ms': round(sum(times) / len(times), 2),
                'min_ms': round(min(times), 2),
                'max_ms': round(max(times), 2),
                'iterations': len(times),
                'rating': 'EXCELLENT' if sum(times)/len(times) < 200 else 'GOOD'
            }
        return {'error': 'Alle Performance-Tests fehlgeschlagen'}

# Verwendung
api = HealthCheckAPI('https://jsonplaceholder.typicode.com/posts')
connectivity = api.connectivity_check()
performance = api.performance_test()
```

## 🧪 API Testing Framework

### Test Suite erstellen
```python
from m004_api_checker import APIChecker

# Test-Endpoints definieren
endpoints = [
    {'url': 'https://api.example.com/users', 'method': 'GET'},
    {'url': 'https://api.example.com/posts', 'method': 'POST', 'data': {'title': 'Test'}},
]

# Checker initialisieren
checker = APIChecker(endpoints)

# Alle Tests ausführen
results = checker.run_all_checks()

# Ergebnisse analysieren
for result in results:
    print(f"{result['url']}: {result['status_code']} ({result['response_time_ms']}ms)")
```

### Batch Testing
```python
import asyncio
import aiohttp
from typing import List, Dict

class AsyncAPITester:
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def test_endpoint(self, session: aiohttp.ClientSession, endpoint: Dict) -> Dict:
        """Asynchroner Endpoint-Test"""
        async with self.semaphore:
            try:
                start_time = time.time()
                async with session.request(
                    endpoint['method'],
                    endpoint['url'],
                    json=endpoint.get('data'),
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    return {
                        'url': endpoint['url'],
                        'method': endpoint['method'],
                        'status_code': response.status,
                        'response_time_ms': round(response_time, 2),
                        'success': 200 <= response.status < 400
                    }
            except Exception as e:
                return {
                    'url': endpoint['url'],
                    'method': endpoint['method'],
                    'error': str(e),
                    'success': False
                }
    
    async def run_batch_test(self, endpoints: List[Dict]) -> List[Dict]:
        """Führt Batch-Tests asynchron aus"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.test_endpoint(session, ep) for ep in endpoints]
            return await asyncio.gather(*tasks)

# Verwendung
async def main():
    tester = AsyncAPITester(max_concurrent=10)
    endpoints = [
        {'url': 'https://jsonplaceholder.typicode.com/posts/1', 'method': 'GET'},
        {'url': 'https://jsonplaceholder.typicode.com/posts/2', 'method': 'GET'},
        {'url': 'https://jsonplaceholder.typicode.com/posts/3', 'method': 'GET'},
    ]
    
    results = await tester.run_batch_test(endpoints)
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['url']}: {result.get('status_code', 'ERROR')}")

# asyncio.run(main())
```

## 🌍 Translation API

### LibreTranslate Integration
```python
import requests
from env_config import APIConfig

class TranslationAPI:
    def __init__(self):
        self.base_url = APIConfig.LIBRETRANSLATE_BASE_URL
        self.api_key = APIConfig.LIBRETRANSLATE_API_KEY
    
    def detect_language(self, text: str) -> dict:
        """Spracherkennung"""
        response = requests.post(
            f"{self.base_url}/detect",
            json={'q': text, 'api_key': self.api_key},
            timeout=30
        )
        return response.json()
    
    def translate(self, text: str, source: str = 'en', target: str = 'de') -> dict:
        """Text übersetzen"""
        response = requests.post(
            f"{self.base_url}/translate",
            json={
                'q': text,
                'source': source,
                'target': target,
                'format': 'text',
                'api_key': self.api_key
            },
            timeout=60
        )
        return response.json()

# Verwendung
translator = TranslationAPI()

# API Response übersetzen
api_response = '{"error": "Invalid API key", "code": 401}'
detected = translator.detect_language(api_response)

if detected[0]['language'] == 'en':
    translated = translator.translate(api_response)
    print(f"Original: {api_response}")
    print(f"Deutsch: {translated['translatedText']}")
```

## 📊 Monitoring & Alerts

### Performance Monitoring
```python
from env_config import AppConfig, NotificationConfig
import smtplib
from email.mime.text import MIMEText

class PerformanceMonitor:
    def __init__(self):
        self.warning_threshold = AppConfig.PERFORMANCE_WARNING_MS
        self.error_threshold = AppConfig.PERFORMANCE_ERROR_MS
    
    def check_performance(self, response_time_ms: float, url: str):
        """Performance-Check mit Alerting"""
        if response_time_ms > self.error_threshold:
            self.send_alert(f"CRITICAL: {url} - {response_time_ms}ms", 'error')
        elif response_time_ms > self.warning_threshold:
            self.send_alert(f"WARNING: {url} - {response_time_ms}ms", 'warning')
    
    def send_alert(self, message: str, level: str):
        """Benachrichtigung senden"""
        if NotificationConfig.is_email_configured():
            self.send_email_alert(message, level)
        if NotificationConfig.is_slack_configured():
            self.send_slack_alert(message, level)
    
    def send_email_alert(self, message: str, level: str):
        """E-Mail Benachrichtigung"""
        try:
            msg = MIMEText(message)
            msg['Subject'] = f'Mini Postman Alert - {level.upper()}'
            msg['From'] = NotificationConfig.SMTP_USERNAME
            msg['To'] = 'admin@example.com'
            
            with smtplib.SMTP(NotificationConfig.SMTP_HOST, NotificationConfig.SMTP_PORT) as server:
                server.starttls()
                server.login(NotificationConfig.SMTP_USERNAME, NotificationConfig.SMTP_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            print(f"E-Mail Alert failed: {e}")
    
    def send_slack_alert(self, message: str, level: str):
        """Slack Benachrichtigung"""
        emoji = "🚨" if level == 'error' else "⚠️"
        payload = {
            'text': f"{emoji} {message}",
            'username': 'Mini Postman',
            'icon_emoji': ':robot_face:'
        }
        
        try:
            requests.post(NotificationConfig.SLACK_WEBHOOK_URL, json=payload)
        except Exception as e:
            print(f"Slack Alert failed: {e}")

# Verwendung
monitor = PerformanceMonitor()

# In Health Check integrieren
response_time = 1500  # ms
monitor.check_performance(response_time, 'https://api.example.com')
```

## 🔄 Scheduled Health Checks

### Cron-ähnliche Scheduler
```python
import schedule
import time
import threading
from datetime import datetime

class ScheduledHealthCheck:
    def __init__(self):
        self.running = False
        self.thread = None
    
    def health_check_job(self, url: str):
        """Geplanter Health Check"""
        print(f"[{datetime.now()}] Running scheduled health check for {url}")
        
        checker = ComprehensiveHealthChecker(url)
        checker.run_comprehensive_check()
        
        # Optional: Ergebnisse an Monitoring senden
        monitor = PerformanceMonitor()
        # monitor.send_summary_report()
    
    def start_scheduler(self, urls: List[str], interval_minutes: int = 15):
        """Startet geplante Health Checks"""
        for url in urls:
            schedule.every(interval_minutes).minutes.do(self.health_check_job, url)
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler)
        self.thread.daemon = True
        self.thread.start()
        
        print(f"✅ Scheduler gestartet - Health Checks alle {interval_minutes} Minuten")
    
    def _run_scheduler(self):
        """Scheduler-Loop"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop_scheduler(self):
        """Stoppt den Scheduler"""
        self.running = False
        schedule.clear()
        print("🛑 Scheduler gestoppt")

# Verwendung
scheduler = ScheduledHealthCheck()

# URLs für regelmäßige Checks
urls = [
    'https://api.example.com',
    'https://jsonplaceholder.typicode.com/posts',
    'https://httpbin.org/get'
]

# Alle 15 Minuten prüfen
scheduler.start_scheduler(urls, interval_minutes=15)

# Läuft im Hintergrund...
# scheduler.stop_scheduler()  # Zum Stoppen
```

## 🔐 Authentication Helpers

### API-Key Management
```python
from cryptography.fernet import Fernet
import base64
import os

class SecureAPIKeyManager:
    def __init__(self):
        self.encryption_key = self._get_or_create_key()
        self.cipher = Fernet(self.encryption_key)
    
    def _get_or_create_key(self) -> bytes:
        """Erstellt oder lädt Verschlüsselungsschlüssel"""
        key_file = '.crypto_key'
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Nur Owner kann lesen
            return key
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Verschlüsselt API-Key"""
        encrypted = self.cipher.encrypt(api_key.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Entschlüsselt API-Key"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_key.encode())
        return self.cipher.decrypt(encrypted_bytes).decode()

# Verwendung
key_manager = SecureAPIKeyManager()

# API-Key verschlüsseln (einmalig)
original_key = "sk-1234567890abcdef"
encrypted = key_manager.encrypt_api_key(original_key)
print(f"Encrypted: {encrypted}")

# API-Key zur Laufzeit entschlüsseln
decrypted = key_manager.decrypt_api_key(encrypted)
print(f"Decrypted: {decrypted}")
```

## 📈 Analytics & Reporting

### Test Results Analytics
```python
import json
from collections import defaultdict
from datetime import datetime, timedelta

class HealthCheckAnalytics:
    def __init__(self, log_directory: str = './'):
        self.log_directory = log_directory
    
    def parse_log_files(self, days_back: int = 7) -> List[Dict]:
        """Parst Log-Dateien der letzten Tage"""
        results = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Log-Dateien finden und parsen
        import glob
        log_files = glob.glob(f"{self.log_directory}/m005_*.log")
        
        for log_file in log_files:
            # Datum aus Dateiname extrahieren
            # m005_example_com_20251006_143544.log
            try:
                parts = log_file.split('_')
                date_str = parts[-2]  # 20251006
                time_str = parts[-1].replace('.log', '')  # 143544
                
                log_date = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                
                if log_date >= cutoff_date:
                    results.append(self._parse_single_log(log_file))
            except:
                continue
        
        return results
    
    def _parse_single_log(self, log_file: str) -> Dict:
        """Parst eine einzelne Log-Datei"""
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # URL extrahieren
        url_line = [line for line in content.split('\n') if 'Ziel URL:' in line]
        url = url_line[0].split('Ziel URL: ')[1] if url_line else 'Unknown'
        
        # Success Rate extrahieren
        success_lines = [line for line in content.split('\n') if 'Success Rate:' in line]
        success_rate = 0
        if success_lines:
            rate_str = success_lines[0].split('Success Rate: ')[1].split('%')[0]
            success_rate = float(rate_str)
        
        return {
            'file': log_file,
            'url': url,
            'success_rate': success_rate,
            'timestamp': log_file.split('_')[-2] + '_' + log_file.split('_')[-1].replace('.log', '')
        }
    
    def generate_report(self) -> Dict:
        """Generiert Analytics-Report"""
        results = self.parse_log_files()
        
        # Gruppiere nach URL
        url_stats = defaultdict(list)
        for result in results:
            url_stats[result['url']].append(result['success_rate'])
        
        # Statistiken berechnen
        report = {
            'total_checks': len(results),
            'unique_urls': len(url_stats),
            'url_statistics': {}
        }
        
        for url, rates in url_stats.items():
            report['url_statistics'][url] = {
                'checks_count': len(rates),
                'avg_success_rate': round(sum(rates) / len(rates), 2),
                'min_success_rate': min(rates),
                'max_success_rate': max(rates),
                'reliability': 'HIGH' if sum(rates) / len(rates) >= 95 else 'MEDIUM' if sum(rates) / len(rates) >= 80 else 'LOW'
            }
        
        return report

# Verwendung
analytics = HealthCheckAnalytics()
report = analytics.generate_report()

print(json.dumps(report, indent=2, ensure_ascii=False))
```

---

**Diese API-Dokumentation wird kontinuierlich erweitert. Für spezifische Fragen siehe README.md oder erstellen Sie ein GitHub Issue.**

**Letzte Aktualisierung**: 6. Oktober 2025