# Gestión de Usuarios

## Crear Usuario Administrador

### Desde Línea de Comandos
```bash
# Activar entorno virtual
source venv/bin/activate

# Crear superusuario interactivo
python manage.py createsuperuser
```

Se solicitará:
- **Username**: Nombre de usuario (ej: admin)
- **Email**: Correo electrónico (opcional)
- **Password**: Contraseña segura

### Desde Panel Admin
1. Acceder a http://localhost:8000/admin/
2. Ir a **Users** → **Add User**
3. Completar datos básicos
4. En **Permissions**, marcar:
   - Staff status
   - Superuser status

## Crear Usuarios Regulares

### Opción 1: Panel Admin (Recomendado)
1. Acceder como admin a http://localhost:8000/admin/
2. Ir a **Users** → **Add User**
3. Completar:
   - Username
   - Password
4. Guardar y continuar editando
5. Completar información adicional:
   - First name / Last name
   - Email
   - **Staff status**: No (usuarios regulares)
   - **Active**: Sí

### Opción 2: Desde Django Shell
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

# Crear usuario regular
user = User.objects.create_user(
    username='juan.perez',
    email='juan@empresa.com',
    password='password123',
    first_name='Juan',
    last_name='Pérez'
)

# Crear usuario con permisos de staff
staff_user = User.objects.create_user(
    username='maria.admin',
    email='maria@empresa.com',
    password='password123',
    first_name='María',
    last_name='González',
    is_staff=True  # Puede acceder al admin
)
```

## Configuración de Perfiles

Cada usuario tiene un **Perfil Personal** que se crea automáticamente:

### Configuraciones Disponibles
- **Horas Máximas por Día**: Límite diario de horas
- **Zona Horaria**: Configuración regional
- **Formato de Fecha**: Preferencia de visualización
- **Configuración de Reportes**: Formatos de exportación

### Acceso a Configuración
1. **Usuario Regular**: `/configuracion/`
2. **Admin**: `/admin/` → **Authentication** → **Perfil Personal**

## Niveles de Acceso

### Superusuario (Admin)
- Acceso completo al sistema
- Panel de administración
- Gestión de usuarios
- Configuración del sistema
- Todas las funcionalidades

### Usuario Regular
- Dashboard personal
- Gestión de horas propias
- Gestión de proyectos propios
- Exportación de reportes
- Configuración personal
- Sin acceso al panel admin
- Sin gestión de otros usuarios

## Gestión de Contraseñas

### Cambiar Contraseña (Admin)
```bash
python manage.py changepassword username
```

### Resetear Contraseña (Django Shell)
```python
from django.contrib.auth.models import User

user = User.objects.get(username='usuario')
user.set_password('nueva_password')
user.save()
```

### Desde Panel Admin
1. Ir a **Users** → Seleccionar usuario
2. Click en **this form** junto a Password
3. Ingresar nueva contraseña dos veces
4. Guardar

## Datos de Usuario

### Información Automática
- **Períodos**: Se crean automáticamente
- **Configuración de Reportes**: Valores por defecto
- **Perfil Personal**: Configuración inicial

### Migración de Datos
Para transferir datos entre usuarios, usar Django Admin:
1. **Proyectos**: Cambiar campo "Usuario"
2. **Registros de Horas**: Cambiar campo "Usuario"
3. **Períodos**: Cambiar campo "Usuario"

## Eliminar Usuarios

### PRECAUCIÓN
Eliminar un usuario borra **TODOS** sus datos:
- Proyectos
- Registros de horas
- Períodos
- Configuraciones

### Proceso de Eliminación
1. **Backup de datos** (recomendado)
2. Panel Admin → **Users**
3. Seleccionar usuario
4. **Delete** → Confirmar

### Alternativa: Desactivar Usuario
En lugar de eliminar, desactivar:
- Desmarcar **Active**
- El usuario no podrá iniciar sesión
- Los datos se conservan
