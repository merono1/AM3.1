# Conexión a PostgreSQL en Neon

Este documento explica la configuración y uso de PostgreSQL en Neon como base de datos principal para la aplicación AM3.1.

## Configuración

La aplicación está configurada para usar exclusivamente PostgreSQL en Neon. Para conectar con la base de datos, se requiere configurar la variable `DATABASE_URL` en el archivo `.env`.

### Estructura de la URL de conexión

```
postgresql://usuario:contraseña@host/nombre_db
```

Por ejemplo:
```
DATABASE_URL=postgresql://neondb_owner:npg_V9nz4xhHPfab@ep-delicate-salad-ab2eh0sf-pooler.eu-west-2.aws.neon.tech/neondb
```

### Credenciales actuales

- **Usuario**: neondb_owner
- **Contraseña**: npg_V9nz4xhHPfab
- **Host**: ep-delicate-salad-ab2eh0sf-pooler.eu-west-2.aws.neon.tech
- **Base de datos**: neondb

## Características de Neon PostgreSQL

Neon es un servicio de PostgreSQL serverless con las siguientes características:

- **Modo sleep**: La base de datos entra en modo inactivo cuando no hay conexiones
- **Activación automática**: Se activa cuando se recibe una conexión
- **Tiempo de activación**: Puede tardar entre 2 y 10 segundos en activarse

## Verificación de conexión

La aplicación incluye el script `test_neon_connection.py` para verificar la conexión a la base de datos:

1. Ejecuta el script para comprobar que la conexión a Neon funciona correctamente
2. El script mostrará información sobre el servidor y las tablas disponibles
3. También se puede usar para "despertar" la base de datos si está en modo sleep

Uso:
```bash
python test_neon_connection.py
```

## Gestión de errores de conexión

La aplicación incluye manejo de errores para situaciones comunes al trabajar con Neon:

### Timeout de conexión

Si la base de datos está en modo sleep, puede ocurrir un timeout de conexión. La aplicación está configurada para:

1. Detectar este error
2. Mostrar mensajes descriptivos sobre el problema
3. Sugerir ejecutar `test_neon_connection.py` para activar la base de datos

### Gestión del modo "sleep"

Para manejar el modo sleep de Neon:

1. Al iniciar la aplicación, se verifica la conexión a PostgreSQL
2. Si hay un error de timeout, se muestra un mensaje informativo
3. Cuando la base de datos está en modo sleep, la primera conexión puede tardar más tiempo
4. La aplicación incluye un timeout de conexión configurado para PostgreSQL

## Recomendaciones

- **Arranque inicial**: Si la aplicación ha estado inactiva mucho tiempo, ejecuta primero `test_neon_connection.py`
- **Reintentos**: Si hay un error de conexión, espera unos segundos y vuelve a intentarlo
- **Verificación**: Si tienes problemas, usa `/check_db` para verificar el estado de la conexión

## Problemas comunes

- **Error "timeout expired"**: La base de datos está en modo sleep
- **Error de autenticación**: Las credenciales pueden ser incorrectas
- **Error de conexión**: Puede haber restricciones de IP o problemas de red
