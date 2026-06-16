# 📋 QUICK REFERENCE - Lifebox Radar

## 🚀 Comandos Principales

```bash
# Instalar
pip install -r requirements.txt

# Ejecutar una sola vez
python main.py

# Ver dashboard
streamlit run dashboard.py

# Ver logs
tail -f logs/lifebox_radar.log
```

## 📁 Estructura Importante

```
src/
├── core/
│   ├── base_scraper.py    # Clase base para todos los scrapers
│   └── orchestrator.py     # Orquestador principal
├── config/
│   └── settings.py         # Configuración centralizada
├── scrapers/               # 10 scrapers específicos
├── database/
│   └── bq_client.py        # Cliente BigQuery
└── utils/                  # Herramientas auxiliares
```

## 🔑 Variables de Entorno

```env
GCP_PROJECT_ID=tu-proyecto
GCP_CREDENTIALS_PATH=credenciales_gcp.json
TELEGRAM_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx
LOG_LEVEL=INFO
```

## 📊 Archivos de Datos

| Tabla | Descripción |
|-------|-------------|
| `licitaciones.oportunidades` | Todas las licitaciones encontradas |
| `licitaciones.estado_scrapers` | Estado de salud de cada scraper |
| `licitaciones.analisis` | Análisis y clasificación de licitaciones |

## 🎯 Portales Monitoreados

1. Proforma
2. OTIC Nacional
3. Pro Aconcagua
4. Agrocap
5. Banotic
6. Alianza Pyme
7. OTIC Sofofa
8. CCC
9. Franco Chileno
10. Wines of Chile

## 🔄 Flujo de Ejecución

```
main.py
  ↓
Orchestrator.procesar_licitaciones()
  ↓
Para cada Scraper:
  - fetch_tender_links() → Obtiene URLs
  - parse_tender() → Extrae datos
  - Compara con histórico (BigQuery)
  ↓
Si hay NUEVAS:
  - Inserta en BigQuery
  - Envía notificación Telegram
  ↓
Registra estado en BigQuery
```

## 🆘 Troubleshooting Rápido

| Error | Solución |
|-------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `credenciales_gcp.json not found` | Descarga desde Google Cloud Console |
| `TELEGRAM_TOKEN not configured` | Verifica `.env` está bien |
| `No new tenders` | Normal, revisar portales manualmente |
| `Chrome not found` | Instala Chromium: `apt-get install chromium` |

## 📚 Documentación

- [Instalación](docs/INSTALLATION.md)
- [Manual de Usuario](docs/USER_GUIDE.md)
- [Arquitectura Técnica](docs/ARCHITECTURE.md)

## 🔗 Links Útiles

- [GCP Console](https://console.cloud.google.com/)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Telegram BotFather](https://t.me/BotFather)
- [Project Repository](https://github.com/consultoria-lifebox/Lifebox-Radar)

## 📞 Soporte

- Email: soporte@lifebox.cl
- GitHub Issues: [Reportar](https://github.com/consultoria-lifebox/Lifebox-Radar/issues)

---

**Última actualización:** Enero 2024
