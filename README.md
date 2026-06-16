# 🎯 Lifebox Radar - Sistema de Vigilancia de Licitaciones

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Monitorea automáticamente las licitaciones de múltiples OTICs y portales en tiempo real**, enviando notificaciones instantáneas a tu teléfono cuando se publican nuevas oportunidades.

---

## 📌 ¿Qué es Lifebox Radar?

Lifebox Radar es una **plataforma de vigilancia inteligente** que:

✅ **Monitorea 10+ portales de licitaciones** de OTICs chilenas en tiempo real  
✅ **Detecta automáticamente nuevas publicaciones** sin que tengas que revisar manualmente  
✅ **Envía alertas instantáneas** por Telegram a tu teléfono  
✅ **Almacena histórico en BigQuery** para análisis y reportes  
✅ **Dashboard interactivo** con visualización de datos en Streamlit  
✅ **Análisis inteligente** de licitaciones con IA  

---

## 🚀 Inicio Rápido (4 pasos)

### 1️⃣ **Clonar el repositorio**
```bash
git clone https://github.com/consultoria-lifebox/Lifebox-Radar.git
cd Lifebox-Radar
```

### 2️⃣ **Instalar dependencias**
```bash
pip install -r requirements.txt
```

### 3️⃣ **Configurar variables de entorno**
```bash
cp .env.example .env
# Edita .env con tus credenciales
```

### 4️⃣ **Ejecutar el sistema**
```bash
# Ejecutar scraping (una sola vez)
python main.py

# Ver el Dashboard
streamlit run dashboard.py
```

---

## 📋 Portales Monitoreados

| Portal | OTIC | Estado |
|--------|------|--------|
| 🔗 Proforma | Proforma | ✅ Activo |
| 🔗 OTIC Nacional | OTIC | ✅ Activo |
| 🔗 Pro Aconcagua | Pro Aconcagua | ✅ Activo |
| 🔗 Agrocap | Agrocap | ✅ Activo |
| 🔗 Banotic | Banotic | ✅ Activo |
| 🔗 Alianza Pyme | Alianza Pyme | ✅ Activo |
| 🔗 OTIC Sofofa | OTIC Sofofa | ✅ Activo |
| 🔗 CCC | CCC | ✅ Activo |
| 🔗 Franco Chileno | Franco Chileno | ✅ Activo |
| 🔗 Wines of Chile | Wines of Chile | ✅ Activo |

---

## 🏗️ Estructura del Proyecto

```
Lifebox-Radar/
├── src/                           # Código fuente
│   ├── core/                      # Lógica principal
│   │   ├── base_scraper.py       # Clase base para todos los scrapers
│   │   └── orchestrator.py       # Orquestador central
│   │
│   ├── config/                    # Configuración centralizada
│   │   └── settings.py           # Variables y configuración
│   │
│   ├── scrapers/                  # Módulos de scraping
│   │   ├── proforma.py
│   │   ├── otic.py
│   │   ├── agrocap.py
│   │   └── ... (7 más)
│   │
│   ├── database/                  # Gestión de datos
│   │   └── bq_client.py          # Cliente de BigQuery
│   │
│   └── utils/                     # Herramientas auxiliares
│       ├── logger.py
│       ├── alerts.py
│       ├── analizador_inteligente.py
│       └── document_parser.py
│
├── docs/                          # Documentación
│   ├── INSTALLATION.md
│   ├── USER_GUIDE.md
│   └── ARCHITECTURE.md
│
├── main.py                        # Script principal
├── dashboard.py                   # Dashboard Streamlit
├── requirements.txt
└── .env.example
```

---

## ⚙️ Requisitos Previos

- Python 3.9+
- Google Cloud Project con BigQuery
- Telegram Bot para notificaciones
- Chrome/Chromium

---

## 📚 Documentación

- **[📖 Guía de Instalación](docs/INSTALLATION.md)** - Paso a paso completo
- **[👤 Manual de Usuario](docs/USER_GUIDE.md)** - Cómo usar el sistema
- **[🏛️ Arquitectura Técnica](docs/ARCHITECTURE.md)** - Para desarrolladores

---

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/mi-feature`)
3. Commit tus cambios
4. Push y abre un Pull Request

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE)

---

## 📞 Soporte

- 📧 soporte@lifebox.cl
- 🐛 [GitHub Issues](https://github.com/consultoria-lifebox/Lifebox-Radar/issues)

**⭐ Si te resulta útil, dale una estrella!**