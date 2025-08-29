# 🕒 Sistema de Gestión de Horas - Django

Una aplicación web completa y moderna para la gestión integral de horas de trabajo, proyectos y períodos laborales, desarrollada con Django 4.2+ y diseñada para uso offline con servidor local.

## 🎯 Características Principales

### ✨ **Funcionalidades Implementadas**
- **Autenticación Avanzada**: Multiusuario con roles y perfiles personalizables
- **CRUD Completo de Proyectos**: Gestión completa con filtros por año y estado
- **Gestión Avanzada de Horas**: Slider intuitivo (0.5h - 12h, incrementos 30min)
- **Tipos de Tarea**: Diferenciación entre Tareas y Reuniones con estadísticas
- **Selector de Período Activo**: Activación exclusiva con gestión de períodos
- **Validaciones Inteligentes**: Bloqueo automático fines de semana y feriados
- **Calendario Interactivo**: Visualización mensual con estados de días
- **Dashboard con Gráficos**: Estadísticas visuales y resúmenes
- **Exportación Configurable**: CSV/Excel con filtros personalizables
- **Admin Interface**: Panel de administración Django completo
- **Datos de Demostración**: Generación automática para testing

### 🏗️ **Arquitectura**
- **Backend**: Django 4.2+ con Django REST Framework
- **Frontend**: HTML5, CSS3, JavaScript ES6+ con Bootstrap 5
- **Base de Datos**: SQLite con migraciones automáticas
- **Autenticación**: Sistema Django Auth extendido
- **API**: Endpoints RESTful para todas las funcionalidades

## 🚀 Instalación y Configuración

### **Requisitos Previos**
- Python 3.8+
- pip (gestor de paquetes de Python)

### **Instalación Rápida**

```bash
# 1. Clonar o descargar el proyecto
cd sis-horas-django

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar migraciones
python manage.py migrate

# 5. Generar datos de demostración
python manage.py setup_demo_data

# 6. Iniciar servidor
python run_server.py
```

### **Inicio Rápido**
```bash
# Activar entorno virtual
source venv/bin/activate

# Iniciar servidor con script personalizado
python run_server.py
```

El servidor se iniciará automáticamente en un puerto disponible (8000-8010) y abrirá el navegador.

## 👥 Usuarios de Prueba

| Usuario | Contraseña | Rol | Descripción |
|---------|------------|-----|-------------|
| `admin` | `admin123` | Superusuario | Acceso completo al sistema y admin |
| `demo1` | `demo123` | Usuario | Juan Pérez - Datos de demostración |
| `demo2` | `demo123` | Usuario | María González - Datos de demostración |

## 📊 Datos de Demostración

El sistema incluye datos de prueba completos:

- **3 Usuarios**: Admin + 2 usuarios demo
- **6 Períodos**: Pasado, actual (activo) y futuro por usuario
- **16 Proyectos**: Variados con diferentes clientes y estados
- **64+ Registros de Horas**: Distribuidos con ambos tipos de tarea
- **28 Días Feriados**: Feriados nacionales argentinos 2025

### **Regenerar Datos**
```bash
# Resetear y regenerar todos los datos
python manage.py setup_demo_data --reset
```

## 🎨 Interfaz de Usuario

### **Dashboard Principal**
- **Información del Período**: Barra de progreso con avance del objetivo
- **Estadísticas**: Total horas, completación, faltantes, días trabajados
- **Calendario Interactivo**: Visualización mensual con estados de días
- **Botones Aceleradores**: Acceso rápido a funciones principales
  - Registrar Horas (simple y múltiple)
  - Ver y gestionar registros
  - Gestión de proyectos
  - Exportar datos, períodos y feriados

### **Gestión de Proyectos**
- **Filtros Avanzados**: Por año, estado, búsqueda por nombre/cliente
- **CRUD Completo**: Crear, editar, activar/desactivar, eliminar
- **Información Completa**: Cliente, fechas, descripción, color personalizado

### **Registro de Horas**
- **Slider Intuitivo**: 0.5h - 12h con incrementos de 30 minutos
- **Tipos de Tarea**: Radio buttons para Tarea/Reunión
- **Validaciones**: Tiempo real para fines de semana, feriados, límites
- **Filtros**: Por fecha, proyecto, tipo de tarea, período

### **Configuración**
- **Períodos**: Gestión completa con objetivos y límites
- **Días Feriados**: CRUD con calendario picker
- **Perfil Personal**: Horas máximas, zona horaria, preferencias

## 🔧 Panel de Administración

Acceso completo a través de `/admin/` con funcionalidades avanzadas:

### **Características del Admin**
- **Usuarios y Perfiles**: Gestión completa con configuraciones
- **Períodos**: Activación masiva, duplicación, filtros avanzados
- **Proyectos**: Badges de estado, preview de colores, estadísticas
- **Registros de Horas**: Resúmenes, exportación CSV, cambios masivos
- **Reportes**: Historial de exportaciones, configuraciones

### **Acciones Masivas**
- Activar/desactivar múltiples elementos
- Duplicar proyectos y períodos
- Exportar datos a CSV
- Cambiar tipos de tarea en lote

## 📈 API REST

Endpoints completos para integración:

### **Autenticación**
- `POST /api/auth/login/` - Iniciar sesión
- `POST /api/auth/logout/` - Cerrar sesión

### **Dashboard**
- `GET /api/dashboard/` - Datos del dashboard
- `GET /api/calendario/{year}/{month}/` - Calendario mensual

### **Períodos**
- `GET /api/periodos/` - Lista de períodos
- `GET /api/periodos/activo/` - Período activo
- `POST /api/periodos/` - Crear período

### **Proyectos**
- `GET /api/proyectos/api/` - Lista de proyectos
- `GET /api/proyectos/api/activos/` - Solo proyectos activos
- `GET /api/proyectos/api/años/` - Años disponibles
- `POST /api/proyectos/api/` - Crear proyecto

### **Horas**
- `GET /api/horas/api/` - Lista de registros
- `GET /api/horas/api/fecha/{fecha}/` - Horas por fecha
- `POST /api/horas/api/` - Crear registro
- `PUT /api/horas/api/{id}/` - Actualizar registro

### **Reportes**
- `GET /api/reportes/api/exportar/csv/` - Exportar CSV
- `GET /api/reportes/api/historial/` - Historial de exportaciones

## 🛠️ Comandos de Gestión

### **Datos de Demostración**
```bash
# Generar datos de prueba
python manage.py setup_demo_data

# Resetear y regenerar
python manage.py setup_demo_data --reset
```

### **Base de Datos**
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

### **Servidor**
```bash
# Servidor de desarrollo
python manage.py runserver

# Servidor con script personalizado
python run_server.py

# Servidor en puerto específico
python manage.py runserver 8080
```

## Estructura del Proyecto

```
sis-horas-django/
├── manage.py                 # Comando principal de Django
├── run_server.py            # Script de inicio personalizado
├── requirements.txt         # Dependencias del proyecto
├── README.md               # Documentación
├── db.sqlite3              # Base de datos SQLite
├── sis_horas/              # Configuración principal
│   ├── settings.py         # Configuración Django
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # WSGI para producción
├── apps/                   # Aplicaciones Django
│   ├── authentication/    # Autenticación y perfiles
│   ├── core/              # Períodos, feriados, dashboard
│   ├── proyectos/         # Gestión de proyectos
│   ├── horas/             # Registros de horas
│   └── reportes/          # Exportación y reportes
├── templates/              # Templates HTML
│   ├── base.html          # Template base
│   ├── dashboard/         # Templates del dashboard
│   ├── authentication/   # Templates de login/registro
│   └── ...               # Otros templates
├── static/                # Archivos estáticos
│   ├── css/              # Estilos CSS
│   ├── js/               # JavaScript
│   └── img/              # Imágenes
└── media/                 # Archivos subidos por usuarios
```

## 🔒 Seguridad

### **Características de Seguridad**
- **Autenticación Django**: Sistema robusto con sesiones
- **Protección CSRF**: Tokens en todos los formularios
- **Validación de Datos**: Backend y frontend
- **Permisos por Usuario**: Aislamiento de datos
- **Sanitización**: Prevención de XSS e inyección

### **Configuración de Producción**
```python
# En settings.py para producción
DEBUG = False
ALLOWED_HOSTS = ['tu-dominio.com']
SECRET_KEY = 'tu-clave-secreta-segura'

# Configurar HTTPS
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
```

## 📊 Validaciones y Reglas de Negocio

### **Validaciones Automáticas**
- **Horas**: Múltiplos de 0.5h, mínimo 0.5h, máximo 12h
- **Fechas**: No fines de semana, no días feriados
- **Límites Diarios**: Máximo configurable por usuario/período
- **Períodos**: Solo uno activo por usuario
- **Proyectos**: Nombres únicos por usuario

### **Reglas de Negocio**
- **Período Activo**: Exclusivo por usuario, auto-desactivación
- **Días Hábiles**: Lunes a viernes, excluyendo feriados
- **Tipos de Tarea**: Estadísticas separadas para análisis
- **Colores de Proyecto**: Visualización consistente en gráficos

## 🎨 Personalización

### **Temas y Estilos**
- **Bootstrap 5**: Framework CSS moderno
- **Font Awesome**: Iconografía completa
- **CSS Personalizado**: Variables CSS para fácil personalización
- **Responsive Design**: Adaptable a móviles y tablets

### **Configuración de Usuario**
- **Horas Máximas**: Personalizable por usuario
- **Zona Horaria**: Configuración regional
- **Formato de Fecha**: Múltiples opciones
- **Tema**: Claro, oscuro, automático

## 🚀 Despliegue

### **Desarrollo Local**
```bash
python run_server.py
```

### **Producción con Gunicorn**
```bash
pip install gunicorn
gunicorn sis_horas.wsgi:application
```

### **Docker (Opcional)**
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "sis_horas.wsgi:application"]
```

## 🤝 Contribución

### **Desarrollo**
1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### **Reportar Bugs**
- Usar GitHub Issues
- Incluir pasos para reproducir
- Especificar versión de Python/Django

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🙏 Agradecimientos

- **Django**: Framework web robusto
- **Bootstrap**: Framework CSS moderno
- **Chart.js**: Gráficos interactivos
- **Font Awesome**: Iconografía completa

---

## 📞 Soporte

Para soporte técnico o consultas:
- 📧 Email: soporte@sishoras.com
- 📖 Documentación: [Wiki del proyecto]
- 🐛 Bugs: [GitHub Issues]

---

**¡Gracias por usar el Sistema de Gestión de Horas!** 🚀
