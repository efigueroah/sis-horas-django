# 📋 Guía de Instalación - Sistema de Gestión de Horas

## 🔧 Requisitos Previos

### Software Necesario
- **Python 3.8+** - [Descargar Python](https://www.python.org/downloads/)
- **pip** - Gestor de paquetes de Python (incluido con Python)
- **Git** - Para clonar el repositorio

### Verificar Instalación
```bash
python --version  # Debe mostrar Python 3.8 o superior
pip --version     # Debe mostrar la versión de pip
```

## 🚀 Instalación Paso a Paso

### 1. Clonar el Repositorio
```bash
git clone https://github.com/efigueroah/sis-horas-django.git
cd sis-horas-django
```

### 2. Crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos
```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario (admin)
python manage.py createsuperuser
```

### 5. Generar Datos de Demostración (Opcional)
```bash
# Generar datos de prueba completos
python manage.py setup_demo_data
```

### 6. Iniciar el Servidor
```bash
# Opción 1: Script personalizado (recomendado)
python run_server.py

# Opción 2: Comando Django estándar
python manage.py runserver
```

## 🌐 Acceso al Sistema

- **URL Principal**: http://localhost:8000
- **Panel Admin**: http://localhost:8000/admin/

### Usuarios de Prueba (si se generaron datos demo)
| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `admin123` | Superusuario |
| `demo1` | `demo123` | Usuario |
| `demo2` | `demo123` | Usuario |

## 🔧 Configuración Adicional

### Variables de Entorno (Opcional)
Crear archivo `.env` en la raíz del proyecto:
```env
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=sqlite:///db.sqlite3
```

### Configuración de Producción
Para despliegue en producción, consultar [DESPLIEGUE.md](DESPLIEGUE.md)

## ❗ Solución de Problemas

### Error: "No module named 'django'"
```bash
# Verificar que el entorno virtual esté activado
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "Port already in use"
```bash
# Usar puerto diferente
python manage.py runserver 8080
```

### Error de Migraciones
```bash
# Resetear migraciones (CUIDADO: borra datos)
rm db.sqlite3
python manage.py migrate
```

## 📞 Soporte

Si encuentras problemas durante la instalación:
1. Revisa los [Issues](https://github.com/efigueroah/sis-horas-django/issues)
2. Crea un nuevo issue con detalles del error
3. Incluye tu sistema operativo y versión de Python
