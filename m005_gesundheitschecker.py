import requests
import time
import os
import argparse
from datetime import datetime
import psutil
import json

def log_message(log_file, message):
    """Schreibt eine Nachricht in die angegebene Logdatei."""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    except IOError as e:
        print(f"Fehler beim Schreiben in die Logdatei: {e}")

class ComprehensiveHealthChecker:
    def __init__(self, target_url):
        self.target_url = target_url
        self.log_file = f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.alert_threshold_ms = 1000
        
        # Initialisiere Logdatei
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("🏥 COMPREHENSIVE SINGLE URL HEALTH CHECK\n")
                f.write("=" * 60 + "\n")
                f.write(f"Ziel URL: {target_url}\n")
                f.write(f"Gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
        except IOError as e:
            print(f"Fehler beim Erstellen der Logdatei: {e}")

    def run_comprehensive_check(self):
        """Führt einen umfassenden Health Check für die Ziel-URL durch"""
        print(f"🏥 STARTE UMFASSENDEN HEALTH CHECK FÜR: {self.target_url}")
        print("=" * 70)
        
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
        print("\n🔗 BASIS CONNECTIVITY CHECK")
        print("-" * 40)
        
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
            
            status_icon = "✅" if result['success'] else "❌"
            print(f"{status_icon} Basic GET | Status: {result['status_code']} | Time: {result['response_time_ms']}ms")
            if result['redirected']:
                print(f"   ↳ Redirected to: {result['final_url']}")
                
        except Exception as e:
            result = {
                'category': 'Connectivity',
                'test': 'Basic HTTP GET',
                'success': False,
                'status_code': None,
                'response_time_ms': None,
                'error': str(e)
            }
            print(f"❌ Basic GET | Error: {result['error']}")
        
        return result

    def _check_http_methods(self):
        """Testet verschiedene HTTP Methoden"""
        print("\n🌐 HTTP METHODEN CHECK")
        print("-" * 40)
        
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
                
                status_icon = "✅" if success else "⚠️"
                print(f"{status_icon} {method:6} | Status: {result['status_code']:3} | Time: {result['response_time_ms']:6}ms")
                
                # Zeige wichtige Header
                if 'server' in response.headers:
                    print(f"   Server: {response.headers['server']}")
                
            except Exception as e:
                result = {
                    'category': 'HTTP Methods',
                    'test': f'{method} Request',
                    'success': False,
                    'status_code': None,
                    'response_time_ms': None,
                    'error': str(e)
                }
                print(f"❌ {method:6} | Error: {result['error']}")
            
            results.append(result)
            time.sleep(0.5)  # Kurze Pause zwischen Requests
        
        return results

    def _check_performance(self):
        """Führt Performance-Tests durch"""
        print("\n⚡ PERFORMANCE CHECK")
        print("-" * 40)
        
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
                
                status_icon = "✅" if response_time < self.alert_threshold_ms else "⚠️"
                speed_indicator = "🐌" if response_time > 1000 else "🚀" if response_time < 200 else "⚡"
                print(f"{status_icon} Request {i+1} | {speed_indicator} {result['response_time_ms']:6}ms")
                
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
                print(f"❌ Request {i+1} | Error: {result['error']}")
                results.append(result)
        
        # Performance-Statistiken
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            print(f"\n📊 Performance Statistics:")
            print(f"   Avg: {avg_time:.2f}ms | Min: {min_time:.2f}ms | Max: {max_time:.2f}ms")
            
            # Performance-Bewertung
            if avg_time < 200:
                rating = "EXCELLENT 🏆"
            elif avg_time < 500:
                rating = "GOOD 👍"
            elif avg_time < 1000:
                rating = "AVERAGE ⚠️"
            else:
                rating = "POOR 🐌"
                
            print(f"   Rating: {rating}")
        
        return results

    def _check_content(self):
        """Validiert Content und Response"""
        print("\n📄 CONTENT VALIDATION")
        print("-" * 40)
        
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
            print(f"✅ Content-Type: {content_type}")
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
            size_indicator = "📦" if content_length > 10000 else "📄"
            print(f"✅ Content Size: {size_indicator} {content_length:,} bytes")
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
                    print(f"✅ JSON: Valid format")
                    results.append(json_check)
                except:
                    json_check = {
                        'category': 'Content',
                        'test': 'JSON Validity', 
                        'success': False,
                        'details': 'Invalid JSON format',
                        'error': 'JSON parsing failed'
                    }
                    print(f"❌ JSON: Invalid format")
                    results.append(json_check)
                    
        except Exception as e:
            error_check = {
                'category': 'Content',
                'test': 'Content Analysis',
                'success': False,
                'details': None,
                'error': str(e)
            }
            print(f"❌ Content Analysis: {error_check['error']}")
            results.append(error_check)
        
        return results

    def _check_system_resources(self):
        """Prüft System-Ressourcen während des Checks"""
        print("\n💻 SYSTEM RESOURCES")
        print("-" * 40)
        
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
            
            print(f"✅ CPU Usage: {cpu_percent}%")
            print(f"✅ Memory Usage: {memory.percent}%")
            print(f"✅ Disk Free: {result['details']['disk_free_gb']} GB")
            
        except Exception as e:
            result = {
                'category': 'System',
                'test': 'Resource Usage',
                'success': False,
                'details': None,
                'error': str(e)
            }
            print(f"❌ System Check: {result['error']}")
        
        return result

    def _generate_comprehensive_report(self, results):
        """Generiert einen umfassenden Report"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE HEALTH CHECK REPORT")
        print("=" * 70)
        
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
        
        print(f"🎯 Target URL: {self.target_url}")
        print(f"🕒 Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📈 Overall Health: {success_rate:.1f}% ({successful_tests}/{total_tests} tests passed)")
        
        # Kategorie-weise Zusammenfassung
        categories = {}
        for result in all_results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'passed': 0}
            categories[cat]['total'] += 1
            if result['success']:
                categories[cat]['passed'] += 1
        
        print(f"\n📋 Category Summary:")
        for cat, stats in categories.items():
            rate = (stats['passed'] / stats['total']) * 100
            indicator = "✅" if rate > 80 else "⚠️" if rate > 50 else "❌"
            print(f"   {indicator} {cat:15}: {rate:5.1f}% ({stats['passed']}/{stats['total']})")
        
        # Fehler-Details
        if failed_tests > 0:
            print(f"\n🔴 Failed Tests:")
            for result in all_results:
                if not result['success']:
                    print(f"   - {result['category']}: {result['test']}")
                    if result.get('error'):
                        print(f"     Error: {result['error']}")
        
        # Gesamt-Bewertung
        print(f"\n🏆 FINAL ASSESSMENT:")
        if success_rate >= 95:
            print("   ✅ EXCELLENT - System is healthy and responsive")
        elif success_rate >= 80:
            print("   ⚠️  GOOD - Minor issues detected")
        elif success_rate >= 60:
            print("   🔶 FAIR - Several issues need attention") 
        else:
            print("   🔴 POOR - Major problems detected")
        
        print(f"\n📁 Detailed log saved to: {self.log_file}")
        
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
    
    try:
        checker.run_comprehensive_check()
    except KeyboardInterrupt:
        print("\nHealth Check wurde abgebrochen")
    except Exception as e:
        print(f"\nFehler während des Health Checks: {e}")

if __name__ == "__main__":
    main()