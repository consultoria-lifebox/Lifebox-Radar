"""
Scraper para CAMACOES - Caja de Manutención del Comercio, Servicios y Otros Trabajadores
Extrae oportunidades de capacitación desde el portal de CAMACOES.
"""
from src.core.base_scraper_simple import SimpleBaseScraper
class CamacoeScraperSelenium(SimpleBaseScraper):
    """
    Scraper para CAMACOES usando Selenium.
    """
    def __init__(self):
        """
        Inicializa el scraper de CAMACOES.
        """
        super().__init__(portal_name="CAMACOES", portal_url="https://www.camacoes.cl/licitaciones/")
