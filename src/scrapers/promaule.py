import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configuración básica de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PromauleScraperSelenium:
    def __init__(self):
        # Apuntando a la nueva sección del Blog
        self.url = "https://www.promaule.cl/blog/"
        self.driver = self._init_driver()

    def _init_driver(self):
        logging.info("Inicializando el navegador automatizado para OTIC PROMAULE...")
        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'eager'
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--headless=new") 

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(30)
        return driver

    def fetch_tender_links(self):
        logging.info(f"Conectando con el portal de PROMAULE: {self.url}")
        
        anio_actual = str(datetime.now().year)
        anio_anterior = str(datetime.now().year - 1)
        anios_a_buscar = [anio_actual, anio_anterior]
        
        titulo_proceso_encontrado = f"Licitación PROMAULE {anio_actual}"
        enlaces_encontrados = set()
        
        try:
            self.driver.get(self.url)
            time.sleep(5) # Pausa técnica para carga del contenido
            
            logging.info("Analizando la estructura HTML del Blog de PROMAULE...")
            html_final = self.driver.page_source
            soup = BeautifulSoup(html_final, 'html.parser')
            
            for anio_objetivo in anios_a_buscar:
                logging.info(f"Escaneando artículos del blog para el año {anio_objetivo}...")
                
                # Buscamos los contenedores de artículos (tarjetas)
                bloques_blog = soup.find_all('div', class_=lambda x: x and ('post' in x.lower() or 'card' in x.lower() or 'entry' in x.lower()))
                
                if not bloques_blog:
                    bloques_blog = soup.find_all('div')

                for bloque in bloques_blog:
                    texto_bloque = bloque.get_text()
                    
                    if anio_objetivo in texto_bloque and any(k in texto_bloque.lower() for k in ["bases", "licitación", "llamado", "becas"]):
                        logging.info(f"¡Título detectado en el blog!: {texto_bloque[:50].strip()}...")
                        
                        for enlace in bloque.find_all('a', href=True):
                            href = enlace['href']
                            if any(ext in href.lower() for ext in ['.pdf', '.docx', '.xlsx', '.zip', '.xls', '.doc']):
                                url_completa = href if href.startswith("http") else f"https://www.promaule.cl{href}"
                                enlaces_encontrados.add(url_completa)
                        
            if not enlaces_encontrados:
                logging.info("No se encontraron documentos de licitación vigentes en PROMAULE.")
                
        except TimeoutException:
            logging.error("Timeout en PROMAULE")
            raise Exception("La carga del sitio web de PROMAULE ha excedido el límite de tiempo.")
        except WebDriverException:
            logging.error("Error de WebDriver en PROMAULE")
            raise Exception("Fallo en la comunicación con el navegador automatizado para PROMAULE.")
        except Exception as e:
            logging.error(f"Fallo crítico en el módulo de PROMAULE: {e}")
            raise Exception("Error imprevisto en el procesamiento de PROMAULE.")
        finally:
            logging.info("Cerrando el navegador de PROMAULE.")
            self.driver.quit()
            
        return enlaces_encontrados, titulo_proceso_encontrado

# Bloque de prueba local
if __name__ == "__main__":
    scraper = PromauleScraperSelenium()
    links, titulo = scraper.fetch_tender_links()
    print(f"\n================ TEST PROMAULE ================")
    print(f"📌 PROCESO DETECTADO: {titulo}")
    if links:
        for link in links:
            print(f"🔗 Enlace: {link}")
    else:
        print("No se encontraron enlaces.")
