import requests
import time
import os
import argparse
from datetime import datetime
import psutil
import json
import sys
from urllib.parse import urlparse
from env_config import APIConfig, DatabaseConfig

# Die Klasse lädt automatisch aus .env
api_key = APIConfig.LIBRETRANSLATE_API_KEY  # "abc123xyz789_ihr_echter_key"
db_pass = DatabaseConfig.PASSWORD  

def check_unicode_support():
    """Prüft, ob die Konsole Unicode-Zeichen unterstützt"""
    try:
        # Teste, ob ein einfaches Unicode-Zeichen ausgegeben werden kann
        sys.stdout.write("✓")
        sys.stdout.flush()
        return True
    except UnicodeEncodeError:
        return False

def get_icon(unicode_char, fallback_char):
    """Gibt Unicode-Zeichen zurück, falls unterstützt, sonst Fallback"""
    if hasattr(get_icon, '_unicode_supported'):
        return unicode_char if get_icon._unicode_supported else fallback_char
    
    get_icon._unicode_supported = check_unicode_support()
    return unicode_char if get_icon._unicode_supported else fallback_char

def log_message(log_file, message):
    """Schreibt eine Nachricht in die angegebene Logdatei."""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    except IOError as e:
        print(f"Fehler beim Schreiben in die Logdatei: {e}")

def print_and_log(message, log_file=None):
    """Gibt eine Nachricht sowohl auf der Konsole als auch in der Log-Datei aus."""
    print(message)
    if log_file:
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{message}\n")
        except IOError as e:
            print(f"Fehler beim Schreiben in die Logdatei: {e}")

class ComprehensiveHealthChecker:
    def __init__(self, target_url):
        self.target_url = target_url
        
        # Extrahiere Domain aus URL für Dateiname
        parsed_url = urlparse(target_url)
        domain = parsed_url.netloc.replace(':', '_').replace('.', '_')  # Ersetze ungültige Dateinamen-Zeichen
        
        self.log_file = f"m005_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.alert_threshold_ms = 1000
        
        # Initialisiere Logdatei
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"{get_icon('🏥', '[HEALTH]')} COMPREHENSIVE SINGLE URL HEALTH CHECK\n")
                f.write("=" * 60 + "\n")
                f.write(f"Ziel URL: {target_url}\n")
                f.write(f"Gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
        except IOError as e:
            print(f"Fehler beim Erstellen der Logdatei: {e}")

    def run_comprehensive_check(self):
        """Führt einen umfassenden Health Check für die Ziel-URL durch"""
        print_and_log(f"{get_icon('🏥', '[HEALTH]')} STARTE UMFASSENDEN HEALTH CHECK FÜR: {self.target_url}", self.log_file)
        print_and_log("=" * 70, self.log_file)
        
        results = []
        
        # 1. Basis Connectivity Check
        results.append(self._check_connectivity())
        
        # 2. HTTP Methoden Tests
        results.extend(self._check_http_methods())
        
        # 3. Performance Tests
        results.extend(self._check_performance())
        
        # 4. Content Validation
        results.extend(self._check_content())
        
        # 5. System Resources während des Checks
        results.append(self._check_system_resources())
        
        # Generiere Report
        self._generate_comprehensive_report(results)

    def _check_connectivity(self):
        """Prüft Basis-Connectivity"""
        print_and_log(f"\n{get_icon('🔗', '[CONN]')} BASIS CONNECTIVITY CHECK", self.log_file)
        print_and_log("• Prüft, ob die Webseite überhaupt erreichbar ist", self.log_file)
        print_and_log("• Misst die Antwortzeit für einen einfachen GET-Request", self.log_file)
        print_and_log("-" * 40, self.log_file)
        
        try:
            start_time = time.time()
            response = requests.get(self.target_url, timeout=10, allow_redirects=True)
            response_time = (time.time() - start_time) * 1000
            
            result = {
                'category': 'Connectivity',
                'test': 'Basic HTTP GET',
                'success': True,
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'final_url': response.url,  # Nach Redirects
                'redirected': response.history != [],
                'error': None
            }
            
            status_icon = get_icon("✅", "[OK]") if result['success'] else get_icon("❌", "[FAIL]")
            status_text = "(Erfolg - Webseite antwortet)" if result['status_code'] == 200 else f"(HTTP {result['status_code']})"
            print_and_log(f"{status_icon} Basic GET | Status: {result['status_code']} {status_text} | Time: {result['response_time_ms']}ms", self.log_file)
            if result['redirected']:
                print_and_log(f"   ↳ Umgeleitet zu: {result['final_url']}", self.log_file)
                
        except Exception as e:
            result = {
                'category': 'Connectivity',
                'test': 'Basic HTTP GET',
                'success': False,
                'status_code': None,
                'response_time_ms': None,
                'error': str(e)
            }
            print_and_log(f"{get_icon('❌', '[FAIL]')} Basic GET | Error: {result['error']}", self.log_file)
        
        return result

    def _check_http_methods(self):
        """Testet verschiedene HTTP Methoden"""
        print_and_log(f"\n{get_icon('🌐', '[HTTP]')} HTTP METHODEN CHECK", self.log_file)
        print_and_log("• Testet verschiedene Arten von HTTP-Anfragen (GET, HEAD, OPTIONS)", self.log_file)
        print_and_log("• Prüft, welche Server-Software verwendet wird", self.log_file)
        print_and_log("-" * 40, self.log_file)
        
        methods = ['GET', 'HEAD', 'OPTIONS']
        results = []
        
        for method in methods:
            try:
                start_time = time.time()
                response = requests.request(method, self.target_url, timeout=10)
                response_time = (time.time() - start_time) * 1000
                
                # Erfolg definieren (2xx/3xx Status Codes)
                success = 200 <= response.status_code < 400
                
                result = {
                    'category': 'HTTP Methods',
                    'test': f'{method} Request',
                    'success': success,
                    'status_code': response.status_code,
                    'response_time_ms': round(response_time, 2),
                    'headers': dict(response.headers),
                    'error': None
                }
                
                status_icon = get_icon("✅", "[OK]") if success else get_icon("⚠️", "[WARN]")
                method_explanation = {
                    'GET': '(Daten abrufen)',
                    'HEAD': '(nur Header abrufen)',
                    'OPTIONS': '(verfügbare Methoden prüfen)'
                }
                print_and_log(f"{status_icon} {method:6} {method_explanation.get(method, '')} | Status: {result['status_code']:3} | Time: {result['response_time_ms']:6}ms", self.log_file)
                
                # Zeige wichtige Header
                if 'server' in response.headers:
                    print_and_log(f"   Server-Software: {response.headers['server']}", self.log_file)
                
            except Exception as e:
                result = {
                    'category': 'HTTP Methods',
                    'test': f'{method} Request',
                    'success': False,
                    'status_code': None,
                    'response_time_ms': None,
                    'error': str(e)
                }
                print_and_log(f"{get_icon('❌', '[FAIL]')} {method:6} | Error: {result['error']}", self.log_file)
            
            results.append(result)
            time.sleep(0.5)  # Kurze Pause zwischen Requests
        
        return results

    def _check_performance(self):
        """Führt Performance-Tests durch"""
        print_and_log(f"\n{get_icon('⚡', '[PERF]')} PERFORMANCE CHECK", self.log_file)
        print_and_log("• Führt mehrere Anfragen durch, um die Geschwindigkeit zu messen", self.log_file)
        print_and_log("• Berechnet Durchschnittswerte für eine zuverlässige Performance-Bewertung", self.log_file)
        print_and_log("-" * 40, self.log_file)
        
        results = []
        response_times = []
        
        # Mehrere Requests für Durchschnittsberechnung
        for i in range(3):
            try:
                start_time = time.time()
                response = requests.get(self.target_url, timeout=10)
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
                
                result = {
                    'category': 'Performance',
                    'test': f'Request #{i+1}',
                    'success': True,
                    'status_code': response.status_code,
                    'response_time_ms': round(response_time, 2),
                    'error': None
                }
                
                status_icon = get_icon("✅", "[OK]") if response_time < self.alert_threshold_ms else get_icon("⚠️", "[WARN]")
                if response_time > 1000:
                    speed_indicator = get_icon("🐌", "[SLOW]")
                    speed_text = "(langsam - über 1s)"
                elif response_time < 200:
                    speed_indicator = get_icon("🚀", "[FAST]")
                    speed_text = "(sehr schnell - unter 200ms)"
                else:
                    speed_indicator = get_icon("⚡", "[MED]")
                    speed_text = "(normale Geschwindigkeit)"
                print_and_log(f"{status_icon} Request {i+1} | {speed_indicator} {result['response_time_ms']:6}ms {speed_text}", self.log_file)
                
                results.append(result)
                time.sleep(1)  # Pause zwischen Performance-Tests
                
            except Exception as e:
                result = {
                    'category': 'Performance',
                    'test': f'Request #{i+1}',
                    'success': False,
                    'status_code': None,
                    'response_time_ms': None,
                    'error': str(e)
                }
                print_and_log(f"{get_icon('❌', '[FAIL]')} Request {i+1} | Error: {result['error']}", self.log_file)
                results.append(result)
        
        # Performance-Statistiken
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            print_and_log(f"\n{get_icon('📊', '[STATS]')} Performance Statistics:", self.log_file)
            print_and_log(f"   Avg: {avg_time:.2f}ms | Min: {min_time:.2f}ms | Max: {max_time:.2f}ms", self.log_file)
            
            # Performance-Bewertung
            if avg_time < 200:
                rating = f"EXCELLENT {get_icon('🏆', '[BEST]')}"
            elif avg_time < 500:
                rating = f"GOOD {get_icon('👍', '[GOOD]')}"
            elif avg_time < 1000:
                rating = f"AVERAGE {get_icon('⚠️', '[WARN]')}"
            else:
                rating = f"POOR {get_icon('🐌', '[SLOW]')}"
                
            print_and_log(f"   Rating: {rating}", self.log_file)
        
        return results

    def _check_content(self):
        """Validiert Content und Response"""
        print_and_log(f"\n{get_icon('📄', '[CONTENT]')} CONTENT VALIDATION", self.log_file)
        print_and_log("• Prüft den Inhaltstyp der Antwort (z.B. JSON, HTML, Text)", self.log_file)
        print_and_log("• Validiert die Datenstruktur und Größe des empfangenen Inhalts", self.log_file)
        print_and_log("-" * 40, self.log_file)
        
        results = []
        
        try:
            response = requests.get(self.target_url, timeout=10)
            
            # Content-Type Validation
            content_type = response.headers.get('content-type', 'unknown')
            content_check = {
                'category': 'Content',
                'test': 'Content-Type Header',
                'success': True,
                'details': content_type,
                'error': None
            }
            content_explanation = "(JSON-Daten)" if 'json' in content_type else "(HTML-Seite)" if 'html' in content_type else "(Textdaten)"
            print_and_log(f"{get_icon('✅', '[OK]')} Content-Type: {content_type} {content_explanation}", self.log_file)
            results.append(content_check)
            
            # Content Length
            content_length = len(response.content)
            length_check = {
                'category': 'Content', 
                'test': 'Content Length',
                'success': content_length > 0,
                'details': f"{content_length} bytes",
                'error': None
            }
            if content_length > 10000:
                size_indicator = get_icon("📦", "[BIG]")
                size_text = "(große Datenmenge)"
            else:
                size_indicator = get_icon("📄", "[SMALL]")
                size_text = "(kompakte Datenmenge)"
            print_and_log(f"{get_icon('✅', '[OK]')} Content Size: {size_indicator} {content_length:,} bytes {size_text}", self.log_file)
            results.append(length_check)
            
            # JSON Validation (falls applicable)
            if 'application/json' in content_type:
                try:
                    json_data = response.json()
                    json_check = {
                        'category': 'Content',
                        'test': 'JSON Validity',
                        'success': True,
                        'details': f"Valid JSON with {len(json_data) if isinstance(json_data, list) else len(json_data.keys())} elements",
                        'error': None
                    }
                    element_count = len(json_data) if isinstance(json_data, list) else len(json_data.keys())
                    print_and_log(f"{get_icon('✅', '[OK]')} JSON: Gültiges Format ({element_count} Datensätze/Felder)", self.log_file)
                    results.append(json_check)
                except:
                    json_check = {
                        'category': 'Content',
                        'test': 'JSON Validity', 
                        'success': False,
                        'details': 'Invalid JSON format',
                        'error': 'JSON parsing failed'
                    }
                    print_and_log(f"{get_icon('❌', '[FAIL]')} JSON: Ungültiges Format (Daten sind beschädigt)", self.log_file)
                    results.append(json_check)
                    
        except Exception as e:
            error_check = {
                'category': 'Content',
                'test': 'Content Analysis',
                'success': False,
                'details': None,
                'error': str(e)
            }
            print_and_log(f"{get_icon('❌', '[FAIL]')} Content Analysis: {error_check['error']}", self.log_file)
            results.append(error_check)
        
        return results

    def _check_system_resources(self):
        """Prüft System-Ressourcen während des Checks"""
        print_and_log(f"\n{get_icon('💻', '[SYSTEM]')} SYSTEM RESOURCES", self.log_file)
        print_and_log("• Überwacht die Systembelastung während der Tests", self.log_file)
        print_and_log("• Stellt sicher, dass genügend CPU, RAM und Speicherplatz verfügbar sind", self.log_file)
        print_and_log("-" * 40, self.log_file)
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            result = {
                'category': 'System',
                'test': 'Resource Usage',
                'success': cpu_percent < 90 and memory.percent < 85,
                'details': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_free_gb': round(disk.free / (1024**3), 1)
                },
                'error': None
            }
            
            cpu_status = "(normal)" if cpu_percent < 50 else "(hoch)" if cpu_percent < 80 else "(sehr hoch)"
            memory_status = "(ausreichend)" if memory.percent < 70 else "(knapp)" if memory.percent < 85 else "(kritisch)"
            disk_status = "(viel Platz)" if result['details']['disk_free_gb'] > 100 else "(wenig Platz)" if result['details']['disk_free_gb'] > 10 else "(kritisch wenig)"
            
            print_and_log(f"{get_icon('✅', '[OK]')} CPU-Auslastung: {cpu_percent}% {cpu_status}", self.log_file)
            print_and_log(f"{get_icon('✅', '[OK]')} Arbeitsspeicher: {memory.percent}% belegt {memory_status}", self.log_file)
            print_and_log(f"{get_icon('✅', '[OK]')} Freier Speicherplatz: {result['details']['disk_free_gb']} GB {disk_status}", self.log_file)
            
        except Exception as e:
            result = {
                'category': 'System',
                'test': 'Resource Usage',
                'success': False,
                'details': None,
                'error': str(e)
            }
            print_and_log(f"{get_icon('❌', '[FAIL]')} System Check: {result['error']}", self.log_file)
        
        return result

    def _generate_comprehensive_report(self, results):
        """Generiert einen umfassenden Report"""
        print_and_log("\n" + "=" * 70, self.log_file)
        print_and_log(f"{get_icon('📊', '[REPORT]')} COMPREHENSIVE HEALTH CHECK REPORT", self.log_file)
        print_and_log("• Zusammenfassung aller durchgeführten Tests und deren Ergebnisse", self.log_file)
        print_and_log("=" * 70, self.log_file)
        
        # Flache Liste aller Ergebnisse erstellen
        all_results = []
        for item in results:
            if isinstance(item, list):
                all_results.extend(item)
            else:
                all_results.append(item)
        
        total_tests = len(all_results)
        successful_tests = len([r for r in all_results if r['success']])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests) * 100
        
        print_and_log(f"{get_icon('🎯', '[TARGET]')} Getestete Webseite: {self.target_url}", self.log_file)
        print_and_log(f"{get_icon('🕒', '[TIME]')} Test-Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.log_file)
        print_and_log(f"{get_icon('📈', '[HEALTH]')} Gesamt-Gesundheit: {success_rate:.1f}% ({successful_tests} von {total_tests} Tests erfolgreich)", self.log_file)
        
        # Kategorie-weise Zusammenfassung
        categories = {}
        for result in all_results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'passed': 0}
            categories[cat]['total'] += 1
            if result['success']:
                categories[cat]['passed'] += 1
        
        print_and_log(f"\n{get_icon('📋', '[SUMMARY]')} Kategorie-Übersicht (Erfolgsrate pro Bereich):", self.log_file)
        for cat, stats in categories.items():
            rate = (stats['passed'] / stats['total']) * 100
            indicator = get_icon("✅", "[OK]") if rate > 80 else get_icon("⚠️", "[WARN]") if rate > 50 else get_icon("❌", "[FAIL]")
            print_and_log(f"   {indicator} {cat:15}: {rate:5.1f}% ({stats['passed']}/{stats['total']})", self.log_file)
        
        # Fehler-Details
        if failed_tests > 0:
            print_and_log(f"\n{get_icon('🔴', '[FAILED]')} Failed Tests:", self.log_file)
            for result in all_results:
                if not result['success']:
                    print_and_log(f"   - {result['category']}: {result['test']}", self.log_file)
                    if result.get('error'):
                        print_and_log(f"     Error: {result['error']}", self.log_file)
        
        # Gesamt-Bewertung
        print_and_log(f"\n{get_icon('🏆', '[ASSESSMENT]')} GESAMT-BEWERTUNG:", self.log_file)
        if success_rate >= 95:
            print_and_log(f"   {get_icon('✅', '[OK]')} AUSGEZEICHNET - Webseite funktioniert einwandfrei und schnell", self.log_file)
            print_and_log("   → Alle wichtigen Funktionen arbeiten optimal", self.log_file)
        elif success_rate >= 80:
            print_and_log(f"   {get_icon('⚠️', '[WARN]')} GUT - Kleinere Probleme erkannt, aber funktionsfähig", self.log_file)
            print_and_log("   → Webseite ist nutzbar, hat aber Verbesserungspotential", self.log_file)
        elif success_rate >= 60:
            print_and_log(f"   {get_icon('🔶', '[FAIR]')} BEFRIEDIGEND - Mehrere Probleme benötigen Aufmerksamkeit", self.log_file)
            print_and_log("   → Grundfunktionen arbeiten, aber Performance oder Zuverlässigkeit sind beeinträchtigt", self.log_file)
        else:
            print_and_log(f"   {get_icon('🔴', '[POOR]')} MANGELHAFT - Schwerwiegende Probleme erkannt", self.log_file)
            print_and_log("   → Webseite hat ernsthafte Funktionsstörungen und benötigt dringend Reparatur", self.log_file)
        
        print_and_log(f"\n{get_icon('📁', '[LOG]')} Detailliertes Protokoll gespeichert in: {self.log_file}", self.log_file)
        print_and_log("   → Diese Datei enthält alle technischen Details für spätere Analyse", self.log_file)
        
        # Log alle Ergebnisse
        log_message(self.log_file, f"\nCOMPREHENSIVE REPORT - Success Rate: {success_rate:.1f}%")
        for result in all_results:
            status = "PASS" if result['success'] else "FAIL"
            log_message(self.log_file, f"{status} | {result['category']}: {result['test']}")
def main():
    """Hauptfunktion mit Argument-Parsing"""
    parser = argparse.ArgumentParser(description="Führt einen umfassenden Health Check für eine URL durch")
    parser.add_argument("--url", required=True, help="Die zu prüfende URL")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout in Sekunden (default: 10)")
    
    args = parser.parse_args()
    
    # Unicode-Zeichen durch ASCII ersetzen
    print(f"START: Comprehensive Health Check für: {args.url}")
    print("=" * 70)
    
    checker = ComprehensiveHealthChecker(args.url)
    checker.alert_threshold_ms = args.timeout * 1000  # Convert to ms
    
    # Schreibe Start-Informationen auch ins Log
    print_and_log(f"START: Comprehensive Health Check für: {args.url}", checker.log_file)
    print_and_log("=" * 70, checker.log_file)
    
    try:
        checker.run_comprehensive_check()
    except KeyboardInterrupt:
        print_and_log("\nHealth Check wurde abgebrochen", checker.log_file)
    except Exception as e:
        print_and_log(f"\nFehler während des Health Checks: {e}", checker.log_file)

if __name__ == "__main__":
    main()