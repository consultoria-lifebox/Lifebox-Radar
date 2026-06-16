import logging
from selenium import webdriver
from bs4 import BeautifulSoup
import time

from src.config import get_config

logger = logging.getLogger(__name__)

class SimpleBaseScraper:
    """
    Clase base para scrapers genéricos que solo buscan enlaces de documentos en una página.
    """
    def __init__(self, portal_name: str, portal_url: str):
        self.portal_name = portal_name
        self.portal_url = portal_url
        self.driver = None
        self.config = get_config()

    def _init_driver(self):
        """Inicializa el webdriver de Chrome con configuración centralizada."""
        scraper_cfg = self.config.scraper
        browser = scraper_cfg.browser

        if browser == "firefox":
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            from selenium.webdriver.firefox.service import Service as FirefoxService
            from webdriver_manager.firefox import GeckoDriverManager
            options = FirefoxOptions()
            if scraper_cfg.headless:
                options.add_argument("--headless")
            service = FirefoxService(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
            
        elif browser == "edge":
            from selenium.webdriver.edge.options import Options as EdgeOptions
            from selenium.webdriver.edge.service import Service as EdgeService
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            options = EdgeOptions()
            if scraper_cfg.headless:
                options.add_argument("headless")
            service = EdgeService(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=options)
            
        else:
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            from selenium.webdriver.chrome.service import Service as ChromeService
            from webdriver_manager.chrome import ChromeDriverManager
            options = ChromeOptions()
            if scraper_cfg.headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument(f"user-agent={scraper_cfg.user_agent}")
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)

    def fetch_tender_links(self):
        """Obtiene enlaces a documentos de forma genérica."""
        links = set()
        try:
            self._init_driver()
            logger.info(f"Accediendo a {self.portal_url}...")
            self.driver.get(self.portal_url)
            time.sleep(5)  # Espera genérica para carga de JS
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(ext in href.lower() for ext in ['.pdf', '.xlsx', '.xls', '.docx', '.doc', '.zip', '.rar']):
                    links.add(self.portal_url + href if href.startswith('/') else href)
            logger.info(f"Se extrajeron {len(links)} enlaces de {self.portal_name}")
        except Exception as e:
            logger.error(f"Error en scraper de {self.portal_name}: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
        
        return links, f"Licitaciones Generales - {self.portal_name}"