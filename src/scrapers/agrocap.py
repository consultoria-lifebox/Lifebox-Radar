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
        self.url_principal = "https://www.agrocap.cl/webid/"  # URL más general
       
        self.opciones = Options()
        self.opciones.page_load_strategy = 'eager'
        self.opciones.add_argument("--disable-gpu")
        self.opciones.add_argument("--headless=new")
        self.opciones.add_argument("--no-sandbox")
        self.opciones.add_argument("--disable-dev-shm-usage")
        self.opciones.add_argument("--window-size=1920,1080")
        # Mejoras anti-detección
        self.opciones.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
        
    def fetch_tender_links(self):
        anio_actual = str(datetime.now().year)
        anio_anterior = str(datetime.now().year - 1)
       
        logging.info(f"Iniciando exploración en Agrocap: {self.url_principal}")
       
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.opciones)
        driver.set_page_load_timeout(60)   # ← Aumentado
        
        try:
            driver.get(self.url_principal)
            time.sleep(4)
            
            # Espera explícita
            wait = WebDriverWait(driver, 20)
            
            # Buscar enlaces que contengan "Becas Laborales" o año actual (más estable)
            enlaces = set()
            titulo_encontrado = f"Llamado Licitación Agrocap {anio_actual}"
            
            # Buscar páginas de licitaciones del año actual o anterior
            posibles_anios = [anio_actual, anio_anterior]
            
            for anio in posibles_anios:
                try:
                    # Buscar enlaces con el año
                    xpath = f"//a[contains(text(), '{anio}') or contains(text(), 'Becas Laborales')]"
                    elementos = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
                    
                    for elem in elementos:
                        href = elem.get_attribute("href")
                        if href and ("page_id" in href or "becas" in href.lower()):
                            logging.info(f"Subpágina encontrada para {anio}: {href}")
                            driver.get(href)
                            time.sleep(4)
                            self.extraer_documentos(driver, enlaces)
                            titulo_encontrado = f"Agrocap - Becas Laborales {anio}"
                            return enlaces, titulo_encontrado
                except:
                    continue
                    
            # Si no encontró nada, intentar búsqueda más amplia
            logging.warning("No se encontró estructura por año. Buscando de forma general...")
            self.extraer_documentos(driver, enlaces)
            
        except TimeoutException:
            logging.error("Timeout en Agrocap - La página está muy lenta o cambió de estructura")
            raise Exception("La página web de Agrocap está caída o cambió su diseño (Timeout).")
        except Exception as e:
            logging.error(f"Error en Agrocap: {e}")
            raise
        finally:
            driver.quit()
            
        return enlaces, titulo_encontrado

    def extraer_documentos(self, driver, enlaces):
        """Extrae botones de descarga"""
        try:
            buttons = driver.find_elements(By.XPATH, "//a[contains(@class, 'elementor-button-link') or contains(@href, '.pdf') or contains(@href, '.doc')]")
            for btn in buttons:
                href = btn.get_attribute("href")
                if href and any(ext in href.lower() for ext in ['.pdf', '.docx', '.doc', '.zip', '.xlsx']):
                    enlaces.add(href)
            logging.info(f"✅ Encontrados {len(enlaces)} documentos")
        except Exception as e:
            logging.warning(f"Error extrayendo documentos: {e}")
