"""
Scraper para OTIC del Comercio - Organismo Técnico de Capacitación del Comercio
Extirae oportunidades de capacitación desde el portal de OTIC del Comercio.
"""
from src.core.base_scraper_simple import SimpleBaseScraper
class OticDelComercioScraperSelenium(SimpleBaseScraper):
    """
    Scraper para la OTIC del Comercio usando Selenium.
    """
    def __init__(self):
        """
        Inicializa el scraper de OTIC del Comercio.
        """
        super().__init__(portal_name="OTIC del Comercio", portal_url="https://www.oticdelcomercio.cl/licitaciones/")
