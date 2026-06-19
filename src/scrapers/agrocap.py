import logging
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException

class AgrocapScraperSelenium:
    def __init__(self):
        self.url_principal = "https://www.agrocap.cl/webid/"
        
        self.opciones = Options()
        self.opciones.page_load_strategy = 'normal'
        self.opciones.add_argument("--disable-gpu")
        self.opciones.add_argument("--headless=new")
        self.opciones.add_argument("--no-sandbox")
        self.opciones.add_argument("--disable-dev-shm-usage")
        self.opciones.add_argument("--window-size=1920,1080")
        self.opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
        
    def fetch_tender_links(self):
        anio_actual = str(datetime.now().year)
        logging.info(f"Iniciando exploración en Agrocap: {self.url_principal}")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.opciones)
        driver.set_page_load_timeout(60)
        wait = WebDriverWait(driver, 30)
        enlaces = set()
        titulo_encontrado = f"Agrocap - Becas Laborales {anio_actual}"
        
        try:
            driver.get(self.url_principal)
            time.sleep(5)
            
            # === Búsqueda directa de documentos en la página principal ===
            logging.info("Buscando documentos directamente en la página principal...")
            
            # Extraer todos los enlaces a PDFs y documentos
            self.extraer_documentos(driver, enlaces)
            
            if not enlaces:
                logging.warning("No se encontraron documentos en la página principal. Intentando en la sección 'Becas Laborales'...")
                try:
                    # Plan B: Navegar a la sección de becas si existe
                    xpath_general = "//a[contains(text(), 'Becas Laborales')]"
                    elem = wait.until(EC.presence_of_element_located((By.XPATH, xpath_general)))
                    url_becas = elem.get_attribute("href")
                    if url_becas:
                        driver.get(url_becas)
                        time.sleep(5)
                        self.extraer_documentos(driver, enlaces)
                except Exception as e_becas:
                    logging.info(f"No se pudo navegar a la sección de becas: {e_becas}")

            if not enlaces:
                logging.info("No se encontraron documentos de licitación vigentes en Agrocap.")
                
        except TimeoutException:
            logging.error("Timeout en Agrocap - Página muy lenta o cambió de estructura")
            raise Exception("La página web de Agrocap está caída o cambió su diseño (Timeout).")
        except Exception as e:
            logging.error(f"Error en Agrocap: {e}")
            raise Exception(f"Error inesperado en Agrocap: {e}")
        finally:
            driver.quit()
            
        return enlaces, titulo_encontrado

    def extraer_documentos(self, driver, enlaces):
        """Extrae enlaces de documentos (PDF, XLSX, ZIP, etc.)"""
        try:
            # Buscar todos los enlaces que terminen en extensiones de archivos
            xpath_docs = "//a[contains(@href, '.pdf') or contains(@href, '.xlsx') or contains(@href, '.zip') or contains(@href, '.doc') or contains(@href, '.docx')]"
            documentos = driver.find_elements(By.XPATH, xpath_docs)
            
            for doc in documentos:
                href = doc.get_attribute("href")
                if href:
                    enlaces.add(href)
        except Exception as e:
            logging.warning(f"Error extrayendo documentos: {e}")

# Bloque de prueba local
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = AgrocapScraperSelenium()
    links, titulo = scraper.fetch_tender_links()
    print(f"\n📌 {titulo}")
    for link in sorted(links):
        print(f"- {link}")
