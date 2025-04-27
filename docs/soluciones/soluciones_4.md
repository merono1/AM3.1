# Soluciones 4: Gestión de Proveedores y Cálculo de Márgenes

## 1. Gestión de Múltiples Proveedores por Partida

### 1.1 Funcionalidades Implementadas
- Asignar múltiples proveedores a cada partida
- Campo "final proveedor" para calcular precio con margen aplicado
- Comparación entre proveedores para una misma partida
- Configuración de proveedor principal

### 1.2 Cambios en Modelo de Datos
- **Modelo ProveedorPartida**:
  - Nuevos campos:
    - `margen_proveedor`: Porcentaje de margen aplicado
    - `final_proveedor`: Precio final calculado
    - `unitario`: Precio unitario (campo que causó el error en PostgreSQL)
    - `cantidad`: Cantidad (campo que causó el error en PostgreSQL)
  - Nuevo método `calcular_final_proveedor()` para cálculo de precio final

### 1.3 Nuevas APIs y Rutas
- `/api/proveedores-partidas/asignar`: Asigna proveedor a partida
- `/api/proveedores-partidas/eliminar/<id>`: Elimina asignación
- `/api/proveedores-partidas/por-partida/<id_partida>`: Lista proveedores
- `/api/proveedores-partidas/establecer-principal`: Define proveedor principal
- `/api/proveedores-partidas/actualizar/<id>`: Actualiza datos
- `/api/proveedores/listar`: Obtiene listado para selector

## 2. Interfaz de Usuario para Gestión de Proveedores

### 2.1 Edición de Hojas de Trabajo
- Sección "Proveedor Principal" en cada partida
- Sección expandible "Proveedores Adicionales"
- Tabla para gestionar múltiples proveedores
- Cálculo automático de margen real y precio final

### 2.2 Uso de la Funcionalidad
1. **Asociar Proveedor Principal**:
   - Seleccionar proveedor del menú desplegable
   - Indicar precio ofrecido
   - El margen real se calcula automáticamente

2. **Añadir Proveedores Adicionales**:
   - Expandir sección "Proveedores Adicionales"
   - Usar "Agregar Proveedor" para abrir formulario
   - Indicar proveedor, precio y margen
   - Opcionalmente, establecer como principal
   - Guardar cambios

3. **Gestionar Proveedores**:
   - "Guardar cambios": Actualiza precio o margen
   - "Establecer como principal": Define proveedor principal
   - "Eliminar proveedor": Quita de la partida

### 2.3 Comparación entre Proveedores
- Comparación de precios entre diferentes proveedores
- Aplicación de márgenes diferentes según proveedor
- Visualización de precio final calculado
- Cambio fácil de proveedor principal

## 3. Cálculo de Márgenes Reales

### 3.1 Fórmula de Cálculo
```
Margen Real = ((Precio Final / Precio Proveedor) - 1) * 100
```

### 3.2 Implementación
- El cálculo se realiza tanto en servidor como cliente
- Los márgenes de proveedores son independientes del margen de partida
- Al establecer proveedor principal, su precio se asigna a la partida

### 3.3 Mejoras Visuales
- Código de colores según el margen (verde para alto, rojo para bajo)
- Actualización en tiempo real al modificar precios
- Formato de números con precisión de dos decimales

## 4. Instalación y Migración

### 4.1 Comandos de Instalación
1. Ejecutar `ejecutar_migracion_final_proveedores.bat` para actualizar BD
2. Ejecutar `actualizar_rutas_hoja_trabajo.bat` para actualizar rutas
3. Reiniciar aplicación

Alternativa: Usar `aplicar_mejoras_proveedores.bat` para ejecutar todos los pasos anteriores.

### 4.2 Scripts de Migración
- `migrate_add_proveedores_partidas.py`: Agrega campos necesarios
- `migrate_postgres_columns.py`: Versión específica para PostgreSQL
- `migrations/postgres_migration.sql`: SQL puro para ejecución manual

### 4.3 Solución de Problemas
- Si hay error en PostgreSQL: usar `migrar_postgres_directo.bat`
- Para volver a la versión normal: `restaurar_carga_proveedores.bat`
- Verificar migración con consulta SQL descrita en la sección 5.3 de soluciones_3.md

## 5. Preservación de Formato HTML en Descripciones

### 5.1 Problema
Al generar hojas de trabajo desde presupuestos, las descripciones perdían formato HTML.

### 5.2 Solución
- Nueva función `clean_html()` que conserva etiquetas básicas
- Reemplazo de textareas por divs con `contenteditable="true"`
- Barra de herramientas para formatear texto
- JavaScript para sincronizar contenido con campos ocultos

### 5.3 Etiquetas HTML Permitidas
- Elementos de texto: p, br, strong, b, em, i, u, s
- Listas: ul, ol, li
- Formateo: blockquote
- Se eliminan scripts y otras etiquetas potencialmente peligrosas
