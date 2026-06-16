"""
Lifebox Radar - Sistema de Vigilancia de Licitaciones

Script principal que orquesta el monitoreo automático de portales OTIC
y notifica al usuario sobre nuevas oportunidades de capacitación.
"""

import os
import logging
import pandas as pd

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
from src.scrapers.ccc import CccScraperSelenium

# Utilidades
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
        
        # Definir scrapers a ejecutar
        scrapers = [
            ("Proforma", ProformaScraperSelenium()),
            ("OTIC", OticScraperSelenium()),
            ("Pro Aconcagua", ProAconcaguaScraperSelenium()),
            ("Agrocap", AgrocapScraperSelenium()), 
            ("Banotic", BanoticScraperSelenium()),
            ("Alianza Pyme", AlianzaPymeScraperSelenium()),
            ("OTIC Sofofa", OticSofofaScraperSelenium()),
            ("CCC", CccScraperSelenium()),
            ("Franco Chileno", FrancoChilenoScraperSelenium()),
            ("Wines of Chile", ChileVinosScraperSelenium())
        ]
        
        # Ejecutar orquestación
        logger.info("=" * 70)
        logger.info("🚀 INICIANDO SISTEMA DE VIGILANCIA MULTI-PORTAL")
        logger.info("=" * 70)
        
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
