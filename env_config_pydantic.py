

"""env_config_pydantic.py
Environment Configuration Manager für Mini Postman mit Pydantic

Hier wird die Konfiguration für die Anwendung definiert, einschließlich API-Keys, Datenbankverbindungen und mehr.
'''
| Vorteil                          | Erklärung                                                    |
| -------------------------------- | ------------------------------------------------------------ |
| ✅ Automatische Typprüfung        | Wenn `LINKEDIN_ACCESS_TOKEN` fehlt → sofortige Fehlermeldung |
| ✅ `.env` bleibt zentral          | Keine Hardcodierung                                          |
| ✅ Zugriff über `Config.linkedin` | Einheitliche Struktur                                        |
| ✅ Ready für Docker/CI            | Keine Änderungen nötig                                       |
| ✅ Erweiterbar                    | Du kannst leicht Slack, Discord, usw. ergänzen               |
'''
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


# =============================================================================
# APP
# =============================================================================
class AppConfig(BaseSettings):
    environment: str = Field("development", description="App Umgebung (development/production)")
    debug: bool = Field(True, description="Debug-Modus aktivieren")
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# =============================================================================
# API libretranslate
# =============================================================================
class APIConfig(BaseSettings):
    libretranslate_api_key: str | None = None
    libretranslate_base_url: str = "http://localhost:5000"
    openai_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env")


# =============================================================================
# DATABASE
# =============================================================================
class DatabaseConfig(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "app_db"
    db_user: str | None = None
    db_password: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def connection_string(self) -> str:
        if self.db_user and self.db_password:
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        return f"postgresql://{self.db_host}:{self.db_port}/{self.db_name}"


# =============================================================================
# SECURITY
# =============================================================================
class SecurityConfig(BaseSettings):
    jwt_secret_key: str | None = None
    encryption_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env")


# =============================================================================
# LINKEDIN
# =============================================================================
class LinkedInConfig(BaseSettings):
    """LinkedIn-spezifische Konfiguration"""
    
    linkedin_access_token: str
    linkedin_client_id: str | None = None
    linkedin_client_secret: str | None = None
    
    linkedin_api_version: str = "202412"
    linkedin_default_timeout: int = 30

    model_config = SettingsConfigDict(env_file=".env")


# =============================================================================
# KOMBINIERTE KONFIG
# =============================================================================
class Config:
    app = AppConfig()
    api = APIConfig()
    db = DatabaseConfig()
    security = SecurityConfig()
    linkedin = LinkedInConfig()

    @staticmethod
    def summary():
        print("=== CONFIG SUMMARY ===")
        print(f"Environment: {Config.app.environment}")
        print(f"Debug: {Config.app.debug}")
        print(f"LibreTranslate URL: {Config.api.libretranslate_base_url}")
        print(f"DB: {Config.db.connection_string}")
        print(f"JWT vorhanden: {bool(Config.security.jwt_secret_key)}")
        print(f"LinkedIn Token vorhanden: {bool(Config.linkedin.linkedin_access_token)}")


if __name__ == "__main__":
    Config.summary()
