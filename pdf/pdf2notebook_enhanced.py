#!/usr/bin/env python3
"""
Erweiterten PDF zu Jupyter Notebook Konverter mit LLM-Integration
Erstellt intelligente, strukturierte Jupyter Notebooks mit Hilfe von Large Language Models.

Autor: Frank Albrecht
Datum: 2025-10-08
Version: 2.0
"""

import os
import sys
import json
import PyPDF2
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Union
import re
import time
import subprocess
import threading
import signal
from time import sleep

# Konfiguration aus config.py importieren
try:
    sys.path.append('..')
    from config import CONFIG
    # Intelligente Pfad-Erkennung basierend auf dem aktuellen Arbeitsverzeichnis
    cwd = Path.cwd()
    if cwd.name == 'pdf':
        # Wir sind im PDF-Ordner
        PDF_FOLDER = '.'
        NOTEBOOK_FOLDER = '../notebook'
    else:
        # Wir sind im Hauptverzeichnis
        PDF_FOLDER = './pdf'
        NOTEBOOK_FOLDER = './notebook'
except ImportError:
    # Fallback-Konfiguration mit intelligenter Pfad-Erkennung
    cwd = Path.cwd()
    if cwd.name == 'pdf':
        PDF_FOLDER = '.'
        NOTEBOOK_FOLDER = '../notebook'
    else:
        PDF_FOLDER = './pdf'
        NOTEBOOK_FOLDER = './notebook'


class OllamaManager:
    """
    Verwaltet Ollama-Installation und Modelle automatisch.
    """
    
    def __init__(self):
        self.ollama_process = None
        self.available_models = []
        self.best_model = None
        self.is_running = False
    
    def check_ollama_installation(self) -> bool:
        """
        Überprüft ob Ollama installiert ist.
        
        :returns: True wenn Ollama verfügbar ist
        :rtype: bool
        """
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def get_available_models(self) -> List[str]:
        """
        Listet verfügbare Ollama-Modelle auf.
        
        :returns: Liste verfügbarer Modelle
        :rtype: List[str]
        """
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Header überspringen
                models = []
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]  # Erste Spalte ist der Name
                        models.append(model_name)
                return models
            return []
        except Exception:
            return []
    
    def select_best_model(self) -> Optional[str]:
        """
        Wählt das beste verfügbare Modell für Code-Generierung.
        
        :returns: Name des besten Modells oder None
        :rtype: Optional[str]
        """
        models = self.get_available_models()
        
        # Priorität für Code-Generierung (beste zuerst)
        priority_models = [
            'qwen2.5-coder:latest',
            'deepseek-r1:7b', 
            'qwen2.5:7b',
            'llama3.2:latest'
        ]
        
        # Finde das erste verfügbare Prioritäts-Modell
        for preferred in priority_models:
            for available in models:
                if preferred in available or available in preferred:
                    return available
        
        # Fallback: Erstes verfügbares Modell
        return models[0] if models else None
    
    def check_ollama_server(self) -> bool:
        """
        Überprüft ob Ollama-Server läuft.
        
        :returns: True wenn Server erreichbar ist
        :rtype: bool
        """
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_ollama_with_model(self, model_name: str) -> bool:
        """
        Startet Ollama mit spezifischem Modell über 'ollama run'.
        
        :param model_name: Name des zu startenden Modells
        :type model_name: str
        :returns: True wenn erfolgreich gestartet
        :rtype: bool
        """
        if self.check_ollama_server():
            print("✅ Ollama-Server läuft bereits")
            return True
        
        try:
            print(f"🚀 Starte Ollama mit Modell: {model_name}")
            
            # Starte Ollama mit spezifischem Modell im Hintergrund
            self.ollama_process = subprocess.Popen(
                ['ollama', 'run', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Warte bis Server verfügbar ist (max 45 Sekunden für Modell-Loading)
            for i in range(45):
                try:
                    sleep(1)
                except KeyboardInterrupt:
                    print(f"\n🛑 Ollama-Start durch Benutzer abgebrochen")
                    if self.ollama_process:
                        self.ollama_process.terminate()
                    raise
                    
                if self.check_ollama_server():
                    print(f"✅ Ollama mit {model_name} erfolgreich gestartet (nach {i+1}s)")
                    self.is_running = True
                    return True
                print(f"⏳ Lade Modell {model_name}... ({i+1}/45s)", end='\r')
            
            print(f"\n❌ Timeout beim Laden von Modell {model_name}")
            return False
            
        except KeyboardInterrupt:
            print(f"\n🛑 Ollama-Start durch Ctrl+C abgebrochen")
            if self.ollama_process:
                self.ollama_process.terminate()
            raise
        except Exception as e:
            print(f"❌ Fehler beim Starten von Ollama mit {model_name}: {e}")
            return False
            return False
    
    def stop_ollama_server(self):
        """
        Stoppt den Ollama-Server falls er von uns gestartet wurde.
        """
        if self.ollama_process and self.is_running:
            print("🛑 Stoppe Ollama...")
            try:
                # Sende Strg+C Signal an den Prozess
                if os.name == 'nt':  # Windows
                    self.ollama_process.send_signal(signal.CTRL_C_EVENT)
                else:  # Unix/Linux/Mac
                    self.ollama_process.terminate()
                
                # Warte auf sauberes Beenden
                self.ollama_process.wait(timeout=15)
                print("✅ Ollama gestoppt")
            except subprocess.TimeoutExpired:
                print("⚠️ Ollama antwortet nicht - forciere Beendigung")
                self.ollama_process.kill()
            except Exception as e:
                print(f"⚠️ Ollama läuft weiter im Hintergrund: {e}")
            finally:
                self.is_running = False
    
    def ensure_ollama_ready(self) -> Optional[str]:
        """
        Stellt sicher, dass Ollama bereit ist und gibt das beste Modell zurück.
        
        :returns: Name des besten verfügbaren Modells
        :rtype: Optional[str]
        """
        # 1. Installation prüfen
        if not self.check_ollama_installation():
            print("❌ Ollama ist nicht installiert!")
            print("💡 Installation: https://ollama.ai/")
            return None
        
        # 2. Bestes Modell auswählen (vor dem Starten)
        best_model = self.select_best_model()
        if not best_model:
            print("❌ Keine Ollama-Modelle gefunden!")
            print("💡 Installiere ein Modell: ollama pull qwen2.5-coder:latest")
            return None
        
        # 3. Ollama mit spezifischem Modell starten
        if not self.start_ollama_with_model(best_model):
            print(f"❌ Konnte Ollama nicht mit Modell {best_model} starten")
            return None
        
        print(f"🤖 Ollama bereit mit Modell: {best_model}")
        return best_model


class LLMNotebookEnhancer:
    """
    Erweitert PDF-zu-Notebook-Konvertierung mit LLM-basierter Intelligenz.
    
    Nutzt automatisch verwaltete Ollama-Installation um aus PDF-Text strukturierte, 
    professionelle Jupyter Notebooks zu erstellen.
    """
    
    def __init__(self, 
                 pdf_folder: str = PDF_FOLDER, 
                 notebook_folder: str = NOTEBOOK_FOLDER):
        """
        Initialisiert den erweiterten PDF-zu-Notebook-Konverter.
        
        :param pdf_folder: Pfad zum PDF-Ordner
        :type pdf_folder: str
        :param notebook_folder: Pfad zum Notebook-Ordner
        :type notebook_folder: str
        """
        self.pdf_folder = Path(pdf_folder)
        self.notebook_folder = Path(notebook_folder)
        
        # Ordner erstellen falls sie nicht existieren
        self.notebook_folder.mkdir(parents=True, exist_ok=True)
        
        # Ollama-Manager initialisieren
        self.ollama_manager = OllamaManager()
        self.current_model = None
        
        # LLM-Konfiguration
        self.llm_config = self._setup_llm_config()
    
    def _setup_llm_config(self) -> Dict:
        """
        Konfiguriert die LLM-API-Einstellungen für Ollama.
        
        :returns: LLM-Konfigurationsdictionary
        :rtype: Dict
        """
        return {
            "base_url": "http://localhost:11434/api/generate",
            "headers": {"Content-Type": "application/json"},
            "timeout": 60  # Längeres Timeout für große Modelle
        }
    
    def initialize_ollama(self) -> bool:
        """
        Initialisiert Ollama und wählt das beste Modell aus.
        
        :returns: True wenn erfolgreich initialisiert
        :rtype: bool
        """
        print("🔧 Initialisiere Ollama...")
        
        # Ollama bereit machen und bestes Modell auswählen
        self.current_model = self.ollama_manager.ensure_ollama_ready()
        
        if not self.current_model:
            print("❌ Ollama-Initialisierung fehlgeschlagen")
            return False
        
        print(f"✅ Ollama bereit mit Modell: {self.current_model}")
        return True
    
    def liste_pdf_dateien(self) -> List[Path]:
        """
        Listet alle PDF-Dateien im PDF-Ordner auf.
        
        :returns: Liste der gefundenen PDF-Dateien
        :rtype: List[Path]
        """
        if not self.pdf_folder.exists():
            print(f"❌ PDF-Ordner '{self.pdf_folder}' existiert nicht!")
            return []
        
        pdf_dateien = list(self.pdf_folder.glob("*.pdf"))
        return sorted(pdf_dateien)
    
    def extrahiere_pdf_text(self, pdf_pfad: Path) -> str:
        """
        Extrahiert Text aus einer PDF-Datei mit verbesserter Fehlerbehandlung.
        
        :param pdf_pfad: Pfad zur PDF-Datei
        :type pdf_pfad: Path
        :returns: Extrahierter und bereinigerter Text aus der PDF
        :rtype: str
        :raises FileNotFoundError: Wenn PDF-Datei nicht gefunden wird
        """
        text = ""
        
        try:
            # Primärer Ansatz: PyPDF2
            with open(pdf_pfad, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- Seite {page_num + 1} ---\n" + page_text
                    except Exception as e:
                        print(f"⚠️ Fehler bei Seite {page_num + 1}: {e}")
                        continue
            
            if not text.strip():
                raise Exception("Kein Text mit PyPDF2 extrahiert")
                
        except Exception as e:
            print(f"⚠️ PyPDF2 Fehler: {e}")
            print("🔄 Versuche mit pdfplumber...")
            
            try:
                import pdfplumber
                with pdfplumber.open(pdf_pfad) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        try:
                            page_text = page.extract_text()
                            if page_text:
                                text += f"\n--- Seite {page_num + 1} ---\n" + page_text
                        except Exception as e:
                            print(f"⚠️ pdfplumber Fehler bei Seite {page_num + 1}: {e}")
                            continue
                            
            except ImportError:
                print("❌ pdfplumber ist nicht installiert!")
                print("💡 Installiere es mit: pip install pdfplumber")
                return ""
            except Exception as e2:
                print(f"❌ pdfplumber Fehler: {e2}")
                return ""
        
        # Text bereinigen (Unicode-Probleme beheben)
        text = text.replace('\u202f', ' ')  # NARROW NO-BREAK SPACE durch SPACE ersetzen
        text = re.sub(r'\s+', ' ', text)  # Mehrfache Leerzeichen reduzieren
        
        return text.strip()
    
    def llm_anfrage(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        Sendet eine Anfrage an Ollama.
        
        :param prompt: Der Prompt für das LLM
        :type prompt: str
        :param max_retries: Maximale Anzahl der Wiederholungsversuche
        :type max_retries: int
        :returns: Antwort des LLMs oder None bei Fehler
        :rtype: Optional[str]
        """
        if not self.current_model:
            print("❌ Kein Ollama-Modell verfügbar!")
            return None
        
        for versuch in range(max_retries):
            try:
                return self._ollama_anfrage(prompt)
                    
            except KeyboardInterrupt:
                print("\n🛑 LLM-Anfrage durch Benutzer abgebrochen")
                raise  # Weitergeben für saubere Beendigung
            except Exception as e:
                print(f"⚠️ LLM-Anfrage Versuch {versuch + 1} fehlgeschlagen: {e}")
                if versuch < max_retries - 1:
                    wartezeit = 2 ** versuch
                    print(f"🔄 Wiederhole in {wartezeit} Sekunden...")
                    try:
                        time.sleep(wartezeit)
                    except KeyboardInterrupt:
                        print("\n🛑 Warteschleife durch Benutzer abgebrochen")
                        raise
                    continue
                else:
                    print(f"❌ Alle {max_retries} Versuche fehlgeschlagen!")
                    return None
    
    def _ollama_anfrage(self, prompt: str) -> str:
        """
        Sendet Anfrage an lokale Ollama-Installation.
        
        :param prompt: Der Prompt für Ollama
        :type prompt: str
        :returns: Antwort von Ollama
        :rtype: str
        """
        payload = {
            "model": self.current_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 2000  # Maximal 2000 Token generieren
            }
        }
        
        print(f"🤖 Sende Anfrage an {self.current_model}...")
        
        response = requests.post(
            self.llm_config["base_url"],
            json=payload,
            headers=self.llm_config["headers"],
            timeout=self.llm_config["timeout"]
        )
        response.raise_for_status()
        
        result = response.json().get("response", "")
        print(f"✅ Antwort erhalten: {len(result)} Zeichen")
        
        return result
    

    
    def analysiere_pdf_mit_llm(self, text: str) -> Optional[Dict]:
        """
        Analysiert PDF-Text mit LLM in kleinen Schritten.
        
        :param text: Extrahierter PDF-Text
        :type text: str
        :returns: Strukturierte Analyse oder None bei Fehler
        :rtype: Optional[Dict]
        """
        if not self.current_model:
            print("⚠️ Kein LLM verfügbar, verwende Fallback-Analyse")
            return self._fallback_analyse(text)
        
        # Schritt 1: Titel und Kategorie erkennen (kurze Anfrage)
        print("🤖 Schritt 1: Analysiere Titel und Thema...")
        basis_info = self._analysiere_basis_info(text[:1000])  # Nur erste 1000 Zeichen
        
        if not basis_info:
            print("❌ Basis-Analyse fehlgeschlagen, verwende Fallback")
            return self._fallback_analyse(text)
        
        # Schritt 2: Aufgaben erkennen (kleine Anfrage)
        print("🤖 Schritt 2: Erkenne Aufgaben...")
        aufgaben = self._erkenne_aufgaben(text)
        
        # Kombiniere Ergebnisse
        struktur = {
            **basis_info,
            "aufgaben": aufgaben,
            "voraussetzungen": ["Python Grundlagen", "HTTP Kenntnisse"],
            "lernziele": [f"Verstehe {basis_info['kategorie']}", "Praktische Anwendung"],
            "verwendete_bibliotheken": ["requests", "json", "pandas"]
        }
        
        print(f"✅ LLM-Analyse erfolgreich: {len(aufgaben)} Aufgaben erkannt")
        return struktur
    
    def _analysiere_basis_info(self, text_anfang: str) -> Optional[Dict]:
        """
        Analysiert nur Titel, Kategorie und Schwierigkeit (schnelle Anfrage).
        
        :param text_anfang: Erste 1000 Zeichen des PDF-Texts
        :type text_anfang: str
        :returns: Basis-Informationen oder None
        :rtype: Optional[Dict]
        """
        basis_prompt = f"""Analysiere diesen Text und gib nur diese 4 Informationen als JSON zurück:

Text: {text_anfang}

Antwort als JSON:
{{
  "titel": "Titel des Dokuments",
  "beschreibung": "Eine Zeile Beschreibung", 
  "kategorie": "API-Tutorial/Datenanalyse/Programmierung/Allgemein",
  "schwierigkeit": "Anfänger/Fortgeschritten/Experte"
}}"""
        
        antwort = self.llm_anfrage(basis_prompt, max_retries=2)
        if not antwort:
            return None
        
        try:
            json_match = re.search(r'\{.*\}', antwort, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return None
    
    def extrahiere_fragen_praezise(self, text: str) -> List[Dict]:
        """
        Extrahiert alle Fragen/Aufgaben aus dem PDF-Text mit verbesserter Erkennung.
        
        :param text: PDF-Text
        :type text: str
        :returns: Liste aller gefundenen Fragen/Aufgaben
        :rtype: List[Dict]
        """
        fragen = []
        
        # Verschiedene Muster für Fragen/Aufgaben
        patterns = [
            # Aufgabe 1:, Übung 2:, etc.
            r'(?:Aufgabe|Übung|Exercise|Task)\s*(\d+)[:\.]?\s*([^\n\r]+(?:\n(?!\s*(?:Aufgabe|Übung|Exercise|Task)\s*\d+)[^\n\r]*)*)',
            # 1., 2., etc. am Zeilenanfang
            r'^\s*(\d+)[\.\)]\s*([^\n\r]+(?:\n(?!\s*\d+[\.\)])[^\n\r]*)*)',
            # a), b), c) etc.
            r'^\s*([a-z])\)\s*([^\n\r]+(?:\n(?!\s*[a-z]\))[^\n\r]*)*)',
            # Frage-Indikatoren
            r'(Frage\s*\d*)[:\.]?\s*([^\n\r]+(?:\n(?!Frage)[^\n\r]*)*)',
            # Direkte Fragen mit Fragezeichen
            r'([^\.\!\n]*\?[^\n\r]*)'
        ]
        
        print("🔍 Extrahiere Fragen mit verschiedenen Mustern...")
        
        for i, pattern in enumerate(patterns, 1):
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            print(f"   Muster {i}: {len(matches)} Treffer")
            
            for match in matches:
                if isinstance(match, tuple):
                    nummer = match[0] if match[0] else str(len(fragen) + 1)
                    frage_text = match[1].strip()
                else:
                    nummer = str(len(fragen) + 1)
                    frage_text = match.strip()
                
                # Bereinige den Fragetext
                frage_text = re.sub(r'\s+', ' ', frage_text)  # Mehrfache Leerzeichen
                frage_text = frage_text.replace('\n', ' ').strip()
                
                # Filter zu kurze oder irrelevante Texte
                if (len(frage_text) > 15 and 
                    not re.match(r'^\d+\s*$', frage_text) and
                    'Seite' not in frage_text[:10]):
                    
                    frage = {
                        "nummer": len(fragen) + 1,
                        "original_nummer": nummer,
                        "frage": frage_text,
                        "typ": self._erkenne_frage_typ(frage_text),
                        "thema": self._erkenne_thema(frage_text)
                    }
                    
                    # Duplikate vermeiden
                    if not any(f["frage"] == frage_text for f in fragen):
                        fragen.append(frage)
        
        # Sortiere nach Nummer falls möglich
        try:
            fragen.sort(key=lambda x: int(x["original_nummer"]) if x["original_nummer"].isdigit() else 999)
            # Nummeriere neu
            for i, frage in enumerate(fragen, 1):
                frage["nummer"] = i
        except:
            pass
        
        print(f"✅ {len(fragen)} Fragen extrahiert")
        return fragen
    
    def _erkenne_frage_typ(self, frage_text: str) -> str:
        """
        Erkennt den Typ einer Frage basierend auf Schlüsselwörtern.
        
        :param frage_text: Text der Frage
        :type frage_text: str
        :returns: Typ der Frage
        :rtype: str
        """
        frage_lower = frage_text.lower()
        
        if any(word in frage_lower for word in ['curl', 'request', 'http', 'api']):
            return 'HTTP/API'
        elif any(word in frage_lower for word in ['json', 'parse', 'data']):
            return 'Datenverarbeitung'
        elif any(word in frage_lower for word in ['python', 'code', 'programmier']):
            return 'Programmierung'
        elif any(word in frage_lower for word in ['get', 'post', 'put', 'delete']):
            return 'REST'
        elif '?' in frage_text:
            return 'Verständnisfrage'
        else:
            return 'Allgemein'
    
    def _erkenne_thema(self, frage_text: str) -> str:
        """
        Erkennt das Hauptthema einer Frage.
        
        :param frage_text: Text der Frage
        :type frage_text: str
        :returns: Hauptthema
        :rtype: str
        """
        frage_lower = frage_text.lower()
        
        # Themen-Mapping
        themen = {
            'authentication': ['auth', 'login', 'token', 'bearer', 'credential'],
            'headers': ['header', 'content-type', 'accept', 'authorization'],
            'methods': ['get', 'post', 'put', 'delete', 'patch'],
            'data': ['json', 'data', 'body', 'payload'],
            'response': ['response', 'status', 'code', 'error'],
            'testing': ['test', 'prüf', 'validier'],
        }
        
        for thema, keywords in themen.items():
            if any(keyword in frage_lower for keyword in keywords):
                return thema.title()
        
        return 'API-Grundlagen'
    
    def _erkenne_schlagwörter(self, titel: str) -> List[str]:
        """
        Erkennt Schlagwörter aus dem Aufgabentitel (sehr kurze LLM-Anfrage).
        
        :param titel: Aufgabentitel
        :type titel: str
        :returns: Liste der Schlagwörter
        :rtype: List[str]
        """
        # Fallback-Schlagwörter basierend auf Titel-Text
        fallback_tags = []
        titel_lower = titel.lower()
        
        if any(word in titel_lower for word in ['curl', 'request', 'http', 'api']):
            fallback_tags.extend(['HTTP', 'API', 'curl'])
        if any(word in titel_lower for word in ['json', 'data']):
            fallback_tags.append('JSON')
        if any(word in titel_lower for word in ['python', 'code']):
            fallback_tags.append('Python')
        if any(word in titel_lower for word in ['get', 'post', 'put', 'delete']):
            fallback_tags.append('REST')
        
        # Kurze LLM-Anfrage (nur wenn verfügbar und schnell)
        if self.current_model and len(fallback_tags) < 2:
            try:
                tag_prompt = f"Gib 2-3 Schlagwörter für diese Aufgabe: '{titel}'. Nur die Wörter, durch Komma getrennt:"
                antwort = self.llm_anfrage(tag_prompt, max_retries=1)
                if antwort and len(antwort) < 100:
                    llm_tags = [tag.strip() for tag in antwort.split(',')[:3]]
                    return llm_tags
            except:
                pass
        
        return fallback_tags or ['Programmierung']
    
    def _fallback_analyse(self, text: str) -> Dict:
        """
        Fallback-Analyse wenn LLM nicht verfügbar ist.
        
        :param text: PDF-Text
        :type text: str
        :returns: Basis-Struktur
        :rtype: Dict
        """
        print("🔄 Verwende Fallback-Analyse...")
        
        # Einfache Struktur-Erkennung
        aufgaben = []
        aufgaben_pattern = r'(\d+)[:.]?\s*([^\n]+)'
        matches = re.findall(aufgaben_pattern, text, re.MULTILINE)
        
        for i, (nummer, beschreibung) in enumerate(matches[:10], 1):
            if len(beschreibung.strip()) > 10:
                aufgabe = {
                    "nummer": int(nummer) if nummer.isdigit() else i,
                    "titel": beschreibung.strip()[:100],
                    "beschreibung": beschreibung.strip(),
                    "typ": "mixed",
                    "schlagwörter": ["PDF", "Konvertierung"],
                    "geschätzte_dauer": "5-10 Minuten"
                }
                aufgaben.append(aufgabe)
        
        return {
            "titel": "PDF zu Notebook Konvertierung",
            "beschreibung": "Automatisch konvertiertes Notebook aus PDF",
            "kategorie": "Allgemein",
            "schwierigkeit": "Anfänger",
            "aufgaben": aufgaben,
            "voraussetzungen": ["Python Grundlagen"],
            "lernziele": ["PDF-Inhalt in strukturierter Form bearbeiten"],
            "verwendete_bibliotheken": ["requests", "json", "pandas"]
        }
    
    def erstelle_fragen_notebook(self, fragen: List[Dict], titel: str = "PDF Fragen-Notebook") -> List[Dict]:
        """
        Erstellt ein strukturiertes Notebook mit allen extrahierten Fragen.
        
        :param fragen: Liste der extrahierten Fragen
        :type fragen: List[Dict]
        :param titel: Titel des Notebooks
        :type titel: str
        :returns: Liste der Notebook-Zellen
        :rtype: List[Dict]
        """
        zellen = []
        
        # 1. Titel und Übersicht
        titel_zelle = {
            "cell_type": "markdown",
            "metadata": {"tags": ["titel"]},
            "source": [
                f"# {titel}\n\n",
                f"**Anzahl Fragen:** {len(fragen)}\n",
                f"**Erstellt am:** {datetime.now().strftime('%d.%m.%Y um %H:%M')}\n\n",
                "## 📋 Übersicht der Fragen\n\n"
            ]
        }
        
        # Füge Übersicht hinzu
        for frage in fragen:
            titel_zelle["source"].append(f"{frage['nummer']}. **{frage['typ']}** - {frage['thema']} - {frage['frage'][:80]}...\n")
        
        titel_zelle["source"].append("\n---\n\n")
        zellen.append(titel_zelle)
        
        # 2. Setup-Zelle für Imports
        setup_zelle = {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {"tags": ["setup"]},
            "outputs": [],
            "source": [
                "# Setup und Imports\n",
                "import requests\n",
                "import json\n",
                "from datetime import datetime\n",
                "import pandas as pd\n\n",
                "print('📚 Notebook Setup erfolgreich')\n",
                "print(f'🕐 Gestartet um: {datetime.now()}')\n"
            ]
        }
        zellen.append(setup_zelle)
        
        # 3. Für jede Frage: Markdown + leere Code-Zelle
        for frage in fragen:
            # Markdown-Zelle mit der Frage
            frage_zelle = {
                "cell_type": "markdown",
                "metadata": {"tags": ["frage", f"frage-{frage['nummer']}"]},
                "source": [
                    f"## Frage {frage['nummer']}: {frage['typ']} - {frage['thema']}\n\n",
                    f"**Originaltext:**\n",
                    f"{frage['frage']}\n\n",
                    "**Hinweise:**\n",
                    "- Diese Frage wird vom LLM beantwortet\n",
                    "- Code-Beispiele werden automatisch generiert\n\n"
                ]
            }
            zellen.append(frage_zelle)
            
            # Platzhalter Code-Zelle (wird später vom LLM gefüllt)
            code_zelle = {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {"tags": ["antwort", f"frage-{frage['nummer']}"]},
                "outputs": [],
                "source": [
                    f"# Antwort für Frage {frage['nummer']}\n",
                    f"# Typ: {frage['typ']} | Thema: {frage['thema']}\n\n",
                    "# TODO: Wird vom LLM ausgefüllt...\n",
                    f"print('Bearbeite Frage {frage['nummer']}: {frage['typ']} - {frage['thema']}')\n"
                ]
            }
            zellen.append(code_zelle)
        
        print(f"✅ Basis-Notebook erstellt: {len(zellen)} Zellen")
        return zellen
    
    def beantworte_frage_mit_llm(self, frage: Dict) -> str:
        """
        Lässt das LLM eine einzelne Frage beantworten.
        
        :param frage: Fragen-Dictionary
        :type frage: Dict
        :returns: Generierte Antwort/Code
        :rtype: str
        """
        if not self.current_model:
            return self._fallback_antwort(frage)
        
        # Spezieller Prompt für cURL/API-Fragen
        if frage['typ'] in ['HTTP/API', 'REST']:
            prompt = self._erstelle_api_prompt(frage)
        else:
            prompt = self._erstelle_allgemeinen_prompt(frage)
        
        try:
            print(f"🤖 LLM beantwortet Frage {frage['nummer']}: {frage['typ']}")
            antwort = self.llm_anfrage(prompt, max_retries=2)
            
            if antwort:
                return self._bereinige_llm_antwort(antwort)
            else:
                return self._fallback_antwort(frage)
                
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"❌ LLM-Fehler bei Frage {frage['nummer']}: {e}")
            return self._fallback_antwort(frage)
    
    def _erstelle_api_prompt(self, frage: Dict) -> str:
        """
        Erstellt einen spezialisierten Prompt für API/HTTP-Fragen.
        
        :param frage: Fragen-Dictionary
        :type frage: Dict
        :returns: Prompt-Text
        :rtype: str
        """
        return f"""Du bist ein Experte für HTTP-APIs und cURL. Beantworte diese Frage mit praktischem Python-Code:

FRAGE: {frage['frage']}

Anforderungen:
- Verwende die requests-Bibliothek in Python
- Gib funktionsfähigen Code zurück
- Erkläre jeden Schritt kurz mit Kommentaren
- Zeige sowohl das requests-Äquivalent als auch das ursprüngliche cURL-Kommando als Kommentar
- Behandle Fehler angemessen
- Maximal 20 Zeilen Code

Antwort als Python-Code:"""
    
    def _erstelle_allgemeinen_prompt(self, frage: Dict) -> str:
        """
        Erstellt einen allgemeinen Prompt für andere Fragen.
        
        :param frage: Fragen-Dictionary
        :type frage: Dict
        :returns: Prompt-Text
        :rtype: str
        """
        return f"""Beantworte diese Frage mit praktischem Python-Code:

FRAGE: {frage['frage']}
TYP: {frage['typ']}
THEMA: {frage['thema']}

Anforderungen:
- Gib funktionsfähigen Python-Code zurück
- Kurze Kommentare für wichtige Schritte
- Verwende Standard-Bibliotheken wo möglich
- Maximal 15 Zeilen Code

Antwort als Python-Code:"""
    
    def _bereinige_llm_antwort(self, antwort: str) -> str:
        """
        Bereinigt und formatiert die LLM-Antwort.
        
        :param antwort: Rohe LLM-Antwort
        :type antwort: str
        :returns: Bereinigte Antwort
        :rtype: str
        """
        # Entferne Code-Block-Marker
        antwort = re.sub(r'```(?:python)?\n?', '', antwort)
        antwort = re.sub(r'```\s*$', '', antwort)
        
        # Bereinige Format
        antwort = antwort.strip()
        
        # Stelle sicher, dass es mit einem Kommentar beginnt
        lines = antwort.split('\n')
        if lines and not lines[0].strip().startswith('#'):
            lines.insert(0, '# LLM-generierte Antwort')
        
        return '\n'.join(lines)
    
    def _fallback_antwort(self, frage: Dict) -> str:
        """
        Fallback-Antwort wenn LLM nicht verfügbar.
        
        :param frage: Fragen-Dictionary
        :type frage: Dict
        :returns: Fallback-Code
        :rtype: str
        """
        return f"""# Fallback-Antwort für Frage {frage['nummer']}
# Typ: {frage['typ']} | Thema: {frage['thema']}

# TODO: Diese Frage manuell bearbeiten
# Originalfrage: {frage['frage']}

print('Diese Frage benötigt manuelle Bearbeitung')
print('Typ: {frage['typ']}')
print('Thema: {frage['thema']}')"""

    def generiere_erweiterte_zellen(self, struktur: Dict, pdf_text: str) -> List[Dict]:
        """
        Generiert erweiterte Notebook-Zellen basierend auf LLM-Analyse.
        DEPRECATED: Wird durch neues System ersetzt.
        
        :param struktur: Analysierte PDF-Struktur
        :type struktur: Dict
        :param pdf_text: Original PDF-Text für Referenz
        :type pdf_text: str
        :returns: Liste erweiterter Notebook-Zellen
        :rtype: List[Dict]
        """
        zellen = []
        
        # 1. Erweiterte Titel-Zelle
        titel_zelle = {
            "cell_type": "markdown",
            "metadata": {"tags": ["titel"]},
            "source": [
                f"# {struktur['titel']}\n\n",
                f"**Beschreibung:** {struktur['beschreibung']}\n\n",
                f"**Kategorie:** {struktur['kategorie']}\n",
                f"**Schwierigkeit:** {struktur['schwierigkeit']}\n",
                f"**Erstellt am:** {datetime.now().strftime('%d.%m.%Y um %H:%M')}\n\n",
                "---\n\n"
            ]
        }
        zellen.append(titel_zelle)
        
        # 2. Lernziele und Voraussetzungen
        if struktur.get('lernziele') or struktur.get('voraussetzungen'):
            info_zelle = {
                "cell_type": "markdown",
                "metadata": {"tags": ["info"]},
                "source": []
            }
            
            if struktur.get('lernziele'):
                info_zelle["source"].extend([
                    "## 🎯 Lernziele\n\n",
                    "Nach diesem Notebook kannst du:\n\n"
                ])
                for ziel in struktur['lernziele']:
                    info_zelle["source"].append(f"- {ziel}\n")
                info_zelle["source"].append("\n")
            
            if struktur.get('voraussetzungen'):
                info_zelle["source"].extend([
                    "## 📋 Voraussetzungen\n\n",
                    "Für dieses Notebook solltest du folgendes mitbringen:\n\n"
                ])
                for voraussetzung in struktur['voraussetzungen']:
                    info_zelle["source"].append(f"- {voraussetzung}\n")
                info_zelle["source"].append("\n")
            
            zellen.append(info_zelle)
        
        # 3. Erweiterte Import-Zelle
        bibliotheken = struktur.get('verwendete_bibliotheken', ['requests', 'json', 'pandas'])
        import_zelle = {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {"tags": ["setup", "imports"]},
            "outputs": [],
            "source": [
                "# Importiere benötigte Bibliotheken\n",
                "import sys\n",
                "from datetime import datetime\n",
                "from pathlib import Path\n\n",
                "# Standard Data Science Libraries\n"
            ]
        }
        
        # Dynamische Imports basierend auf erkannten Bibliotheken
        for lib in bibliotheken:
            if lib.lower() == 'requests':
                import_zelle["source"].append("import requests\n")
            elif lib.lower() == 'pandas':
                import_zelle["source"].append("import pandas as pd\n")
            elif lib.lower() == 'json':
                import_zelle["source"].append("import json\n")
            elif lib.lower() == 'numpy':
                import_zelle["source"].append("import numpy as np\n")
            elif lib.lower() in ['matplotlib', 'pyplot']:
                import_zelle["source"].append("import matplotlib.pyplot as plt\n")
            elif lib.lower() == 'seaborn':
                import_zelle["source"].append("import seaborn as sns\n")
        
        import_zelle["source"].extend([
            "\n# Konfiguration\n",
            "print(f'Python Version: {sys.version}')\n",
            "print(f'Notebook erstellt am: {datetime.now()}')\n"
        ])
        
        zellen.append(import_zelle)
        
        # 4. Aufgaben-Zellen mit LLM-Enhancement
        for aufgabe in struktur['aufgaben']:
            # Markdown-Zelle für Aufgabe
            markdown_zelle = {
                "cell_type": "markdown",
                "metadata": {"tags": ["aufgabe", f"aufgabe-{aufgabe['nummer']}"]},
                "source": [
                    f"## Aufgabe {aufgabe['nummer']}: {aufgabe['titel']}\n\n",
                    f"**Beschreibung:** {aufgabe['beschreibung']}\n\n"
                ]
            }
            
            if aufgabe.get('geschätzte_dauer'):
                markdown_zelle["source"].append(f"**⏱️ Geschätzte Dauer:** {aufgabe['geschätzte_dauer']}\n\n")
            
            if aufgabe.get('schlagwörter'):
                markdown_zelle["source"].append("**🏷️ Schlagwörter:** ")
                markdown_zelle["source"].append(", ".join(f"`{tag}`" for tag in aufgabe['schlagwörter']))
                markdown_zelle["source"].append("\n\n")
            
            zellen.append(markdown_zelle)
            
            # Code-Zelle für Lösung (mit LLM-generiertem Starter-Code)
            starter_code = self._generiere_starter_code(aufgabe, struktur)
            
            code_zelle = {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {
                    "tags": ["solution", f"aufgabe-{aufgabe['nummer']}"],
                    "scrolled": False
                },
                "outputs": [],
                "source": starter_code
            }
            zellen.append(code_zelle)
        
        # 5. Zusammenfassung und nächste Schritte
        zusammenfassung_zelle = {
            "cell_type": "markdown", 
            "metadata": {"tags": ["zusammenfassung"]},
            "source": [
                "## 🎉 Zusammenfassung\n\n",
                "In diesem Notebook haben wir folgende Themen behandelt:\n\n"
            ]
        }
        
        for aufgabe in struktur['aufgaben']:
            zusammenfassung_zelle["source"].append(f"- **Aufgabe {aufgabe['nummer']}:** {aufgabe['titel']}\n")
        
        zusammenfassung_zelle["source"].extend([
            "\n## 📚 Weiterführende Ressourcen\n\n",
            "- [Python Dokumentation](https://docs.python.org/3/)\n",
            "- [Requests Dokumentation](https://requests.readthedocs.io/)\n",
            "- [Pandas Dokumentation](https://pandas.pydata.org/docs/)\n\n",
            "---\n",
            f"**Erstellt mit PDF2Notebook Enhanced v2.0 am {datetime.now().strftime('%d.%m.%Y')}**\n"
        ])
        
        zellen.append(zusammenfassung_zelle)
        
        return zellen
    
    def _generiere_starter_code(self, aufgabe: Dict, struktur: Dict) -> List[str]:
        """
        Generiert intelligenten Starter-Code für eine Aufgabe.
        
        :param aufgabe: Aufgaben-Dictionary
        :type aufgabe: Dict
        :param struktur: Gesamt-Struktur
        :type struktur: Dict
        :returns: Starter-Code-Zeilen
        :rtype: List[str]
        """
        code_zeilen = [
            f"# Aufgabe {aufgabe['nummer']}: {aufgabe['titel']}\n",
            f"# {aufgabe['beschreibung']}\n\n"
        ]
        
        # Intelligenter Code basierend auf Schlagwörtern
        schlagwörter = [tag.lower() for tag in aufgabe.get('schlagwörter', [])]
        
        if any(word in schlagwörter for word in ['api', 'http', 'request']):
            code_zeilen.extend([
                "# HTTP-Request Beispiel\n",
                "# url = 'https://api.example.com/data'\n",
                "# response = requests.get(url)\n",
                "# print(f'Status Code: {response.status_code}')\n\n"
            ])
        
        if any(word in schlagwörter for word in ['json', 'data']):
            code_zeilen.extend([
                "# JSON-Datenverarbeitung\n",
                "# data = response.json()\n",
                "# print(json.dumps(data, indent=2))\n\n"
            ])
        
        if any(word in schlagwörter for word in ['pandas', 'dataframe', 'csv']):
            code_zeilen.extend([
                "# Pandas DataFrame Erstellung\n",
                "# df = pd.DataFrame(data)\n",
                "# print(df.head())\n\n"
            ])
        
        if any(word in schlagwörter for word in ['plot', 'visualisierung', 'chart']):
            code_zeilen.extend([
                "# Visualisierung\n",
                "# plt.figure(figsize=(10, 6))\n",
                "# plt.plot(df['x'], df['y'])\n",
                "# plt.show()\n\n"
            ])
        
        # Fallback für allgemeine Aufgaben
        if len(code_zeilen) <= 2:
            code_zeilen.extend([
                "# TODO: Implementierung hinzufügen\n",
                f"print('Starte Aufgabe {aufgabe['nummer']}: {aufgabe['titel']}')\n\n",
                "# Dein Code hier...\n"
            ])
        
        return code_zeilen
    
    def speichere_notebook(self, zellen: List[Dict], output_pfad: Path, struktur: Dict):
        """
        Speichert erweitertes Notebook mit Metadaten.
        
        :param zellen: Liste der Notebook-Zellen
        :type zellen: List[Dict]
        :param output_pfad: Pfad für die Ausgabedatei
        :type output_pfad: Path
        :param struktur: Struktur-Metadaten
        :type struktur: Dict
        """
        notebook_struktur = {
            "cells": zellen,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "codemirror_mode": {
                        "name": "ipython",
                        "version": 3
                    },
                    "file_extension": ".py",
                    "mimetype": "text/x-python",
                    "name": "python",
                    "nbconvert_exporter": "python",
                    "pygments_lexer": "ipython3",
                    "version": "3.13.0"
                },
                "toc": {
                    "base_numbering": 1,
                    "nav_menu": {},
                    "number_sections": True,
                    "sideBar": True,
                    "skip_h1_title": False,
                    "title_cell": "Inhaltsverzeichnis",
                    "title_sidebar": "Contents",
                    "toc_cell": False,
                    "toc_position": {},
                    "toc_section_display": True,
                    "toc_window_display": True
                },
                # Custom Metadaten
                "pdf2notebook": {
                    "version": "2.1",
                    "created": datetime.now().isoformat(),
                    "titel": struktur['titel'],
                    "kategorie": struktur['kategorie'], 
                    "schwierigkeit": struktur['schwierigkeit'],
                    "llm_provider": "ollama",
                    "llm_model": self.current_model or "fallback",
                    "aufgaben_anzahl": len(struktur['aufgaben'])
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        # Schöne Formatierung mit Einrückung
        with open(output_pfad, 'w', encoding='utf-8') as f:
            json.dump(notebook_struktur, f, indent=2, ensure_ascii=False)
    
    def konvertiere_pdf_enhanced_v2(self, pdf_pfad: Path) -> str:
        """
        Neue Konvertierung: Extrahiert Fragen, erstellt Notebook, dann LLM-Beantwortung.
        
        :param pdf_pfad: Pfad zur PDF-Datei
        :type pdf_pfad: Path
        :returns: Pfad zum erstellten Notebook
        :rtype: str
        """
        print(f"\n📄 Verarbeite mit neuem System: {pdf_pfad.name}")
        
        # Schritt 1: Text extrahieren
        print("📖 Schritt 1: Extrahiere PDF-Text...")
        text = self.extrahiere_pdf_text(pdf_pfad)
        if not text.strip():
            print("❌ Kein Text aus PDF extrahiert!")
            return ""
        print(f"✅ {len(text)} Zeichen extrahiert")
        
        # Schritt 2: Fragen präzise extrahieren
        print("🔍 Schritt 2: Extrahiere alle Fragen...")
        fragen = self.extrahiere_fragen_praezise(text)
        if not fragen:
            print("❌ Keine Fragen gefunden!")
            return ""
        
        # Statistik anzeigen
        typen_stats = {}
        for frage in fragen:
            typ = frage['typ']
            typen_stats[typ] = typen_stats.get(typ, 0) + 1
        
        print(f"� Fragen-Statistik:")
        for typ, anzahl in typen_stats.items():
            print(f"   {typ}: {anzahl}")
        
        # Schritt 3: Basis-Notebook erstellen
        print("📓 Schritt 3: Erstelle Basis-Notebook...")
        titel = f"{pdf_pfad.stem} - Fragen-Notebook"
        zellen = self.erstelle_fragen_notebook(fragen, titel)
        
        # Schritt 4: Notebook speichern
        zeitstempel = datetime.now().strftime("%Y%m%d_%H%M%S")
        notebook_name = f"{pdf_pfad.stem}_fragen_{zeitstempel}.ipynb"
        output_pfad = self.notebook_folder / notebook_name
        
        # Basis-Struktur für Metadaten
        basis_struktur = {
            "titel": titel,
            "kategorie": "PDF-Fragen",
            "schwierigkeit": "Variiert",
            "aufgaben": fragen
        }
        
        self.speichere_notebook(zellen, output_pfad, basis_struktur)
        print(f"💾 Basis-Notebook gespeichert: {output_pfad}")
        
        # Schritt 5: LLM initialisieren für Beantwortung
        print("🤖 Schritt 4: Initialisiere LLM für Beantwortung...")
        if not self.initialize_ollama():
            print("⚠️ LLM nicht verfügbar - Notebook mit Platzhaltern erstellt")
            return str(output_pfad)
        
        # Schritt 6: Jede Frage einzeln beantworten lassen
        print("🎯 Schritt 5: Beantworte Fragen mit LLM...")
        beantwortet = 0
        
        for i, frage in enumerate(fragen, 1):
            try:
                print(f"\n🔄 Bearbeite Frage {i}/{len(fragen)}: {frage['typ']}")
                antwort = self.beantworte_frage_mit_llm(frage)
                
                # Aktualisiere die entsprechende Code-Zelle im Notebook
                self.aktualisiere_frage_im_notebook(output_pfad, frage['nummer'], antwort)
                beantwortet += 1
                print(f"   ✅ Frage {i} beantwortet")
                
            except KeyboardInterrupt:
                print(f"\n🛑 Benutzer hat abgebrochen bei Frage {i}")
                break
            except Exception as e:
                print(f"   ❌ Fehler bei Frage {i}: {e}")
                continue
        
        print(f"\n🎉 Fertig! {beantwortet}/{len(fragen)} Fragen beantwortet")
        print(f"📓 Finales Notebook: {output_pfad}")
        
        return str(output_pfad)
    
    def aktualisiere_frage_im_notebook(self, notebook_pfad: Path, frage_nummer: int, antwort: str):
        """
        Aktualisiert eine spezifische Frage im Notebook mit der LLM-Antwort.
        
        :param notebook_pfad: Pfad zum Notebook
        :type notebook_pfad: Path
        :param frage_nummer: Nummer der Frage
        :type frage_nummer: int
        :param antwort: LLM-generierte Antwort
        :type antwort: str
        """
        try:
            # Notebook laden
            with open(notebook_pfad, 'r', encoding='utf-8') as f:
                notebook = json.load(f)
            
            # Finde die entsprechende Code-Zelle
            for zelle in notebook['cells']:
                if (zelle['cell_type'] == 'code' and 
                    'antwort' in zelle['metadata'].get('tags', []) and
                    f'frage-{frage_nummer}' in zelle['metadata'].get('tags', [])):
                    
                    # Ersetze den Platzhalter-Code mit der LLM-Antwort
                    zelle['source'] = antwort.split('\n')
                    # Stelle sicher, dass jede Zeile mit \n endet (außer der letzten)
                    for i in range(len(zelle['source']) - 1):
                        if not zelle['source'][i].endswith('\n'):
                            zelle['source'][i] += '\n'
                    break
            
            # Notebook zurückschreiben
            with open(notebook_pfad, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Fehler beim Aktualisieren von Frage {frage_nummer}: {e}")

    def konvertiere_pdf_enhanced(self, pdf_pfad: Path) -> str:
        """
        Legacy-Methode: Weiterleitung an neues System.
        
        :param pdf_pfad: Pfad zur PDF-Datei
        :type pdf_pfad: Path
        :returns: Pfad zum erstellten Notebook
        :rtype: str
        """
        print("🔄 Verwende neues Fragen-basiertes System...")
        return self.konvertiere_pdf_enhanced_v2(pdf_pfad)
    
    def cleanup(self):
        """
        Räumt Ressourcen auf (stoppt Ollama falls nötig).
        """
        if self.ollama_manager:
            self.ollama_manager.stop_ollama_server()


# Globale Variable für saubere Beendigung
converter_instance = None

def signal_handler(signum, frame):
    """
    Signal-Handler für saubere Beendigung mit Ctrl+C.
    
    :param signum: Signal-Nummer
    :type signum: int
    :param frame: Frame-Objekt
    :type frame: frame
    """
    print("\n\n🛑 Ctrl+C erkannt - beende Programm sauber...")
    
    if converter_instance:
        print("🧹 Räume Ressourcen auf...")
        converter_instance.cleanup()
    
    print("👋 Programm erfolgreich beendet.")
    sys.exit(0)

def hauptmenu_enhanced():
    """
    Hauptmenü-Funktion mit automatischer Ollama-Integration und Ctrl+C-Behandlung.
    """
    global converter_instance
    
    # Signal-Handler für Ctrl+C registrieren
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n" + "="*70)
    print("🚀 PDF zu Jupyter Notebook Konverter - Enhanced Edition v2.1")
    print("🤖 Automatische Ollama-Integration")
    print("💡 Beende mit Ctrl+C für saubere Bereinigung")
    print("="*70)
    
    # Enhanced Converter initialisieren
    converter = LLMNotebookEnhancer()
    converter_instance = converter  # Für Signal-Handler verfügbar machen
    
    try:
        while True:
            print("\n" + "="*70)
            print("📚 Enhanced PDF zu Notebook Konverter")
            print("="*70)
            
            # PDF-Dateien auflisten
            pdf_dateien = converter.liste_pdf_dateien()
            
            if not pdf_dateien:
                print("❌ Keine PDF-Dateien im PDF-Ordner gefunden!")
                print(f"📁 PDF-Ordner: {converter.pdf_folder}")
                break
            
            print(f"📁 Gefundene PDF-Dateien in '{converter.pdf_folder}':")
            print()
            
            for i, pdf_datei in enumerate(pdf_dateien, 1):
                dateigröße = pdf_datei.stat().st_size / 1024  # KB
                print(f"  {i:2d}. {pdf_datei.name:<40} ({dateigröße:.1f} KB)")
            
            print(f"  {len(pdf_dateien)+1:2d}. Alle PDFs konvertieren (Enhanced)")
            print(f"  {len(pdf_dateien)+2:2d}. Beenden")
            
            # Benutzer-Auswahl
            try:
                auswahl = input(f"\n🔢 Wähle eine Option (1-{len(pdf_dateien)+2}): ").strip()
                
                if not auswahl:
                    continue
                    
                auswahl_nr = int(auswahl)
                
                if auswahl_nr == len(pdf_dateien) + 2:  # Beenden
                    print("👋 Programm beendet.")
                    break
                    
                elif auswahl_nr == len(pdf_dateien) + 1:  # Alle konvertieren
                    print(f"\n🚀 Konvertiere alle {len(pdf_dateien)} PDF-Dateien (Enhanced)...")
                    erfolgreiche_konvertierungen = 0
                    
                    for pdf_datei in pdf_dateien:
                        try:
                            notebook_pfad = converter.konvertiere_pdf_enhanced(pdf_datei)
                            if notebook_pfad:
                                erfolgreiche_konvertierungen += 1
                        except Exception as e:
                            print(f"❌ Fehler bei {pdf_datei.name}: {e}")
                    
                    print(f"\n🎉 {erfolgreiche_konvertierungen}/{len(pdf_dateien)} PDFs erfolgreich konvertiert!")
                    
                elif 1 <= auswahl_nr <= len(pdf_dateien):  # Einzelne PDF konvertieren
                    ausgewählte_pdf = pdf_dateien[auswahl_nr - 1]
                    try:
                        notebook_pfad = converter.konvertiere_pdf_enhanced(ausgewählte_pdf)
                        if notebook_pfad:
                            print(f"\n🎉 Enhanced Konvertierung erfolgreich!")
                            print(f"📓 Notebook: {notebook_pfad}")
                    except Exception as e:
                        print(f"❌ Fehler bei der Konvertierung: {e}")
                        
                else:
                    print("❌ Ungültige Auswahl!")
                    
            except ValueError:
                print("❌ Bitte gib eine gültige Zahl ein!")
            except KeyboardInterrupt:
                print("\n\n� Ctrl+C erkannt - beende sauber...")
                break
            except Exception as e:
                print(f"❌ Unerwarteter Fehler: {e}")
                
    finally:
        # Cleanup beim Beenden
        print("🧹 Räume Ressourcen auf...")
        converter.cleanup()
        print("👋 Programm sauber beendet.")


if __name__ == "__main__":
    try:
        hauptmenu_enhanced()
    except KeyboardInterrupt:
        # Falls Signal-Handler nicht greift
        print("\n\n🛑 Programm durch Ctrl+C beendet.")
        if converter_instance:
            converter_instance.cleanup()
        sys.exit(0)