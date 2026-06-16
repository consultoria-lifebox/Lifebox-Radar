"""
Scraper para CGCI - Corporación de Gestión y Capacitación Integral
Extrae oportunidades de capacitación desde el portal de CGCI.
"""
from src.core.base_scraper_simple import SimpleBaseScraper
class CgciScraperSelenium(SimpleBaseScraper):
    """
    Scraper para CGCI usando Selenium.
    """
    def __init__(self):
        """
        Inicializa el scraper de CGCI.
        """
        super().__init__(portal_name="CGCI", portal_url="https://www.cgci.cl/licitaciones/")
