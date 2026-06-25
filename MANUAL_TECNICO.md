# Manual Técnico: Lifebox Radar

**Versión:** 1.0
**Fecha:** Agosto 2024
**Audiencia:** Equipo de TI, Desarrolladores, Administradores de Sistemas.

---

## 1. Resumen de Arquitectura

**Lifebox Radar** es un sistema de inteligencia de negocio automatizado diseñado para el monitoreo, extracción y análisis de licitaciones públicas en portales de OTICs chilenas.

El sistema se compone de los siguientes módulos principales:

- **Scrapers (`src/scrapers/`):** Módulos individuales basados en Selenium responsables de la extracción de datos (links a documentos) desde los portales web de las OTICs. Están diseñados para ser resilientes a cambios menores en el DOM.
- **Orquestador (`main.py`):** El cerebro del sistema. Gestiona la ejecución secuencial de los scrapers, implementa una lógica de reintentos para manejar fallos temporales de red o de los sitios web, y coordina el flujo de datos hacia los módulos de análisis y almacenamiento.
- **Analizador de Documentos (`src/utils/document_parser.py`):** Utiliza la API de **Groq** con el modelo `llama-3.3-70b-versatile` para procesar documentos. Realiza dos funciones críticas:
    1.  **Extracción de Fechas:** Analiza PDFs (`PyPDF2`) para identificar la fecha de cierre de la licitación.
    2.  **Análisis de Contenido (IA):** Procesa archivos Excel, extrae filas relevantes basadas en palabras clave y utiliza un sistema de doble-pase con la IA para (a) estructurar los datos en JSON y (b) realizar un filtro semántico para descartar cursos no relacionados con "Power Skills".
- **Cliente de Base de Datos (`src/database/bq_client.py`):** Interfaz para la ingesta de datos en **Google BigQuery**. Utiliza `pandas-gbq` para la carga eficiente de DataFrames.
- **Notificador (`src/utils/notificador.py`):** Módulo centralizado para el envío de alertas de éxito (nuevas licitaciones) y de error (fallos críticos de scrapers) a través de **Telegram** y **Email (SMTP)**.
- **Dashboard (`dashboard.py`):** Interfaz de visualización y gestión construida con **Streamlit**. Permite a los usuarios finales consultar las oportunidades activas, filtrar datos y realizar acciones como "descartar" o "restaurar" registros directamente en BigQuery.

---

## 2. Flujo de Datos (Data Pipeline)

1.  **Ejecución:** El `orquestador()` en `main.py` es invocado, ya sea localmente o mediante un workflow de GitHub Actions.
2.  **Memoria:** El orquestador consulta la tabla `oportunidades` en BigQuery para cargar en memoria los documentos y oportunidades ya procesados, evitando duplicados.
3.  **Patrullaje (Scraping):** El orquestador itera sobre la lista de scrapers.
    - Cada scraper (`fetch_tender_links()`) se ejecuta con una lógica de **3 reintentos** con pausas incrementales (30s, 60s) para mitigar fallos por inestabilidad de los sitios.
    - Si un scraper falla todos los intentos, el `Notificador` envía una alerta de error y el orquestador continúa con el siguiente.
4.  **Clasificación de Documentos:** Los enlaces recolectados son clasificados por el `AnalizadorLicitaciones`. Se priorizan los archivos Excel que parecen ser "Planes de Capacitación".
5.  **Análisis de Fecha (PDF):** Se busca un PDF de "bases" o "cronograma" para extraer la fecha de cierre usando `document_parser.py` y la IA de Groq. Si la fecha ya pasó, el proceso se marca como "Vencido" y se ahorra el análisis del Excel.
6.  **Análisis de Contenido (Excel):**
    - El Excel "ganador" se descarga localmente en un directorio temporal.
    - `document_parser.py` lee el Excel y pre-filtra las filas que contienen palabras clave de negocio.
    - Las filas relevantes se envían en lotes (batches) a la API de Groq para su estructuración y filtrado semántico.
7.  **Ingesta de Datos:**
    - Las oportunidades válidas (cursos) se convierten en un DataFrame de `pandas`.
    - El `BigQueryClient` utiliza `to_gbq()` para añadir los nuevos registros a la tabla `oportunidades` en BigQuery.
8.  **Notificación de Éxito:** Si la ingesta es exitosa, el `Notificador` envía una alerta a Telegram y por correo electrónico con los detalles de la nueva licitación.
9.  **Registro de Salud:** Al finalizar el ciclo de cada scraper (con éxito o fallo), se registra su estado en la tabla `estado_scrapers` de BigQuery.
10. **Visualización:** El `dashboard.py` consulta periódicamente las tablas `oportunidades` y `estado_scrapers` para mostrar la información actualizada. Utiliza `st.cache_data` para optimizar el rendimiento y `st_autorefresh` para la vista en vivo.

---

## 3. Configuración del Entorno

### 3.1. Prerrequisitos
- Python >= 3.10
- `pip` y `virtualenv` (recomendado)

### 3.2. Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/usuario/Lifebox-Radar.git
cd Lifebox-Radar

# 2. (Recomendado) Crear y activar un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

### 3.3. Variables de Entorno y Credenciales

El sistema se configura mediante un archivo `.env` para desarrollo local y mediante "Secrets" para despliegues en producción (ej. GitHub Actions).

Crear un archivo `.env` en la raíz del proyecto con la siguiente estructura:

```ini
# --- Credenciales de Google Cloud ---
# ID del proyecto en GCP.
GCP_PROJECT_ID="project-2c5ea44d-6d9d-4f1d-9a5"
# Ruta al archivo JSON de la cuenta de servicio con permisos para BigQuery.
GCP_CREDENTIALS_PATH="credenciales_gcp.json"

# --- Credenciales de la IA (Groq) ---
# API Key obtenida desde la consola de Groq.
GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxxxxxx"

# --- Credenciales de Telegram ---
# Token del bot de Telegram, obtenido de BotFather.
TELEGRAM_TOKEN="xxxxxxxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxx"
# ID del chat o canal donde se enviarán las notificaciones.
TELEGRAM_CHAT_ID="-100xxxxxxxxxx"

# --- Credenciales para envío de Correos (SMTP) ---
# Servidor SMTP (ej. smtp.gmail.com).
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
# Correo desde el cual se enviarán las notificaciones.
EMAIL_SENDER="tu_correo@gmail.com"
# Contraseña de aplicación (para Gmail) o contraseña del correo.
EMAIL_PASSWORD="xxxx xxxx xxxx xxxx"
# Correo(s) de destino. El notificador está configurado para leer una lista.
EMAIL_RECEIVER="destinatario1@ejemplo.com,destinatario2@ejemplo.com"

# --- Licencia (Opcional, para src/utils/sec.py) ---
URL_GIST=""
```

**IMPORTANTE:** El archivo `credenciales_gcp.json` debe ser obtenido desde la consola de Google Cloud (IAM y Administración > Cuentas de servicio) y colocado en la raíz del proyecto. **Nunca debe ser subido al repositorio.**

---

## 4. Mantenimiento y Troubleshooting

### 4.1. Añadir un Nuevo Scraper

1.  **Crear el archivo:** Crea un nuevo archivo Python en `src/scrapers/`, por ejemplo, `nuevootic.py`.
2.  **Implementar la clase:** La clase debe seguir la estructura de los scrapers existentes (ej. `AsimetScraperSelenium`). Debe tener un método `__init__` que configure el driver de Selenium y un método `fetch_tender_links()` que devuelva una tupla `(set_de_enlaces, titulo_del_proceso)`.
3.  **Integrar en el Orquestador:** Importa la nueva clase en `main.py` y añádela a la lista `scrapers` dentro de la función `orquestador()`.

    ```python
    # En main.py
    from src.scrapers.nuevootic import NuevaOticScraper
    ...
    scrapers = [
        ...
        ("Nueva OTIC", NuevaOticScraper())
    ]
    ```

### 4.2. Scraper Falla por "Cambio de Diseño"

Este es el error más común. Ocurre cuando la estructura HTML del sitio web de una OTIC cambia.

1.  **Identificar el Scraper:** La alerta de Telegram y los logs indicarán qué portal falló.
2.  **Ejecución Local:** Ejecuta el scraper de forma aislada para depurar.

    ```bash
    python src/scrapers/nombre_del_scraper.py
    ```

3.  **Inspección Manual:** Abre la URL del scraper en un navegador y utiliza las herramientas de desarrollador (F12) para inspeccionar los nuevos selectores (XPath o CSS) de los elementos que necesitas extraer.
4.  **Actualizar el Código:** Modifica los selectores en el archivo del scraper correspondiente.

### 4.3. Errores de Autenticación

- **Google BigQuery:**
    - Verifica que el archivo `credenciales_gcp.json` existe y la ruta en `.env` es correcta.
    - Asegúrate de que la cuenta de servicio tiene los roles `BigQuery Data Editor` y `BigQuery User`.
- **Groq API:**
    - Confirma que `GROQ_API_KEY` en `.env` es válida y no ha expirado.
- **Telegram / Email:**
    - Revisa los tokens, IDs y contraseñas en el archivo `.env`. Para Gmail, recuerda que se necesita una "Contraseña de aplicación".

### 4.4. Actualizar Dependencias

Si se añade una nueva librería, debe ser registrada en `requirements.txt`.

```bash
# Después de instalar una nueva librería (ej. pip install nueva-libreria)
pip freeze > requirements.txt
```

---