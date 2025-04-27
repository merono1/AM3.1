# Refactorización Abril 2025 - AM3.1

## Problemas Identificados y Soluciones Implementadas

### 1. Incoherencias en los archivos de inicialización

#### Problema 1: Inconsistencia en la verificación de base de datos
- **main.py**: Obligaba el uso de PostgreSQL (líneas 12-15)
- **app/config.py**: Tenía un mecanismo de fallback a SQLite (líneas 45-53)
- **app/init.py**: También forzaba el uso de PostgreSQL (líneas 30-34)

**Solución**: Se ha centralizado la verificación de PostgreSQL en `app/config.py` con una función `verify_postgres_connection()` que se utiliza consistentemente. Se eliminó completamente el mecanismo de fallback a SQLite ya que la aplicación requiere PostgreSQL exclusivamente.

#### Problema 2: Importaciones redundantes
- Se importaba `psycopg2` repetidamente en distintos archivos

**Solución**: La verificación de `psycopg2` se realiza ahora solo en `main.py` y en la función de verificación de conexión en `app/config.py`.

#### Problema 3: Variables globales de control
- `app/config.py` utilizaba variables globales `CONNECTION_VERIFIED` y `DB_INFO_PRINTED`

**Solución**: Se han eliminado las variables globales, reemplazándolas por un enfoque basado en funciones donde cada verificación de conexión devuelve un resultado y mensaje.

### 2. Repeticiones de código

#### Problema 1: Código repetido para la inicialización
- **main.py** y **app_run.py** tenían código similar

**Solución**: `app_run.py` ahora simplemente importa desde `main.py` y está marcado como deprecado.

#### Problema 2: Verificación redundante de directorios
- Tanto `config.py` (raíz) como `app/config.py` tenían funciones para asegurar que existan directorios

**Solución**: Funciones centralizadas en `app/config.py`, mientras que `config.py` en la raíz ahora simplemente importa y reexporta esas funciones.

#### Problema 3: Mensajes de error y diagnóstico repetidos
- Múltiples bloques de código para diagnóstico de conexión a la base de datos

**Solución**: Mensajes unificados y manejo centralizado de errores usando logging en lugar de prints directos.

### 3. Posibles errores

#### Problema 1: Configuración forzada a PostgreSQL
- El código eliminaba la posibilidad de usar SQLite, pero había referencias a SQLite

**Solución**: Se han eliminado todas las referencias a SQLite y se ha clarificado que PostgreSQL es el único motor de base de datos soportado.

#### Problema 2: Nombre incorrecto en variable
- `sqlite_sqlite_db_dir` en config.py (línea 61) tenía nombre redundante

**Solución**: Eliminado al centralizar la configuración en `app/config.py`.

#### Problema 3: Riesgo de exposición de credenciales en registros
- `main.py` y `app/config.py` imprimían partes de la URL de conexión a la base de datos

**Solución**: Se ha implementado un filtrado que solo muestra la parte del host de la URL, omitiendo cualquier credencial.

#### Problema 4: Gestión inconsistente de excepciones
- Algunos bloques terminaban el programa y otros continuaban

**Solución**: Política consistente de manejo de errores: errores críticos de configuración o conexión a la base de datos terminan la aplicación, mientras que errores no críticos se registran con logger.

### 4. Problemas de arquitectura

#### Problema 1: Conflicto entre configuraciones
- Había dos archivos de configuración (`config.py` en la raíz y `app/config.py`)

**Solución**: `app/config.py` es ahora el único archivo de configuración principal. `config.py` en la raíz se mantiene por compatibilidad pero marcado como deprecado.

#### Problema 2: Código de inicialización entrelazado
- La lógica de inicialización estaba dispersa entre varios archivos

**Solución**: División clara de responsabilidades:
- `main.py`: Punto de entrada y verificación de dependencias externas
- `app/config.py`: Configuración centralizada y verificación de conexión a la base de datos
- `app/__init__.py`: Inicialización de la aplicación Flask y extensiones

## Mejoras adicionales

1. **Sistema de logging**: Implementado sistema estructurado de logging en lugar de prints directos
2. **Documentación actualizada**: README.md actualizado para reflejar los cambios
3. **Mensajes de deprecación**: Advertencias claras en componentes deprecados
4. **Seguridad mejorada**: Ocultamiento de credenciales en logs y mensajes de diagnóstico
5. **Claridad en archivos .env**: Archivo de ejemplo actualizado con comentarios claros

## Implicaciones y pasos a seguir

1. Siempre usar `main.py` como punto de entrada a la aplicación
2. Configurar `DATABASE_URL` en `.env` es obligatorio (la aplicación no arranca sin este parámetro)
3. Asegurarse de tener `psycopg2-binary` instalado
4. Cualquier modificación futura a la configuración debe realizarse en `app/config.py`

## Archivos modificados

1. `app/config.py`
2. `app/__init__.py`
3. `main.py`
4. `config.py`
5. `app_run.py`
6. `.env`
7. `README.md`

## Próximos pasos recomendados

1. Migrar completamente al uso de logger en lugar de prints directos en todo el código
2. Considerar eliminar completamente `config.py` en la raíz en una futura versión
3. Implementar tests automatizados para verificar que la inicialización funciona correctamente
