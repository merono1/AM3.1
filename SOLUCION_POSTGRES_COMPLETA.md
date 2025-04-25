# Solución completa para problema con PostgreSQL

## Problema detectado

Se ha encontrado un error al acceder a las hojas de trabajo después de implementar los campos `unitario` y `cantidad` en el modelo `ProveedorPartida`. El error indica que estas columnas no existen en la base de datos PostgreSQL:

```
Error de programación
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) columna proveedores_partidas.unitario no existe
```

## Archivos y soluciones creadas

He preparado varias soluciones alternativas para resolver este problema:

1. **Conexión directa a PostgreSQL**:
   - `migrations/migrate_postgres_columns.py`: Script que utiliza psycopg2 directamente
   - `migrar_postgres_directo.bat`: Ejecuta el script anterior

2. **Script SQL puro**:
   - `migrations/postgres_migration.sql`: SQL que puedes ejecutar manualmente en tu cliente PostgreSQL

3. **Solución temporal**:
   - `app/templates/hojas_trabajo/editar_hoja_multiprov.html`: Versión temporal de la vista
   - `restaurar_carga_proveedores.bat`: Para volver a la carga normal cuando la migración esté completa

## Pasos recomendados

1. **Ejecutar la migración directa a PostgreSQL**:
   ```
   migrar_postgres_directo.bat
   ```
   Este es el método más confiable ya que evita problemas de contexto de aplicación.

2. **Si la migración directa falla**, utiliza el script SQL manual:
   - Abre tu cliente PostgreSQL (pgAdmin, DBeaver, etc.)
   - Conéctate a tu base de datos
   - Abre y ejecuta el archivo `migrations/postgres_migration.sql`

3. **Cuando la migración esté completa**, restaura la carga de proveedores:
   ```
   restaurar_carga_proveedores.bat
   ```

4. **Reinicia la aplicación** para que los cambios surtan efecto.

## Verificación

Para comprobar que la migración se ha realizado correctamente, puedes ejecutar esta consulta SQL:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'proveedores_partidas' 
ORDER BY ordinal_position;
```

Deberían aparecer las columnas `unitario` (tipo VARCHAR) y `cantidad` (tipo float8/double) en el resultado.

## Mejoras implementadas

Además de la migración, he implementado las siguientes mejoras:

1. **Campos ocultos de proveedor**:
   - Se han reemplazado los campos visibles con inputs tipo `hidden`
   - Se ha reorganizado la interfaz de gestión de proveedores

2. **Cálculo mejorado del margen real**:
   - El método `calcular_final_proveedor()` ahora considera la cantidad
   - La visualización del margen es más precisa

3. **Botones mejorados de proveedores**:
   - Simplificación de la interfaz con un único botón
   - Mensajes más claros en la UI

Estos cambios mejoran la experiencia de usuario y mantienen la funcionalidad completa del sistema.
