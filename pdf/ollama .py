#!/usr/bin/env python3
"""
Ollama Interactive Script - Startet Ollama automatisch und nimmt Benutzereingaben entgegen
Testet die Ollama-Installation und ermöglicht interaktive Fragen
"""

import subprocess
import os
import time
import signal
import sys
import requests
import json
from pathlib import Path

class OllamaTestManager:
    """
    Verwaltet Ollama-Tests mit automatischem Start und interaktiven Fragen.
    """
    
    def __init__(self):
        self.ollama_executable = None
        self.ollama_process = None
        self.is_running = False
        self.available_models = []
        self.best_model = None
        
        # Signal-Handler für sauberes Beenden
        signal.signal(signal.SIGINT, self._signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Signal-Handler für Ctrl+C"""
        print(f"\n🛑 Signal {signum} empfangen. Beende Ollama...")
        self.stop_ollama()
        sys.exit(0)
    
    def diagnose_ollama(self):
        """
        Führt vollständige Ollama-Diagnose durch.
        
        :returns: True wenn Ollama funktioniert
        :rtype: bool
        """
        print("🔍 Ollama-Diagnose gestartet...\n")
        
        # 1. Prüfe PATH-Variable
        print("1️⃣ PATH-Variable:")
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        ollama_in_path = False
        for path_dir in path_dirs:
            if 'ollama' in path_dir.lower():
                print(f"   ✅ Ollama-Pfad gefunden: {path_dir}")
                ollama_in_path = True
        
        if not ollama_in_path:
            print("   ⚠️ Kein Ollama-Pfad in PATH gefunden")
        print()
        
        # 2. Suche Ollama-Installation
        print("2️⃣ Suche Ollama-Installation:")
        possible_paths = [
            "ollama",  # Falls im PATH
            "ollama.exe",
            r"C:\Users\Frank\AppData\Local\Programs\Ollama\ollama.exe",
            r"C:\Program Files\Ollama\ollama.exe",
            r"C:\Program Files (x86)\Ollama\ollama.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Ollama\ollama.exe"),
        ]
        
        for path in possible_paths:
            if path.startswith('C:') or path.startswith(os.path.expanduser('~')):
                if Path(path).exists():
                    print(f"   ✅ Datei gefunden: {path}")
                else:
                    print(f"   ❌ Datei nicht gefunden: {path}")
                    continue
            
            # Teste Ausführbarkeit
            try:
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"   ✅ FUNKTIONIERT: {path}")
                    print(f"      Version: {result.stdout.strip()}")
                    self.ollama_executable = path
                    return True
                else:
                    print(f"   ❌ Exit-Code {result.returncode}: {path}")
                    
            except FileNotFoundError:
                print(f"   ❌ Nicht ausführbar: {path}")
            except subprocess.TimeoutExpired:
                print(f"   ⏰ Timeout: {path}")
            except Exception as e:
                print(f"   ❌ Fehler: {path} - {e}")
        
        print("\n❌ PROBLEM: Ollama nicht gefunden oder nicht funktionsfähig!")
        print("💡 Lösungen:")
        print("   1. Installiere Ollama: https://ollama.ai/download")
        print("   2. Füge Ollama zum PATH hinzu")
        print("   3. Starte Terminal als Administrator")
        return False
    
    def check_ollama_server(self) -> bool:
        """
        Prüft ob Ollama-Server läuft.
        
        :returns: True wenn Server erreichbar ist
        :rtype: bool
        """
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> list:
        """
        Holt verfügbare Modelle von Ollama.
        
        :returns: Liste der Modellnamen
        :rtype: list
        """
        if not self.ollama_executable:
            return []
        
        try:
            print(f"🔍 Prüfe verfügbare Modelle...")
            result = subprocess.run([self.ollama_executable, 'list'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Header überspringen
                models = []
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                        print(f"   📦 Verfügbares Modell: {model_name}")
                
                self.available_models = models
                return models
            else:
                print(f"❌ Fehler beim Abrufen der Modelle: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return []
    
    def choose_best_model(self) -> str:
        """
        Wählt das beste verfügbare Modell aus.
        
        :returns: Name des besten Modells
        :rtype: str
        """
        if not self.available_models:
            return None
        
        # Prioritätsliste (beste zuerst)
        priority_models = [
            "qwen2.5-coder:latest",
            "qwen2.5:7b", 
            "deepseek-r1:7b",
            "llama3.2:latest"
        ]
        
        # Suche bestes verfügbares Modell
        for preferred in priority_models:
            if preferred in self.available_models:
                print(f"🎯 Bestes Modell gefunden: {preferred}")
                self.best_model = preferred
                return preferred
        
        # Fallback: Erstes verfügbares Modell
        first_model = self.available_models[0]
        print(f"🎯 Verwende erstes verfügbares Modell: {first_model}")
        self.best_model = first_model
        return first_model
    
    def start_ollama_server(self) -> bool:
        """
        Startet Ollama-Server falls nicht läuft.
        
        :returns: True wenn Server läuft
        :rtype: bool
        """
        if self.check_ollama_server():
            print("✅ Ollama-Server läuft bereits")
            self.is_running = True
            return True
        
        if not self.ollama_executable:
            print("❌ Ollama-Executable nicht gefunden!")
            return False
        
        if not self.best_model:
            print("❌ Kein Modell ausgewählt!")
            return False
        
        try:
            print(f"🚀 Starte Ollama-Server mit Modell: {self.best_model}")
            print("   Dies kann einige Minuten dauern...")
            
            # Starte Ollama im Hintergrund
            self.ollama_process = subprocess.Popen(
                [self.ollama_executable, 'serve'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Warte auf Server-Start
            for i in range(30):
                time.sleep(2)
                if self.check_ollama_server():
                    print(f"✅ Ollama-Server gestartet (nach {(i+1)*2}s)")
                    self.is_running = True
                    
                    # Lade gewähltes Modell
                    return self.load_model(self.best_model)
                
                if i % 5 == 0:
                    print(f"⏳ Warte auf Server-Start... ({(i+1)*2}/60s)")
            
            print("❌ Timeout beim Server-Start")
            return False
            
        except KeyboardInterrupt:
            print(f"\n🛑 Start durch Ctrl+C abgebrochen")
            self.stop_ollama()
            raise
        except Exception as e:
            print(f"❌ Fehler beim Starten: {e}")
            return False
    
    def load_model(self, model_name: str) -> bool:
        """
        Lädt ein spezifisches Modell in Ollama.
        
        :param model_name: Name des zu ladenden Modells
        :type model_name: str
        :returns: True wenn Modell geladen wurde
        :rtype: bool
        """
        try:
            print(f"📥 Lade Modell: {model_name}")
            print("   Dies kann beim ersten Mal länger dauern...")
            
            # Führe 'ollama run' aus um Modell zu laden
            result = subprocess.run(
                [self.ollama_executable, 'run', model_name, '--help'],
                capture_output=True, text=True, timeout=120
            )
            
            if result.returncode == 0:
                print(f"✅ Modell {model_name} erfolgreich geladen")
                return True
            else:
                print(f"❌ Fehler beim Laden von {model_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout beim Laden von {model_name}")
            return False
        except Exception as e:
            print(f"❌ Exception beim Laden: {e}")
            return False
    
    def ask_question(self, question: str) -> str:
        """
        Stellt eine Frage an Ollama.
        
        :param question: Die zu stellende Frage
        :type question: str
        :returns: Antwort von Ollama
        :rtype: str
        """
        if not self.is_running:
            print("❌ Ollama-Server läuft nicht!")
            return None
        
        if not self.best_model:
            print("❌ Kein Modell geladen!")
            return None
        
        try:
            print(f"\n🤖 Stelle Frage an {self.best_model}:")
            print(f"❓ Frage: {question}")
            print("⏳ Warte auf Antwort...")
            
            # API-Request an Ollama
            payload = {
                "model": self.best_model,
                "prompt": question,
                "stream": False
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', 'Keine Antwort erhalten')
                
                print(f"\n✅ Antwort erhalten:")
                print(f"💬 {answer}")
                return answer
            else:
                print(f"❌ HTTP-Fehler {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout bei der Anfrage")
            return None
        except Exception as e:
            print(f"❌ Fehler bei der Anfrage: {e}")
            return None
    
    def interactive_session(self):
        """
        Startet eine interaktive Frage-Antwort-Session.
        """
        print(f"\n🎪 Interaktive Ollama-Session gestartet!")
        print(f"🤖 Aktives Modell: {self.best_model}")
        print("📝 Gib deine Fragen ein (oder 'quit'/'exit' zum Beenden)")
        print("💡 Befehle: 'help' für Hilfe, 'stats' für Statistiken")
        print("=" * 60)
        
        question_count = 0
        
        while True:
            try:
                # Benutzereingabe holen
                print(f"\n� Deine Frage #{question_count + 1}: ", end="")
                user_input = input().strip()
                
                # Leer-Eingabe ignorieren
                if not user_input:
                    print("⚠️ Leere Eingabe - bitte eine Frage eingeben!")
                    continue
                
                # Beenden-Befehle
                if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
                    print("👋 Session beendet. Auf Wiedersehen!")
                    break
                
                # Hilfe-Befehl
                elif user_input.lower() in ['help', 'h', '?']:
                    self.show_help()
                    continue
                
                # Statistiken-Befehl
                elif user_input.lower() in ['stats', 'statistics', 'info']:
                    self.show_statistics(question_count)
                    continue
                
                # Modell wechseln
                elif user_input.lower().startswith('model'):
                    self.change_model_interactive()
                    continue
                
                # Frage an Ollama stellen
                else:
                    question_count += 1
                    answer = self.ask_question(user_input)
                    
                    if not answer:
                        print("⚠️ Keine Antwort erhalten - versuche es erneut")
                        question_count -= 1  # Fehlgeschlagene Fragen nicht zählen
            
            except KeyboardInterrupt:
                print(f"\n🛑 Session durch Ctrl+C beendet")
                break
            except EOFError:
                print(f"\n👋 Session beendet")
                break
    
    def show_help(self):
        """Zeigt Hilfe-Informationen."""
        print("\n📚 Ollama Interactive - Hilfe")
        print("=" * 40)
        print("🔤 Gib einfach deine Frage ein und drücke Enter")
        print("📝 Verfügbare Befehle:")
        print("   • help, h, ?        - Diese Hilfe anzeigen")
        print("   • stats, info       - Statistiken anzeigen")
        print("   • model             - Modell wechseln")
        print("   • quit, exit, q     - Session beenden")
        print("\n💡 Beispiel-Fragen:")
        print("   • Was ist Python?")
        print("   • Erkläre mir Machine Learning")
        print("   • Schreibe einen Hello World Code")
        print("   • Was ist die Hauptstadt von Deutschland?")
    
    def show_statistics(self, question_count: int):
        """
        Zeigt Session-Statistiken.
        
        :param question_count: Anzahl gestellter Fragen
        :type question_count: int
        """
        print(f"\n📊 Ollama Session-Statistiken")
        print("=" * 40)
        print(f"🤖 Aktives Modell: {self.best_model}")
        print(f"🔧 Ollama-Pfad: {self.ollama_executable}")
        print(f"📦 Verfügbare Modelle: {len(self.available_models)}")
        print(f"❓ Gestellte Fragen: {question_count}")
        print(f"🌐 Server-Status: {'🟢 Läuft' if self.is_running else '🔴 Gestoppt'}")
        
        if self.available_models:
            print(f"\n📋 Verfügbare Modelle:")
            for i, model in enumerate(self.available_models, 1):
                status = "🎯 (aktiv)" if model == self.best_model else ""
                print(f"   {i}. {model} {status}")
    
    def change_model_interactive(self):
        """Ermöglicht interaktiven Modell-Wechsel."""
        if not self.available_models:
            print("❌ Keine Modelle verfügbar!")
            return
        
        print(f"\n� Modell wechseln")
        print("=" * 30)
        print(f"🎯 Aktuelles Modell: {self.best_model}")
        print(f"\n📋 Verfügbare Modelle:")
        
        for i, model in enumerate(self.available_models, 1):
            status = "🎯 (aktiv)" if model == self.best_model else ""
            print(f"   {i}. {model} {status}")
        
        try:
            print(f"\n🔢 Wähle Modell (1-{len(self.available_models)}) oder Enter für aktuelles: ", end="")
            choice = input().strip()
            
            if not choice:  # Enter gedrückt
                print(f"✅ Behalte aktuelles Modell: {self.best_model}")
                return
            
            model_index = int(choice) - 1
            if 0 <= model_index < len(self.available_models):
                new_model = self.available_models[model_index]
                if new_model != self.best_model:
                    print(f"🔄 Wechsle zu Modell: {new_model}")
                    if self.load_model(new_model):
                        self.best_model = new_model
                        print(f"✅ Modell gewechselt zu: {new_model}")
                    else:
                        print(f"❌ Fehler beim Laden von: {new_model}")
                else:
                    print(f"✅ Modell {new_model} ist bereits aktiv")
            else:
                print("❌ Ungültige Auswahl!")
                
        except ValueError:
            print("❌ Bitte eine Zahl eingeben!")
        except Exception as e:
            print(f"❌ Fehler beim Modell-Wechsel: {e}")
    
    def stop_ollama(self):
        """Stoppt Ollama-Server sauber."""
        if self.ollama_process:
            try:
                print("🛑 Stoppe Ollama-Server...")
                if os.name == 'nt':
                    # Windows: Verwende taskkill
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.ollama_process.pid)], 
                                 capture_output=True)
                else:
                    # Unix: Verwende SIGTERM
                    self.ollama_process.terminate()
                    self.ollama_process.wait(timeout=10)
                
                print("✅ Ollama gestoppt")
            except Exception as e:
                print(f"⚠️ Fehler beim Stoppen: {e}")
            finally:
                self.ollama_process = None
                self.is_running = False

def main():
    """Hauptfunktion für interaktive Ollama-Session."""
    ollama_manager = OllamaTestManager()
    
    try:
        print("🚀 Ollama Interactive Script gestartet")
        print("   Drücke Ctrl+C zum Beenden\n")
        
        # 1. Diagnose durchführen
        if not ollama_manager.diagnose_ollama():
            print("\n❌ Ollama-Diagnose fehlgeschlagen!")
            return
        
        # 2. Verfügbare Modelle abrufen
        models = ollama_manager.get_available_models()
        if not models:
            print("\n❌ Keine Modelle verfügbar!")
            print("💡 Installiere ein Modell mit: ollama pull qwen2.5:7b")
            return
        
        # 3. Bestes Modell wählen
        best_model = ollama_manager.choose_best_model()
        if not best_model:
            print("\n❌ Kein geeignetes Modell gefunden!")
            return
        
        # 4. Ollama-Server starten
        if not ollama_manager.start_ollama_server():
            print("\n❌ Ollama-Server konnte nicht gestartet werden!")
            return
        
        # 5. Interaktive Session starten
        ollama_manager.interactive_session()
    
    except KeyboardInterrupt:
        print(f"\n🛑 Script durch Benutzer abgebrochen")
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
    finally:
        # Cleanup
        ollama_manager.stop_ollama()
        print("\n👋 Interactive Script beendet")

if __name__ == "__main__":
    main()