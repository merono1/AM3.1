# Migración a Neon PostgreSQL

Este documento explica cómo migrar la aplicación para usar Neon PostgreSQL como base de datos remota en lugar de SQLite local.

## ¿Por qué migrar a Neon?

- **Base de datos accesible desde cualquier lugar**: Podrás trabajar en tu aplicación desde diferentes ordenadores.
- **Seguridad**: Los datos están protegidos en la nube con copias de seguridad automáticas.
- **Separación de la aplicación y datos**: Facilita el despliegue de la aplicación en Google Cloud Run.
- **Escalabilidad**: PostgreSQL ofrece mejor rendimiento para aplicaciones en crecimiento.
- **Gratuito**: Neon ofrece un plan gratuito con 3GB de almacenamiento.

## Pasos para migrar

### 1. Instalar dependencias

Ejecuta el script `instalar_dependencias_postgres.bat` o instala manualmente:

```
pip install psycopg2-binary sqlalchemy-utils
```

### 2. Crear cuenta en Neon

1. Ve a [https://neon.tech](https://neon.tech) y regístrate
2. Crea un nuevo proyecto
3. Anota la cadena de conexión que te proporcionan

### 3. Configurar la conexión

Ejecuta el script `configurar_neon.bat` que te guiará en el proceso de configuración:
- Introducir los datos de conexión de Neon
- Probar la conexión
- Actualizar automáticamente el archivo `.env`

### 4. Migrar los datos

Si no lo has hecho durante la configuración, ejecuta:

```
python migrate_to_postgres.py
```

Este script:
- Exporta el esquema de SQLite a PostgreSQL
- Migra todos los datos existentes
- Configura la aplicación para usar PostgreSQL

### 5. Probar la aplicación

Ejecuta la aplicación normalmente:

```
python main.py
```

La aplicación ahora debería estar usando Neon PostgreSQL como base de datos.

## Solución de problemas

### Error de conexión

Si aparece un error al conectar a Neon:

1. Verifica que los datos de conexión sean correctos
2. Asegúrate de que la IP desde la que te conectas esté permitida en Neon
3. Verifica que el servidor de Neon esté activo

### Error al migrar datos

Si hay problemas durante la migración:

1. Asegúrate de que la base de datos SQLite original existe y tiene datos
2. Verifica que tienes permisos para crear tablas en Neon
3. Revisa los mensajes de error para identificar problemas específicos

## Volver a SQLite (si es necesario)

Para volver a usar SQLite, edita el archivo `.env` y:

1. Descomenta la línea `DB_PATH=...`
2. Comenta o elimina la línea `DATABASE_URL=...`

## Despliegue en Google Cloud Run

Con la base de datos en Neon, ahora puedes desplegar tu aplicación en Google Cloud Run sin preocuparte por la persistencia de los datos. El proceso general es:

1. Construir la imagen de Docker con tu aplicación
2. Subir la imagen al Container Registry de Google
3. Configurar Cloud Run con la misma variable de entorno `DATABASE_URL`
4. Desplegar la aplicación

Esto te permitirá actualizar tu aplicación en Google Cloud Run cuando sea necesario sin afectar a los datos almacenados en Neon PostgreSQL.
