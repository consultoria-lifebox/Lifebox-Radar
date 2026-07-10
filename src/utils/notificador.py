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
            contenido_telegram = f"🚨 <b>¡NUEVA PUBLICACIÓN EN {portal.upper()}!</b> 🚨\nProceso: <b>{titulo}</b>\n\n⚠️ <i>Este portal usa Drive. Revisar manualmente:</i>\n{link_especial}"
        else:
            contenido_telegram = f"🚨 <b>¡NUEVA LICITACIÓN EN {portal.upper()}!</b> 🚨\nProceso: <b>{titulo}</b>\n🎯 Se inyectaron <b>{cantidad}</b> oportunidades al sistema."

        self._enviar_telegram(contenido_telegram)

        # --- Mensaje para Correo (AHORA SE ENVÍA SIEMPRE) ---
        if link_especial:
            # Plantilla especial para cuando es un link de Drive
            cuerpo_html = f"""
            <html style="font-family: sans-serif;">
                <h2 style="color: #f39c12;">⚠️ Nueva Publicación (Requiere Revisión Manual)</h2>
                <p>El sistema <b>Lifebox Radar</b> ha detectado una nueva publicación en un portal que utiliza una carpeta externa.</p><hr>
                <p><b>Portal:</b> {portal.upper()}</p>
                <p><b>Proceso:</b> {titulo}</p>
                <p><b>Enlace a la carpeta (Drive/Web):</b> <a href="{link_especial}">{link_especial}</a></p><hr>
                <p><small>Este es un correo automático. Por favor, ingresa al enlace para revisar los documentos manualmente.</small></p>
            </html>
            """
        else:
            # Plantilla normal para cuando descarga Excels
            cuerpo_html = f"""
            <html style="font-family: sans-serif;">
                <h2 style="color: #27ae60;">🎉 Nueva Oportunidad de Licitación</h2>
                <p>El sistema <b>Lifebox Radar</b> ha detectado una nueva oportunidad y ya la procesó:</p><hr>
                <p><b>Portal:</b> {portal.upper()}</p>
                <p><b>Proceso:</b> {titulo}</p>
                <p><b>Oportunidades Encontradas:</b> {cantidad}</p><hr>
                <p><small>Este es un correo automático. Para ver los detalles, accede al dashboard.</small></p>
            </html>
            """
            
        self._enviar_correo(asunto=f"Nueva Licitación Detectada en {portal.upper()}", cuerpo_html=cuerpo_html)


    def notificar_error(self, portal, mensaje_error):
        """Envía notificaciones de fallo crítico de un scraper SOLO a Telegram."""
        error_corto = str(mensaje_error)[:200]
        contenido_telegram = (
            f"🚨 *¡ALERTA CRÍTICA DE SCRAPER!* 🚨\n\n"
            f"🔴 *Portal Caído:* {portal}\n"
            f"⚠️ *Motivo:* `{error_corto}...`\n\n"
            f"🔍 _Revisa el código, es posible que la página haya cambiado su diseño._"
        )
        self._enviar_telegram(contenido_telegram, parse_mode="Markdown")
        # Aquí eliminamos toda la lógica de enviar correos para los errores

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
        destinatarios = ["sales@lifebox.cl","antonia.flores@lifebox.cl"]

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
