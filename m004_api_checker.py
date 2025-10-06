import requests
import time
import json
from datetime import datetime
import argparse

class APIChecker:
    def __init__(self, endpoints):
        self.endpoints = endpoints
        self.results = []
    
    def check_endpoint(self, url, method='GET', headers=None, data=None):
        """Prüft einen einzelnen API-Endpoint"""
        try:
            start_time = time.time()
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=10
            )
            
            response_time = round((time.time() - start_time) * 1000, 2)  # ms
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'success': 200 <= response.status_code < 300,
                'error': None
            }
            
        except requests.exceptions.RequestException as e:
            result = {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'status_code': None,
                'response_time_ms': None,
                'success': False,
                'error': str(e)
            }
        
        self.results.append(result)
        return result
    
    def check_all(self):
        """Prüft alle Endpoints"""
        for endpoint in self.endpoints:
            self.check_endpoint(**endpoint)
            time.sleep(1)  # Kurze Pause zwischen Checks
    
    def generate_report(self):
        """Erstellt einen Bericht"""
        total_checks = len(self.results)
        successful_checks = len([r for r in self.results if r['success']])
        success_rate = (successful_checks / total_checks) * 100

        # Ersetze das Unicode-Zeichen durch ein ASCII-Zeichen
        print(f"[REPORT] API Check Report - {datetime.now()}")
        print(f"✅ Successful: {successful_checks}/{total_checks} ({success_rate:.1f}%)")
        print("=" * 50)
        
        for result in self.results:
            status_icon = "✅" if result['success'] else "❌"
            print(f"{status_icon} {result['url']}")
            print(f"   Status: {result['status_code']} | Time: {result['response_time_ms']}ms")
            if result['error']:
                print(f"   Error: {result['error']}")
            print()

# Beispiel-Nutzung
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prüft einen einzelnen API-Endpunkt.")
    parser.add_argument("--url", required=True, help="Die zu prüfende URL.")
    parser.add_argument("--method", default="GET", help="HTTP-Methode (z. B. GET, POST).")
    parser.add_argument("--data", help="JSON-Daten für POST-Anfragen.")
    args = parser.parse_args()

    # Endpunkt basierend auf den Argumenten erstellen
    endpoint = {
        "url": args.url,
        "method": args.method,
        "data": json.loads(args.data) if args.data else None
    }

    # API-Checker initialisieren und den Endpunkt prüfen
    checker = APIChecker([endpoint])
    checker.check_all()
    checker.generate_report()