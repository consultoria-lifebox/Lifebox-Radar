import os
import pandas as pd
import logging

from src.config import get_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BigQueryClient:
    def __init__(self, project_id=None, dataset_id=None, table_id=None, credentials_path=None):
        config = get_config()
        self.project_id = project_id or config.gcp.project_id
        self.dataset_id = dataset_id or config.gcp.dataset_id
        self.table_id = table_id or config.gcp.table_opportunities
        self.credentials_path = credentials_path or config.gcp.credentials_path
        
        # 1. AUTENTICACIÓN
        if not os.path.exists(self.credentials_path):
            logging.error(f"🚨 No se encontró el archivo de credenciales en: {self.credentials_path}")
        else:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path
            
        # Ruta hacia tabla
        self.destination_table = f"{self.dataset_id}.{self.table_id}"

    def inyectar_datos(self, df):
        """Recibe un DataFrame de Pandas y lo inserta en la tabla de BigQuery."""
        if df.empty:
            logging.warning("El DataFrame está vacío. No hay nada que subir a BigQuery.")
            return False

        try:
            logging.info(f"Conectando a Google Cloud... Subiendo {len(df)} filas a {self.destination_table}")
            
            #Inyectar a bigquery
            
            df.to_gbq(
                destination_table=self.destination_table,
                project_id=self.project_id,
                if_exists='append' 
            )
            
            logging.info("✅ ¡Inyección exitosa! Los datos ya están en la nube.")
            return True
            
        except Exception as e:
            logging.error(f"❌ Falló la inyección a BigQuery: {e}")
            return False