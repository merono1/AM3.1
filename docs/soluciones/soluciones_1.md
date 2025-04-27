# Soluciones 1: Estructura del Proyecto y Problemas Básicos

## Estructura del Proyecto

```
AM3.1/
├── .env (configuración)
├── app/
│   ├── __init__.py (inicialización de la aplicación)
│   ├── config.py (configuraciones)
│   ├── models/ (modelos de datos)
│   ├── routes/ (controladores/rutas)
│   ├── services/ (servicios compartidos)
│   ├── static/ (archivos estáticos)
│   └── templates/ (vistas HTML)
├── main.py (punto de entrada principal)
├── app_run.py (script para ejecutar la aplicación)
└── requirements.txt (dependencias)
```

## Base de Datos
- **SQLite (local)**: `app/data/app.db`
- **PostgreSQL (Neon)**: Configuración en `.env` (remota)

## Componentes Principales

### Modelos
- `cliente.py`: Gestión de clientes
- `proyecto.py`: Gestión de proyectos
- `presupuesto.py`: Presupuestos, capítulos y partidas
- `hoja_trabajo.py`: Hojas de trabajo
- `factura.py`: Facturas y líneas de factura
- `proveedor.py`: Gestión de proveedores
- `proveedor_partida.py`: Asociación entre partidas y proveedores

### Controladores
- `cliente_routes.py`: Rutas para clientes
- `proyecto_routes.py`: Rutas para proyectos
- `presupuesto_routes.py`: Rutas para presupuestos
- `hoja_trabajo_routes.py`: Rutas para hojas de trabajo
- `factura_routes.py`: Rutas para facturas
- `proveedor_routes.py`: Rutas para proveedores
- `partida_routes.py`: API para actualizar descripciones

## Problemas Principales y Soluciones

### 1. Errores de Base de Datos
**Problema**: Errores de conexión a SQLite y columnas inexistentes.
**Solución**: 
- Scripts `check_db.py`, `reset_db.py` e `init_db.py` para verificar y reiniciar la BD
- `actualizar_estado_workflow.py` para añadir columna faltante `estado_workflow`

### 2. Problemas de Plantillas
**Problema**: Errores con secuencias de escape y sintaxis en Jinja2.
**Solución**:
- Uso del filtro `e('js')` para escape correcto
- Corrección en macros de paginación usando `**(extra_params or {})`

### 3. Consultas SQL Directas
**Problema**: Uso incorrecto de SQL directo en SQLAlchemy.
**Solución**:
- Importación de `text()` en archivos de rutas
- Modificación de consultas: `db.session.execute(text("SQL QUERY"))`

### 4. Compatibilidad entre Paquetes
**Problema**: Conflictos entre versiones de dependencias.
**Solución**:
- Script `setup_venv.py` para crear entorno con versiones específicas:
  - Flask==2.2.3
  - Werkzeug==2.2.3
  - SQLAlchemy==1.4.46
  - Flask-SQLAlchemy==3.0.3

## Comandos Útiles

```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Verificar base de datos
python check_db.py

# Inicializar base de datos
python init_db.py

# Ejecutar aplicación
python app_run.py

# Probar generación de PDFs
python generar_pdf_prueba.py
```

## Solución de Problemas Comunes

### Error "unable to open database file"
1. Ejecutar `python check_db.py`
2. Si persiste: `python reset_db.py`
3. Luego: `python init_db.py`

### Error con Jinja2 y escape de caracteres
- Usar filtro `e('js')` en lugar de escape manual
- Simplificar función `editarPartida()`

### Errores con SQLAlchemy
- Siempre usar `from sqlalchemy import text`
- Convertir consultas SQL directas: `db.session.execute(text("SQL QUERY"))`
