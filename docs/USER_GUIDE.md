# 👤 Manual de Usuario - Lifebox Radar

Esta guía te mostrará cómo usar Lifebox Radar para monitorear licitaciones.

---

## 🎯 ¿Cómo Funciona?

Lifebox Radar automatiza el proceso de búsqueda de licitaciones:

```
┌─────────────────┐
│  Portales OTIC  │
│  (10 sitios)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Web Scraping (Selenium)    │
│  Extrae nuevas licitaciones │
└────────┬────────────────────┘
         │
         ▼
┌──────────────────────────┐
│  BigQuery                │
│  Almacena datos          │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Tu Teléfono             │
│  (Notificación Telegram) │
└──────────────────────────┘
```

---

## 🚀 Formas de Usar el Sistema

### 1️⃣ Ejecutar una Sola Vez

```bash
python main.py
```

**Ideal para:** Hacer una búsqueda rápida ahora

**Output esperado:**
```
=== INICIANDO SISTEMA DE VIGILANCIA MULTI-PORTAL ===
🧠 Consultando memoria en BigQuery...
✅ 245 registros en memoria
🚀 Ejecutando Proforma...
📊 Encontrados 3 enlaces en Proforma
🆕 2 licitaciones nuevas en Proforma
🚀 Ejecutando OTIC...
...
```

### 2️⃣ Ver el Dashboard

```bash
streamlit run dashboard.py
```

**Accede a:** `http://localhost:8501`

**Qué ves:**
- Licitaciones nuevas
- Tendencias por OTIC
- Tabla histórica completa
- Gráficos de actividad

### 3️⃣ Ejecutar Automáticamente

**En Windows (Programador de tareas):**

1. Abre **Ejecutar** y escribe: `taskschd.msc`
2. Click derecho en **Task Scheduler Library**
3. **Create Basic Task...**
   - Name: "Lifebox Radar Monitor"
   - Trigger: "Diariamente" a las 8:00 AM
   - Action: Ejecutar `python main.py`

**En Mac/Linux (Cron):**

```bash
crontab -e
```

Agrega esta línea para ejecutar cada hora:

```cron
0 * * * * cd /ruta/Lifebox-Radar && python main.py
```

---

## 📊 Entender el Dashboard

El dashboard muestra:

### KPIs Principales
- **Total Licitaciones:** Todas las registradas
- **Nuevas Hoy:** Publicadas en las últimas 24 horas
- **OTICs Activas:** Cuántas tienen llamados abiertos
- **Última Actualización:** Hora del último scraping

### Gráfico de Tendencias
- Muestra licitaciones por día
- Identifica picos de actividad
- Ayuda a planificar

### Tabla de Licitaciones
- Filtrar por OTIC, fecha, estado
- Descargar como CSV
- Ver detalles completos

---

## 🔔 Notificaciones por Telegram

### Recibir Alertas

Cuando se encuentra una licitación nueva, recibirás en Telegram:

```
🚨 ¡NUEVA LICITACIÓN EN PROFORMA! 🚨
Proceso: Diplomado en Gestión Empresarial
🎯 Se inyectaron 1 oportunidades en BigQuery.
```

### Tipos de Notificaciones

| Tipo | Ejemplo |
|------|---------|
| 🆕 Nueva Licitación | Ej: "Curso de Excel" |
| ⚠️ Error en Scraper | Ej: "Portal caído" |
| ✅ Ejecución Exitosa | "Scraping completado" |

### Deshabilitar Notificaciones

En `.env`, comenta estas líneas:

```env
# TELEGRAM_TOKEN=...
# TELEGRAM_CHAT_ID=...
```

---

## 💾 Datos en BigQuery

### Acceder a tus Datos

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Abre **BigQuery**
3. Navega a tu proyecto

### Consultas Útiles

#### Ver todas las licitaciones

```sql
SELECT * 
FROM `proyecto-life-box-licitaciones.licitaciones.oportunidades`
ORDER BY fecha_publicacion DESC
LIMIT 50
```

#### Licitaciones por OTIC

```sql
SELECT portal, COUNT(*) as cantidad
FROM `proyecto-life-box-licitaciones.licitaciones.oportunidades`
GROUP BY portal
ORDER BY cantidad DESC
```

#### Licitaciones de hoy

```sql
SELECT *
FROM `proyecto-life-box-licitaciones.licitaciones.oportunidades`
WHERE DATE(fecha_publicacion) = CURRENT_DATE()
ORDER BY fecha_publicacion DESC
```

---

## 🎨 Personalización

### Cambiar Portales a Monitorear

En `main.py`, comenta los scrapers que no quieras:

```python
scrapers = [
    ("Proforma", ProformaScraperSelenium()),
    # ("OTIC", OticScraperSelenium()),  # 🔇 Desactivado
    ("Pro Aconcagua", ProAconcaguaScraperSelenium()),
    # ... más
]
```

### Cambiar Frecuencia de Actualización

En `dashboard.py`:

```python
# Cambiar de 300 segundos (5 min) a 600 (10 min)
st_autorefresh(interval=600000, limit=None, key="autorefresh")
```

### Personalizar Notificaciones Telegram

En `src/utils/alerts.py`, edita el mensaje:

```python
contenido = f"🎯 NUEVA OPORTUNIDAD EN {portal}\n{titulo}"
```

---

## 📈 Casos de Uso

### Caso 1: Empleador Buscando Capacitar Personal

```
1. Ejecuta: python main.py
2. Abre el dashboard
3. Filtra por OTIC de tu interés
4. Recibe alertas cuando hay nuevos cursos
```

### Caso 2: Consultor de Recursos Humanos

```
1. Configura auto-ejecución cada mañana
2. Revisa el dashboard antes de llamar clientes
3. Identifica tendencias de capacitación
```

### Caso 3: Responsable de Cumplimiento

```
1. Exporta datos mensualmente
2. Crea reportes para auditoría
3. Documenta todos los llamados encontrados
```

---

## 🔍 Interpretar Datos

### Campos de una Licitación

| Campo | Significado |
|-------|-------------|
| **título_llamado_web** | Nombre del curso/programa |
| **portal** | OTIC que lo publica |
| **link_documento** | URL para ver detalles |
| **fecha_publicacion** | Cuándo se publicó |
| **estado** | activo, cerrado, etc |

### Filtros Recomendados

```python
# Ver solo licitaciones activas
df = df[df['estado'] == 'activo']

# Ver solo últimas 7 días
df = df[df['fecha_publicacion'] >= '2024-01-08']

# Ver solo una OTIC
df = df[df['portal'] == 'Proforma']
```

---

## ⏰ Horarios Recomendados

### Para Ejecutar Scraping

| Horario | Ventaja |
|---------|---------|
| **08:00 AM** | Antes de trabajar, ves novedades |
| **12:00 PM** | Medio día, actualizaciones matinales |
| **17:00 (5 PM)** | Fin de día, todo actualizado |
| **Cada hora** | Máxima actualizaciones |

---

## 🐛 Problemas Comunes

### "No recibo notificaciones en Telegram"

1. Verifica que `.env` tiene `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID`
2. Abre el bot en Telegram y envía: `/start`
3. Reinicia el script

### "El dashboard carga muy lento"

1. Tienes muchos datos en BigQuery
2. Solución: Filtra por fecha más reciente en `dashboard.py`

### "No encuentra nuevas licitaciones"

1. Revisa si realmente hay nuevas en los portales
2. Verifica los logs: `logs/lifebox_radar.log`
3. Abre issue en GitHub si el portal cambió su diseño

---

## 📞 Soporte

- **Email:** soporte@lifebox.cl
- **Discord:** [Únete aquí](https://discord.gg/lifebox)
- **GitHub Issues:** [Reporta problemas](https://github.com/consultoria-lifebox/Lifebox-Radar/issues)

---

**¡Disfruta usando Lifebox Radar!** 🎉
