# Soluciones 3: Migraciones y Configuración

## 1. Sistema de Rutas Relativas

### 1.1 Problema
La aplicación utilizaba rutas absolutas, lo que dificultaba su portabilidad entre diferentes equipos.

### 1.2 Solución Implementada
1. **Archivo `config.py` centralizado**:
   - Define todas las rutas como relativas usando `pathlib.Path`
   - Carga variables de `.env` para personalización
   - Ofrece funciones utilitarias para directorios

2. **Modificaciones clave**:
   - `main.py`: Actualizado para usar `config.py`
   - `.env.example`: Añadidas variables para rutas
   - Documentación en `docs/rutas_relativas.md`

### 1.3 Ventajas
- Portabilidad entre diferentes sistemas
- Centralización de configuraciones
- Creación automática de directorios necesarios
- Soporte mejorado para PostgreSQL/SQLite

### 1.4 Uso Básico
```python
# Importar configuración
from config import DB_PATH, APP_DIR, ensure_directories

# Asegurar que existan directorios
ensure_directories()

# Usar rutas relativas
archivo_config = APP_DIR / 'config' / 'settings.json'
```

## 2. Migración de Hojas de Trabajo

### 2.1 Cambio Estructural
- **Cambio**: Hojas de trabajo vinculadas a presupuestos (antes a proyectos)
- **Scripts**: `migrate_hojas_trabajo_v2.py`, `update_constraint_hojas_trabajo.py`
- **Batch**: `migrar_hojas_trabajo.bat`, `actualizar_restricciones.bat`

### 2.2 Problemas Resueltos
1. **Relación obsoleta en Proyecto**:
   - Eliminada línea `hojas_trabajo = db.relationship('HojaTrabajo', back_populates='proyecto', cascade='all, delete-orphan')`
   - Archivo modificado: `app/models/proyecto.py`

2. **URLs incorrectas en plantillas**:
   ```python
   # De:
   'url': url_for('hojas_trabajo.hojas_por_proyecto', id_proyecto=proyecto.id)
   # A:
   'url': url_for('hojas_trabajo.hojas_por_presupuesto', id_presupuesto=presupuesto.id)
   ```

3. **Columna id_presupuesto inexistente**:
   - Uso de conexiones independientes para cada operación
   - Aplicación de `isolation_level="AUTOCOMMIT"`
   - Mejor manejo de errores y transacciones

4. **Restricción NOT NULL en id_proyecto**:
   - Modificada la columna `id_proyecto` para permitir NULL
   - Verificación de que `id_presupuesto` tenga restricción NOT NULL

### 2.3 Pasos para Migrar
1. Hacer copia de seguridad: `copy app\data\app.db app\data\app.db.backup`
2. Ejecutar: `migrar_hojas_trabajo.bat`
3. Verificar la migración
4. Ejecutar `actualizar_restricciones.bat` si es necesario

## 3. Migración a PostgreSQL/Neon

### 3.1 Ventajas
- Base de datos accesible desde cualquier lugar
- Seguridad con copias de seguridad automáticas
- Separación de aplicación y datos
- Mejor rendimiento con PostgreSQL
- Plan gratuito con 3GB de almacenamiento

### 3.2 Pasos para Migrar
1. **Instalar dependencias**:
   - Ejecutar `instalar_dependencias_postgres.bat` o
   - `pip install psycopg2-binary sqlalchemy-utils`

2. **Crear cuenta en Neon**:
   - Registrarse en https://neon.tech
   - Crear nuevo proyecto
   - Anotar cadena de conexión

3. **Configurar conexión**:
   - Ejecutar `configurar_neon.bat`
   - Introducir datos de conexión
   - Probar conexión
   - Actualizar `.env`

4. **Migrar datos**:
   - Ejecutar `python migrate_to_postgres.py`
   - Verificar que los datos se hayan migrado correctamente

### 3.3 Volver a SQLite (si es necesario)
1. Editar `.env`:
   - Descomentar `DB_PATH=...`
   - Comentar `DATABASE_URL=...`

### 3.4 Despliegue en Google Cloud Run
Con la base de datos en Neon, es posible desplegar en Google Cloud Run:
1. Construir imagen Docker
2. Subir imagen al Container Registry de Google
3. Configurar Cloud Run con `DATABASE_URL` correcto
4. Desplegar la aplicación

## 4. Solución Error "no such column: presupuestos.estado_workflow"

### 4.1 Problema
Error: `no such column: presupuestos.estado_workflow`

### 4.2 Solución
- **Scripts**:
  - `add_estado_workflow.py`
  - `fix_add_workflow_column.py`
  - `reset_and_fix_db.py` (para casos extremos)
- **Batch**: `ejecutar_actualizacion.bat`

### 4.3 Pasos para Implementar
1. Ejecutar `ejecutar_actualizacion.bat`
2. Reiniciar la aplicación
3. Verificar con `python verificar_bd.py`

### 4.4 Alternativa Radical
Si la actualización no funciona, usar `reset_database.bat` (elimina todos los datos)

## 5. Solución para Problema con Columnas en PostgreSQL

### 5.1 Problema Detectado
Error al acceder a hojas de trabajo después de implementar campos `unitario` y `cantidad`:
```
Error de programación
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) columna proveedores_partidas.unitario no existe
```

### 5.2 Soluciones Implementadas
1. **Conexión directa a PostgreSQL**:
   - Script `migrations/migrate_postgres_columns.py` con psycopg2
   - Batch `migrar_postgres_directo.bat`

2. **Script SQL puro**:
   - `migrations/postgres_migration.sql` para ejecución manual

3. **Solución temporal**:
   - Versión especial de `editar_hoja_multiprov.html` sin los campos problemáticos
   - Batch `restaurar_carga_proveedores.bat` para volver a la normalidad

### 5.3 Verificación
Consulta SQL para verificar la migración:
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'proveedores_partidas' 
ORDER BY ordinal_position;
```

### 5.4 Mejoras Adicionales
- Campos ocultos de proveedor con inputs tipo `hidden`
- Cálculo mejorado del margen real
- Interfaz simplificada para gestión de proveedores
