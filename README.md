# Lifebox Radar

Monitoreo automático de licitaciones y alertas. Este proyecto rastrea portales y OTICs, centraliza datos en Google BigQuery y envía notificaciones por Telegram. Incluye scrapers basados en Selenium y un dashboard en Streamlit para visualización.

---

**Estado del repositorio**

- Lenguaje: Python 3.10+
- Orquestador: `main.py`
- Dashboard: `dashboard.py` (Streamlit)

---

## Dependencias principales

Lista de librerías usadas (ver `requirements.txt`):

- `streamlit`
- `pandas`
- `pandas-gbq`
- `google-auth`, `google-cloud-bigquery`
- `webdriver-manager`, `selenium`
- `beautifulsoup4` (`bs4`)
- `PyPDF2`
- `groq`
- `python-dotenv`

Instalación rápida:

```bash
pip install -r requirements.txt
```

---

## Variables de entorno y Secrets

Configurar en `.env` localmente (NO subir) o como Secrets en GitHub Actions:

- `GCP_PROJECT_ID` — ID del proyecto GCP
- `GCP_CREDENTIALS_PATH` — Ruta al JSON de la service account (ej. `credenciales_gcp.json`)
- `GCP_CREDENTIALS` — (GitHub Actions secret) JSON de credenciales para CI
- `TELEGRAM_TOKEN` — Token del bot de Telegram
- `TELEGRAM_CHAT_ID` — Chat ID receptor de notificaciones
- `GROQ_API_KEY` — API key para Groq
- `URL_GIST` — URL para validación de licencia (opcional)

El workflow en `.github/workflows/motor.yml` utiliza los secrets: `GCP_CREDENTIALS`, `GROQ_API_KEY`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`, `URL_GIST`.

---

## OTICs y portales

Estado de integraciones (actualízalo según progreso):

- En funcionamiento:
	- Proforma
	- OTIC Nacional
	- Pro Aconcagua
	- Agrocap
	- Banotic
	- AlianzaPyme
	- OTIC Sofofa
	- Franco Chileno
	- Wines of Chile
	- CCC

- En progreso / revisar:
	- (Agregar los scrapers en desarrollo o con errores de diseño)

---

## Tecnologías y servicios usados

- Google BigQuery — Almacenamiento y consultas
- Telegram API — Envío de notificaciones
- Selenium + WebDriver — Scraping de sitios dinámicos
- Streamlit — Dashboard
- Groq — Procesamiento y extracción desde documentos (IA)

---

## Ejecución local

1. Copia y edita `.env` desde `.env.example`.
2. Instala dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecuta el orquestador:

```bash
python main.py
```

4. Levanta el dashboard:

```bash
streamlit run dashboard.py
```

---

## Buenas prácticas

- No subir credenciales ni tokens al repositorio.
- Usa GitHub Secrets para CI/CD.
- Mantén `requirements.txt` actualizado.

---
