import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException 

# Configuración de Logging coincidente con Lifebox-Radar
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CorficapScraperSelenium:
    def __init__(self):
        # Apuntamos al portal general de noticias para descubrir convocatorias nuevas de forma dinámica
        self.url = "https://www.corficap.cl/noticias/"
        self.driver = self._init_driver()

    def _init_driver(self):
        logging.info("Inicializando el navegador automatizado para OTIC CORFICAP...")
        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'eager'
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")            # Requisito para entornos Linux / GitHub Actions
        options.add_argument("--disable-dev-shm-usage") # Evita saturar la memoria RAM en contenedores
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--headless=new")           # Modo invisible
        
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(30)
        return driver

    def fetch_tender_links(self):
        logging.info(f"Escaneando el portal de novedades de CORFICAP: {self.url}")
        
        anio_actual = str(datetime.now().year)
        anio_anterior = str(datetime.now().year - 1)
        
        titulo_proceso_encontrado = f"Licitación CORFICAP {anio_actual}" 
        enlaces_encontrados = set()
        urls_noticias_descubiertas = set()
        
        try:
            self.driver.get(self.url)
            time.sleep(5) # Espera técnica para renderizado de tarjetas de noticias

            html_principal = self.driver.page_source
            soup_principal = BeautifulSoup(html_principal, 'html.parser')
            
            anios_a_buscar = [anio_actual, anio_anterior]
            hubo_exito = False

            # PASO 1: Identificar artículos o noticias de licitaciones del año objetivo
            for anio_objetivo in anios_a_buscar:
                logging.info(f"Buscando convocatorias de becas para el periodo {anio_objetivo}...")
                
                # Buscamos en todos los enlaces del muro de noticias
                for enlace in soup_principal.find_all('a', href=True):
                    href = enlace['href']
                    texto_enlace = enlace.get_text().lower()
                    
                    # Filtro inteligente: buscar patrones clave y el año respectivo
                    if anio_objetivo in href or anio_objetivo in texto_enlace:
                        if any(k in href.lower() or k in texto_enlace for k in ["becas", "licitacion", "llamado", "corficap"]):
                            url_completa = href if href.startswith("http") else f"https://www.corficap.cl{href}"
                            urls_noticias_descubiertas.add((url_completa, anio_objetivo))

            # PASO 2: Entrar a la noticia detectada y extraer sus archivos adjuntos (Bases, Anexos)
            if urls_noticias_descubiertas:
                # Priorizamos revisar lo más reciente primero (Año Actual)
                lista_ordenada = sorted(list(urls_noticias_discovered), key=lambda x: x[1], reverse=True)
                
                for url_noticia, anio_target in lista_ordenada:
                    logging.info(f"Ingresando a la publicación específica: {url_noticia}")
                    self.driver.get(url_noticia)
                    time.sleep(3)
                    
                    html_noticia = self.driver.page_source
                    soup_noticia = BeautifulSoup(html_noticia, 'html.parser')
                    
                    # Captura dinámica del encabezado principal para tu Dashboard
                    etiqueta_titulo = soup_noticia.find(['h1', 'h2', 'title'])
                    if etiqueta_titulo:
                        titulo_proceso_encontrado = f"CORFICAP - {etiqueta_titulo.get_text(strip=True)[:50]}"
                    else:
                        titulo_proceso_encontrado = f"CORFICAP - Licitación {anio_target}"

                    # Extraemos todos los links de descarga de documentos dentro del artículo
                    for enlace_doc in soup_noticia.find_all('a', href=True):
                        href_doc = enlace_doc['href']
                        if any(ext in href_doc.lower() for ext in ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.zip']):
                            # Asegurar URL absoluta
                            doc_completo = href_doc if href_doc.startswith("http") else f"https://www.corficap.cl{href_doc}"
                            enlaces_encontrados.add(doc_completo)
                    
                    if enlaces_encontrados:
                        logging.info(f"Éxito: Se capturaron {len(enlaces_encontrados)} documentos válidos.")
                        hubo_exito = True
                        break # Rompemos el ciclo al consolidar la información más reciente
            
            if not hubo_exito:
                raise Exception("Cambio de diseño: No se encontraron publicaciones ni bases vigentes en la web de CORFICAP.")

            return enlaces_encontrados, titulo_proceso_encontrado

        # Manejo de excepciones unificado para la tubería de automatización
        except TimeoutException:
            logging.error("Timeout en CORFICAP")
            raise Exception("El servidor de CORFICAP no respondió a tiempo (Timeout).")
        except WebDriverException:
            logging.error("Error de WebDriver en CORFICAP")
            raise Exception("Ocurrió un problema con el navegador automatizado al acceder a CORFICAP.")
        except Exception as e:
            logging.error(f"Fallo crítico en CORFICAP: {e}")
            if "Cambio de diseño" in str(e):
                raise e
            else:
                raise Exception("Error inesperado en el módulo de CORFICAP. Revise la consola.")

        finally:
            logging.info("Cerrando sesión del navegador de CORFICAP.")
            self.driver.quit()

# Bloque de ejecución local autónomo
if __name__ == "__main__":
    scraper = CorficapScraperSelenium()
    links, titulo = scraper.fetch_tender_links()
    print(f"\n================ PRUEBA RADAR CORFICAP ================")
    print(f"📌 ALERTA: {titulo}")
    print(f"=======================================================")
    for link in links:
        print(f"🔗 Enlace de descarga: {link}")
