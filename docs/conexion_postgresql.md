# Conexión a PostgreSQL en Neon

Este documento explica cómo se ha implementado la conexión a PostgreSQL en Neon para la aplicación AM3.1.

## Configuración de PostgreSQL en Neon

La aplicación AM3.1 utiliza PostgreSQL en Neon como base de datos primaria en entorno de producción. Neon es una plataforma de PostgreSQL serverless que ofrece:

- Escalabilidad automática
- Modo "sleep" cuando no hay actividad (ahorro de recursos)
- Alta disponibilidad
- Copias de seguridad automáticas

## Credenciales de conexión

Las credenciales para conectarse a la base de datos PostgreSQL en Neon son:

- **Usuario**: neondb_owner
- **Contraseña**: npg_V9nz4xhHPfab
- **Host**: ep-delicate-salad-ab2eh0sf-pooler.eu-west-2.aws.neon.tech
- **Base de datos**: neondb

## Configuración en la aplicación

### Archivo .env

La conexión a PostgreSQL se configura en el archivo `.env` mediante la variable `DATABASE_URL`:

```
DATABASE_URL=postgresql://neondb_owner:npg_V9nz4xhHPfab@ep-delicate-salad-ab2eh0sf-pooler.eu-west-2.aws.neon.tech/neondb
```

Para activar PostgreSQL, simplemente descomenta esta línea y comenta la línea de `DB_PATH` si existe.

### Configuración de timeouts

Neon utiliza un modelo serverless que puede poner en "sleep" la base de datos cuando no hay actividad. Esto puede provocar timeouts al intentar conectarse después de un período de inactividad. Para manejar este comportamiento, se han implementado las siguientes mejoras:

1. **Timeout de conexión**: Se ha configurado un timeout de 10-15 segundos para evitar bloqueos indefinidos.
2. **Pool de conexiones**: Se utiliza un pool de conexiones para mantener conexiones activas y reducir el tiempo de activación.
3. **Reconexión automática**: La aplicación intenta reconectarse si detecta que la base de datos está en modo "sleep".

### Configuración en app/config.py

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_timeout': 30,  # 30 segundos
    'pool_recycle': 1800,  # 30 minutos
    'pool_pre_ping': True,  # Verificación de conexión antes de usarla
    'pool_size': 5,  # Tamaño del pool
    'max_overflow': 10,  # Conexiones adicionales si es necesario
    'connect_args': {
        'connect_timeout': 10,  # 10 segundos para timeout de conexión
        'application_name': 'AM3.1'  # Nombre de la aplicación en el servidor
    }
}
```

## Sistema de notificación para modo "sleep"

Cuando la base de datos está en modo "sleep", es necesario que la primera conexión la active. Para facilitar este proceso:

1. La aplicación detecta si la base de datos está en modo "sleep" durante el inicio.
2. Muestra un mensaje claro en la consola cuando detecta este estado.
3. Proporciona instrucciones para reactivar la base de datos.

### Mensajes de notificación

Cuando la base de datos está en modo "sleep", la aplicación muestra mensajes como:

```
⚠️ Error al conectar a PostgreSQL: timeout expired
🔄 La base de datos PostgreSQL podría estar en modo sleep.
   Espere un momento e intente nuevamente para activarla.
```

## Herramienta de prueba de conexión

Se incluye el script `test_neon_connection.py` que permite:

1. Probar la conexión a la base de datos
2. Activar la base de datos si está en modo "sleep"
3. Verificar la configuración correcta de las credenciales

Para ejecutar esta herramienta, use:

```
python test_neon_connection.py
```

O el script batch incluido:

```
test_neon_connection.bat
```

## Migración desde SQLite

Si has estado utilizando SQLite y deseas migrar a PostgreSQL:

1. Configura `DATABASE_URL` en el archivo `.env`
2. Ejecuta el script de migración:

```
python migrate_to_postgres.py
```

Este script:
- Conecta a ambas bases de datos
- Migra todos los datos preservando relaciones
- Verifica la integridad de los datos migrados

## Solución de problemas comunes

### La aplicación se queda "colgada" al iniciar

**Causa**: La base de datos está en modo "sleep" y la conexión está esperando indefinidamente.

**Solución**: 
1. Ejecuta `test_neon_connection.py` para activar la base de datos
2. Reinicia la aplicación después de que la base de datos esté activa

### Error "timeout expired"

**Causa**: La base de datos está en modo "sleep" y el timeout configurado ha expirado.

**Solución**: 
1. Ejecuta `test_neon_connection.py` para activar la base de datos
2. Si el problema persiste, verifica la conectividad a Internet

### Error de autenticación

**Causa**: Credenciales incorrectas en el archivo `.env`.

**Solución**: Verifica que `DATABASE_URL` contenga las credenciales correctas.

## Recomendaciones

1. **Ambiente de desarrollo**: Para desarrollo local, puedes seguir usando SQLite configurando `DB_PATH` en lugar de `DATABASE_URL`.
2. **Ambiente de producción**: Usa siempre PostgreSQL en Neon para producción.
3. **Antes de iniciar la aplicación**: Si ha pasado tiempo desde el último uso, ejecuta primero `test_neon_connection.py` para activar la base de datos.
4. **Copia de seguridad**: Aunque Neon realiza copias de seguridad automáticas, es recomendable realizar copias de seguridad periódicas manualmente.