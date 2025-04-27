# Mejoras al Sistema de Gestión de Base de Datos en AM3.1

## Descripción del Problema

El sistema de gestión de bases de datos de AM3.1 tenía varias limitaciones y problemas de usabilidad:

1. No existía un indicador claro y visible sobre qué base de datos estaba en uso (local SQLite o remota PostgreSQL)
2. Los cambios entre bases de datos requerían reiniciar manualmente la aplicación desde fuera de la interfaz
3. No había un método para verificar si la base de datos actual coincidía realmente con la configuración
4. La interfaz no proporcionaba suficiente retroalimentación visual
5. Las peticiones AJAX fallaban con errores HTTP 400 (Bad Request)

## Problemas Detectados y Resueltos

### Error de "Bad Request" en Peticiones AJAX

**Problema:**
Las peticiones AJAX estaban configuradas incorrectamente, lo que provocaba errores HTTP 400 (Bad Request) cuando se intentaba acceder a funciones como "Descargar de Neon" o "Usar base de datos local".

**Causa:**
Se estaba especificando un encabezado `Content-Type: 'application/json'` pero no se incluía un cuerpo JSON en la petición, lo que hace que el servidor espere un cuerpo con formato JSON y genere un error cuando no lo encuentra.

**Solución:**
1. Se eliminó el encabezado `Content-Type: 'application/json'` de las peticiones AJAX
2. Se utilizó `FormData` para enviar un cuerpo de formulario vacío pero válido
3. Se añadió explícitamente el encabezado `X-Requested-With: XMLHttpRequest` para identificar correctamente las peticiones AJAX
4. Se mejoró la detección de peticiones AJAX en el servidor para ser más flexible

**Implementación Técnica:**
Se actualizaron los métodos de petición AJAX en el archivo `templates/db_manager/index.html`:

```javascript
fetch('{{ url_for("db_manager.download_db") }}', {
  method: 'POST',
  headers: {
    'X-CSRFToken': csrfToken,
    'X-Requested-With': 'XMLHttpRequest'
  },
  body: new FormData(),  // Enviar FormData vacío
  credentials: 'same-origin'
})
```

Y en el servidor se mejoró la detección en `routes/db_manager_routes.py`:

```python
is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
          request.headers.get('Content-Type') == 'application/json' or \
          request.headers.get('Accept') == 'application/json' or \
          request.headers.get('Sec-Fetch-Mode') == 'cors'
```

## Soluciones Implementadas

### 1. Banner de Estado Claro y Distintivo

- Se ha añadido un banner con código de colores en la página de gestión de base de datos:
  - **Verde** para modo local (SQLite)
  - **Azul** para modo remoto (PostgreSQL/Neon)
- El banner muestra claramente el estado actual de la conexión

### 2. Reinicio de Aplicación desde la Interfaz Web

- Se ha implementado la capacidad de reiniciar la aplicación directamente desde la interfaz web
- Añadido botón de reinicio después de cambiar la configuración de la base de datos
- Implementado sistema de verificación de reconexión que recarga automáticamente la página

### 3. Verificación en Tiempo Real de la Base de Datos

- Añadida función de verificación que realiza una consulta directa para confirmar qué base de datos está realmente en uso
- Implementadas consultas específicas para cada tipo de base de datos (SQLite y PostgreSQL)
- Feedback visual cuando la configuración no coincide con la base de datos real en uso

### 4. Actualizaciones Automáticas y Banner Global

- Banner global en todas las páginas de la aplicación mostrando el estado de la base de datos
- Actualización automática del estado cada 30 segundos
- Opción para el usuario de ocultar el banner global si lo desea

### 5. Corrección de Errores AJAX

- Se corrigió el formato de las peticiones AJAX para evitar errores HTTP 400
- Se mejoró la detección de peticiones AJAX en el servidor
- Se añadió un mejor manejo de errores en las peticiones

## Detalles Técnicos

### Archivos Modificados

1. **app/routes/db_manager_routes.py**
   - Añadida ruta `/restart` para reiniciar la aplicación desde la interfaz
   - Mejorada ruta `/status` para incluir más información sobre el estado
   - Añadida ruta `/verify_db` para verificación en tiempo real
   - Mejorada detección de peticiones AJAX

2. **app/services/db_backup_service.py**
   - Mejorado método `get_current_db_info()` con más metadatos e indicadores visuales
   - Implementado método `perform_verification_query()` para consultas de verificación

3. **app/templates/db_manager/index.html**
   - Añadido banner con código de colores para indicar el estado actual
   - Implementados botones para reiniciar la aplicación directamente
   - Añadida función JavaScript `verificarBaseDatos()` para verificación en tiempo real
   - Añadida función JavaScript `reiniciarAplicacion()` para reinicio automático
   - Mejorado sistema de actualización automática con más información visual
   - Corregidas peticiones AJAX usando FormData y encabezados correctos

4. **app/templates/layout/base.html**
   - Añadido banner global para mostrar el estado en todas las páginas
   - Implementado script para detectar y mostrar el estado de la base de datos
   - Añadidos estilos CSS para el banner global

### Nuevas Características

#### Reinicio de Aplicación

El sistema ahora puede reiniciarse automáticamente utilizando el siguiente proceso:

1. El usuario hace clic en el botón "Reiniciar aplicación ahora"
2. Se envía una solicitud AJAX a la ruta `/db-manager/restart`
3. El servidor inicia un nuevo proceso Python con el mismo script (`main.py`)
4. El proceso actual finaliza después de enviar una respuesta satisfactoria
5. El cliente intenta reconectar cada segundo durante 10 intentos
6. La página se recarga automáticamente cuando se detecta que el servidor está activo nuevamente

#### Verificación Real de Base de Datos

El sistema ahora verifica qué base de datos está realmente en uso mediante:

1. Ejecución de consultas específicas para cada tipo de base de datos
   - Para SQLite: `SELECT sqlite_version() AS version, 'SQLite' AS db_type`
   - Para PostgreSQL: `SELECT version() AS version, 'PostgreSQL' AS db_type`
2. Comprobación de que el tipo de base de datos verificado coincide con la configuración
3. Mostrar un modal con información detallada sobre la verificación
4. Alerta visual si hay discrepancia entre la configuración y la base de datos real

## Beneficios para el Usuario

- **Claridad:** Indicación visual clara del estado actual de la base de datos
- **Confianza:** Verificación real de qué base de datos está actualmente en uso
- **Eficiencia:** No es necesario salir de la aplicación para reiniciarla
- **Consistencia:** Banner global presente en toda la aplicación
- **Fiabilidad:** Las operaciones AJAX funcionan correctamente sin errores de Bad Request

## Uso

### Para Cambiar entre Bases de Datos

1. Acceder a la página de gestión (*/db-manager/*)
2. Seleccionar la base de datos deseada (local o remota) usando los botones correspondientes
3. Hacer clic en "Reiniciar aplicación ahora" directamente desde la interfaz

### Para Verificar la Base de Datos Actual

1. Hacer clic en el botón "Verificar" en el banner de estado
2. Revisar el modal con información detallada sobre la base de datos actual
3. Si hay discrepancia, utilizar el botón de reinicio para sincronizar la configuración

## Futuras Mejoras

- Implementar sincronización selectiva de tablas específicas
- Añadir más herramientas de diagnóstico en la interfaz
- Implementar un sistema de bloqueo para prevenir cambios mientras hay operaciones en curso
- Mejorar el sistema de reconexión para soportar aplicaciones en producción
