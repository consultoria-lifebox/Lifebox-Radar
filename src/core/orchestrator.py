"""
Orquestador central del sistema

Coordina la ejecución de scrapers, validación de licencias, 
procesamiento de datos y notificaciones.
"""
import logging
import os
import pandas as pd
from typing import Dict, List, Set, Tuple
from urllib.parse import unquote
from google.oauth2 import service_account

from src.config import get_config
from src.utils.sec import verificar_lic
from src.utils.alerts import enviar_notificacion, enviar_alerta_error
from src.database.bq_client import BigQueryClient


class Orchestrator:
    """
    Orquestador principal del sistema de vigilancia de licitaciones
    
    Responsabilidades:
    - Ejecutar todos los scrapers
    - Validar datos
    - Comparar con histórico
    - Enviar notificaciones
    - Registrar estado
    """
    
    def __init__(self):
        self.logger = logging.getLogger("Orchestrator")
        self.config = get_config()
        self.archivos_conocidos: Set[str] = set()
        self.bq_client = BigQueryClient()
    
    def obtener_archivos_conocidos(self) -> Set[str]:
        """
        Obtiene el historial de licitaciones ya procesadas desde BigQuery
        
        Returns:
            Set con nombres de archivos/títulos ya conocidos
        """
        self.logger.info("🧠 Consultando memoria en BigQuery...")
        try:
            query = f"""
                SELECT DISTINCT link_documento, titulo_llamado_web 
                FROM `{self.config.gcp.project_id}.{self.config.gcp.dataset_id}.{self.config.gcp.table_opportunities}`
            """
            
            df_historial = pd.read_gbq(
                query,
                project_id=self.config.gcp.project_id,
                credentials=self._get_credentials()
            )
            
            archivos_en_bq = set()
            for _, fila in df_historial.iterrows():
                link = fila.get('link_documento')
                if pd.notna(link):
                    nombre_archivo = unquote(str(link).split('/')[-1].split('?')[0].strip())
                    archivos_en_bq.add(nombre_archivo)
                
                titulo = fila.get('titulo_llamado_web')
                if pd.notna(titulo):
                    archivos_en_bq.add(str(titulo).strip())
            
            self.archivos_conocidos = archivos_en_bq
            self.logger.info(f"✅ {len(archivos_en_bq)} registros en memoria")
            return archivos_en_bq
            
        except Exception as e:
            self.logger.warning(f"⚠️ No se pudo leer historial: {e}")
            return set()
    
    def _get_credentials(self):
        """Obtiene las credenciales de GCP"""
        try:
            return service_account.Credentials.from_service_account_file(
                self.config.gcp.credentials_path
            )
        except Exception as e:
            self.logger.error(f"Error cargando credenciales GCP: {e}")
            return None
    
    def registrar_estado_scraper(self, portal: str, estado: str, mensaje: str = "Funcionando correctamente"):
        """
        Registra el estado de salud de cada scraper en BigQuery
        
        Args:
            portal: Nombre del portal
            estado: Estado ('success', 'error', 'warning')
            mensaje: Mensaje descriptivo
        """
        try:
            df_estado = pd.DataFrame([{
                "fecha_ejecucion": pd.Timestamp.now('America/Santiago'),
                "portal": portal,
                "estado": estado,
                "mensaje": str(mensaje)
            }])
            
            pd.io.gbq.to_gbq(
                df_estado,
                destination_table=f'{self.config.gcp.dataset_id}.{self.config.gcp.table_status}',
                project_id=self.config.gcp.project_id,
                if_exists='append',
                credentials=self._get_credentials()
            )
            
            self.logger.info(f"✅ Estado de {portal} registrado en BigQuery")
            
        except Exception as e:
            self.logger.error(f"Error registrando estado de {portal}: {e}")
    
    def ejecutar_scraper(self, nombre_portal: str, scraper) -> Tuple[bool, List[dict]]:
        """
        Ejecuta un scraper individual con manejo de errores
        
        Args:
            nombre_portal: Nombre del portal
            scraper: Instancia del scraper a ejecutar
            
        Returns:
            Tupla (éxito: bool, licitaciones: List[dict])
        """
        try:
            self.logger.info(f"🚀 Ejecutando {nombre_portal}...")
            licitaciones = scraper.execute()
            
            self.registrar_estado_scraper(nombre_portal, "success", "Scraping completado exitosamente")
            return True, licitaciones
            
        except Exception as e:
            self.logger.error(f"❌ Error en {nombre_portal}: {e}")
            self.registrar_estado_scraper(nombre_portal, "error", str(e))
            enviar_alerta_error(nombre_portal, str(e))
            return False, []
    
    def procesar_licitaciones(
        self,
        scrapers: List[Tuple[str, any]]
    ) -> Dict[str, List[dict]]:
        """
        Procesa todos los scrapers
        
        Args:
            scrapers: Lista de tuplas (nombre, instancia_scraper)
            
        Returns:
            Diccionario con resultados por portal
        """
        verificar_lic()
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO SISTEMA DE VIGILANCIA MULTI-PORTAL")
        self.logger.info("=" * 60)
        
        self.obtener_archivos_conocidos()
        
        resultados = {}
        
        for nombre_portal, scraper in scrapers:
            exito, licitaciones = self.ejecutar_scraper(nombre_portal, scraper)
            
            if exito:
                # Filtrar licitaciones nuevas
                licitaciones_nuevas = [
                    lic for lic in licitaciones
                    if lic.get('titulo') not in self.archivos_conocidos
                ]
                
                if licitaciones_nuevas:
                    self.logger.info(
                        f"🆕 {len(licitaciones_nuevas)} licitaciones nuevas en {nombre_portal}"
                    )
                    enviar_notificacion(
                        titulo=licitaciones_nuevas[0].get('titulo'),
                        cantidad=len(licitaciones_nuevas),
                        portal=nombre_portal
                    )
                
                resultados[nombre_portal] = licitaciones
            else:
                resultados[nombre_portal] = []
        
        return resultados
