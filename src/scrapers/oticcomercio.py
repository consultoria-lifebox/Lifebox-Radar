import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException 

# Configuración básica de Logging coincidente con la arquitectura Lifebox
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OticComercioScraperSelenium:
    def __init__(self):
        self.url = "https://oticdelcomercio.cl/becas-laborales/"
        self.driver = self._init_driver()

    def _init_driver(self):
        logging.info("Inicializando el navegador automatizado para OTIC del Comercio...")
        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'eager'
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")            # Requisito indispensable para GitHub Actions
        options.add_argument("--disable-dev-shm-usage") # Optimización crítica de memoria RAM
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--headless=new")           # Ejecución en segundo plano
        
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(30)
        return driver

    def fetch_tender_links(self):
        logging.info(f"Conectando con la plataforma de OTIC del Comercio: {self.url}")
        
        anio_actual = str(datetime.now().year)
        anio_anterior = str(datetime.now().year - 1)
        
        titulo_proceso_encontrado = f"Licitación OTIC Comercio {anio_actual}" 
        enlaces_encontrados = set()
        
        try:
            self.driver.get(self.url)
            time.sleep(5) # Margen de espera para la renderización del DOM dinámico

            logging.info("Capturando el código fuente de la página...")
            html_final = self.driver.page_source
            soup = BeautifulSoup(html_final, 'html.parser')
            
            anios_a_buscar = [anio_actual, anio_anterior]
            hubo_exito = False

            # Bucle de resiliencia temporal idéntico al de Proforma
            for anio_objetivo in anios_a_buscar:
                logging.info(f"Analizando convocatorias publicadas para el año {anio_objetivo}...")
                
                # En la OTIC del Comercio, las licitaciones se listan en bloques contenedores (divs, tr, o listas)
                elementos_pagina = soup.find_all(['div', 'li', 'p', 'tr', 'h3'])
                
                for elemento in elementos_pagina:
                    texto_elemento = elemento.get_text()
                    
                    # Filtro inteligente: el bloque debe contener el año buscado y palabras clave del proceso
                    if anio_objetivo in texto_elemento and any(k in texto_elemento.lower() for k in ["llamado", "licitación", "bases"]):
                        logging.info(f"Se identificó un bloque válido para el periodo {anio_objetivo}.")
                        
                        # Capturamos el contexto del título para el Dashboard de control
                        if "llamado" in texto_elemento.lower():
                            # Limpiamos el texto para no arrastrar saltos de línea gigantes
                            lineas = [l.strip() for l in texto_elemento.split('\n') if l.strip()]
                            titulo_contexto = lineas[0] if lineas else f"Proceso Licitación {anio_objetivo}"
                            titulo_proceso_encontrado = f"Comercio - {titulo_contexto[:60]}"
                        
                        # Extraemos todos los accesos a documentos y sub-enlaces de ese bloque
                        for enlace in elemento.find_all('a', href=True):
                            href = enlace['href']
                            
                            # Validamos extensiones de archivos compatibles o subrutas de descarga
                            if any(ext in href.lower() for ext in ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.zip']) or "llamado" in href.lower():
                                enlaces_encontrados.add(href)
                                
                        if enlaces_encontrados:
                            hubo_exito = True
                            logging.info(f"Éxito: Se recolectaron {len(enlaces_encontrados)} recursos para el año {anio_objetivo}.")
                            break 
                
                if hubo_exito:
                    break # Interrumpe el retroceso de año si ya capturó la data más reciente

            if not enlaces_encontrados:
                raise Exception("Cambio de diseño: No se detectaron documentos ni enlaces de licitación en la OTIC del Comercio.")

            return enlaces_encontrados, titulo_proceso_encontrado

        # Bloque de excepciones estandarizado para la tubería (Pipeline) de GitHub Actions
        except TimeoutException:
            logging.error("Timeout al intentar cargar OTIC del Comercio")
            raise Exception("La respuesta del servidor de la OTIC del Comercio excedió el límite de tiempo.")
        except WebDriverException:
            logging.error("Fallo de WebDriver en OTIC del Comercio")
            raise Exception("Error en la instancia del navegador para OTIC del Comercio. Verifique configuración.")
        except Exception as e:
            logging.error(f"Error crítico ejecutando el scraper: {e}")
            if "Cambio de diseño" in str(e):
                raise e
            else:
                raise Exception("Error inesperado en el módulo de OTIC del Comercio. Revise registros.")

        finally:
            logging.info("Terminando proceso y liberando recursos del navegador.")
            self.driver.quit()

# Ejecución de prueba local aislada
if __name__ == "__main__":
    scraper = OticComercioScraperSelenium()
    links, titulo = scraper.fetch_tender_links()
    
    print(f"\n================ TÍTULO DE ALERTA ================")
    print(f"📌 {titulo}")
    
    print(f"\n================ ENLACES RECOLECTADOS ================")
    for link in links:
        print(f"🔗 {link}")
