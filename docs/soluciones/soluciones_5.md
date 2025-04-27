# Soluciones 5: Resumen de Problemas Comunes y Comandos Útiles

## 1. Problemas Comunes y Soluciones

### 1.1 Error "unable to open database file"
**Pasos para solucionar**:
1. Ejecutar `python check_db.py` para diagnóstico
2. Si persiste el error: `python reset_db.py` para reinicializar
3. Completar con: `python init_db.py` para crear estructura inicial
4. Si todo falla: Usar `reset_database.bat` (elimina todos los datos)

### 1.2 Error con PDFs
**Solución principal**:
1. Instalar wkhtmltopdf desde https://wkhtmltopdf.org/downloads.html
2. Verificar instalación con: `wkhtmltopdf --version`
3. Reiniciar la aplicación

**Alternativa**: El sistema tiene un mecanismo de fallback automático que usará:
1. Alternativa FPDF si falla pdfkit
2. PDF mínimo si fallan las dos primeras opciones

**Archivos para diagnosticar problemas**:
- `last_presupuesto.html`
- `last_hoja_trabajo.html`
- `last_factura.html`

### 1.3 Error "no such column: presupuestos.estado_workflow"
**Solución rápida**:
1. Ejecutar `ejecutar_actualizacion.bat`
2. Reiniciar la aplicación

**Solución alternativa**:
1. Ejecutar manualmente `python add_estado_workflow.py`
2. Si falla, ejecutar `python fix_add_workflow_column.py`

### 1.4 Error con caracteres especiales en JavaScript
**Solución**:
1. Usar filtro `e('js')` de Jinja2 en lugar de escape manual
2. Utilizar el filtro `tojson` para valores pasados a JavaScript
3. Reemplazar código problemático como:
   ```javascript
   // De:
   var descripcion = "{{ partida.descripcion }}";
   // A:
   var descripcion = {{ partida.descripcion|tojson|safe }};
   ```

### 1.5 Errores con SQLAlchemy y consultas directas
**Solución**:
1. Importar text(): `from sqlalchemy import text`
2. Modificar consultas: `db.session.execute(text("SQL QUERY"))`
3. Para consultas parametrizadas:
   ```python
   db.session.execute(
      text("SELECT * FROM presupuestos WHERE id = :id"),
      {"id": presupuesto_id}
   )
   ```

## 2. Comandos Útiles

### 2.1 Gestión del Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate

# Activar entorno (Mac/Linux)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2.2 Gestión de Base de Datos
```bash
# Verificar base de datos
python check_db.py

# Inicializar base de datos
python init_db.py

# Reiniciar base de datos (elimina datos)
python reset_db.py

# Verificar estructura después de actualizaciones
python verificar_bd.py
```

### 2.3 Ejecución de la Aplicación
```bash
# Modo normal
python app_run.py

# Modo desarrollo (recarga automática)
python app_run.py --debug

# Ejecutar con script bat
app_run.bat
```

### 2.4 Migración y Actualización
```bash
# Actualizar columna estado_workflow
ejecutar_actualizacion.bat

# Migrar hojas de trabajo a presupuestos
migrar_hojas_trabajo.bat

# Actualizar restricciones de hojas de trabajo
actualizar_restricciones.bat

# Migrar a PostgreSQL (Neon)
python migrate_to_postgres.py

# Configurar PostgreSQL
configurar_neon.bat
```

### 2.5 Pruebas
```bash
# Probar generación de PDFs
python generar_pdf_prueba.py

# Actualizar referencias de proyectos
python fix_proyecto_referencias.py --apply

# Probar conexión a PostgreSQL
python test_neon_connection.py
```

## 3. Dependencias Recomendadas

La aplicación funciona correctamente con las siguientes versiones de dependencias:

- Flask==2.2.3
- Werkzeug==2.2.3
- SQLAlchemy==1.4.46
- Flask-SQLAlchemy==3.0.3
- Flask-WTF==1.1.1
- Flask-Migrate==4.0.4
- pdfkit==1.0.0
- fpdf2==2.7.5
- psycopg2-binary==2.9.5 (solo para PostgreSQL)
- python-dotenv==1.0.0

Es importante mantener estas versiones específicas para evitar problemas de compatibilidad.

## 4. Recomendaciones para Futuros Desarrollos

1. **Sistema de Creación/Edición de Partidas**:
   - Implementar un enfoque más modular para los formularios
   - Mejorar la validación en el lado del cliente
   - Refinar la integración con CKEditor

2. **Cálculo de Márgenes**:
   - Añadir opciones para diferentes estrategias de margen
   - Implementar histórico de cambios de margen

3. **Generación de PDFs**:
   - Mejorar personalización de plantillas
   - Implementar opciones para diferentes formatos

4. **Arquitectura General**:
   - Mantener un archivo de dependencias con versiones específicas
   - Implementar pruebas automatizadas
   - Mejorar la documentación del código
