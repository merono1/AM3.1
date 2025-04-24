# AM3.1 - Funcionalidades Principales

## 1. Sistema de Partidas en Presupuestos

### 1.1 Creación y Edición de Partidas
**Archivos clave**:
- `app/templates/presupuestos/editar_pres.html`
- `app/static/js/presupuestos_modal.js`
- `app/static/js/presupuestos_edicion.js`
- `app/routes/presupuesto_routes.py`

**Solución implementada**:
- Modal para nuevas partidas en lugar de formulario integrado
- Campo oculto para almacenar contenido del editor CKEditor
- Función `guardarNuevaPartida()` para el proceso completo
- Mejor manejo de caracteres especiales con `tojson`

### 1.2 Partidas Intercaladas
**Implementación**:
- Botón "+" en cada fila de partida existente
- Modal con distinción entre "Nueva Partida" y "Nueva Partida Intercalada"
- Renumeración automática de partidas tras inserción
- Lógica secuencial (1.1, 1.2, 1.3) mantenida

### 1.3 Editor de Texto Enriquecido para Descripciones
**Archivos clave**:
- `app/static/js/editor_inline.js`
- `app/routes/partida_routes.py`

**Características**:
- Editor WYSIWYG activado con doble clic en la descripción
- Barra de herramientas con opciones de formato
- Guardado AJAX sin recargar la página
- Filas de datos numéricos siempre visibles

## 2. Gestión del Margen

### 2.1 Cálculo del Margen Medio
**Implementación**:
- Promedio ponderado por valor de cada partida
- Interfaz actualizada para mostrar el valor real
- Función `aplicar_margen_todas` mejorada

### 2.2 Cálculo de Margen Real con Proveedores
**Implementación**:
- Modelo `ProveedorPartida` para asociar partidas y proveedores
- Campos `id_proveedor_principal` y `precio_proveedor` en `PartidaHoja`
- Cálculo: `((Precio Final / Precio Proveedor) - 1) * 100`

## 3. Generación de PDFs

### 3.1 Sistema de Tres Capas
**Archivo clave**: `app/services/pdf_service.py`

**Implementación**:
1. **HTML a PDF con `pdfkit`**: Requiere `wkhtmltopdf`
2. **Alternativa con `FPDF`**: PDF estructurado cuando falla la primera opción
3. **PDF mínimo mejorado**: Versión básica pero completa como último recurso

### 3.2 Solución a Variables No Evaluadas
**Problema**: Variables aparecían como `{presupuesto.referencia}`
**Solución**:
```python
# Primero se crea el contenido con f-string (para evaluar variables)
pdf_content = f'%PDF-1.7\n... (Presupuesto: {presupuesto.referencia}) ...'
# Luego se codifica a bytes
minimal_pdf = pdf_content.encode('utf-8')
```

### 3.3 Mejoras Visuales
- Tablas con bordes y colores
- Textos con tamaño y estilo apropiados
- Manejo correcto de descripciones largas
- Colores corporativos y mejor estructura

## 4. Sistema de Referencias

### 4.1 Referencias para Proyectos
**Formato**: PRXXXTT-DDMMAA
- PR: Prefijo fijo (2 caracteres)
- XXX: Número de cliente con padding de ceros (3 dígitos)
- TT: Primera y tercera letra del tipo de proyecto (2 caracteres)
- Guion separador
- DDMMAA: Fecha de creación (día, mes, año - 6 dígitos)

**Archivo clave**: `app/routes/proyecto_routes.py`

### 4.2 Referencias para Presupuestos Clonados
**Implementación**:
- Formato cambiado de `-P{num:02d}` a `-V{num:02d}`
- Expresión regular actualizada para buscar último número de versión
- Archivo modificado: `app/routes/presupuesto_routes.py`

## 5. Listado Avanzado de Presupuestos

### 5.1 Campos Adicionales
- Cliente, Tipo de Proyecto, Nombre del Proyecto
- Técnico Encargado, Aprobado, Fecha de Aprobación
- Estado de Workflow

### 5.2 Filtros Avanzados
- Cliente, Tipo de Proyecto, Técnico Encargado
- Estado de Workflow, Rango de fechas
- Aprobado/No aprobado, Referencia

### 5.3 Mejoras Visuales
- Código de colores (verde: aprobados, rojo: no aprobados)
- Actualización en tiempo real
- Exportación a CSV

## 6. Hojas de Trabajo Vinculadas a Presupuestos

### 6.1 Archivos Modificados
- `app/models/hoja_trabajo.py`: Modelo actualizado para relacionarse con presupuestos
- `app/models/presupuesto.py`: Relación con hojas de trabajo
- `app/routes/hoja_trabajo_routes.py`: Rutas actualizadas
- `app/templates/hojas_trabajo/*.html`: Plantillas actualizadas
- `app/templates/presupuestos/editar_pres.html`: Botones para gestionar hojas

### 6.2 Funcionalidades
- Creación de hojas desde presupuestos
- Listado de hojas por presupuesto
- Referencias con formato `referencia_presupuesto + HT`
