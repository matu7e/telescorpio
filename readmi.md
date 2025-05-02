# 🕵️ Telescorpio

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Telethon](https://img.shields.io/badge/Telethon-1.25%2B-green)
![License](https://img.shields.io/badge/License-MIT-red)

Herramienta profesional para análisis forense e investigación OSINT en chats de Telegram con interfaz estilo hacker.

<img src="img/image.png" alt="Menú Principal" width="600">

## 🌟 Características Clave

- **Extracción completa** de metadatos y contenido multimedia
- **Análisis temporal** avanzado con detección de patrones
- **Detección automática** de información sensible (emails, IPs, etc.)
- **Generación de reportes** en múltiples formatos (CSV, TXT, PNG)
- **Interfaz intuitiva** con menú interactivo

## 🚀 Instalación Rápida

### Requisitos previos
- Python 3.8+
- Cuenta de [Telegram API](https://my.telegram.org/auth)

### Pasos de instalación:
```bash
# 1. Clonar repositorio
git clone https://github.com/matu7e/telescorpio.git
cd telescorpio

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4.🔐 Configuración de API

1. Crea tu propio `API_ID` y `API_HASH` gratis en:
https://my.telegram.org/auth

2. Crea un archivo `.env` con:
API_ID=TU_ID_AQUI
API_HASH=TU_HASH_AQUI

3. Añade .env a tu .gitignore

```

### 🧭 Guía de Uso
```bash
python3 telescorpio.py
```

### Menú Principal
1. Analizar chat por enlace
2. Analizar mis chats
0. Salir

### Menú de Análisis (por chat)
<img src="img/image2.png" alt="Menú Principal" width="600">

## 📊 Funcionalidades Detalladas

### 🔍 Análisis Básico

| Opción | Descripción | Archivos Generados |
| --- | --- | --- |
| 1 | Metadatos del chat (fecha creación, participantes, etc.) | `informacion_general.txt` |
| 2 | Listado completo de usuarios con estadísticas de actividad | `usuarios.csv`, `usuarios_detallado.txt` |
| 3 | Todos los enlaces compartidos con metadatos | `enlaces.csv`, `enlaces_detallado.txt` |
| 9 | Ejecuta todas las opciones básicas simultáneamente | Directorio completo |

## 📊 Funcionalidades Detalladas

### 🔍 Análisis Básico

| Opción | Descripción | Archivos Generados |
| --- | --- | --- |
| 1 | Metadatos del chat (fecha creación, participantes, etc.) | `informacion_general.txt` |
| 2 | Listado completo de usuarios con estadísticas de actividad | `usuarios.csv`, `usuarios_detallado.txt` |
| 3 | Todos los enlaces compartidos con metadatos | `enlaces.csv`, `enlaces_detallado.txt` |
| 9 | Ejecuta todas las opciones básicas simultáneamente | Directorio completo |

### 📸 Descarga de Medios

| Opción | Tipo de Contenido | Directorio Destino |
| --- | --- | --- |
| 4 | Imágenes (JPG, PNG) | `media/fotos/` |
| 5 | Videos (MP4, GIF) | `media/videos/` |
| 6 | Mensajes de voz y audios | `media/audios/` |
| 7 | Stickers y paquetes | `media/stickers/` |
| 8 | Documentos (PDF, ZIP, etc.) | `media/documentos/` |

### 📈 Análisis Avanzado

| Opción | Función | Output |
| --- | --- | --- |
| 10 | Gráfico de actividad por horas | `activity_plot.png` |
| 11 | Detección de días con picos de actividad | Reporte en consola |
| 12 | Análisis de dominios en enlaces compartidos | Listado ordenado |
| 13 | Detección de emails, IPs y criptodirecciones | `patrones_report.txt` |

## ⚠️ Limitaciones Técnicas

- Máximo ~5000 mensajes/minuto (límite de la API)
- Chats privados requieren permisos de administrador
- Medios grandes pueden fallar en descarga

## 📜 Licencia

Este proyecto está bajo licencia MIT. **Uso exclusivo para:**

- Investigación forense autorizada
- Auditorías de seguridad
- Análisis OSINT legítimo

> ⚠️
 El uso incorrecto de esta herramienta puede violar los Términos de 
Servicio de Telegram. El desarrollador no se hace responsable del mal 
uso.
> 

## 🆘 Soporte

Para reportar bugs o solicitar características:

- Abrir issue en GitHub
- Contactar via email: [correo](https://mailto:soporteparacorreos3@gmail.com/)