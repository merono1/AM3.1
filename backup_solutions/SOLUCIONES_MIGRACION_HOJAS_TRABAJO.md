# Solución de Problemas en la Migración de Hojas de Trabajo

## Problemas encontrados y sus soluciones

### 1. Relación obsoleta en el modelo Proyecto

**Problema:** El modelo `Proyecto` mantenía una relación obsoleta con `hojas_trabajo` que ya no existía tras la migración a presupuestos.

**Solución:** Eliminamos la relación en el archivo `app/models/proyecto.py`:
```python
# Eliminada línea:
hojas_trabajo = db.relationship('HojaTrabajo', back_populates='proyecto', cascade='all, delete-orphan')
```

### 2. URLs incorrectas en las plantillas

**Problema:** La plantilla `presupuestos/avanzado/lista.html` seguía usando `hojas_trabajo.hojas_por_proyecto` en lugar de la nueva ruta `hojas_trabajo.hojas_por_presupuesto`.

**Solución:** Actualizamos la referencia en la plantilla:
```python
# De:
'url': url_for('hojas_trabajo.hojas_por_proyecto', id_proyecto=proyecto.id)
# A:
'url': url_for('hojas_trabajo.hojas_por_presupuesto', id_presupuesto=presupuesto.id)
```

### 3. Columna id_presupuesto inexistente en la base de datos

**Problema:** La base de datos no tenía la columna `id_presupuesto` en la tabla `hojas_trabajo`, causando errores en las consultas.

**Solución:** Creamos un script mejorado (`migrate_hojas_trabajo_v2.py`) con mejor manejo de transacciones para añadir la columna y migrar los datos.

Principales mejoras:
- Uso de conexiones independientes para cada operación
- Aplicación de `isolation_level="AUTOCOMMIT"`
- Eliminación del uso de sesión global para evitar transacciones pendientes
- Mejor manejo de errores

### 4. Restricción NOT NULL en id_proyecto

**Problema:** Al crear nuevas hojas de trabajo, se producía un error por la restricción NOT NULL en la columna `id_proyecto` obsoleta.

**Solución:** Creamos un script adicional (`update_constraint_hojas_trabajo.py`) para:
- Modificar la columna `id_proyecto` para permitir NULL
- Verificar que `id_presupuesto` tenga la restricción NOT NULL

### 5. Preservación de formato HTML en descripciones de partidas (AM3.1)

**Problema:** Al generar hojas de trabajo a partir de presupuestos, las descripciones de partidas perdían su formato HTML al usar la función `sanitize_html()`.

**Solución:** 
- Creamos una nueva función `clean_html()` que conserva etiquetas básicas (p, br, strong, b, em, i, u, s, ul, ol, li, blockquote)
- Reemplazamos los elementos textarea por divs editables con atributo `contenteditable="true"`
- Implementamos una barra de herramientas para formatear texto
- Agregamos JavaScript para sincronizar el contenido del editor con campos ocultos

### 6. Soporte para asignación de proveedores a partidas (AM3.1)

**Problema:** Era necesario poder asignar proveedores a partidas específicas, junto con sus precios y calcular márgenes reales.

**Solución:**
- Creamos un modelo `ProveedorPartida` para la asociación entre partidas y proveedores
- Añadimos campos `id_proveedor_principal` y `precio_proveedor` al modelo `PartidaHoja`
- Implementamos un script de migración para PostgreSQL Neon (`migrate_add_proveedores_partidas.py`)
- Agregamos a la interfaz selección de proveedores en cada partida
- Implementamos cálculo de margen real usando la fórmula: `((Precio Final / Precio Proveedor) - 1) * 100`

## Resumen de cambios realizados

1. **Archivos corregidos/creados:**
   - `app/models/proyecto.py` - Eliminada relación obsoleta
   - `app/templates/presupuestos/avanzado/lista.html` - Actualizadas URLs 
   - `app/routes/hoja_trabajo_routes.py` - Añadida función `clean_html()` y soporte para proveedores
   - `app/templates/hojas_trabajo/editar.html` - Actualizada con editor HTML y selección de proveedores
   - `app/models/proveedor_partida.py` - Nuevo modelo para asociar partidas y proveedores
   - `app/models/hoja_trabajo.py` - Actualizado con nuevos campos para proveedores

2. **Scripts de migración creados:**
   - `migrate_hojas_trabajo_v2.py` - Migración mejorada con mejor manejo de transacciones
   - `update_constraint_hojas_trabajo.py` - Actualización de restricciones NOT NULL
   - `migrate_add_proveedores_partidas.py` - Script para añadir soporte de proveedores en base de datos Neon

3. **Archivos batch:**
   - `migrar_hojas_trabajo.bat` - Actualizado para usar el nuevo script de migración
   - `actualizar_restricciones.bat` - Creado para ejecutar la actualización de restricciones
   - `ejecutar_migracion_proveedores.bat` - Creado para ejecutar la migración de proveedores

Estos cambios permiten la correcta migración del sistema de hojas de trabajo, mantienen el formato HTML en las descripciones, y añaden la funcionalidad para asignar proveedores a partidas específicas con cálculo automático de márgenes reales.