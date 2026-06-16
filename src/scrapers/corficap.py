import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CorficapScraperSelenium:
    def __init__(self):
        self.url = "https://www.corficap.com/licitaciones/"  # actualizar
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
        enlaces = set()
        titulo = "Corficap"
        try:
            logging.info(f"Navegando {self.url}")
            self.driver.get(self.url)
            time.sleep(4)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if any(ext in href.lower() for ext in ['.pdf', '.xlsx', '.xls', '.docx']):
                    enlaces.add(href)

            return enlaces, titulo
        finally:
            self.driver.quit()


if __name__ == '__main__':
    s = CorficapScraperSelenium()
    print(s.fetch_tender_links())
