# AM3.1 - Aplicación de Gestión

Sistema de gestión y administración de proyectos con soporte para PostgreSQL en Neon.

## Características principales

- Base de datos flexible: SQLite (desarrollo) o PostgreSQL (producción)
- Sistema de rutas relativas para portabilidad entre equipos
- Optimizado para entornos serverless con PostgreSQL en Neon
- Manejo de timeout para conexiones a bases de datos
- Sistema de notificaciones para activación de base de datos en modo "sleep"

## Requisitos

- Python 3.8 o superior
- Dependencias (ver requirements.txt)
- PostgreSQL en Neon (opcional, recomendado para producción)

## Instalación y configuración

1. Clonar el repositorio
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instalar dependencias: `pip install -r requirements.txt`
5. Copiar `.env.example` a `.env` y configurar variables
6. Para usar PostgreSQL, configurar `DATABASE_URL` en el archivo `.env`

## Iniciar la aplicación

```bash
python run.py
```

## Verificar conexión a PostgreSQL

Si utilizas PostgreSQL en Neon, puedes verificar la conexión con:

```bash
python test_neon_connection.py
```

O ejecutar el script batch:

```
test_neon_connection.bat
```

## Documentación

Para más información consulta:

- [Documentación de Rutas Relativas](docs/rutas_relativas.md)
- [Documentación de Conexión PostgreSQL](docs/conexion_postgresql.md)

## Estructura del proyecto

- `app/`: Módulo principal de la aplicación
  - `__init__.py`: Inicialización de Flask y configuración de base de datos
  - `config.py`: Configuración de la aplicación
  - `models/`: Modelos de la base de datos
  - `routes/`: Rutas de la aplicación
  - `templates/`: Plantillas HTML
  - `static/`: Archivos estáticos (CSS, JS, imágenes)
- `docs/`: Documentación del proyecto
- `migrations/`: Migraciones de la base de datos
- `config.py`: Configuración global (rutas relativas)
- `.env`: Variables de entorno (configuración local)

## Información adicional

Para migrar de SQLite a PostgreSQL, ejecuta:

```bash
python migrate_to_postgres.py
```