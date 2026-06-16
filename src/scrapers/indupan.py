import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException 

# Configuración de Logging estándar de la arquitectura de Lifebox
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IndupanScraperSelenium:
    def __init__(self):
        self.url = "https://www.indupan.cl/otic"
        self.driver = self._init_driver()

    def _init_driver(self):
        logging.info("Inicializando el navegador automatizado para OTIC INDUPAN...")
        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'eager'
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")            # Necesario para entornos de servidores / GitHub Actions
        options.add_argument("--disable-dev-shm-usage") # Previene errores por falta de RAM en Linux
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--headless=new")           # Modo invisible para el motor automatizado
        
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(30)
        return driver

    def fetch_tender_links(self):
        logging.info(f"Navegando en el portal de INDUPAN: {self.url}")
        
        anio_actual = str(datetime.now().year)
        anio_anterior = str(datetime.now().year - 1)
        
        titulo_proceso_encontrado = f"Licitación INDUPAN {anio_actual}" 
        enlaces_encontrados = set()
        
        try:
            self.driver.get(self.url)
            time.sleep(5) # Margen de espera para la carga de scripts e imágenes

            logging.info("Extrayendo el código HTML de INDUPAN...")
            html_final = self.driver.page_source
            soup = BeautifulSoup(html_final, 'html.parser')
            
            anios_a_buscar = [anio_actual, anio_anterior]
            hubo_exito = False

            # Búsqueda estructurada por bloques de texto anuales
            for anio_objetivo in anios_a_buscar:
                logging.info(f"Revisando contenidos para el año {anio_objetivo}...")
                bloques_pagina = soup.find_all(['div', 'p', 'tr', 'li', 'h3'])
                
                for bloque in bloques_pagina:
                    texto_bloque = bloque.get_text()
                    
                    # Filtramos bloques que tengan relación directa con licitaciones vigentes
                    if anio_objetivo in texto_bloque and any(k in texto_bloque.lower() for k in ["bases", "licitación", "llamado", "becas"]):
                        logging.info(f"¡Bloque válido detectado para INDUPAN {anio_objetivo}!")
                        
                        # Captura de un título limpio para el Dashboard
                        etiqueta_titulo = bloque.find(['h1', 'h2', 'h3', 'strong'])
                        if etiqueta_titulo:
                            titulo_proceso_encontrado = f"INDUPAN - {etiqueta_titulo.get_text(strip=True)[:50]}"
                        else:
                            titulo_proceso_encontrado = f"INDUPAN - Convocatoria {anio_objetivo}"
                        
                        # Extraemos los archivos descargables dentro del bloque
                        for enlace in bloque.find_all('a', href=True):
                            href = enlace['href']
                            if any(ext in href.lower() for ext in ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.zip']):
                                url_completa = href if href.startswith("http") else f"https://www.indupan.cl{href}"
                                enlaces_encontrados.add(url_completa)
                                
                        if enlaces_encontrados:
                            hubo_exito = True
                            logging.info(f"Éxito: Se encontraron {len(enlaces_encontrados)} documentos vigentes.")
                            break
                
                if hubo_exito:
                    break

            # Respaldo de extracción agresiva por si la estructura visual cambia
            if not enlaces_encontrados:
                logging.info("Aplicando filtro de respaldo para documentos directos...")
                for enlace in soup.find_all('a', href=True):
                    href = enlace['href']
                    if any(ext in href.lower() for ext in ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.zip']):
                        # Buscamos que de alguna manera el enlace mencione el año o palabras clave básicas
                        if any(k in href.lower() for k in ["otic", "becas", "licitacio", anio_actual]):
                            url_completa = href if href.startswith("http") else f"https://www.indupan.cl{href}"
                            enlaces_encontrados.add(url_completa)
                            hubo_exito = True

            if not enlaces_encontrados:
                raise Exception("Cambio de diseño: No se detectaron enlaces de licitaciones ni documentos en la OTIC de INDUPAN.")

            return enlaces_encontrados, titulo_proceso_encontrado

        except TimeoutException:
            logging.error("Timeout en INDUPAN")
            raise Exception("El sitio web de INDUPAN está demasiado lento o caído (Timeout).")
        except WebDriverException:
            logging.error("Error de WebDriver en INDUPAN")
            raise Exception("No se pudo iniciar la navegación automatizada en INDUPAN.")
        except Exception as e:
            logging.error(f"Error imprevisto en INDUPAN: {e}")
            if "Cambio de diseño" in str(e):
                raise e
            else:
                raise Exception("Error interno en el módulo de INDUPAN. Verifique registros.")

        finally:
            logging.info("Cerrando el navegador de INDUPAN.")
            self.driver.quit()

if __name__ == "__main__":
    scraper = IndupanScraperSelenium()
    links, titulo = scraper.fetch_tender_links()
    print(f"\n================ TEST INDUPAN ================")
    print(f"📌 PROCESO DETECTADO: {titulo}")
    print(f"==============================================")
    for link in links:
        print(f"🔗 Enlace: {link}")
