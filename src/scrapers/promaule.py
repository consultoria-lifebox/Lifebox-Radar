import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException 

# Configuración de Logging estándar para la tubería de Lifebox-Radar
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PromauleScraperSelenium:
    def __init__(self):
        # Intentamos entrar directamente a la sección de licitaciones, si no, el script barre desde el inicio
        self.url = "https://www.promaule.cl/licitaciones/"
        self.driver = self._init_driver()

    def _init_driver(self):
        logging.info("Inicializando el navegador automatizado para OTIC PROMAULE...")
        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'eager'
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")            # Indispensable para el contenedor de GitHub Actions
        options.add_argument("--disable-dev-shm-usage") # Evita problemas de memoria virtual en Linux
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--headless=new")           # Modo invisible para producción
        
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(30)
        return driver

    def fetch_tender_links(self):
        logging.info(f"Conectando con el portal de PROMAULE: {self.url}")
        
        anio_actual = str(datetime.now().year)
        anio_anterior = str(datetime.now().year - 1)
        
        titulo_proceso_encontrado = f"Licitación PROMAULE {anio_actual}" 
        enlaces_encontrados = set()
        
        try:
            # Intentamos acceder a la sección específica
            try:
                self.driver.get(self.url)
            except (TimeoutException, WebDriverException):
                logging.warning("No se pudo acceder a /licitaciones/, reintentando con la URL raíz...")
                self.url = "https://www.promaule.cl/"
                self.driver.get(self.url)
                
            time.sleep(5) # Pausa técnica para carga del contenido dinámico

            logging.info("Analizando la estructura HTML de PROMAULE...")
            html_final = self.driver.page_source
            soup = BeautifulSoup(html_final, 'html.parser')
            
            anios_a_buscar = [anio_actual, anio_anterior]
            hubo_exito = False

            # Búsqueda adaptativa por año de vigencia
            for anio_objetivo in anios_a_buscar:
                logging.info(f"Escaneando bloques informativos para el año {anio_objetivo}...")
                
                # Barremos contenedores comunes de texto y enlaces
                bloques_pagina = soup.find_all(['div', 'tr', 'p', 'li', 'article'])
                
                for bloque in bloques_pagina:
                    texto_bloque = bloque.get_text()
                    
                    # Buscamos patrones clave de licitaciones asociados al año
                    if anio_objetivo in texto_bloque and any(k in texto_bloque.lower() for k in ["bases", "licitación", "llamado", "becas"]):
                        logging.info(f"Se localizó un bloque válido que coincide con PROMAULE {anio_objetivo}.")
                        
                        # Extraer un título limpio para el Dashboard
                        etiqueta_titulo = bloque.find(['h1', 'h2', 'h3', 'strong'])
                        if etiqueta_titulo:
                            titulo_proceso_encontrado = f"PROMAULE - {etiqueta_titulo.get_text(strip=True)[:50]}"
                        else:
                            titulo_proceso_encontrado = f"PROMAULE - Convocatoria {anio_objetivo}"
                        
                        # Capturamos todos los documentos descargables dentro de esta sección
                        for enlace in bloque.find_all('a', href=True):
                            href = enlace['href']
                            
                            if any(ext in href.lower() for ext in ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.zip']):
                                url_completa = href if href.startswith("http") else f"https://www.promaule.cl{href}"
                                enlaces_encontrados.add(url_completa)
                                
                        if enlaces_encontrados:
                            hubo_exito = True
                            logging.info(f"Éxito: Se encontraron {len(enlaces_encontrados)} documentos vigentes.")
                            break
                            
                if hubo_exito:
                    break

            # Si no encontró nada específico con filtros de texto, aplicamos la lógica agresiva de respaldo
            if not enlaces_encontrados:
                logging.info("Buscando cualquier documento descargable residual en la página...")
                for enlace in soup.find_all('a', href=True):
                    href = enlace['href']
                    if any(ext in href.lower() for ext in ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.zip']) and anio_actual in href:
                        url_completa = href if href.startswith("http") else f"https://www.promaule.cl{href}"
                        enlaces_encontrados.add(url_completa)
                        hubo_exito = True

            if not enlaces_encontrados:
                logging.info("No se encontraron documentos de licitación vigentes en PROMAULE.")

            return enlaces_encontrados, titulo_proceso_encontrado

        # Control estructural de excepciones homologado
        except TimeoutException:
            logging.error("Timeout en PROMAULE")
            raise Exception("La carga del sitio web de PROMAULE ha excedido el límite de tiempo.")
        except WebDriverException:
            logging.error("Error de WebDriver en PROMAULE")
            raise Exception("Fallo en la comunicación con el navegador automatizado para PROMAULE.")
        except Exception as e:
            logging.error(f"Fallo crítico en el módulo de PROMAULE: {e}")
            if "Cambio de diseño" in str(e):
                raise e
            else:
                raise Exception("Error imprevisto en el procesamiento de PROMAULE.")

        finally:
            logging.info("Cerrando el navegador de PROMAULE.")
            self.driver.quit()

if __name__ == "__main__":
    scraper = PromauleScraperSelenium()
    links, titulo = scraper.fetch_tender_links()
    print(f"\n================ TEST PROMAULE ================")
    print(f"📌 PROCESO DETECTADO: {titulo}")
    print(f"===============================================")
    for link in links:
        print(f"🔗 Enlace: {link}")
