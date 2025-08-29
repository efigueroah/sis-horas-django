# ⚙️ Configuración del Sistema

## 🎛️ Configuración General

### Acceso a Configuración
- **URL**: `/configuracion/`
- **Requisitos**: Usuario autenticado

### Configuración de Reportes (Todos los usuarios)
- **Formato de Exportación**: CSV, Excel, PDF
- **Separador CSV**: Coma, punto y coma, pipe
- **Separador Decimal**: Punto (internacional) o Coma (español)
- **Incluir Encabezados**: Sí/No
- **Solo Proyectos Activos**: Filtro por defecto
- **Columnas a Incluir**: Fecha, Proyecto, Horas, etc.

### Configuración del Sistema (Solo Superusuarios)
- **Incremento de Horas**: Valor por defecto
- **Horas Máximas por Día**: Límite global
- **Permitir Fines de Semana**: Validación
- **Validar Feriados**: Activar/desactivar
- **Nombre del Sistema**: Personalización

## 📊 Configuración de Períodos

### Crear Período
1. Ir a **Períodos** → **Crear Nuevo**
2. Completar:
   - **Nombre**: Descriptivo (ej: "Enero 2025")
   - **Fecha Inicio/Fin**: Rango del período
   - **Horas Objetivo**: Meta de horas
   - **Horas Máximas por Día**: Límite diario

### Activar Período
- Solo **un período activo** por usuario
- El período activo determina dónde se registran las horas
- Cambiar período activo desde la lista de períodos

## 🎯 Configuración de Proyectos

### Crear Proyecto
1. **Proyectos** → **Crear Nuevo**
2. Datos básicos:
   - **Nombre**: Identificador del proyecto
   - **Cliente**: Empresa o persona
   - **Descripción**: Detalles opcionales
   - **Color**: Para visualización en gráficos

### Estados de Proyecto
- **Activo**: Disponible para registro de horas
- **Inactivo**: No aparece en formularios (datos conservados)

## 📅 Configuración de Feriados

### Gestión de Feriados
- **URL**: `/feriados/`
- **Funcionalidad**: CRUD completo

### Crear Feriado
1. **Feriados** → **Crear Nuevo**
2. Completar:
   - **Nombre**: Descripción del feriado
   - **Fecha**: Día específico
   - **Tipo**: Nacional, Regional, Personal
   - **Descripción**: Detalles adicionales

### Feriados Automáticos
El sistema incluye feriados nacionales argentinos 2025 por defecto.

## 🔧 Configuración Avanzada

### Variables de Entorno
Crear archivo `.env` en la raíz:

```env
# Desarrollo
DEBUG=True
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura

# Base de datos
DATABASE_URL=sqlite:///db.sqlite3

# Configuración de email (opcional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-de-app

# Configuración de archivos estáticos
STATIC_URL=/static/
MEDIA_URL=/media/
```

### Configuración de Base de Datos

#### SQLite (Por defecto)
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### PostgreSQL (Producción)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sis_horas',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Configuración de Seguridad

#### Producción
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['tu-dominio.com', 'www.tu-dominio.com']

# Seguridad HTTPS
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies seguras
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## 📁 Configuración de Archivos

### Archivos Estáticos
```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

### Archivos de Media
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## 🔄 Comandos de Configuración

### Resetear Configuración
```bash
# Resetear base de datos (CUIDADO: borra datos)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser

# Regenerar datos de demo
python manage.py setup_demo_data --reset
```

### Backup de Configuración
```bash
# Exportar datos
python manage.py dumpdata > backup.json

# Importar datos
python manage.py loaddata backup.json
```

### Recolectar Archivos Estáticos
```bash
python manage.py collectstatic
```

## 🎨 Personalización

### Cambiar Nombre del Sistema
1. **Configuración** → **Configuración del Sistema**
2. Modificar **Nombre del Sistema**
3. Se refleja en títulos y encabezados

### Personalizar Colores y Estilos
Modificar archivos en `static/css/`:
- `custom.css`: Estilos personalizados
- Variables CSS para colores principales

### Configurar Zona Horaria
```python
# settings.py
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_TZ = True
```
