# PDF2Notebook Enhanced - Konfiguration
# Diese Datei kann angepasst werden um verschiedene LLM-Provider zu konfigurieren

# Standard-Ordner-Struktur
PDF_FOLDER = "../pdf"      # Relativ vom Script-Ort
NOTEBOOK_FOLDER = "../notebook"

# LLM-Konfigurationen
LLM_CONFIGS = {
    "ollama": {
        "base_url": "http://localhost:11434/api/generate",
        "model": "qwen2.5-coder:latest",  # Gut für Code-Generierung
        "alternative_models": [
            "llama3.2:latest",
            "deepseek-r1:7b",
            "qwen2.5:7b"
        ],
        "timeout": 60,
        "temperature": 0.7,
        "max_tokens": 2000
    },
    
    "openai": {
        "base_url": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-3.5-turbo",
        "alternative_models": [
            "gpt-4",
            "gpt-4-turbo"
        ],
        "timeout": 30,
        "temperature": 0.7,
        "max_tokens": 2000
    },
    
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1/messages",
        "model": "claude-3-sonnet-20240229", 
        "alternative_models": [
            "claude-3-haiku-20240307",
            "claude-3-opus-20240229"
        ],
        "timeout": 30,
        "temperature": 0.7,
        "max_tokens": 2000
    }
}

# PDF-Parsing-Einstellungen
PDF_SETTINGS = {
    "max_text_length": 4000,  # Begrenzung für LLM-Input
    "clean_unicode": True,     # Unicode-Zeichen bereinigen
    "remove_page_numbers": True,
    "min_text_length": 50,    # Mindestlänge für validen Text
}

# Notebook-Template-Einstellungen  
NOTEBOOK_SETTINGS = {
    "add_toc": True,           # Table of Contents hinzufügen
    "add_timestamps": True,    # Zeitstempel in Dateinamen
    "add_metadata": True,      # Erweiterte Metadaten
    "use_emoji": True,         # Emojis in Überschriften
    "add_tags": True,          # Tags für bessere Organisation
    "estimated_time": True,    # Geschätzte Bearbeitungszeiten
}

# Ausgabe-Formatierung
OUTPUT_SETTINGS = {
    "indent_json": 2,          # JSON-Einrückung
    "ensure_ascii": False,     # Unicode-Zeichen erlauben
    "add_learning_objectives": True,
    "add_prerequisites": True,
    "add_resources": True,
    "add_summary": True
}

# Fallback-Einstellungen (ohne LLM)
FALLBACK_SETTINGS = {
    "max_tasks": 10,           # Maximale Anzahl erkannter Aufgaben
    "min_task_length": 20,     # Minimale Länge für Aufgabentitel
    "default_category": "Allgemein",
    "default_difficulty": "Anfänger",
    "default_duration": "5-10 Minuten"
}

# Code-Generierung-Templates
CODE_TEMPLATES = {
    "api_request": {
        "imports": ["requests", "json"],
        "pattern": "requests.get(url)",
        "error_handling": True
    },
    "data_processing": {
        "imports": ["pandas", "json"],
        "pattern": "pd.DataFrame(data)",
        "error_handling": True
    },
    "file_operations": {
        "imports": ["pathlib", "json"],
        "pattern": "Path('file').write_text(data)",
        "error_handling": True
    },
    "visualization": {
        "imports": ["matplotlib.pyplot", "seaborn"],
        "pattern": "plt.plot(x, y)",
        "error_handling": False
    }
}

# Debug-Einstellungen
DEBUG_SETTINGS = {
    "verbose_logging": False,
    "save_raw_pdf_text": False,
    "save_llm_prompts": False,
    "show_token_usage": False
}