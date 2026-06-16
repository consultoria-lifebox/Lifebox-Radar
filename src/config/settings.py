"""
Configuración centralizada para Lifebox Radar

Este módulo maneja todas las variables de entorno y configuraciones globales
del proyecto.
"""
import os
import logging
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class GoogleCloudConfig:
    """Configuración de Google Cloud"""
    project_id: str = os.getenv("GCP_PROJECT_ID", "proyecto-life-box-licitaciones")
    credentials_path: str = os.getenv("GCP_CREDENTIALS_PATH", "credenciales_gcp.json")
    dataset_id: str = "licitaciones"
    table_opportunities: str = "oportunidades"
    table_status: str = "estado_scrapers"


@dataclass
class TelegramConfig:
    """Configuración de notificaciones Telegram"""
    token: Optional[str] = os.getenv("TELEGRAM_TOKEN")
    chat_id: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")
    
    def is_configured(self) -> bool:
        """Verifica si Telegram está correctamente configurado"""
        return self.token is not None and self.chat_id is not None


@dataclass
class GroqConfig:
    """Configuración de la API de Groq / Graq"""
    api_key: Optional[str] = os.getenv("GROQ_API_KEY")


@dataclass
class ExternalConfig:
    """Configuración externa y de licencia"""
    url_gist: Optional[str] = os.getenv("URL_GIST")


@dataclass
class LoggingConfig:
    """Configuración de logging"""
    level: str = os.getenv("LOG_LEVEL", "INFO")
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file: str = "logs/lifebox_radar.log"


@dataclass
class ScraperConfig:
    """Configuración de scrapers"""
    browser: str = os.getenv("SCRAPER_BROWSER", "chrome").lower()
    timeout: int = 30  # segundos
    headless: bool = True
    disable_gpu: bool = True
    page_load_strategy: str = "eager"
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class Config:
    """Configuración centralizada del proyecto"""
    
    def __init__(self):
        self.gcp = GoogleCloudConfig()
        self.telegram = TelegramConfig()
        self.groq = GroqConfig()
        self.external = ExternalConfig()
        self.logging = LoggingConfig()
        self.scraper = ScraperConfig()
        self._validate()
    
    def _validate(self):
        """Valida que las configuraciones críticas estén disponibles"""
        if not os.path.exists(self.gcp.credentials_path):
            logging.warning(
                f"⚠️ Credenciales de GCP no encontradas en {self.gcp.credentials_path}"
            )
        
        if not self.telegram.is_configured():
            logging.warning(
                "⚠️ Telegram no configurado. Las notificaciones estarán deshabilitadas."
            )

        if not self.groq.api_key:
            logging.warning(
                "⚠️ GROQ_API_KEY no configurada. El análisis de documentos quedará limitado."
            )

        if not self.external.url_gist:
            logging.warning(
                "⚠️ URL_GIST no configurada. La validación de licencia no funcionará."
            )
    
    def to_dict(self) -> dict:
        """Retorna la configuración como diccionario"""
        return {
            "gcp": self.gcp.__dict__,
            "telegram": self.telegram.__dict__,
            "groq": self.groq.__dict__,
            "external": self.external.__dict__,
            "logging": self.logging.__dict__,
            "scraper": self.scraper.__dict__,
        }


# Instancia global de configuración
_config = None


def get_config() -> Config:
    """Retorna la instancia global de configuración"""
    global _config
    if _config is None:
        _config = Config()
    return _config
