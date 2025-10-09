#!/usr/bin/env python3
"""
PDF zu Jupyter Notebook Konverter
Ermöglicht die Auswahl und Konvertierung von PDF-Dateien in strukturierte Jupyter Notebooks.

Autor: Frank Albrecht
Datum: 2025-10-08
Version: 1.0
"""

import os
import sys
import json
import PyPDF2
from pathlib import Path
from datetime import datetime
import re

# Konfiguration aus config.py importieren
try:
    from config import CONFIG
    PDF_FOLDER = CONFIG.get('PDF_FOLDER', './pdf')
    NOTEBOOK_FOLDER = CONFIG.get('NOTEBOOK_FOLDER', './notebook')
except ImportError:
    # Fallback-Konfiguration
    PDF_FOLDER = './pdf'
    NOTEBOOK_FOLDER = './notebook'

class PDFNotebookConverter:
    """
    Konvertiert PDF-Dateien in strukturierte Jupyter Notebooks.
    
    Diese Klasse ermöglicht es, PDF-Dateien aus einem Ordner auszuwählen
    und in gut strukturierte Jupyter Notebooks umzuwandeln.
    """
    
    def __init__(self, pdf_folder: str = PDF_FOLDER, notebook_folder: str = NOTEBOOK_FOLDER):
        """
        Initialisiert den PDF-zu-Notebook-Konverter.
        
        :param pdf_folder: Pfad zum PDF-Ordner
        :type pdf_folder: str
        :param notebook_folder: Pfad zum Notebook-Ordner  
        :type notebook_folder: str
        """
        self.pdf_folder = Path(pdf_folder)
        self.notebook_folder = Path(notebook_folder)
        
        # Ordner erstellen falls sie nicht existieren
        self.notebook_folder.mkdir(parents=True, exist_ok=True)
    
    def liste_pdf_dateien(self) -> list:
        """
        Listet alle PDF-Dateien im PDF-Ordner auf.
        
        :returns: Liste der gefundenen PDF-Dateien
        :rtype: list
        """
        if not self.pdf_folder.exists():
            print(f"❌ PDF-Ordner '{self.pdf_folder}' existiert nicht!")
            return []
        
        pdf_dateien = list(self.pdf_folder.glob("*.pdf"))
        return sorted(pdf_dateien)
    
    def extrahiere_pdf_text(self, pdf_pfad: Path) -> str:
        """
        Extrahiert Text aus einer PDF-Datei.
        
        :param pdf_pfad: Pfad zur PDF-Datei
        :type pdf_pfad: Path
        :returns: Extrahierter Text aus der PDF
        :rtype: str
        :raises FileNotFoundError: Wenn PDF-Datei nicht gefunden wird
        """
        text = ""
        
        try:
            # Versuche zuerst mit PyPDF2
            with open(pdf_pfad, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + '\n'
            
            if not text.strip():
                raise Exception("Kein Text mit PyPDF2 extrahiert")
                
        except Exception as e:
            print(f"⚠️ PyPDF2 Fehler: {e}")
            print("🔄 Versuche mit pdfplumber...")
            
            try:
                import pdfplumber
                with pdfplumber.open(pdf_pfad) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + '\n'
            except ImportError:
                print("❌ pdfplumber ist nicht installiert!")
                print("Installiere es mit: pip install pdfplumber")
                return ""
            except Exception as e2:
                print(f"❌ pdfplumber Fehler: {e2}")
                return ""
        
        return text
    
    def analysiere_pdf_struktur(self, text: str) -> dict:
        """
        Analysiert die Struktur des PDF-Textes und identifiziert Aufgaben/Fragen.
        
        :param text: Extrahierter PDF-Text
        :type text: str  
        :returns: Strukturierte Daten mit Aufgaben und Beschreibungen
        :rtype: dict
        """
        struktur = {
            "titel": "PDF zu Notebook Konvertierung",
            "datum": datetime.now().isoformat(),
            "aufgaben": []
        }
        
        # Suche nach Aufgaben/Nummerierten Abschnitten
        aufgaben_pattern = r'(\d+)[:.]?\s*([^\n]+)'
        matches = re.findall(aufgaben_pattern, text, re.MULTILINE)
        
        for nummer, beschreibung in matches:
            if len(beschreibung.strip()) > 10:  # Nur sinnvolle Beschreibungen
                aufgabe = {
                    "nummer": int(nummer),
                    "titel": beschreibung.strip(),
                    "text": ""
                }
                struktur["aufgaben"].append(aufgabe)
        
        # Falls keine nummerierten Aufgaben gefunden, Text in Blöcke aufteilen
        if not struktur["aufgaben"]:
            textblöcke = [block.strip() for block in text.split('\n\n') if block.strip()]
            for i, block in enumerate(textblöcke[:10], 1):  # Max 10 Blöcke
                if len(block) > 20:
                    aufgabe = {
                        "nummer": i,
                        "titel": f"Abschnitt {i}",
                        "text": block
                    }
                    struktur["aufgaben"].append(aufgabe)
        
        return struktur
    
    def erstelle_notebook_zellen(self, struktur: dict) -> list:
        """
        Erstellt Notebook-Zellen basierend auf der PDF-Struktur.
        
        :param struktur: Analysierte PDF-Struktur
        :type struktur: dict
        :returns: Liste der Notebook-Zellen
        :rtype: list
        """
        zellen = []
        
        # Titel-Zelle
        titel_zelle = {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                f"# {struktur['titel']}\n",
                f"\n",
                f"**Erstellt am:** {struktur['datum'][:10]}\n",
                f"**Quelle:** PDF-Konvertierung\n\n"
            ]
        }
        zellen.append(titel_zelle)
        
        # Import-Zelle
        import_zelle = {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Importiere benötigte Bibliotheken\n",
                "import requests\n", 
                "import json\n",
                "import pandas as pd\n",
                "from datetime import datetime\n"
            ]
        }
        zellen.append(import_zelle)
        
        # Aufgaben-Zellen
        for aufgabe in struktur["aufgaben"]:
            # Markdown-Zelle für Aufgabenbeschreibung
            markdown_zelle = {
                "cell_type": "markdown", 
                "metadata": {},
                "source": [
                    f"## Aufgabe {aufgabe['nummer']}: {aufgabe['titel']}\n\n",
                    f"{aufgabe['text']}\n\n" if aufgabe['text'] else ""
                ]
            }
            zellen.append(markdown_zelle)
            
            # Code-Zelle für Lösung
            code_zelle = {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    f"# Aufgabe {aufgabe['nummer']}: {aufgabe['titel']}\n",
                    "# TODO: Implementierung hinzufügen\n",
                    f"print('Aufgabe {aufgabe['nummer']} - {aufgabe['titel']}')\n"
                ]
            }
            zellen.append(code_zelle)
        
        return zellen
    
    def speichere_notebook(self, zellen: list, output_pfad: Path):
        """
        Speichert die Zellen als Jupyter Notebook.
        
        :param zellen: Liste der Notebook-Zellen
        :type zellen: list
        :param output_pfad: Pfad für die Ausgabedatei
        :type output_pfad: Path
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
                    "name": "python",
                    "version": "3.13.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        with open(output_pfad, 'w', encoding='utf-8') as f:
            json.dump(notebook_struktur, f, indent=2, ensure_ascii=False)
    
    def konvertiere_pdf(self, pdf_pfad: Path) -> str:
        """
        Konvertiert eine PDF-Datei in ein Jupyter Notebook.
        
        :param pdf_pfad: Pfad zur PDF-Datei
        :type pdf_pfad: Path
        :returns: Pfad zum erstellten Notebook
        :rtype: str
        """
        print(f"📄 Verarbeite: {pdf_pfad.name}")
        
        # Text extrahieren
        text = self.extrahiere_pdf_text(pdf_pfad)
        if not text.strip():
            print("❌ Kein Text aus PDF extrahiert!")
            return ""
        
        print(f"✅ Text extrahiert: {len(text)} Zeichen")
        
        # Struktur analysieren
        struktur = self.analysiere_pdf_struktur(text)
        print(f"📋 Gefundene Aufgaben: {len(struktur['aufgaben'])}")
        
        # Notebook-Zellen erstellen
        zellen = self.erstelle_notebook_zellen(struktur)
        
        # Output-Dateiname erstellen
        notebook_name = pdf_pfad.stem + "_notebook.ipynb"
        output_pfad = self.notebook_folder / notebook_name
        
        # Notebook speichern
        self.speichere_notebook(zellen, output_pfad)
        
        print(f"💾 Notebook gespeichert: {output_pfad}")
        return str(output_pfad)

def hauptmenu():
    """
    Zeigt das Hauptmenü und behandelt die Benutzerinteraktion.
    """
    converter = PDFNotebookConverter()
    
    while True:
        print("\n" + "="*60)
        print("📚 PDF zu Jupyter Notebook Konverter")
        print("="*60)
        
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
        
        print(f"  {len(pdf_dateien)+1:2d}. Alle PDFs konvertieren")
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
                print(f"\n🔄 Konvertiere alle {len(pdf_dateien)} PDF-Dateien...")
                erfolgreiche_konvertierungen = 0
                
                for pdf_datei in pdf_dateien:
                    try:
                        notebook_pfad = converter.konvertiere_pdf(pdf_datei)
                        if notebook_pfad:
                            erfolgreiche_konvertierungen += 1
                    except Exception as e:
                        print(f"❌ Fehler bei {pdf_datei.name}: {e}")
                
                print(f"\n✅ {erfolgreiche_konvertierungen}/{len(pdf_dateien)} PDFs erfolgreich konvertiert!")
                
            elif 1 <= auswahl_nr <= len(pdf_dateien):  # Einzelne PDF konvertieren
                ausgewählte_pdf = pdf_dateien[auswahl_nr - 1]
                try:
                    notebook_pfad = converter.konvertiere_pdf(ausgewählte_pdf)
                    if notebook_pfad:
                        print(f"\n✅ Konvertierung erfolgreich abgeschlossen!")
                        print(f"📓 Notebook: {notebook_pfad}")
                except Exception as e:
                    print(f"❌ Fehler bei der Konvertierung: {e}")
                    
            else:
                print("❌ Ungültige Auswahl!")
                
        except ValueError:
            print("❌ Bitte gib eine gültige Zahl ein!")
        except KeyboardInterrupt:
            print("\n\n👋 Programm durch Benutzer beendet.")
            break
        except Exception as e:
            print(f"❌ Unerwarteter Fehler: {e}")

if __name__ == "__main__":
    hauptmenu()