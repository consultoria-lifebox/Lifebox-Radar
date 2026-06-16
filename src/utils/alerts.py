import logging
import requests
from typing import Optional

from src.config import get_config


def _get_telegram_config():
    config = get_config()
    if not config.telegram.is_configured():
        logging.warning("Telegram no está configurado. No se enviarán notificaciones.")
        return None, None
    return config.telegram.token, config.telegram.chat_id


def enviar_notificacion(titulo: str, cantidad: int, portal: str):
    """Envía una notificación de nueva licitación a Telegram."""
    token, chat_id = _get_telegram_config()
    if not token or not chat_id:
        return

    mensaje = (
        f"📌 *Nueva licitación detectada*\n"
        f"Portal: *{portal}*\n"
        f"Título: _{titulo}_\n"
        f"Cantidad de nuevas oportunidades: *{cantidad}*"
    )
    _send_telegram_message(token, chat_id, mensaje)


def enviar_alerta_error(portal: str, error: str):
    """Envía una alerta de error a Telegram."""
    token, chat_id = _get_telegram_config()
    if not token or not chat_id:
        return

    mensaje = (
        f"⚠️ *Error en el scraping*\n"
        f"Portal: *{portal}*\n"
        f"Detalle: `{error}`"
    )
    _send_telegram_message(token, chat_id, mensaje)


def _send_telegram_message(token: str, chat_id: str, text: str, parse_mode: str = "Markdown"):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logging.info("Notificación Telegram enviada correctamente.")
    except Exception as e:
        logging.error(f"Error enviando notificación Telegram: {e}")
