"""
env_config.py
Environment Configuration Manager für Mini Postman
🔄 Python lädt die env_config.py
🔍 Sie sucht nach einer .env Datei
📥 Sie lädt alle Umgebungsvariablen
⚙️ Alle Config-Klassen werden initialisiert
✅ Fertig! - Werte sind verfügbar
"""

import os
from typing import Optional, Union
import logging

# Versuche python-dotenv zu importieren (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()  # Lädt .env Datei
except ImportError:
    logging.warning("python-dotenv nicht installiert. .env Datei wird nicht automatisch geladen.")
    logging.info("Installieren Sie mit: pip install python-dotenv")

class EnvConfig:
    """Environment Configuration Manager"""
    
    @staticmethod
    def get(key: str, default: Optional[str] = None) -> Optional[str]:
        """Holt Umgebungsvariable mit optionalem Default-Wert"""
        return os.getenv(key, default)
    
    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        """Holt Boolean-Umgebungsvariable"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    @staticmethod
    def get_int(key: str, default: int = 0) -> int:
        """Holt Integer-Umgebungsvariable"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    @staticmethod
    def get_float(key: str, default: float = 0.0) -> float:
        """Holt Float-Umgebungsvariable"""
        try:
            return float(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    @staticmethod
    def require(key: str) -> str:
        """Erfordert eine Umgebungsvariable (Fehler wenn nicht vorhanden)"""
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Erforderliche Umgebungsvariable '{key}' nicht gefunden!")
        return value

# =============================================================================
# API KONFIGURATION
# =============================================================================

class APIConfig:
    """API-spezifische Konfiguration"""
    
    # LibreTranslate
    LIBRETRANSLATE_API_KEY = EnvConfig.get('LIBRETRANSLATE_API_KEY', '')
    LIBRETRANSLATE_BASE_URL = EnvConfig.get('LIBRETRANSLATE_BASE_URL', os.getenv('LIBRETRANSLATE_BASE_URL', 'http://192.168.178.185:5000'))
    
    # OpenAI (optional)
    OPENAI_API_KEY = EnvConfig.get('OPENAI_API_KEY', '')
    
    # Google Translate (optional)
    GOOGLE_TRANSLATE_API_KEY = EnvConfig.get('GOOGLE_TRANSLATE_API_KEY', '')
    
    # Azure (optional)
    AZURE_TRANSLATOR_KEY = EnvConfig.get('AZURE_TRANSLATOR_KEY', '')
    AZURE_TRANSLATOR_REGION = EnvConfig.get('AZURE_TRANSLATOR_REGION', '')
    
    # LinkedIn
    LINKEDIN_ACCESS_TOKEN = EnvConfig.get('LINKEDIN_ACCESS_TOKEN', '')
    LINKEDIN_CLIENT_ID = EnvConfig.get('LINKEDIN_CLIENT_ID', '')
    LINKEDIN_CLIENT_SECRET = EnvConfig.get('LINKEDIN_CLIENT_SECRET', '')
    LINKEDIN_API_VERSION = EnvConfig.get('LINKEDIN_API_VERSION', '202412')
    LINKEDIN_DEFAULT_TIMEOUT = EnvConfig.get_int('LINKEDIN_DEFAULT_TIMEOUT', 30)
    
    # Test APIs
    JSONPLACEHOLDER_BASE_URL = EnvConfig.get('JSONPLACEHOLDER_BASE_URL', 'https://jsonplaceholder.typicode.com')
    HTTPBIN_BASE_URL = EnvConfig.get('HTTPBIN_BASE_URL', 'https://httpbin.org')

# =============================================================================
# ANWENDUNGS-KONFIGURATION
# =============================================================================

class AppConfig:
    """Allgemeine Anwendungskonfiguration"""
    
    # Environment
    ENVIRONMENT = EnvConfig.get('ENVIRONMENT', 'development')
    DEBUG = EnvConfig.get_bool('DEBUG', True)
    
    # Logging
    LOG_LEVEL = EnvConfig.get('LOG_LEVEL', 'INFO')
    
    # Performance
    PERFORMANCE_WARNING_MS = EnvConfig.get_int('PERFORMANCE_WARNING_MS', 1000)
    PERFORMANCE_ERROR_MS = EnvConfig.get_int('PERFORMANCE_ERROR_MS', 5000)
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE = EnvConfig.get_int('MAX_REQUESTS_PER_MINUTE', 60)
    MAX_CONCURRENT_REQUESTS = EnvConfig.get_int('MAX_CONCURRENT_REQUESTS', 10)
    
    # Health Checks
    HEALTH_CHECK_INTERVAL = EnvConfig.get_int('HEALTH_CHECK_INTERVAL', 300)
    
    # Custom Headers
    CUSTOM_USER_AGENT = EnvConfig.get('CUSTOM_USER_AGENT', 'Mini-Postman/1.0.0')
    CUSTOM_API_HEADER = EnvConfig.get('CUSTOM_API_HEADER', 'X-Mini-Postman-Client')

# =============================================================================
# DATABASE KONFIGURATION
# =============================================================================

class DatabaseConfig:
    """Datenbank-Konfiguration (falls benötigt)"""
    
    HOST = EnvConfig.get('DB_HOST', 'localhost')
    PORT = EnvConfig.get_int('DB_PORT', 5432)
    NAME = EnvConfig.get('DB_NAME', 'mini_postman_db')
    USER = EnvConfig.get('DB_USER', '')
    PASSWORD = EnvConfig.get('DB_PASSWORD', '')
    
    @classmethod
    def get_connection_string(cls) -> str:
        """Erstellt Datenbank-Verbindungsstring"""
        if cls.USER and cls.PASSWORD:
            return f"postgresql://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.NAME}"
        else:
            return f"postgresql://{cls.HOST}:{cls.PORT}/{cls.NAME}"

# =============================================================================
# NOTIFICATION KONFIGURATION
# =============================================================================

class NotificationConfig:
    """Benachrichtigungs-Konfiguration"""
    
    # E-Mail
    SMTP_HOST = EnvConfig.get('SMTP_HOST', '')
    SMTP_PORT = EnvConfig.get_int('SMTP_PORT', 587)
    SMTP_USERNAME = EnvConfig.get('SMTP_USERNAME', '')
    SMTP_PASSWORD = EnvConfig.get('SMTP_PASSWORD', '')
    
    # Slack
    SLACK_WEBHOOK_URL = EnvConfig.get('SLACK_WEBHOOK_URL', '')
    
    # Discord
    DISCORD_WEBHOOK_URL = EnvConfig.get('DISCORD_WEBHOOK_URL', '')
    
    @classmethod
    def is_email_configured(cls) -> bool:
        """Prüft ob E-Mail-Konfiguration vollständig ist"""
        return bool(cls.SMTP_HOST and cls.SMTP_USERNAME and cls.SMTP_PASSWORD)
    
    @classmethod
    def is_slack_configured(cls) -> bool:
        """Prüft ob Slack-Konfiguration vorhanden ist"""
        return bool(cls.SLACK_WEBHOOK_URL)

# =============================================================================
# SECURITY KONFIGURATION
# =============================================================================

class SecurityConfig:
    """Sicherheits-Konfiguration"""
    
    JWT_SECRET_KEY = EnvConfig.get('JWT_SECRET_KEY', '')
    ENCRYPTION_KEY = EnvConfig.get('ENCRYPTION_KEY', '')
    
    @classmethod
    def is_jwt_configured(cls) -> bool:
        """Prüft ob JWT konfiguriert ist"""
        return bool(cls.JWT_SECRET_KEY and len(cls.JWT_SECRET_KEY) >= 32)

# =============================================================================
# HILFSFUNKTIONEN
# =============================================================================

def print_config_summary():
    """Gibt eine Zusammenfassung der Konfiguration aus (ohne Passwörter)"""
    print("=" * 60)
    print("MINI POSTMAN - KONFIGURATION")
    print("=" * 60)
    
    print(f"Environment: {AppConfig.ENVIRONMENT}")
    print(f"Debug Mode: {AppConfig.DEBUG}")
    print(f"Log Level: {AppConfig.LOG_LEVEL}")
    print()
    
    print("API Konfiguration:")
    print(f"  LibreTranslate URL: {APIConfig.LIBRETRANSLATE_BASE_URL}")
    print(f"  LibreTranslate API Key: {'✓ Konfiguriert' if APIConfig.LIBRETRANSLATE_API_KEY else '✗ Nicht konfiguriert'}")
    print(f"  OpenAI API Key: {'✓ Konfiguriert' if APIConfig.OPENAI_API_KEY else '✗ Nicht konfiguriert'}")
    print()
    
    print("Performance Settings:")
    print(f"  Warning Threshold: {AppConfig.PERFORMANCE_WARNING_MS}ms")
    print(f"  Error Threshold: {AppConfig.PERFORMANCE_ERROR_MS}ms")
    print(f"  Max Requests/Min: {AppConfig.MAX_REQUESTS_PER_MINUTE}")
    print()
    
    print("Benachrichtigungen:")
    print(f"  E-Mail: {'✓ Konfiguriert' if NotificationConfig.is_email_configured() else '✗ Nicht konfiguriert'}")
    print(f"  Slack: {'✓ Konfiguriert' if NotificationConfig.is_slack_configured() else '✗ Nicht konfiguriert'}")
    print()
    
    print("Sicherheit:")
    print(f"  JWT: {'✓ Konfiguriert' if SecurityConfig.is_jwt_configured() else '✗ Nicht konfiguriert'}")
    print("=" * 60)

def validate_required_config():
    """Validiert erforderliche Konfiguration"""
    errors = []
    
    # Hier können Sie kritische Konfigurationsprüfungen hinzufügen
    # Beispiel:
    # if not APIConfig.LIBRETRANSLATE_BASE_URL:
    #     errors.append("LIBRETRANSLATE_BASE_URL ist erforderlich")
    
    if errors:
        print("❌ KONFIGURATIONSFEHLER:")
        for error in errors:
            print(f"  - {error}")
        raise ValueError("Konfiguration unvollständig!")
    else:
        print("✅ Konfiguration erfolgreich validiert")

# =============================================================================
# EXPORT FÜR LEGACY CODE
# =============================================================================

# Für Rückwärtskompatibilität mit bestehenden Importen
CONFIG = {
    'version': '1.0',
    'author': 'Watchkido'
}

if __name__ == "__main__":
    # Test der Konfiguration
    print_config_summary()
    validate_required_config()