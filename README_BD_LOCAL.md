# Configuración de Base de Datos Local SQLite

Este proyecto ha sido configurado para trabajar exclusivamente con una base de datos local SQLite, eliminando toda la complejidad relacionada con sincronización y cambios entre bases de datos.

## Configuración Actual

- La aplicación utiliza exclusivamente **SQLite** como base de datos local
- La base de datos se encuentra en `instance/app.db`
- Las optimizaciones específicas para SQLite garantizan un rendimiento adecuado

## Beneficios de Trabajar con SQLite Local

1. **Simplicidad**: No hay necesidad de gestionar credenciales o conexiones remotas
2. **Velocidad**: Todas las consultas se realizan localmente, sin latencia de red
3. **Portabilidad**: La base de datos es un archivo único que puede respaldarse fácilmente
4. **Trabajo Offline**: No requiere conexión a Internet para funcionar
5. **Depuración**: Más fácil depurar problemas al tener todo localmente

## Estructura de Archivos

- `instance/app.db`: Archivo de base de datos SQLite
- `.env`: Contiene la configuración de la ruta de la base de datos (`DB_PATH`)

## Respaldos

Si deseas hacer copias de seguridad manuales de la base de datos:

1. Cierra la aplicación para evitar escrituras durante la copia
2. Copia el archivo `instance/app.db` a una ubicación segura
3. Para restaurar, simplemente reemplaza el archivo con la copia

## Solución de Problemas

Si encuentras errores relacionados con la base de datos:

1. **Base de datos bloqueada**: Asegúrate de que no hay otras instancias de la aplicación en ejecución
2. **No se encuentra el archivo**: Verifica que el directorio `instance` existe y tiene permisos de escritura
3. **Tablas no encontradas**: Es posible que la base de datos esté corrupta, intenta restaurar desde una copia o reiniciar la aplicación para que cree las tablas

Para verificar el estado de la base de datos, puedes acceder a la ruta `/check_db` en la aplicación.

## Optimizaciones Aplicadas

La aplicación aplica automáticamente las siguientes optimizaciones a SQLite:

- **Write-Ahead Logging (WAL)**: Mejor rendimiento en operaciones concurrentes
- **Caché optimizada**: Mayor uso de memoria para reducir accesos a disco
- **Almacenamiento temporal en memoria**: Las operaciones temporales son más rápidas
- **Modo de sincronización NORMAL**: Balance óptimo entre seguridad y rendimiento
