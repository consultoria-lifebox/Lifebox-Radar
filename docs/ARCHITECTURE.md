# 🏛️ Documentación Técnica - Arquitectura

Documentación detallada de la arquitectura técnica de Lifebox Radar para desarrolladores.

---

## 🏗️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                    LIFEBOX RADAR                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Tier de Presentación                                │   │
│  │  ├── main.py (Script CLI)                            │   │
│  │  └── dashboard.py (Streamlit Web UI)                 │   │
│  └────────────┬─────────────────────────────────────────┘   │
│               │                                              │
│  ┌────────────▼─────────────────────────────────────────┐   │
│  │  Tier de Lógica de Negocio                           │   │
│  │  ├── src/core/                                       │   │
│  │  │   ├── orchestrator.py (Orquestación)              │   │
│  │  │   └── base_scraper.py (Clase base)                │   │
│  │  ├── src/config/ (Configuración)                     │   │
│  │  └── src/utils/ (Utilidades)                         │   │
│  │      ├── alerts.py (Notificaciones)                  │   │
│  │      ├── logger.py (Logging)                         │   │
│  │      └── analizador_inteligente.py (IA)              │   │
│  └────────────┬─────────────────────────────────────────┘   │
│               │                                              │
│  ┌────────────▼─────────────────────────────────────────┐   │
│  │  Tier de Acceso a Datos                              │   │
│  │  ├── src/scrapers/ (10 scrapers Selenium)            │   │
│  │  └── src/database/ (BigQuery Client)                 │   │
│  └────────────┬─────────────────────────────────────────┘   │
│               │                                              │
│  ┌────────────▼─────────────────────────────────────────┐   │
│  │  Tier de Integración Externa                         │   │
│  │  ├── Google BigQuery (Data Lake)                     │   │
│  │  ├── Telegram API (Notificaciones)                   │   │
│  │  └── Portales OTIC (Fuentes de datos)                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Estructura de Directorios

```
src/
├── core/                    # 🎯 Lógica principal
│   ├── __init__.py
│   ├── base_scraper.py     # Clase abstracta padre de todos los scrapers
│   └── orchestrator.py      # Coordinador de scrapers y flujo de datos
│
├── config/                  # ⚙️ Configuración centralizada
│   ├── __init__.py
│   └── settings.py          # Variables de entorno y configuración
│
├── scrapers/                # 🕷️ Módulos de web scraping
│   ├── __init__.py
│   ├── proforma.py
│   ├── otic.py
│   ├── agrocap.py
│   ├── banotic.py
│   ├── alianzapyme.py
│   ├── oticsosofa.py
│   ├── ccc.py
│   ├── francochileno.py
│   └── winesofchile.py
│
├── database/                # 💾 Acceso a datos
│   ├── __init__.py
│   └── bq_client.py        # Cliente de Google BigQuery
│
└── utils/                   # 🛠️ Herramientas auxiliares
    ├── __init__.py
    ├── logger.py           # Configuración de logging
    ├── alerts.py           # Notificaciones por Telegram
    ├── analizador_inteligente.py  # Análisis con IA
    ├── document_parser.py  # Extracción de PDFs
    └── sec.py              # Verificación de licencias
```

---

## 🔄 Flujo de Datos

### 1. Inicio de Ejecución

```python
# main.py
if __name__ == "__main__":
    orchestrator = Orchestrator()
    
    # Obtiene histórico de BigQuery
    archivos_conocidos = orchestrator.obtener_archivos_conocidos()
    
    # Lista de scrapers a ejecutar
    scrapers = [
        ("Proforma", ProformaScraperSelenium()),
        ("OTIC", OticScraperSelenium()),
        # ... más
    ]
    
    # Ejecuta todos
    resultados = orchestrator.procesear_licitaciones(scrapers)
```

### 2. Ejecución de un Scraper

```
BaseScraper
  ├── start() → Abre navegador Chrome con Selenium
  ├── fetch_tender_links() → Extrae URLs de licitaciones
  ├── parse_tender(url) → Parsea cada licitación
  ├── stop() → Cierra navegador
  └── Retorna lista de diccionarios
```

### 3. Almacenamiento en BigQuery

```python
# Datos se envían a BigQuery con:
{
    "link_documento": "https://...",
    "titulo_llamado_web": "Diplomado en...",
    "portal": "Proforma",
    "fecha_publicacion": "2024-01-15",
    "estado": "activo",
    "descripcion": "...",
    "fecha_ingesta": "2024-01-15 10:30:00"
}
```

### 4. Notificación al Usuario

```
Si es NUEVA → Envía alert a Telegram
Si es ERROR → Envía alert de error
Si es OK → Log en archivo
```

---

## 🔑 Clases Principales

### BaseScraper

**Ubicación:** `src/core/base_scraper.py`

**Propósito:** Clase abstracta que proporciona funcionalidad común

**Métodos principales:**

```python
class BaseScraper(ABC):
    def __init__(self, portal_name: str, url: str)
    def _init_driver() → WebDriver
    def start()
    def stop()
    def wait_for_element(by, selector, timeout)
    def safe_get(url)
    def extract_text(element)
    
    @abstractmethod
    def fetch_tender_links() → Set[str]
    
    @abstractmethod
    def parse_tender(url) → dict
    
    def execute() → List[dict]  # Ejecuta el scraping
```

**Uso:**

```python
class ProformaScraperSelenium(BaseScraper):
    def __init__(self):
        super().__init__("Proforma", "https://proforma.cl")
    
    def fetch_tender_links(self):
        # Implementación específica
        pass
    
    def parse_tender(self, url):
        # Implementación específica
        pass
```

### Orchestrator

**Ubicación:** `src/core/orchestrator.py`

**Propósito:** Coordina la ejecución de todos los scrapers

**Métodos principales:**

```python
class Orchestrator:
    def obtener_archivos_conocidos() → Set[str]
    def registrar_estado_scraper(portal, estado, mensaje)
    def ejecutar_scraper(nombre, scraper) → Tuple[bool, List]
    def procesar_licitaciones(scrapers) → Dict
```

### Config

**Ubicación:** `src/config/settings.py`

**Propósito:** Gestión centralizada de configuración

**Componentes:**

```python
@dataclass
class GoogleCloudConfig:
    project_id
    credentials_path
    dataset_id
    
@dataclass
class TelegramConfig:
    token
    chat_id
    
@dataclass
class ScraperConfig:
    timeout
    headless
    user_agent
```

---

## 🌐 Integración con Google BigQuery

### Esquema de Tabla

```sql
CREATE TABLE `proyecto.licitaciones.oportunidades` (
  link_documento STRING,
  titulo_llamado_web STRING,
  portal STRING,
  fecha_publicacion TIMESTAMP,
  estado STRING,
  descripcion STRING,
  requiere_postulacion BOOL,
  fecha_ingesta TIMESTAMP,
  
  PRIMARY KEY (link_documento)
);

CREATE TABLE `proyecto.licitaciones.estado_scrapers` (
  fecha_ejecucion TIMESTAMP,
  portal STRING,
  estado STRING,
  mensaje STRING
);
```

### Operaciones Comunes

```python
from src.database.bq_client import BigQueryClient

bq = BigQueryClient()

# Insertar licitaciones
bq.insert_licitaciones(df_licitaciones)

# Consultar histórico
df = bq.get_licitaciones_desde(dias=30)

# Actualizar estado
bq.update_estado_scraper("Proforma", "success")
```

---

## 🔐 Seguridad

### Variables de Entorno

```env
# ✅ NUNCA commitear estos valores
GCP_CREDENTIALS_PATH=credenciales_gcp.json
TELEGRAM_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx
```

### .gitignore

```
.env
credenciales_gcp.json
*.pyc
__pycache__/
logs/
venv/
.DS_Store
```

### Permisos Recomendados

**Service Account GCP:**
- `roles/bigquery.dataEditor` (escribir datos)
- `roles/bigquery.jobUser` (ejecutar queries)

**Token Telegram:**
- Específico para un bot
- Regenerable si se compromete

---

## 🚀 Desempeño y Escalabilidad

### Optimizaciones Implementadas

1. **Selenium Configuration**
   - `page_load_strategy = "eager"` (no espera load completo)
   - `--disable-gpu` y `--headless` (menos recursos)
   - Timeouts configurables

2. **BigQuery**
   - Batch inserts (más eficiente)
   - Particionamiento por fecha
   - Índices en columnas frecuentes

3. **Concurrencia Futura**
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   with ThreadPoolExecutor(max_workers=3) as executor:
       futures = [executor.submit(scraper.execute) for scraper in scrapers]
   ```

---

## 🧪 Testing

### Tests Unitarios

```python
# tests/test_base_scraper.py
def test_init_driver():
    scraper = BaseScraper("Test", "https://test.com")
    driver = scraper._init_driver()
    assert driver is not None
    driver.quit()

def test_extract_text():
    scraper = BaseScraper("Test", "https://test.com")
    from selenium.webdriver.remote.webelement import WebElement
    # Mock element
    assert scraper.extract_text(None) == ""
```

### Tests de Integración

```python
# tests/test_orchestrator.py
def test_obtener_archivos_conocidos():
    orch = Orchestrator()
    archivos = orch.obtener_archivos_conocidos()
    assert isinstance(archivos, set)
```

---

## 📊 Monitoreo y Logging

### Niveles de Log

```python
logging.DEBUG    # Detalles de ejecución
logging.INFO     # Eventos importantes
logging.WARNING  # Advertencias
logging.ERROR    # Errores
logging.CRITICAL # Fallos críticos
```

### Ubicación de Logs

```
logs/
├── lifebox_radar.log      # Log general
├── scrapers.log           # Log de scrapers
└── errors.log             # Solo errores
```

### Ejemplo de Output

```
2024-01-15 10:30:45 - Orchestrator - INFO - === INICIANDO SISTEMA ===
2024-01-15 10:30:46 - Orchestrator - INFO - 🧠 Consultando BigQuery...
2024-01-15 10:30:48 - Scraper.Proforma - INFO - 🚀 Ejecutando Proforma...
2024-01-15 10:30:52 - Scraper.Proforma - INFO - 📊 Encontrados 3 enlaces
2024-01-15 10:30:58 - Scraper.Proforma - INFO - ✅ Completado (2 nuevas)
```

---

## 🔄 Ciclo de Vida de una Licitación

```
1. DISCOVERY (Scraping)
   └─ Scraper encuentra URL

2. PARSING
   └─ Extrae información

3. DEDUPLICATION
   └─ Compara con histórico

4. STORAGE
   └─ Guarda en BigQuery

5. NOTIFICATION
   └─ Si es nueva, notifica usuario

6. ANALYTICS (Dashboard)
   └─ Se visualiza en dashboard
```

---

## 🚦 Estados de un Scraper

```
┌──────────┐
│  INICIO  │
└────┬─────┘
     │
     ▼
┌──────────────┐    TIMEOUT    ┌───────────┐
│   SCRAPING   ├──────────────►│  TIMEOUT  │
└────┬─────────┘                └───────────┘
     │ ERROR
     ├───────────────┐
     │               ▼
     │          ┌──────────┐
     │          │  ERROR   │
     │          └──────────┘
     │ OK
     ▼
┌──────────────┐
│  COMPLETADO  │
└──────────────┘
```

---

## 📝 Extender el Sistema

### Agregar un Nuevo Scraper

1. Crea archivo `src/scrapers/mi_otic.py`

```python
from src.core.base_scraper import BaseScraper

class MiOticScraper(BaseScraper):
    def __init__(self):
        super().__init__("Mi OTIC", "https://mi-otic.cl")
    
    def fetch_tender_links(self):
        self.safe_get(self.url)
        # Tu lógica aquí
        return set(links)
    
    def parse_tender(self, url):
        # Tu lógica aquí
        return {
            "titulo": "...",
            "link": url,
            # ...
        }
```

2. Actualiza `main.py`:

```python
from src.scrapers.mi_otic import MiOticScraper

scrapers = [
    # ...
    ("Mi OTIC", MiOticScraper()),
]
```

---

## 🔗 Recursos Útiles

- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Google BigQuery Python Client](https://cloud.google.com/bigquery/docs/reference/python)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Python Logging](https://docs.python.org/3/library/logging.html)

---

**¡Felicidades! Ya entiendes la arquitectura de Lifebox Radar.** 🎉
