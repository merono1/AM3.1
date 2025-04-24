# Documentación: Gestión de Múltiples Proveedores por Partida

## Introducción

Esta actualización implementa la capacidad de asignar múltiples proveedores a cada partida en las hojas de trabajo, con funcionalidades para:

1. Añadir un campo "final proveedor" que calcula el precio final del proveedor con margen aplicado
2. Agregar múltiples proveedores a una misma partida para su comparación
3. Establecer cualquiera de los proveedores como "proveedor principal" de la partida

## Cambios Realizados los que sean

### Modelo de Datos

- **ProveedorPartida**:
  - Nuevos campos:
    - `margen_proveedor`: Porcentaje de margen aplicado al proveedor
    - `final_proveedor`: Precio final calculado (precio * (1 + margen_proveedor/100))
  - Nuevo método:
    - `calcular_final_proveedor()`: Calcula el precio final con el margen aplicado

### Rutas y APIs

- **Nueva API para Proveedores**:
  - `/api/proveedores-partidas/asignar`: Asigna un proveedor a una partida
  - `/api/proveedores-partidas/eliminar/<id>`: Elimina una asignación de proveedor
  - `/api/proveedores-partidas/por-partida/<id_partida>`: Lista proveedores de una partida
  - `/api/proveedores-partidas/establecer-principal`: Define proveedor principal
  - `/api/proveedores-partidas/actualizar/<id>`: Actualiza datos de proveedor

- **Rutas de Proveedores**:
  - `/api/proveedores/listar`: Obtiene listado de proveedores para el selector

### Interfaz de Usuario

- **Edición de Hojas de Trabajo**:
  - Sección expandible de "Proveedores Adicionales" por partida
  - Tabla para gestionar múltiples proveedores por partida
  - Botones para agregar, editar y eliminar proveedores
  - Cálculo automático del margen real y del precio final

## Cómo Usar la Nueva Funcionalidad

### Paso 1: Asociar un Proveedor Principal

1. En la edición de hoja de trabajo, cada partida tiene una sección "Proveedor Principal"
2. Seleccione un proveedor del menú desplegable
3. Indique el precio ofrecido por el proveedor
4. El margen real se calculará automáticamente

### Paso 2: Añadir Proveedores Adicionales

1. Haga clic en el botón "Proveedores Adicionales" para expandir la sección
2. Pulse "Agregar Proveedor" para abrir el formulario
3. Seleccione el proveedor, indique precio y margen
4. Opcionalmente, marque "Establecer como proveedor principal" 
5. Guarde los cambios

### Paso 3: Gestionar los Proveedores

Cada proveedor en la lista tiene tres opciones:
- **Guardar cambios**: Guarda modificaciones de precio o margen
- **Establecer como principal**: Define este proveedor como el principal para la partida 
- **Eliminar proveedor**: Quita el proveedor de la partida

## Comparación entre Proveedores

La nueva funcionalidad permite:

1. **Comparar precios** entre diferentes proveedores para una misma partida
2. **Aplicar márgenes diferentes** según el proveedor
3. **Ver el precio final** calculado para cada proveedor
4. **Cambiar fácilmente** el proveedor principal

## Notas Técnicas

- El cálculo del precio final se realiza tanto en el servidor como en el cliente para garantizar consistencia
- Los márgenes de proveedores son independientes del margen de la partida
- Al establecer un proveedor como principal, su precio se asigna a la partida para el cálculo del margen real

## Comandos de Instalación

Para instalar la nueva funcionalidad:

1. Ejecute `ejecutar_migracion_final_proveedores.bat` para actualizar la base de datos
2. Ejecute `actualizar_rutas_hoja_trabajo.bat` para actualizar las rutas
3. Reinicie la aplicación

También puede usar `aplicar_mejoras_proveedores.bat` para ejecutar todos los pasos anteriores automáticamente.
