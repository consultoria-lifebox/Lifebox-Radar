import os
import requests
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Notificador:
    """
    Clase centralizada para manejar todas las notificaciones del sistema (Telegram, Email).
    """
    def __init__(self):
        # Credenciales de Telegram
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # Credenciales de Correo
        self.email_sender = os.getenv("EMAIL_SENDER")
        self.email_password = os.getenv("EMAIL_PASSWORD")

    def notificar_exito(self, titulo, cantidad, portal, link_especial=None):
        """Envía notificaciones de éxito (nuevas licitaciones encontradas)."""
        # --- Mensaje para Telegram ---
        if link_especial: 
            contenido_telegram = f"🚨 <b>¡NUEVA PUBLICACIÓN EN {portal.upper()}!</b> 🚨\nProceso: <b>{titulo}</b>\n⚠️ <i>Este portal usa Drive. Revisar manualmente:</i> {link_especial}"
        else: 
            contenido_telegram = f"🚨 <b>¡NUEVA LICITACIÓN EN {portal.upper()}!</b> 🚨\nProceso: <b>{titulo}</b>\n🎯 Se inyectaron <b>{cantidad}</b> oportunidades en BigQuery."
        
        self._enviar_telegram(contenido_telegram)

        # --- Mensaje para Correo ---
        if not link_especial: # Solo enviamos correo para oportunidades concretas
            self._enviar_correo(
                asunto=f"Nueva Licitación Detectada en {portal.upper()}",
                cuerpo_html=f"""
                <html><body style="font-family: sans-serif;">
                    <h2>🚨 Nueva Oportunidad de Licitación</h2>
                    <p>El sistema <b>Lifebox Radar</b> ha detectado una nueva oportunidad:</p><hr>
                    <p><b>Portal:</b> {portal.upper()}</p>
                    <p><b>Proceso:</b> {titulo}</p>
                    <p><b>Oportunidades Encontradas:</b> {cantidad}</p><hr>
                    <p><small>Este es un correo automático. Para ver los detalles, accede al dashboard.</small></p>
                </body></html>
                """
            )

    def notificar_error(self, portal, mensaje_error):
        """Envía notificaciones de fallo crítico de un scraper."""
        error_corto = str(mensaje_error)[:200]
        contenido_telegram = (
            f"🚨 *¡ALERTA CRÍTICA DE SCRAPER!* 🚨\n\n"
            f"🔴 *Portal Caído:* {portal}\n"
            f"⚠️ *Motivo:* `{error_corto}...`\n\n"
            f"🔍 _Revisa el código, es posible que la página haya cambiado su diseño._"
        )
        self._enviar_telegram(contenido_telegram, parse_mode="Markdown")

        # --- ALERTA TEMPORAL POR CORREO PARA PRUEBAS ---
        asunto_error = f"❌ ALERTA CRÍTICA: Falló Scraper en {portal.upper()}"
        cuerpo_error_html = f"""
        <html><body style="font-family: sans-serif;">
            <h2 style="color: #d9534f;">🚨 Falla Crítica de Scraper</h2>
            <p>El bot detectó un problema técnico al patrullar un portal.</p>
            <hr>
            <p><b>Portal afectado:</b> {portal.upper()}</p>
            <p><b>Detalle del Error:</b> {error_corto}...</p>
            <hr>
            <p><small>Este correo de diagnóstico es temporal para verificación del sistema.</small></p>
        </body></html>
        """
        self._enviar_correo(asunto_error, cuerpo_error_html)

    def _enviar_telegram(self, contenido, parse_mode="HTML"):
        if not all([self.telegram_token, self.telegram_chat_id]):
            logging.warning("Credenciales de Telegram incompletas. Saltando notificación.")
            return
        try:
            requests.post(f"https://api.telegram.org/bot{self.telegram_token}/sendMessage", 
                          json={"chat_id": self.telegram_chat_id, "text": contenido, "parse_mode": parse_mode})
            logging.info("✅ Notificación por Telegram enviada.")
        except Exception as e:
            logging.error(f"Error enviando a Telegram: {e}")

    def _enviar_correo(self, asunto, cuerpo_html):
        # --- AQUÍ DEFINES TODOS LOS DESTINATARIOS ---
        destinatarios = ["bmontesc@udd.cl", "danimunozp@udd.cl"]

        if not all([self.email_sender, self.email_password]):
            logging.warning("Credenciales de correo incompletas en GitHub. Saltando notificación.")
            return

        try:
            # Conexión directa y fija a Gmail
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.email_sender, self.email_password)
                
                # --- EL SECRETO: ENVIAR UNO POR UNO ---
                for destinatario in destinatarios:
                    msg = MIMEMultipart()
                    msg['From'] = self.email_sender
                    msg['To'] = destinatario # El correo va solo a nombre de esta persona
                    msg['Subject'] = asunto
                    msg.attach(MIMEText(cuerpo_html, 'html'))
                    
                    server.send_message(msg)
                    
                logging.info(f"✅ Notificaciones individuales enviadas a {len(destinatarios)} destinatarios.")
        except Exception as e:
            logging.error(f"❌ Falló el envío de correo: {e}")
