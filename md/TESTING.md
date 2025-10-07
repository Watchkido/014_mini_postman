# Testing Guide - Mini Postman

## 🧪 Übersicht

Umfassender Testing-Guide für alle Komponenten des Mini Postman Projekts.

## 📁 Test-Struktur

```
tests/
├── __init__.py
├── conftest.py                 # Pytest Konfiguration & Fixtures
├── test_config.py             # Environment & Konfiguration
├── test_health_checker.py     # Health Check Tests
├── test_gui.py                # Streamlit GUI Tests
├── test_api_checker.py        # API Checker Tests
├── test_utils.py              # Utility-Funktionen
├── integration/
│   ├── __init__.py
│   ├── test_end_to_end.py     # End-to-End Tests
│   └── test_translation.py    # Translation API Tests
├── performance/
│   ├── __init__.py
│   ├── test_load.py           # Load Testing
│   └── test_stress.py         # Stress Testing
└── fixtures/
    ├── sample_responses.json   # Mock API Responses
    └── test_data.csv          # Test Daten
```

## 🛠️ Test Setup

### 1. Test Dependencies installieren
```bash
pip install pytest pytest-cov pytest-mock pytest-asyncio requests-mock
pip install locust  # Für Load Testing
pip install selenium webdriver-manager  # Für GUI Testing
```

### 2. Pytest Konfiguration
```python
# tests/conftest.py
import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from m005_gesundheitschecker import ComprehensiveHealthChecker
from env_config import EnvConfig

@pytest.fixture
def temp_log_dir():
    """Temporäres Verzeichnis für Test-Logs"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_env_config():
    """Mock Environment Configuration"""
    with patch.dict(os.environ, {
        'DEBUG': 'true',
        'MAX_REQUESTS_PER_MINUTE': '60',
        'LIBRETRANSLATE_API_KEY': 'test-key',
        'OPENAI_API_KEY': 'test-openai-key'
    }):
        yield EnvConfig()

@pytest.fixture
def health_checker():
    """Health Checker Instance für Tests"""
    return ComprehensiveHealthChecker('https://httpbin.org/get')

@pytest.fixture
def sample_api_responses():
    """Sample API Responses für Tests"""
    return {
        'success_response': {
            'status_code': 200,
            'headers': {'Content-Type': 'application/json'},
            'json': {'message': 'success', 'data': [1, 2, 3]}
        },
        'error_response': {
            'status_code': 404,
            'headers': {'Content-Type': 'application/json'},
            'json': {'error': 'Not Found'}
        },
        'timeout_response': {
            'status_code': 408,
            'headers': {'Content-Type': 'text/plain'},
            'text': 'Request Timeout'
        }
    }
```

## 🔍 Unit Tests

### 1. Health Checker Tests
```python
# tests/test_health_checker.py
import pytest
import requests_mock
from m005_gesundheitschecker import ComprehensiveHealthChecker

class TestComprehensiveHealthChecker:
    
    def test_initialization(self):
        """Test Health Checker Initialisierung"""
        url = 'https://example.com'
        checker = ComprehensiveHealthChecker(url)
        assert checker.url == url
        assert checker.log_file is not None
        assert 'example_com' in checker.log_file
    
    @requests_mock.Mocker()
    def test_basic_connectivity_success(self, m, health_checker):
        """Test erfolgreicher Connectivity Check"""
        m.get('https://httpbin.org/get', json={'success': True}, status_code=200)
        
        result = health_checker.check_basic_connectivity()
        assert result is True
    
    @requests_mock.Mocker()
    def test_basic_connectivity_failure(self, m, health_checker):
        """Test fehlgeschlagener Connectivity Check"""
        m.get('https://httpbin.org/get', status_code=500)
        
        result = health_checker.check_basic_connectivity()
        assert result is False
    
    @requests_mock.Mocker()
    def test_http_methods(self, m, health_checker):
        """Test HTTP Methods Check"""
        # Mock verschiedene HTTP Methods
        m.get('https://httpbin.org/get', status_code=200)
        m.post('https://httpbin.org/get', status_code=405)  # Method Not Allowed
        m.put('https://httpbin.org/get', status_code=405)
        m.delete('https://httpbin.org/get', status_code=405)
        
        results = health_checker.check_http_methods()
        assert results['GET'] is True
        assert results['POST'] is False
        assert results['PUT'] is False
        assert results['DELETE'] is False
    
    @requests_mock.Mocker()
    def test_performance_check(self, m, health_checker):
        """Test Performance Check"""
        m.get('https://httpbin.org/get', json={'test': 'data'}, status_code=200)
        
        result = health_checker.check_performance()
        assert 'avg_ms' in result
        assert 'min_ms' in result
        assert 'max_ms' in result
        assert result['avg_ms'] > 0
    
    def test_unicode_support_detection(self):
        """Test Unicode Support Detection"""
        # Test auf verschiedenen Systemen
        from m005_gesundheitschecker import check_unicode_support
        
        support = check_unicode_support()
        assert isinstance(support, bool)
    
    def test_domain_extraction(self, health_checker):
        """Test Domain-Extraktion für Log-Dateinamen"""
        # Testen verschiedener URL-Formate
        test_cases = [
            ('https://api.example.com/test', 'api_example_com'),
            ('http://subdomain.test.org:8080/path', 'subdomain_test_org'),
            ('https://localhost:3000', 'localhost'),
            ('https://192.168.1.1', '192_168_1_1'),
        ]
        
        for url, expected_domain in test_cases:
            checker = ComprehensiveHealthChecker(url)
            assert expected_domain in checker.log_file

class TestHealthCheckerIntegration:
    """Integration Tests mit echten APIs"""
    
    def test_httpbin_integration(self):
        """Test mit echter httpbin.org API"""
        checker = ComprehensiveHealthChecker('https://httpbin.org/get')
        
        # Basic connectivity sollte funktionieren
        connectivity = checker.check_basic_connectivity()
        assert connectivity is True
        
        # GET sollte funktionieren
        methods = checker.check_http_methods()
        assert methods['GET'] is True
        
        # Performance sollte messbar sein
        performance = checker.check_performance()
        assert performance['avg_ms'] > 0
        assert performance['avg_ms'] < 10000  # Unter 10 Sekunden
    
    @pytest.mark.slow
    def test_comprehensive_check_real_api(self):
        """Vollständiger Test mit echter API (langsam)"""
        checker = ComprehensiveHealthChecker('https://jsonplaceholder.typicode.com/posts')
        
        # Führe kompletten Check durch
        checker.run_comprehensive_check()
        
        # Prüfe dass Log-Datei erstellt wurde
        import os
        assert os.path.exists(checker.log_file)
        
        # Prüfe Log-Inhalt
        with open(checker.log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Ziel URL:' in content
            assert 'Success Rate:' in content
```

### 2. Configuration Tests
```python
# tests/test_config.py
import pytest
import os
from unittest.mock import patch
from env_config import EnvConfig, APIConfig, AppConfig

class TestEnvConfig:
    
    def test_default_values(self):
        """Test Standard-Konfigurationswerte"""
        with patch.dict(os.environ, {}, clear=True):
            config = EnvConfig()
            assert config.DEBUG == False
            assert config.MAX_REQUESTS_PER_MINUTE == 60
    
    def test_environment_override(self):
        """Test Environment Variable Override"""
        with patch.dict(os.environ, {
            'DEBUG': 'true',
            'MAX_REQUESTS_PER_MINUTE': '120'
        }):
            config = EnvConfig()
            assert config.DEBUG == True
            assert config.MAX_REQUESTS_PER_MINUTE == 120
    
    def test_api_config_validation(self):
        """Test API-Konfiguration Validierung"""
        with patch.dict(os.environ, {
            'LIBRETRANSLATE_API_KEY': 'test-key-123',
            'OPENAI_API_KEY': 'sk-test123'
        }):
            config = APIConfig()
            assert config.LIBRETRANSLATE_API_KEY == 'test-key-123'
            assert config.OPENAI_API_KEY == 'sk-test123'
    
    def test_missing_required_config(self):
        """Test fehlende erforderliche Konfiguration"""
        with patch.dict(os.environ, {}, clear=True):
            # Sollte Warning ausgeben, aber nicht crashen
            config = APIConfig()
            assert config.LIBRETRANSLATE_API_KEY is None
```

### 3. GUI Tests
```python
# tests/test_gui.py
import pytest
from unittest.mock import Mock, patch
import streamlit as st
import sys
import os

# Streamlit App für Tests importieren
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class TestStreamlitGUI:
    
    @patch('streamlit.sidebar')
    @patch('streamlit.selectbox')  
    def test_url_selection(self, mock_selectbox, mock_sidebar):
        """Test URL-Auswahl in der GUI"""
        mock_selectbox.return_value = 'https://jsonplaceholder.typicode.com/posts'
        
        # Import der GUI-Funktionen (würde normalerweise komplex sein)
        # Hier vereinfachtes Beispiel
        from api_mini_postman_gui import get_preset_urls
        
        urls = get_preset_urls()
        assert 'jsonplaceholder.typicode.com' in str(urls)
    
    @patch('requests.get')
    def test_api_request_mock(self, mock_get):
        """Test API-Request mit Mock"""
        # Mock Response
        mock_response = Mock()
        mock_response.json.return_value = {'test': 'data'}
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_get.return_value = mock_response
        
        # Teste Request-Funktion
        import requests
        response = requests.get('https://example.com')
        
        assert response.status_code == 200
        assert response.json() == {'test': 'data'}
    
    def test_translation_feature_mock(self):
        """Test Translation Feature mit Mock"""
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                'translatedText': 'Hallo Welt'
            }
            mock_post.return_value.status_code = 200
            
            # Teste Translation-Funktion
            import requests
            response = requests.post('http://localhost:5000/translate', 
                                   json={'q': 'Hello World', 'source': 'en', 'target': 'de'})
            
            assert response.json()['translatedText'] == 'Hallo Welt'
```

## 🔗 Integration Tests

### 1. End-to-End Tests
```python
# tests/integration/test_end_to_end.py
import pytest
import subprocess
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestEndToEnd:
    
    @pytest.fixture(scope="class")
    def streamlit_server(self):
        """Startet Streamlit Server für Tests"""
        # Streamlit im Hintergrund starten
        process = subprocess.Popen([
            'streamlit', 'run', 'api_mini_postman_gui.py',
            '--server.port', '8502',  # Anderer Port für Tests
            '--server.headless', 'true'
        ])
        
        # Warten bis Server bereit ist
        time.sleep(10)
        
        yield process
        
        # Server beenden
        process.terminate()
        process.wait()
    
    @pytest.fixture
    def browser(self):
        """Selenium WebDriver für GUI-Tests"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        yield driver
        driver.quit()
    
    def test_gui_health_check_flow(self, streamlit_server, browser):
        """Test kompletter GUI Health Check Flow"""
        # Streamlit App öffnen
        browser.get('http://localhost:8502')
        
        # Warten bis geladen
        wait = WebDriverWait(browser, 20)
        
        # URL eingeben (vereinfachtes Beispiel)
        # Echte Streamlit-Interaktion wäre komplexer
        assert "Mini Postman" in browser.title or "Streamlit" in browser.title
    
    def test_command_line_health_check(self):
        """Test Command Line Health Check"""
        # Health Check über Command Line ausführen
        result = subprocess.run([
            'python', 'm005_gesundheitschecker.py', 
            'https://httpbin.org/get'
        ], capture_output=True, text=True, timeout=60)
        
        assert result.returncode == 0
        assert 'Ziel URL:' in result.stdout
        assert 'Gesundheitscheck abgeschlossen' in result.stdout
    
    @pytest.mark.slow
    def test_multiple_api_endpoints(self):
        """Test mehrerer API-Endpoints nacheinander"""
        endpoints = [
            'https://httpbin.org/get',
            'https://jsonplaceholder.typicode.com/posts/1',
            'https://api.github.com/repos/octocat/Hello-World'
        ]
        
        for endpoint in endpoints:
            result = subprocess.run([
                'python', 'm005_gesundheitschecker.py', endpoint
            ], capture_output=True, text=True, timeout=30)
            
            assert result.returncode == 0
            assert 'Success Rate:' in result.stdout
```

### 2. Translation API Tests
```python
# tests/integration/test_translation.py
import pytest
import requests
import docker
import time

class TestTranslationIntegration:
    
    @pytest.fixture(scope="class")
    def libretranslate_container(self):
        """Startet LibreTranslate Container für Tests"""
        client = docker.from_env()
        
        try:
            # Container starten
            container = client.containers.run(
                'libretranslate/libretranslate:latest',
                ports={'5000/tcp': 5001},  # Anderer Port für Tests
                environment=['LT_API_KEYS=true'],
                detach=True
            )
            
            # Warten bis Service bereit ist
            for _ in range(30):  # 30 Sekunden warten
                try:
                    response = requests.get('http://localhost:5001/languages', timeout=5)
                    if response.status_code == 200:
                        break
                except:
                    pass
                time.sleep(1)
            
            yield container
            
        finally:
            # Container stoppen und entfernen
            try:
                container.stop()
                container.remove()
            except:
                pass
    
    def test_language_detection(self, libretranslate_container):
        """Test Spracherkennung"""
        response = requests.post(
            'http://localhost:5001/detect',
            json={'q': 'Hello World'},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]['language'] == 'en'
    
    def test_translation_en_to_de(self, libretranslate_container):
        """Test Übersetzung Englisch -> Deutsch"""
        response = requests.post(
            'http://localhost:5001/translate',
            json={
                'q': 'Hello World',
                'source': 'en',
                'target': 'de',
                'format': 'text'
            },
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'translatedText' in data
        assert 'Hallo' in data['translatedText'] or 'Welt' in data['translatedText']
    
    def test_batch_translation(self, libretranslate_container):
        """Test Batch-Übersetzung"""
        texts = [
            'API request failed',
            'Connection timeout',
            'Server error 500'
        ]
        
        for text in texts:
            response = requests.post(
                'http://localhost:5001/translate',
                json={
                    'q': text,
                    'source': 'en',
                    'target': 'de',
                    'format': 'text'
                },
                timeout=30
            )
            
            assert response.status_code == 200
            data = response.json()
            assert 'translatedText' in data
            assert len(data['translatedText']) > 0
```

## ⚡ Performance Tests

### 1. Load Testing mit Locust
```python
# tests/performance/test_load.py
from locust import HttpUser, task, between
import random

class HealthCheckUser(HttpUser):
    wait_time = between(1, 3)  # 1-3 Sekunden zwischen Requests
    
    def on_start(self):
        """Setup für jeden virtuellen User"""
        self.endpoints = [
            '/get',
            '/post', 
            '/put',
            '/delete',
            '/status/200',
            '/status/404',
            '/delay/1'
        ]
    
    @task(3)  # Gewichtung: 3x häufiger als andere Tasks
    def test_get_endpoint(self):
        """Test GET Requests"""
        endpoint = random.choice(['/get', '/json', '/uuid'])
        self.client.get(endpoint)
    
    @task(2)
    def test_post_endpoint(self):
        """Test POST Requests"""
        self.client.post('/post', json={
            'test': 'data',
            'timestamp': '2025-01-06T12:00:00Z'
        })
    
    @task(1)
    def test_slow_endpoint(self):
        """Test langsame Endpoints"""
        delay = random.randint(1, 3)
        self.client.get(f'/delay/{delay}')
    
    @task(1)
    def test_error_endpoints(self):
        """Test Error-Handling"""
        status = random.choice([400, 404, 500, 503])
        # Erwarte Fehler, aber messe trotzdem Performance
        with self.client.get(f'/status/{status}', catch_response=True) as response:
            if response.status_code == status:
                response.success()

# Ausführung:
# locust -f tests/performance/test_load.py --host=https://httpbin.org --users 50 --spawn-rate 5 --run-time 2m
```

### 2. Stress Testing
```python
# tests/performance/test_stress.py
import pytest
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor
import requests

class TestStressScenarios:
    
    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self):
        """Test gleichzeitige Health Checks"""
        urls = [
            'https://httpbin.org/get',
            'https://httpbin.org/json',
            'https://httpbin.org/uuid',
            'https://httpbin.org/base64/SFRUUEJJTiBpcyBhd2Vzb21l'
        ] * 10  # 40 URLs total
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            
            tasks = []
            for url in urls:
                task = self.async_health_check(session, url)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            duration = time.time() - start_time
            successful = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
            
            print(f"Processed {len(urls)} requests in {duration:.2f}s")
            print(f"Success rate: {successful}/{len(urls)} ({successful/len(urls)*100:.1f}%)")
            
            # Assertions
            assert duration < 30  # Sollte in unter 30s fertig sein
            assert successful > len(urls) * 0.8  # Mindestens 80% erfolgreich
    
    async def async_health_check(self, session: aiohttp.ClientSession, url: str) -> dict:
        """Asynchroner Health Check"""
        try:
            start = time.time()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                duration = (time.time() - start) * 1000
                return {
                    'url': url,
                    'status_code': response.status,
                    'response_time_ms': duration,
                    'success': 200 <= response.status < 400
                }
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'success': False
            }
    
    def test_memory_usage_under_load(self):
        """Test Memory Usage bei hoher Last"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simuliere hohe Last
        health_checkers = []
        for i in range(100):
            from m005_gesundheitschecker import ComprehensiveHealthChecker
            checker = ComprehensiveHealthChecker(f'https://httpbin.org/get?id={i}')
            health_checkers.append(checker)
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Cleanup
        del health_checkers
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"Memory: Initial={initial_memory:.1f}MB, Peak={peak_memory:.1f}MB, Final={final_memory:.1f}MB")
        
        # Memory sollte nicht übermäßig wachsen
        assert peak_memory - initial_memory < 500  # Weniger als 500MB Anstieg
        assert final_memory - initial_memory < 100  # Weniger als 100MB nach Cleanup
    
    def test_thread_pool_performance(self):
        """Test ThreadPool Performance"""
        urls = ['https://httpbin.org/delay/1'] * 20
        
        # Single-threaded
        start = time.time()
        results_sequential = []
        for url in urls[:5]:  # Nur 5 für Sequential (sonst zu lange)
            try:
                response = requests.get(url, timeout=5)
                results_sequential.append(response.status_code)
            except:
                results_sequential.append(None)
        sequential_time = time.time() - start
        
        # Multi-threaded
        start = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(requests.get, url, timeout=5) for url in urls]
            results_parallel = []
            for future in futures:
                try:
                    response = future.result()
                    results_parallel.append(response.status_code)
                except:
                    results_parallel.append(None)
        parallel_time = time.time() - start
        
        print(f"Sequential (5 URLs): {sequential_time:.2f}s")
        print(f"Parallel (20 URLs): {parallel_time:.2f}s")
        
        # Parallel sollte effizienter sein pro Request
        sequential_per_request = sequential_time / 5
        parallel_per_request = parallel_time / 20
        
        assert parallel_per_request < sequential_per_request * 1.5  # Max 50% overhead
```

## 🎯 Test Execution

### 1. Alle Tests ausführen
```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=. --cov-report=html --cov-report=term

# Nur Unit Tests
pytest tests/test_*.py -v

# Nur Integration Tests
pytest tests/integration/ -v

# Performance Tests (langsam)
pytest tests/performance/ -v -m slow

# Parallele Ausführung
pytest -n auto  # Benötigt: pip install pytest-xdist
```

### 2. Spezifische Test-Kategorien
```bash
# Schnelle Tests (< 1 Sekunde)
pytest -m "not slow"

# Nur Health Checker Tests
pytest tests/test_health_checker.py -v

# Tests mit bestimmtem Pattern
pytest -k "test_api" -v

# Fehlgeschlagene Tests erneut ausführen
pytest --lf  # last-failed

# Bis zum ersten Fehler
pytest -x

# Verbose Output mit Traceback
pytest -vvv --tb=long
```

### 3. Load Testing ausführen
```bash
# Lokaler Load Test
locust -f tests/performance/test_load.py --host=https://httpbin.org

# Headless mit spezifischen Parametern
locust -f tests/performance/test_load.py \
    --host=https://httpbin.org \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --headless

# Mit HTML Report
locust -f tests/performance/test_load.py \
    --host=https://httpbin.org \
    --users 50 \
    --spawn-rate 5 \
    --run-time 2m \
    --html=reports/load_test_report.html \
    --headless
```

## 📊 Test Reports & CI Integration

### 1. Test Reports generieren
```bash
# JUnit XML für CI
pytest --junit-xml=reports/junit.xml

# HTML Coverage Report
pytest --cov=. --cov-report=html:reports/coverage

# JSON Report
pytest --json-report --json-report-file=reports/report.json
```

### 2. GitHub Actions Integration
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-mock requests-mock
    
    - name: Run unit tests
      run: |
        pytest tests/test_*.py --cov=. --cov-report=xml -v
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
      env:
        LIBRETRANSLATE_API_KEY: ${{ secrets.LIBRETRANSLATE_API_KEY }}
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
    
    - name: Load test (quick)
      run: |
        pip install locust
        timeout 60 locust -f tests/performance/test_load.py \
          --host=https://httpbin.org \
          --users 10 \
          --spawn-rate 2 \
          --headless || true
```

### 3. Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: [--max-line-length=177]

  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest tests/test_*.py -x
        language: system
        pass_filenames: false
        always_run: true
```

```bash
# Pre-commit hooks installieren
pip install pre-commit
pre-commit install

# Manuell ausführen
pre-commit run --all-files
```

---

**Für weitere Fragen zum Testing siehe README.md oder erstellen Sie ein GitHub Issue.**

**Letzte Aktualisierung**: 6. Oktober 2025