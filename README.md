# AM3.1 - Aplicación de Gestión

Sistema de gestión y administración de proyectos con soporte exclusivo para PostgreSQL en Neon.

## Características principales

- Base de datos PostgreSQL (obligatorio para producción)
- Sistema de rutas relativas para portabilidad entre equipos
- Optimizado para entornos serverless con PostgreSQL en Neon
- Manejo de timeout para conexiones a bases de datos
- Sistema de notificaciones para activación de base de datos en modo "sleep"

## Requisitos

- Python 3.8 o superior
- Dependencias (ver requirements.txt)
- PostgreSQL en Neon (obligatorio)
- Módulo psycopg2-binary instalado

## Instalación y configuración

1. Clonar el repositorio
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno virtual:
   - Windows: `venv\Scripts\activate` o usar `activate_venv.bat`
   - Linux/Mac: `source venv/bin/activate`
4. Instalar dependencias: `pip install -r requirements.txt`
5. Para PostgreSQL: ejecutar `instalar_dependencias_postgres.bat`
6. Configurar variables en el archivo `.env` (DATABASE_URL es obligatorio)

## Iniciar la aplicación

```bash
# Método recomendado
python main.py
```

## Verificar conexión a PostgreSQL

Para verificar la conexión a PostgreSQL, inicia la aplicación y visita:

```
http://localhost:5000/check_db
```

## Estructura del proyecto

- `app/`: Módulo principal de la aplicación
  - `__init__.py`: Inicialización de Flask y extensiones
  - `config.py`: Configuración centralizada de la aplicación
  - `models/`: Modelos de la base de datos
  - `routes/`: Rutas de la aplicación
  - `templates/`: Plantillas HTML
  - `static/`: Archivos estáticos (CSS, JS, imágenes)
- `docs/`: Documentación del proyecto
- `migrations/`: Migraciones de la base de datos
- `utils/`: Scripts de utilidad y herramientas
- `main.py`: Script principal para ejecutar la aplicación
- `.env`: Variables de entorno (configuración local)

## Scripts de utilidad

### Archivos .bat disponibles

1. **activate_venv.bat**
   - **Función:** Activa el entorno virtual Python para la aplicación
   - **Uso:** Ejecutar directamente para preparar el entorno de desarrollo

2. **instalar_dependencias_postgres.bat**
   - **Función:** Instala los paquetes Python necesarios para trabajar con PostgreSQL
   - **Uso:** Ejecutar cuando se necesite configurar la conexión con PostgreSQL

## Variables de entorno (.env)

```
# Obligatorias
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/database?sslmode=require

# Opcionales
SECRET_KEY=clave_secreta_personalizada
FLASK_ENV=development|production|testing
PORT=5000
CHECK_DB_CONNECTION=true|false
```

## Cambios en versión refactorizada

Se han realizado las siguientes mejoras:

1. **Configuración centralizada**:
   - Toda la configuración se ha consolidado en `app/config.py`
   - Eliminado código duplicado de verificación de base de datos

2. **Solo PostgreSQL**:
   - La aplicación ahora requiere PostgreSQL (eliminado soporte SQLite)
   - Verificación unificada de requisitos de PostgreSQL

3. **Mejoras de seguridad**:
   - Protección de credenciales en logs de diagnóstico
   - Uso de logger para mensajes de depuración en lugar de prints directos

4. **Simplificación de entrada**:
   - `main.py` es ahora el único punto de entrada recomendado
   - `app_run.py` marcado como deprecado

5. **Gestión de errores mejorada**:
   - Manejo coherente de excepciones
   - Mensajes de error más claros y específicos

## Despliegue en Docker

La aplicación está preparada para ser desplegada en Docker:

```bash
# Construir imagen
docker build -t am31-app .

# Ejecutar contenedor
docker-compose up
```

---

**Nota:** Este proyecto ha sido refactorizado para eliminar incoherencias, repeticiones y errores en el código. Se ha centralizado la configuración y se ha mejorado la gestión de errores.
