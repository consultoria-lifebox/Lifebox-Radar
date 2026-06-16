# 🏗️ Estructura del Proyecto Detallada

## 📂 Vista Completa del Proyecto

```
Lifebox-Radar/
│
├── 📄 README.md                          ← EMPIEZA AQUÍ
├── 📄 QUICK_REFERENCE.md                 ← Referencia rápida
├── 📄 main.py                            ← Script principal
├── 📄 dashboard.py                       ← Dashboard Streamlit
├── 📄 requirements.txt                   ← Dependencias Python
├── 📄 .env.example                       ← Template de configuración
├── 📄 .gitignore                         ← Archivos ignorados
│
├── 📁 docs/                              ← DOCUMENTACIÓN
│   ├── 📄 INSTALLATION.md                ← Guía de instalación
│   ├── 📄 USER_GUIDE.md                  ← Manual de usuario
│   └── 📄 ARCHITECTURE.md                ← Documentación técnica
│
├── 📁 src/                               ← CÓDIGO FUENTE
│   │
│   ├── 📁 core/                          ← 🎯 LÓGICA PRINCIPAL
│   │   ├── 📄 __init__.py
│   │   ├── 📄 base_scraper.py            ← Clase base para scrapers
│   │   │   └── Proporciona:
│   │   │       - Inicialización Selenium
│   │   │       - Métodos de navegación segura
│   │   │       - Manejo de errores centralizado
│   │   │       - Logging automático
│   │   │
│   │   └── 📄 orchestrator.py            ← Orquestador principal
│   │       └── Responsable de:
│   │           - Coordinar todos los scrapers
│   │           - Comparar con histórico BigQuery
│   │           - Enviar notificaciones
│   │           - Registrar estado
│   │
│   ├── 📁 config/                        ← ⚙️ CONFIGURACIÓN
│   │   ├── 📄 __init__.py
│   │   └── 📄 settings.py                ← Configuración centralizada
│   │       ├── GoogleCloudConfig
│   │       ├── TelegramConfig
│   │       ├── LoggingConfig
│   │       ├── ScraperConfig
│   │       └── Config (agregador)
│   │
│   ├── 📁 scrapers/                      ← 🕷️ WEB SCRAPING
│   │   ├── 📄 __init__.py
│   │   ├── 📄 proforma.py               ← Scraper para Proforma OTIC
│   │   ├── 📄 otic.py                   ← Scraper para OTIC Nacional
│   │   ├── 📄 proaconcagua.py           ← Scraper para Pro Aconcagua
│   │   ├── 📄 agrocap.py                ← Scraper para Agrocap
│   │   ├── 📄 banotic.py                ← Scraper para Banotic
│   │   ├── 📄 alianzapyme.py            ← Scraper para Alianza Pyme
│   │   ├── 📄 oticsosofa.py             ← Scraper para OTIC Sofofa
│   │   ├── 📄 ccc.py                    ← Scraper para CCC
│   │   ├── 📄 francochileno.py          ← Scraper para Franco Chileno
│   │   └── 📄 winesofchile.py           ← Scraper para Wines of Chile
│   │       └── Cada scraper extiende:
│   │           - BaseScraper
│   │           - Implementa fetch_tender_links()
│   │           - Implementa parse_tender()
│   │
│   ├── 📁 database/                      ← 💾 ACCESO A DATOS
│   │   ├── 📄 __init__.py
│   │   └── 📄 bq_client.py              ← Cliente Google BigQuery
│   │       └── Maneja:
│   │           - Conexión a BigQuery
│   │           - Inserts de licitaciones
│   │           - Queries para histórico
│   │           - Registros de estado
│   │
│   └── 📁 utils/                         ← 🛠️ HERRAMIENTAS
│       ├── 📄 __init__.py
│       ├── 📄 logger.py                 ← Configuración de logs
│       │   └── Logger centralizado
│       ├── 📄 alerts.py                 ← Notificaciones Telegram
│       │   ├── enviar_notificacion()
│       │   └── enviar_alerta_error()
│       ├── 📄 analizador_inteligente.py ← Análisis con IA
│       │   └── AnalizadorLicitaciones
│       ├── 📄 document_parser.py        ← Extracción de PDFs
│       │   └── DocumentAnalyzer
│       └── 📄 sec.py                    ← Verificación de licencias
│           └── verificar_lic()
│
├── 📁 logs/                              ← 📊 ARCHIVOS DE LOG
│   ├── lifebox_radar.log                ← Log general
│   ├── scrapers.log                     ← Log de scrapers
│   └── errors.log                       ← Solo errores
│
└── 📁 tests/                             ← 🧪 TESTS (Opcional)
    ├── test_base_scraper.py
    ├── test_orchestrator.py
    └── test_config.py
```

---

## 🔄 Relaciones entre Módulos

```
main.py
  │
  ├─► Orchestrator (src/core/orchestrator.py)
  │   ├─► Config.get_config() (src/config/settings.py)
  │   ├─► BaseScraper (src/core/base_scraper.py)
  │   │   └─► Cada scraper específico
  │   │       (src/scrapers/*.py)
  │   ├─► BigQueryClient (src/database/bq_client.py)
  │   ├─► enviar_notificacion() (src/utils/alerts.py)
  │   └─► verificar_lic() (src/utils/sec.py)
  │
  └─► AnalizadorLicitaciones (src/utils/analizador_inteligente.py)
  
dashboard.py
  ├─► pandas_gbq (para consultas)
  ├─► BigQueryClient
  └─► Streamlit (visualización)
```

---

## 📝 Descripción de Cada Archivo

### Archivos Raíz

| Archivo | Propósito |
|---------|----------|
| `main.py` | Punto de entrada principal, ejecuta los scrapers |
| `dashboard.py` | Dashboard interactivo con Streamlit |
| `requirements.txt` | Dependencias Python del proyecto |
| `.env.example` | Template de variables de entorno |
| `README.md` | Documentación principal |
| `QUICK_REFERENCE.md` | Referencia rápida |

### src/core/

| Archivo | Responsabilidad |
|---------|-----------------|
| `base_scraper.py` | Clase abstracta con métodos comunes de scraping |
| `orchestrator.py` | Orquesta la ejecución de todos los scrapers |

### src/config/

| Archivo | Responsabilidad |
|---------|-----------------|
| `settings.py` | Define todas las configuraciones del proyecto |

### src/scrapers/

Cada archivo implementa un scraper específico para un portal OTIC.

**Estructura típica:**

```python
from src.core.base_scraper import BaseScraper

class NombreOticScraper(BaseScraper):
    def __init__(self):
        super().__init__("Nombre OTIC", "https://url.com")
    
    def fetch_tender_links(self) -> Set[str]:
        # Lógica específica para extraer links
        pass
    
    def parse_tender(self, url: str) -> dict:
        # Lógica específica para parsear licitación
        pass
```

### src/database/

| Archivo | Responsabilidad |
|---------|-----------------|
| `bq_client.py` | Gestiona conexiones y operaciones con BigQuery |

### src/utils/

| Archivo | Responsabilidad |
|---------|-----------------|
| `logger.py` | Configuración de logging centralizado |
| `alerts.py` | Envío de notificaciones por Telegram |
| `analizador_inteligente.py` | Análisis y clasificación de licitaciones con IA |
| `document_parser.py` | Extracción de información de PDFs |
| `sec.py` | Verificación de licencias |

### docs/

| Documento | Audiencia |
|-----------|-----------|
| `INSTALLATION.md` | Usuarios finales |
| `USER_GUIDE.md` | Usuarios finales |
| `ARCHITECTURE.md` | Desarrolladores |

---

## 🎯 Flujo de Datos

```
ENTRADA
  ↓
┌─────────────────────────────────────────┐
│  main.py                                │
│  └─ Importa Orchestrator                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Orchestrator                           │
│  ├─ Carga Config                        │
│  ├─ Obtiene histórico de BigQuery       │
│  └─ Ejecuta cada scraper                │
└──────────────┬──────────────────────────┘
               │
        ┌──────┴──────┬──────┬────────┐
        │             │      │        │
        ▼             ▼      ▼        ▼
    ┌─────────┐  ┌────────┐ ┌─────────┐
    │ Proforma│  │ OTIC   │ │Agrocap  │
    │ Scraper │  │Scraper │ │ Scraper │ ...
    └────┬────┘  └───┬────┘ └─────────┘
         │           │
         └─────┬─────┘
               │
               ▼
    ┌──────────────────────────┐
    │  BigQuery (Base de Datos)│
    │  - Inserta licitaciones  │
    │  - Registra estado       │
    └────────────┬─────────────┘
                 │
                 ├──► Telegram (Notificaciones)
                 ├──► Logs (Archivos log)
                 └──► Dashboard (Visualización)

SALIDA: Datos organizados, usuarios notificados
```

---

## 💡 Mejoras Implementadas vs Estructura Anterior

### ❌ Anterior
- Código duplicado en cada scraper
- main.py con 300+ líneas de lógica mezclada
- Configuración esparcida en múltiples archivos
- Sin separación de responsabilidades

### ✅ Ahora
- BaseScraper centraliza código común
- main.py limpio y legible (importa Orchestrator)
- src/config/settings.py concentra toda configuración
- Cada módulo tiene una responsabilidad clara
- Fácil de mantener y extender

---

## 🚀 Cómo Navegar el Código

### 1. Entender el flujo general
```
LEE: README.md → QUICK_REFERENCE.md → main.py
```

### 2. Entender cómo funcionan los scrapers
```
LEE: src/core/base_scraper.py → src/scrapers/proforma.py
```

### 3. Entender la configuración
```
LEE: src/config/settings.py → .env.example
```

### 4. Entender orquestación
```
LEE: src/core/orchestrator.py → main.py
```

### 5. Entender integración con GCP
```
LEE: src/database/bq_client.py → docs/ARCHITECTURE.md
```

---

## 📊 Estadísticas del Proyecto

| Métrica | Valor |
|---------|-------|
| Total Scrapers | 10 |
| Líneas de Código (src/) | ~2000 |
| Módulos | 8+ |
| Portales Monitoreados | 10 OTICs |
| Tablas BigQuery | 3+ |

---

**¡Ahora entiendes la estructura completa del proyecto!** 🎉
