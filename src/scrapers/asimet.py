"""
Scraper para OTIC ASIMET - Asociación de Industriales Metalúrgicos
Extrae oportunidades de capacitación desde el portal de ASIMET.
"""
from src.core.base_scraper_simple import SimpleBaseScraper
class AsimetScraperSelenium(SimpleBaseScraper):
    """
    Scraper para la OTIC ASIMET usando Selenium.
    """
    def __init__(self):
        """
        Inicializa el scraper de ASIMET.
        """
        super().__init__(portal_name="ASIMET", portal_url="https://www.asimet.cl/category/otic/licitaciones-otic/")
