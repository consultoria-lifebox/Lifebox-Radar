import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AsimetScraperSelenium:
    def __init__(self):
        self.url = "https://www.oticasimet.cl/becas-laborales-v2"
        self.driver = self._init_driver()

    def _init_driver(self):
        logging.info("Inicializando el navegador automatizado para OTIC ASIMET (Versión Agresiva)...")
        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'eager'
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")            
        options.add_argument("--disable-dev-shm-usage") 
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--headless=new")           
        
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(45) # Le damos un poco más de tiempo por seguridad
        return driver

    def fetch_tender_links(self):
        logging.info(f"Conectando con el portal de ASIMET: {self.url}")
        titulo_proceso_encontrado = f"ASIMET - Portal Licitaciones Vigentes" 
        enlaces_encontrados = set()
        
        try:
            self.driver.get(self.url)
            wait = WebDriverWait(self.driver, 20)

            logging.info("Esperando y extrayendo todos los documentos descargables de la página...")

            # Usamos Selenium directamente para mayor fiabilidad
            xpath_docs = "//a[contains(@href, '.pdf') or contains(@href, '.docx') or contains(@href, '.doc') or contains(@href, '.xlsx') or contains(@href, '.xls') or contains(@href, '.zip')]"

            enlaces_elementos = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_docs)))
            
            for enlace in enlaces_elementos:
                href = enlace['href']
                if href:
                    url_completa = href if href.startswith("http") else f"https://www.oticasimet.cl{href}"
                    enlaces_encontrados.add(url_completa)

            if not enlaces_encontrados:
                # Si no hay enlaces, no es un error crítico, solo no hay datos.
                logging.info("No se encontraron documentos de licitación vigentes en ASIMET.")

            logging.info(f"Éxito: Se recolectaron {len(enlaces_encontrados)} documentos desde ASIMET.")
            return enlaces_encontrados, titulo_proceso_encontrado

        except TimeoutException:
            logging.error("Timeout en ASIMET")
            raise Exception("El sitio de la OTIC ASIMET tardó demasiado en cargar (Timeout). Revisa la conexión o la URL.")
        except WebDriverException as e:
            logging.error(f"Error de WebDriver en ASIMET: {e.msg}")
            raise Exception(f"Fallo en el navegador al abrir ASIMET: {e.msg}")
        except Exception as e:
            logging.error(f"Error crítico en el scraper de ASIMET: {e}")
            raise Exception(f"Error inesperado en ASIMET: {e}")

        finally:
            logging.info("Cerrando la instancia del navegador de ASIMET.")
            self.driver.quit()

if __name__ == "__main__":
    scraper = AsimetScraperSelenium()
    links, titulo = scraper.fetch_tender_links()
    print(f"\n📌 TÍTULO: {titulo}")
    for link in links:
        print(f"🔗 Documento: {link}")
