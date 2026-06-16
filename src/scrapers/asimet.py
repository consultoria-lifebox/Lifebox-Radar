import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException 

# Configuración de Logging compatible con Lifebox-Radar
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AsimetScraperSelenium:
    def __init__(self):
        self.url = "https://www.oticasimet.cl/becas-laborales-v2"
        self.driver = self._init_driver()

    def _init_driver(self):
        logging.info("Inicializando el navegador automatizado para OTIC ASIMET...")
        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'eager'
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")            # Vital para el entorno Linux de GitHub Actions
        options.add_argument("--disable-dev-shm-usage") # Evita caídas por desbordamiento de memoria
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--headless=new")           # Modo invisible obligatorio
        
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(30)
        return driver

    def fetch_tender_links(self):
        logging.info(f"Conectando con el portal de ASIMET: {self.url}")
        
        anio_actual = str(datetime.now().year)
        anio_anterior = str(datetime.now().year - 1)
        
        titulo_proceso_encontrado = f"Licitación ASIMET {anio_actual}" 
        enlaces_encontrados = set()
        
        try:
            self.driver.get(self.url)
            time.sleep(5) # Espera prudente para la carga de los elementos internos

            logging.info("Analizando el DOM de ASIMET...")
            html_final = self.driver.page_source
            soup = BeautifulSoup(html_final, 'html.parser')
            
            anios_a_buscar = [anio_actual, anio_anterior]
            hubo_exito = False

            # Búsqueda iterativa por año
            for anio_objetivo in anios_a_buscar:
                logging.info(f"Escaneando tablas y secciones para el año {anio_objetivo}...")
                
                # Buscamos en etiquetas comunes de organización visual (tablas, filas, divs de bloques)
                bloques_asimet = soup.find_all(['tr', 'div', 'p', 'li'])
                
                for bloque in bloques_asimet:
                    texto_bloque = bloque.get_text()
                    
                    # Filtramos bloques que tengan relación con el año y procesos de licitación
                    if anio_objetivo in texto_bloque and any(keyword in texto_bloque.lower() for keyword in ["bases", "llamado", "licitación", "anexo"]):
                        logging.info(f"Se detectó un bloque de información válido para ASIMET {anio_objetivo}.")
                        
                        # Intentamos capturar un encabezado o texto fuerte cercano para el Dashboard
                        etiqueta_titulo = bloque.find(['h2', 'h3', 'h4', 'strong', 'th'])
                        if etiqueta_titulo:
                            titulo_proceso_encontrado = f"ASIMET - {etiqueta_titulo.get_text(strip=True)[:50]}"
                        else:
                            titulo_proceso_encontrado = f"ASIMET - Licitación Becas {anio_objetivo}"
                        
                        # Extraemos los archivos descargables asociados a este bloque
                        for enlace in bloque.find_all('a', href=True):
                            href = enlace['href']
                            
                            # Validamos formatos estándar de licitaciones
                            if any(ext in href.lower() for ext in ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.zip']):
                                # Asegurar que la URL sea absoluta
                                url_completa = href if href.startswith("http") else f"https://www.oticasimet.cl{href}"
                                enlaces_encontrados.add(url_completa)
                                
                        if enlaces_encontrados:
                            hubo_exito = True
                            logging.info(f"Éxito: Se encontraron {len(enlaces_encontrados)} documentos para el periodo {anio_objetivo}.")
                            break
                            
                if hubo_exito:
                    break # Si encontramos la data del año más reciente, detenemos la búsqueda hacia atrás

            if not enlaces_encontrados:
                raise Exception("Cambio de diseño: No se encontraron documentos de licitación vigentes en OTIC ASIMET.")

            return enlaces_encontrados, titulo_proceso_encontrado

        # Manejo homogéneo de errores
        except TimeoutException:
            logging.error("Timeout en ASIMET")
            raise Exception("El sitio de la OTIC ASIMET tardó demasiado en cargar (Timeout).")
        except WebDriverException:
            logging.error("Error de WebDriver en ASIMET")
            raise Exception("Fallo en la automatización del navegador al intentar abrir ASIMET.")
        except Exception as e:
            logging.error(f"Error crítico en el scraper de ASIMET: {e}")
            if "Cambio de diseño" in str(e):
                raise e
            else:
                raise Exception("Error imprevisto en el módulo de ASIMET. Revise registros.")

        finally:
            logging.info("Cerrando la instancia del navegador de ASIMET.")
            self.driver.quit()

# Bloque de prueba de entorno local
if __name__ == "__main__":
    scraper = AsimetScraperSelenium()
    links, titulo = scraper.fetch_tender_links()
    
    print(f"\n================ MONITOR DE PRUEBA ASIMET ================")
    print(f"📌 TÍTULO CAPTURADO: {titulo}")
    print(f"==========================================================")
    for link in links:
        print(f"🔗 Documento Disponible: {link}")
