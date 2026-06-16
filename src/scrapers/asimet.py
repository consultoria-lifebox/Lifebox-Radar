import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class AsimetScraperSelenium:
    """Plantilla de scraper para Asimet. Reemplazar `self.url` y selectores según diseño real."""
    def __init__(self):
        self.url = "https://www.asimet.cl/licitaciones/"  # <- actualizar si cambia
        self.driver = self._init_driver()

    def _init_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent=Mozilla/5.0')

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(30)
        return driver

    def fetch_tender_links(self):
        enlaces_encontrados = set()
        titulo = "Asimet"
        try:
            logging.info(f"Navegando {self.url}")
            self.driver.get(self.url)
            time.sleep(4)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if any(ext in href.lower() for ext in ['.pdf', '.xlsx', '.xls', '.docx', '.doc']):
                    enlaces_encontrados.add(href)

            # intenta sacar un título descriptivo
            h1 = soup.find('h1')
            if h1 and h1.get_text(strip=True):
                titulo = h1.get_text(strip=True)

            if not enlaces_encontrados:
                logging.info("No se encontraron enlaces directos; revisar selectores o cargar JS adicional.")

            return enlaces_encontrados, titulo

        except TimeoutException:
            logging.error("Timeout en Asimet")
            raise
        except WebDriverException:
            logging.error("WebDriver error en Asimet")
            raise
        finally:
            self.driver.quit()


if __name__ == '__main__':
    s = AsimetScraperSelenium()
    links, t = s.fetch_tender_links()
    print(t, len(links))
