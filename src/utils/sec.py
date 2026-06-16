import requests
import sys
import logging
import os
import pandas as pd
from google.oauth2 import   service_account
from google.cloud import bigquery

def verificar_lic():
    
    url_licencia = os.getenv("URL_GIST")
    
    # Si URL_GIST no está configurada, solo aviso pero no rompo la ejecución (modo desarrollo)
    if not url_licencia:
        logging.warning("⚠️ URL_GIST no configurada. Continuando en modo desarrollo/prueba.")
        return
    
    try:
        respuesta = requests.get(url_licencia, timeout=5).text.strip()
        if respuesta != "ACTIVO":
            logging.error("🚨 Licencia Expirada")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Error de validación de lic: {e}")
        sys.exit(1)

def registrar_error_lic(detalle="Lic inválida"):
    """Registra el error en BigQuery para que el Dashboard lo muestre."""
    try:
        credenciales = service_account.Credentials.from_service_account_file("credenciales_gcp.json")
        cliente = bigquery.Client(project="proyecto-life-box-licitaciones", credentials=credenciales)
        
        
        query = f"""
            INSERT INTO `proyecto-life-box-licitaciones.licitaciones.estado_scrapers` 
            (fecha_ejecucion, portal, estado, mensaje)
            VALUES (CURRENT_TIMESTAMP(), 'SISTEMA CORE', 'ERROR', 'ERROR AL CORRER MAIN: {detalle}')
        """
        cliente.query(query).result()
        logging.error(f"Error registrado en BigQuery: {detalle}")
    except Exception as e:
        logging.error(f"No se pudo registrar el error en BigQuery: {e}")