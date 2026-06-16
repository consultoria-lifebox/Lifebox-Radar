"""
Scraper para CORFICAP - Corporación de Formación e Intermediación para la Capacitación
Extrae oportunidades de capacitación desde el portal de CORFICAP.
"""
from src.core.base_scraper_simple import SimpleBaseScraper
class CorficapScraperSelenium(SimpleBaseScraper):
    """
    Scraper para CORFICAP usando Selenium.
    """
    def __init__(self):
        """
        Inicializa el scraper de CORFICAP.
        """
        super().__init__(portal_name="CORFICAP", portal_url="https://www.corficap.cl/licitaciones-y-concursos/")
