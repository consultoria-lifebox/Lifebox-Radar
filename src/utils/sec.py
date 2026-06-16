import requests
import sys
import logging
import os
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery

from src.config import get_config

def verificar_lic():
    config = get_config()
    url_licencia = config.external.url_gist

    if not url_licencia:
        logging.error("🚨 URL_GIST no está configurada")
        sys.exit(1)

    try:
        respuesta = requests.get(url_licencia, timeout=5).text.strip()
        if respuesta != "ACTIVO":
            logging.error("🚨 Expirado")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Error de validación de lic: {e}")
        sys.exit(1)

def registrar_error_lic(detalle="Lic inválida"):
    """Registra el error en BigQuery para que el Dashboard lo muestre."""
    config = get_config()
    try:
        credenciales = service_account.Credentials.from_service_account_file(
            config.gcp.credentials_path
        )
        cliente = bigquery.Client(project=config.gcp.project_id, credentials=credenciales)

        query = f"""
            INSERT INTO `{config.gcp.project_id}.{config.gcp.dataset_id}.{config.gcp.table_status}` 
            (fecha_ejecucion, portal, estado, mensaje)
            VALUES (CURRENT_TIMESTAMP(), 'SISTEMA CORE', 'ERROR', 'ERROR AL CORRER MAIN: {detalle}')
        """
        cliente.query(query).result()
        logging.error(f"Error registrado en BigQuery: {detalle}")
    except Exception as e:
        logging.error(f"No se pudo registrar el error en BigQuery: {e}")