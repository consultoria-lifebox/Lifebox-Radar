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

Si quieres, puedo generar una checklist automática de OTICs basada en los scrapers presentes en `src/scrapers/` y añadirla a este README.

---

**Checklist de scrapers**

A continuación hay una lista automática de los scrapers detectados en `src/scrapers/`. Marca el estado según corresponda.

- [ ] [agrocap](src/scrapers/agrocap.py)
- [ ] [alianzapyme](src/scrapers/alianzapyme.py)
- [ ] [banotic](src/scrapers/banotic.py)
- [ ] [ccc](src/scrapers/ccc.py)
- [ ] [francochileno](src/scrapers/francochileno.py)
- [ ] [otic](src/scrapers/otic.py)
- [ ] [oticsosofa](src/scrapers/oticsosofa.py)
- [ ] [proaconcagua](src/scrapers/proaconcagua.py)
- [ ] [proforma](src/scrapers/proforma.py)
- [ ] [winesofchile](src/scrapers/winesofchile.py)

- [ ] [asimet](src/scrapers/asimet.py)
- [ ] [otic_del_comercio](src/scrapers/otic_del_comercio.py)
- [ ] [corficap](src/scrapers/corficap.py)
- [ ] [camacoes](src/scrapers/camacoes.py)
- [ ] [cgci](src/scrapers/cgci.py)

Si quieres, puedo marcar automáticamente algunos como "En funcionamiento" según el historial del proyecto, o generar issues para los que falten pruebas.