"""
Clase base para todos los scrapers

Proporciona funcionalidades comunes a todos los scrapers de OTIC,
evitando duplicación de código.
"""
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Set, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from src.config import get_config


class BaseScraper(ABC):
    """
    Clase base para todos los scrapers de licitaciones
    
    Proporciona métodos comunes para:
    - Inicialización de Selenium
    - Manejo de errores
    - Logging
    - Extracción de datos
    """
    
    def __init__(self, portal_name: str, url: str):
        """
        Inicializa el scraper
        
        Args:
            portal_name: Nombre del portal (ej: "Proforma")
            url: URL del portal a scrapear
        """
        self.portal_name = portal_name
        self.url = url
        self.logger = logging.getLogger(f"Scraper.{portal_name}")
        self.config = get_config()
        self.driver = None
        self.tender_links: Set[str] = set()
    
    def _init_driver(self) -> webdriver.Chrome:
        """
        Inicializa y configura el driver de Selenium
        
        Returns:
            Chrome WebDriver configurado
        """
        browser = self.config.scraper.browser
        self.logger.info(f"Inicializando navegador {browser} para {self.portal_name}...")
        
        if browser == "firefox":
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            from selenium.webdriver.firefox.service import Service as FirefoxService
            from webdriver_manager.firefox import GeckoDriverManager
            options = FirefoxOptions()
            options.page_load_strategy = self.config.scraper.page_load_strategy
            if self.config.scraper.headless:
                options.add_argument("--headless")
            driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
            
        elif browser == "edge":
            from selenium.webdriver.edge.options import Options as EdgeOptions
            from selenium.webdriver.edge.service import Service as EdgeService
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            options = EdgeOptions()
            options.page_load_strategy = self.config.scraper.page_load_strategy
            if self.config.scraper.headless:
                options.add_argument("headless")
            driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
            
        else:
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            from selenium.webdriver.chrome.service import Service as ChromeService
            from webdriver_manager.chrome import ChromeDriverManager
            options = ChromeOptions()
            options.page_load_strategy = self.config.scraper.page_load_strategy
            options.add_argument("--disable-gpu" if self.config.scraper.disable_gpu else "")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"user-agent={self.config.scraper.user_agent}")
            if self.config.scraper.headless:
                options.add_argument("--headless=new")
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            
        driver.set_page_load_timeout(self.config.scraper.timeout)
        
        return driver
    
    def start(self):
        """Inicia el driver"""
        self.driver = self._init_driver()
    
    def stop(self):
        """Detiene el driver y libera recursos"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info(f"Driver de {self.portal_name} cerrado correctamente")
            except Exception as e:
                self.logger.warning(f"Error cerrando driver: {e}")
    
    def wait_for_element(self, by: By, selector: str, timeout: int = 10):
        """
        Espera a que un elemento esté presente en la página
        
        Args:
            by: Tipo de selector (By.ID, By.CLASS_NAME, etc)
            selector: Selector CSS/XPATH
            timeout: Tiempo máximo de espera en segundos
            
        Returns:
            Elemento encontrado o None
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, selector)))
            return element
        except TimeoutException:
            self.logger.warning(f"Timeout esperando elemento: {selector}")
            return None
    
    def safe_get(self, url: str) -> bool:
        """
        Accede a una URL de forma segura
        
        Args:
            url: URL a acceder
            
        Returns:
            True si fue exitoso, False si hay error
        """
        try:
            self.logger.info(f"Accediendo a: {url}")
            self.driver.get(url)
            time.sleep(2)  # Espera para que la página cargue
            return True
        except Exception as e:
            self.logger.error(f"Error accediendo a {url}: {e}")
            return False
    
    def extract_text(self, element) -> str:
        """Extrae texto de un elemento de forma segura"""
        try:
            return element.text.strip() if element else ""
        except Exception as e:
            self.logger.warning(f"Error extrayendo texto: {e}")
            return ""
    
    def extract_attribute(self, element, attribute: str) -> str:
        """Extrae un atributo de un elemento de forma segura"""
        try:
            return element.get_attribute(attribute) or ""
        except Exception as e:
            self.logger.warning(f"Error extrayendo atributo {attribute}: {e}")
            return ""
    
    @abstractmethod
    def fetch_tender_links(self) -> Set[str]:
        """
        Obtiene los links de licitaciones del portal
        
        Este método debe ser implementado por cada scraper específico
        
        Returns:
            Set con los links encontrados
        """
        pass
    
    @abstractmethod
    def parse_tender(self, url: str) -> dict:
        """
        Parsea una licitación específica
        
        Este método debe ser implementado por cada scraper específico
        
        Args:
            url: URL de la licitación
            
        Returns:
            Diccionario con datos de la licitación
        """
        pass
    
    def execute(self) -> List[dict]:
        """
        Ejecuta el scraping completo
        
        Returns:
            Lista de licitaciones extraídas
        """
        licitaciones = []
        try:
            self.start()
            
            self.logger.info(f"🔍 Iniciando scraping de {self.portal_name}...")
            links = self.fetch_tender_links()
            
            self.logger.info(f"📊 Encontrados {len(links)} enlaces en {self.portal_name}")
            
            for link in links:
                try:
                    licitacion = self.parse_tender(link)
                    licitaciones.append(licitacion)
                except Exception as e:
                    self.logger.warning(f"Error parseando {link}: {e}")
            
            self.logger.info(f"✅ {self.portal_name} completado ({len(licitaciones)} licitaciones)")
            
        except Exception as e:
            self.logger.error(f"❌ Error en {self.portal_name}: {e}")
            raise
        finally:
            self.stop()
        
        return licitaciones
