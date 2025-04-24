# AM3.1 - Migraciones y Configuración

## 1. Migración de Hojas de Trabajo

### 1.1 Cambio Estructural
- **Cambio**: Hojas de trabajo vinculadas a presupuestos (antes a proyectos)
- **Scripts**: `migrate_hojas_trabajo_v2.py`, `update_constraint_hojas_trabajo.py`
- **Batch**: `migrar_hojas_trabajo.bat`, `actualizar_restricciones.bat`

### 1.2 Problemas Resueltos
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

### 1.3 Pasos para Migrar
1. Hacer copia de seguridad: `copy app\data\app.db app\data\app.db.backup`
2. Ejecutar: `migrar_hojas_trabajo.bat`
3. Verificar la migración
4. Ejecutar `actualizar_restricciones.bat` si es necesario

## 2. Migración a Neon PostgreSQL

### 2.1 Ventajas
- Base de datos accesible desde cualquier lugar
- Seguridad con copias de seguridad automáticas
- Separación de aplicación y datos
- Mejor rendimiento con PostgreSQL
- Plan gratuito con 3GB de almacenamiento

### 2.2 Pasos para Migrar
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
   - Verifica que los datos se hayan migrado correctamente

### 2.3 Volver a SQLite (si es necesario)
1. Editar `.env`:
   - Descomentar `DB_PATH=...`
   - Comentar `DATABASE_URL=...`

### 2.4 Despliegue en Google Cloud Run
Con la base de datos en Neon, es posible desplegar en Google Cloud Run:
1. Construir imagen Docker
2. Subir imagen al Container Registry de Google
3. Configurar Cloud Run con `DATABASE_URL` correcto
4. Desplegar la aplicación

## 3. Columna estado_workflow

### 3.1 Problema
Error: `no such column: presupuestos.estado_workflow`

### 3.2 Solución
- **Scripts**:
  - `add_estado_workflow.py`
  - `fix_add_workflow_column.py`
  - `reset_and_fix_db.py` (para casos extremos)
- **Batch**: `ejecutar_actualizacion.bat`

### 3.3 Pasos para Implementar
1. Ejecutar `ejecutar_actualizacion.bat`
2. Reiniciar la aplicación
3. Verificar con `python verificar_bd.py`

### 3.4 Alternativa Radical
Si la actualización no funciona, usar `reset_database.bat` (elimina todos los datos)

## 4. Añadir Proveedores a Partidas

### 4.1 Implementación
- Nuevo modelo `ProveedorPartida` para asociar partidas y proveedores
- Campos `id_proveedor_principal` y `precio_proveedor` en `PartidaHoja`
- Script: `migrate_add_proveedores_partidas.py`
- Batch: `ejecutar_migracion_proveedores.bat`

### 4.2 Cálculo de Margen Real
- Fórmula: `((Precio Final / Precio Proveedor) - 1) * 100`
- Interfaz actualizada para mostrar este cálculo

## 5. Solución de Problemas Comunes

### 5.1 Error "unable to open database file"
1. Ejecutar `python check_db.py`
2. Si persiste: `python reset_db.py`
3. Luego: `python init_db.py`

### 5.2 Error con PDFs
1. **Alternativa principal**: Instalar wkhtmltopdf
   - Descargar desde https://wkhtmltopdf.org/downloads.html
   - Verificar instalación: `wkhtmltopdf --version`

2. **Archivos de diagnóstico**:
   - `last_presupuesto.html`
   - `last_hoja_trabajo.html`
   - `last_factura.html`

### 5.3 Error con Jinja2 y escape de caracteres
- Usar filtro `e('js')` en lugar de escape manual
- Simplificar función `editarPartida()`

### 5.4 Errores con SQLAlchemy
- Siempre usar `from sqlalchemy import text`
- Convertir consultas SQL directas: `db.session.execute(text("SQL QUERY"))`

## 6. Configuración de Entorno de Desarrollo

### 6.1 Dependencias Recomendadas
- Flask==2.2.3
- Werkzeug==2.2.3
- SQLAlchemy==1.4.46
- Flask-SQLAlchemy==3.0.3
- Flask-WTF==1.1.1
- Flask-Migrate==4.0.4

### 6.2 Configurar Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6.3 Variables de Entorno (.env)
```
# SQLite (local)
DB_PATH=app/data/app.db

# PostgreSQL (Neon)
# DATABASE_URL=postgresql://usuario:password@ep-nombre-id.eu-central-1.aws.neon.tech/neondb
```
