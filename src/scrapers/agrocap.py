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
        self.opciones.page_load_strategy = 'eager'
        self.opciones.add_argument("--disable-gpu")
        self.opciones.add_argument("--headless=new")
        self.opciones.add_argument("--no-sandbox")
        self.opciones.add_argument("--disable-dev-shm-usage")
        self.opciones.add_argument("--window-size=1920,1080")
        self.opciones.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
        
    def fetch_tender_links(self):
        anio_actual = str(datetime.now().year)
        logging.info(f"Iniciando exploración en Agrocap: {self.url_principal}")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.opciones)
        driver.set_page_load_timeout(60)
        wait = WebDriverWait(driver, 25)
        enlaces = set()
        titulo_encontrado = f"Agrocap - Becas Laborales {anio_actual}"
        
        try:
            driver.get(self.url_principal)
            time.sleep(5)
            
            # === Buscar el enlace a "Becas Laborales" del año actual o anterior ===
            logging.info("Buscando sección de Becas Laborales...")
            posibles_anios = [anio_actual, str(int(anio_actual)-1)]
            
            url_becas = None
            for anio in posibles_anios:
                try:
                    # Buscar enlaces que contengan "Becas Laborales" + año
                    xpath_becas = f"//a[contains(text(), 'Becas Laborales') and contains(text(), '{anio}')]"
                    elementos = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_becas)))
                    
                    for elem in elementos:
                        href = elem.get_attribute("href")
                        if href:
                            url_becas = href
                            logging.info(f"✅ Encontrada página de Becas Laborales {anio}: {url_becas}")
                            break
                except:
                    continue
                    
            if not url_becas:
                # Búsqueda más amplia si no encuentra por año
                try:
                    xpath_general = "//a[contains(text(), 'Becas Laborales')]"
                    elem = wait.until(EC.presence_of_element_located((By.XPATH, xpath_general)))
                    url_becas = elem.get_attribute("href")
                except:
                    raise Exception("No se encontró la sección de Becas Laborales")
            
            # Ir a la página de becas
            driver.get(url_becas)
            time.sleep(5)
            
            # Extraer todos los enlaces a PDFs y documentos
            self.extraer_documentos(driver, enlaces)
            
            if not enlaces:
                logging.warning("No se encontraron documentos PDF. Intentando búsqueda más amplia...")
                self.extraer_documentos_amplia(driver, enlaces)
                
        except TimeoutException:
            logging.error("Timeout en Agrocap - Página muy lenta o cambió de estructura")
            raise Exception("La página web de Agrocap está caída o cambió su diseño (Timeout).")
        except Exception as e:
            logging.error(f"Error en Agrocap: {e}")
            raise
        finally:
            driver.quit()
            
        return enlaces, titulo_encontrado

    def extraer_documentos(self, driver, enlaces):
        """Extrae enlaces de documentos (PDF, XLSX, ZIP, etc.)"""
        try:
            # Buscar todos los enlaces que terminen en extensiones de archivos
            xpath_docs = "//a[contains(@href, '.pdf') or contains(@href, '.xlsx') or contains(@href, '.zip') or contains(@href, '.doc')]"
            documentos = driver.find_elements(By.XPATH, xpath_docs)
            
            for doc in documentos:
                href = doc.get_attribute("href")
                if href:
                    enlaces.add(href)
                    
            logging.info(f"✅ Extraídos {len(enlaces)} documentos desde la página de becas.")
        except Exception as e:
            logging.warning(f"Error extrayendo documentos: {e}")

    def extraer_documentos_amplia(self, driver, enlaces):
        """Búsqueda más amplia de enlaces"""
        try:
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and any(ext in href.lower() for ext in ['.pdf', '.xlsx', '.zip', '.docx', '.doc']):
                    enlaces.add(href)
        except:
            pass

# Bloque de prueba local
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = AgrocapScraperSelenium()
    links, titulo = scraper.fetch_tender_links()
    print(f"\n📌 {titulo}")
    for link in sorted(links):
        print(f"- {link}")
