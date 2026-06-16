"""
Lifebox Radar - Sistema de Vigilancia de Licitaciones

Script principal que orquesta el monitoreo automático de portales OTIC
y notifica al usuario sobre nuevas oportunidades de capacitación.
"""

import os
import logging
import pandas as pd
import pandas_gbq

# Configuración
from src.config import get_config
from src.core import Orchestrator

# Scrapers
from src.scrapers.proforma import ProformaScraperSelenium 
from src.scrapers.otic import OticScraperSelenium 
from src.scrapers.proaconcagua import ProAconcaguaScraperSelenium 
from src.scrapers.agrocap import AgrocapScraperSelenium 
from src.scrapers.banotic import BanoticScraperSelenium 
from src.scrapers.alianzapyme import AlianzaPymeScraperSelenium 
from src.scrapers.oticsosofa import OticSofofaScraperSelenium 
from src.scrapers.francochileno import FrancoChilenoScraperSelenium
from src.scrapers.winesofchile import ChileVinosScraperSelenium
from src.scrapers.ccc import CccScraperSelenium # Mantener para lógica específica
from src.scrapers.asimet import AsimetScraperSelenium
from src.scrapers.otic_del_comercio import OticDelComercioScraperSelenium
from src.scrapers.corficap import CorficapScraperSelenium
from src.scrapers.camacoes import CamacoeScraperSelenium
from src.scrapers.cgci import CgciScraperSelenium

# Utilidades
from src.core.base_scraper_simple import SimpleBaseScraper
from src.utils.sec import verificar_lic
from src.utils.analizador_inteligente import AnalizadorLicitaciones
from src.utils.document_parser import DocumentAnalyzer
from src.database.bq_client import BigQueryClient

# Logger
logger = logging.getLogger(__name__)
config = get_config()

# Configurar logging
logging.basicConfig(
    level=config.logging.level,
    format=config.logging.format
)



def main():
    """
    Función principal que ejecuta el sistema de vigilancia
    """
    try:
        # Verificar licencia
        verificar_lic()
        
        # Crear orquestador
        orchestrator = Orchestrator()
        
        # Definir scrapers a ejecutar con lazy instantiation
        scrapers_config = [
            ("Proforma", ProformaScraperSelenium),
            ("OTIC", OticScraperSelenium),
            ("Pro Aconcagua", ProAconcaguaScraperSelenium),
            ("Agrocap", AgrocapScraperSelenium), 
            ("Banotic", BanoticScraperSelenium),
            ("Alianza Pyme", AlianzaPymeScraperSelenium),
            ("OTIC Sofofa", OticSofofaScraperSelenium),
            ("CCC", CccScraperSelenium),
            ("Franco Chileno", FrancoChilenoScraperSelenium),
            ("Wines of Chile", ChileVinosScraperSelenium),
            ("ASIMET", AsimetScraperSelenium),
            ("OTIC del Comercio", OticDelComercioScraperSelenium),
            ("CORFICAP", CorficapScraperSelenium),
            ("CAMACOES", CamacoeScraperSelenium),
            ("CGCI", CgciScraperSelenium)
        ]
        
        # Ejecutar orquestación con lazy instantiation
        logger.info("=" * 70)
        logger.info("🚀 INICIANDO SISTEMA DE VIGILANCIA MULTI-PORTAL")
        logger.info("=" * 70)
        
        scrapers = []
        for nombre_portal, scraper_class in scrapers_config:
            try:
                scraper_instance = scraper_class()
                scrapers.append((nombre_portal, scraper_instance))
                logger.info(f"✅ {nombre_portal} inicializado correctamente")
            except Exception as e:
                logger.error(f"❌ No se pudo inicializar scraper de {nombre_portal}: {str(e)}")
                continue
        
        resultados = orchestrator.procesar_licitaciones(scrapers)
        
        logger.info("=" * 70)
        logger.info("✅ VIGILANCIA COMPLETADA EXITOSAMENTE")
        logger.info("=" * 70)
        
        # Resumen de resultados
        total_licitaciones = sum(len(lics) for lics in resultados.values())
        logger.info(f"📊 Total licitaciones procesadas: {total_licitaciones}")
        
        for portal, licitaciones in resultados.items():
            logger.info(f"   {portal}: {len(licitaciones)} licitaciones")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fatal en main: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    exit(0 if main() else 1)
