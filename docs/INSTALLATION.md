# 📖 Guía de Instalación - Lifebox Radar

Sigue estos pasos para instalar y configurar Lifebox Radar en tu computadora o servidor.

---

## ✅ Requisitos Previos

Antes de comenzar, asegúrate de tener:

### 📦 Software Requerido
- **Python 3.9 o superior** - [Descargar](https://www.python.org/downloads/)
- **Git** - [Descargar](https://git-scm.com/)
- **Google Chrome o Chromium** (para web scraping)

### 🔐 Cuentas Requeridas
- **Google Cloud Project** con BigQuery habilitado
- **Telegram Bot** (para notificaciones)

---

## 🚀 Instalación Paso a Paso

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/consultoria-lifebox/Lifebox-Radar.git
cd Lifebox-Radar
```

### Paso 2: Crear Entorno Virtual

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 4: Configurar Google Cloud

#### 4.1 Crear un Proyecto en Google Cloud

1. Accede a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto (nombre: "Lifebox Radar")
3. Habilita BigQuery API
4. Habilita Cloud Resource Manager API

#### 4.2 Crear una Clave de Servicio

1. Ve a **IAM & Admin** > **Service Accounts**
2. Crea una nueva service account
3. Dale el rol **BigQuery Admin**
4. Crea una clave JSON
5. Descarga el archivo (guardar como `credenciales_gcp.json`)
6. Coloca el archivo en la raíz del proyecto

### Paso 5: Configurar Telegram Bot

#### 5.1 Crear un Bot en Telegram

1. Abre Telegram y busca **@BotFather**
2. Envía: `/newbot`
3. Elige un nombre para tu bot
4. BotFather te dará un **TOKEN** como: `123456789:ABCDefgh...`
5. Copia este token

#### 5.2 Obtener tu Chat ID

1. Envía un mensaje a tu bot
2. Abre en navegador: `https://api.telegram.org/bot[TOKEN]/getUpdates`
3. Busca el campo `"id"` en la respuesta - ese es tu **CHAT_ID**

### Paso 6: Crear archivo .env

Crea un archivo `.env` en la raíz del proyecto:

```env
# Google Cloud
GCP_PROJECT_ID=tu-proyecto-gcp-aqui
GCP_CREDENTIALS_PATH=credenciales_gcp.json

# Telegram
TELEGRAM_TOKEN=123456789:ABCDefghijklmnopqrstuvwxyz
TELEGRAM_CHAT_ID=987654321

# Logging
LOG_LEVEL=INFO
```

**⚠️ IMPORTANTE:** Nunca compartas este archivo. Agrega a `.gitignore`:

```
.env
credenciales_gcp.json
logs/
__pycache__/
*.pyc
```

---

## 🧪 Verificar Instalación

### Prueba 1: Verificar Python

```bash
python --version
# Debe mostrar 3.9 o superior
```

### Prueba 2: Verificar Dependencias

```bash
pip list | grep -E "selenium|pandas|streamlit|google-cloud"
# Debe mostrar todos los paquetes instalados
```

### Prueba 3: Verificar Credenciales

```bash
python -c "from google.oauth2 import service_account; print('✅ GCP OK')"
```

### Prueba 4: Ejecutar Scraper de Prueba

```bash
python -c "from src.scrapers.proforma import ProformaScraperSelenium; print('✅ Scrapers OK')"
```

---

## 🎯 Primer Ejecución

### Opción A: Ejecutar Manualmente

```bash
python main.py
```

Verás algo como esto:
```
2024-01-15 10:30:45 - INFO - === INICIANDO SISTEMA DE VIGILANCIA MULTI-PORTAL ===
2024-01-15 10:30:46 - INFO - 🧠 Consultando memoria en BigQuery...
2024-01-15 10:30:48 - INFO - 🚀 Ejecutando Proforma...
...
```

### Opción B: Ver Dashboard

```bash
streamlit run dashboard.py
```

Se abrirá en `http://localhost:8501`

---

## 🔧 Configuración Avanzada

### Scheduler (Ejecutar Automáticamente)

Para ejecutar el sistema cada hora:

#### En Windows (Task Scheduler)

1. Abre **Task Scheduler**
2. **Create Task** > Name: "Lifebox Radar"
3. **Trigger**: Set to repeat hourly
4. **Action**: `python.exe` con argument `C:\ruta\a\Lifebox-Radar\main.py`

#### En Linux/macOS (Cron)

```bash
crontab -e
```

Agrega esta línea para ejecutar cada hora:

```cron
0 * * * * cd /ruta/a/Lifebox-Radar && /ruta/a/venv/bin/python main.py >> logs/cron.log 2>&1
```

### Configurar Logging Avanzado

Edita `.env`:

```env
LOG_LEVEL=DEBUG  # Para más detalles: DEBUG, INFO, WARNING, ERROR
```

Los logs se guardan en `logs/lifebox_radar.log`

---

## ❌ Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'selenium'"

```bash
# Reinstala las dependencias
pip install --force-reinstall -r requirements.txt
```

### Error: "credenciales_gcp.json not found"

```bash
# Verifica que el archivo esté en la raíz
ls credenciales_gcp.json

# O define la ruta en .env
GCP_CREDENTIALS_PATH=/ruta/completa/a/credenciales.json
```

### Error: "TELEGRAM_TOKEN not configured"

```bash
# Verifica tu archivo .env
cat .env

# Reinicia Python después de cambiar .env
```

### Chrome no se abre en modo headless

```bash
# Instala Chrome para Linux
sudo apt-get install chromium-browser

# O ajusta en settings.py:
HEADLESS: False  # Para ver el navegador mientras scrapea
```

---

## 📚 Próximos Pasos

1. Lee el [Manual de Usuario](USER_GUIDE.md) para aprender a usar el sistema
2. Revisa la [Arquitectura Técnica](ARCHITECTURE.md) si eres desarrollador
3. Personaliza los scrapers según tus necesidades

---

## 🆘 ¿Necesitas Ayuda?

- 📧 Email: soporte@lifebox.cl
- 🐛 [Abre un Issue en GitHub](https://github.com/consultoria-lifebox/Lifebox-Radar/issues)
- 💬 Discord: [Únete a nuestro server](https://discord.gg/lifebox)

---

**¡Listo! Tu instalación está completa.** 🎉
