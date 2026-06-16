import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException 

# Configuración básica de Logging coincidente con Lifebox-Radar
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CamacoesScraperSelenium:
    def __init__(self):
        # Entramos a la sección general de noticias para descubrir los llamados nuevos y antiguos
        self.url = "https://otic-camacoes.cl/noticias"
        self.driver = self._init_driver()

    def _init_driver(self):
        logging.info("Inicializando el navegador automatizado para OTIC CAMACOES...")
        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'eager'
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")            # Requisito para correr en GitHub Actions
        options.add_argument("--disable-dev-shm-usage") # Evita caídas por falta de RAM en contenedores
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--headless=new")           # Ejecución invisible
        
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(30)
        return driver

    def fetch_tender_links(self):
        logging.info(f"Navegando en el portal de noticias de CAMACOES: {self.url}")
        
        anio_actual = str(datetime.now().year)
        anio_anterior = str(datetime.now().year - 1)
        
        titulo_proceso_encontrado = f"Licitación CAMACOES {anio_actual}" 
        enlaces_encontrados = set()
        sub_enlaces_noticias = set()
        
        try:
            self.driver.get(self.url)
            time.sleep(5) # Espera técnica para carga de componentes

            html_principal = self.driver.page_source
            soup_principal = BeautifulSoup(html_principal, 'html.parser')
            
            anios_a_buscar = [anio_actual, anio_anterior]
            hubo_exito = False

            # PASO 1: Buscar links de noticias que correspondan a los años objetivos
            for anio_objetivo in anios_a_buscar:
                logging.info(f"Buscando artículos de becas laborales para el año {anio_objetivo}...")
                
                # Buscamos todos los enlaces en la página de noticias
                for enlace in soup_principal.find_all('a', href=True):
                    href = enlace['href']
                    texto_enlace = enlace.get_text().lower()
                    
                    # Si el link o su texto mencionan "becas" o "llamado" y el año objetivo
                    if anio_objetivo in href or anio_objetivo in texto_enlace:
                        if any(k in href.lower() or k in texto_enlace for k in ["becas", "llamado", "licitacion"]):
                            # Construimos la URL completa si es relativa
                            url_completa = href if href.startswith("http") else f"https://otic-camacoes.cl{href}"
                            sub_enlaces_noticias.add((url_completa, anio_objetivo))

            # PASO 2: Si encontramos noticias del año, entramos a extraer sus documentos (PDF, Word, etc.)
            if sub_enlaces_noticias:
                # Ordenamos para revisar primero lo más reciente (Año Actual)
                lista_noticias = sorted(list(sub_enlaces_noticias), key=lambda x: x[1], reverse=True)
                
                for url_noticia, anio_target in lista_noticias:
                    logging.info(f"Entrando a la noticia específica: {url_noticia}")
                    self.driver.get(url_noticia)
                    time.sleep(3)
                    
                    html_noticia = self.driver.page_source
                    soup_noticia = BeautifulSoup(html_noticia, 'html.parser')
                    
                    # Capturamos el título de la noticia para el Dashboard
                    etiqueta_titulo = soup_noticia.find(['h1', 'h2', '.title'])
                    if etiqueta_titulo:
                        titulo_proceso_encontrado = f"CAMACOES - {etiqueta_titulo.get_text(strip=True)[:50]}"
                    else:
                        titulo_proceso_encontrado = f"CAMACOES - Llamado Becas {anio_target}"

                    # Extraemos los documentos descargables dentro de la noticia
                    for enlace_doc in soup_noticia.find_all('a', href=True):
                        href_doc = enlace_doc['href']
                        if any(ext in href_doc.lower() for ext in ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.zip']):
                            enlaces_encontrados.add(href_doc)
                    
                    if enlaces_encontrados:
                        logging.info(f"Se encontraron {len(enlaces_encontrados)} documentos válidos en esta noticia.")
                        hubo_exito = True
                        break # Si ya encontramos los documentos del año más reciente, nos quedamos con estos
            
            if not hubo_exito:
                raise Exception("Cambio de diseño: No se encontraron noticias ni documentos de becas vigentes en CAMACOES.")

            return enlaces_encontrados, titulo_proceso_encontrado

        except TimeoutException:
            logging.error("Timeout en CAMACOES")
            raise Exception("La página de CAMACOES tardó demasiado en responder.")
        except WebDriverException:
            logging.error("Error de WebDriver en CAMACOES")
            raise Exception("Error en el navegador automatizado al acceder a CAMACOES.")
        except Exception as e:
            logging.error(f"Error explorando CAMACOES: {e}")
            if "Cambio de diseño" in str(e):
                raise e
            else:
                raise Exception("Error inesperado en el scraper de CAMACOES.")

        finally:
            logging.info("Cerrando el navegador de CAMACOES.")
            self.driver.quit()

if __name__ == "__main__":
    scraper = CamacoesScraperSelenium()
    links, titulo = scraper.fetch_tender_links()
    print(f"\n📌 TÍTULO: {titulo}")
    for link in links:
        print(f"🔗 Documento: {link}")
