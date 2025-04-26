# Documentación: Sistema de Gestión de Proveedores Integrado

Este documento describe la implementación del nuevo sistema de gestión de proveedores integrado directamente en la página de edición de hojas de trabajo.

## Cambios realizados

1. **Nueva plantilla de edición**: Se ha creado una nueva plantilla `editar_nueva.html` que integra la gestión de proveedores inline.

2. **JavaScript mejorado**: Se ha implementado un nuevo archivo JS (`proveedores_mejorado.js`) que gestiona la funcionalidad de proveedores directamente en la página.

3. **API para proveedores**: Se ha creado una API específica para gestionar proveedores (`proveedor_api_routes.py`).

4. **Rutas actualizadas**: Se han actualizado las rutas para utilizar la nueva plantilla y las nuevas APIs.

## Arquitectura del sistema

### Modelo de datos
- `Proveedor`: Información general del proveedor
- `PartidaHoja`: Partidas individuales del presupuesto que tienen un proveedor_principal
- `ProveedorPartida`: Relación entre partidas y proveedores (muchos a muchos)

### API para proveedores

Se han implementado las siguientes rutas API:

- **GET /api/proveedores/listar**: Lista todos los proveedores disponibles
- **GET /api/proveedores/buscar?q={query}**: Busca proveedores por nombre o especialidad
- **GET /api/proveedores/obtener/{id}**: Obtiene detalles de un proveedor específico
- **GET /api/proveedores/partidas/{id_proveedor}**: Lista las partidas asociadas a un proveedor

### API para asignación de proveedores a partidas

Las siguientes rutas gestionan la asignación de proveedores a partidas:

- **GET /api/proveedores-partidas/por-partida/{id_partida}**: Lista los proveedores asignados a una partida
- **POST /api/proveedores-partidas/asignar**: Asigna un proveedor a una partida
- **POST /api/proveedores-partidas/actualizar/{id}**: Actualiza la información de un proveedor asignado
- **DELETE /api/proveedores-partidas/eliminar/{id}**: Elimina la asignación de un proveedor
- **POST /api/proveedores-partidas/establecer-principal**: Establece un proveedor como principal

## Funcionalidades implementadas

1. **Vista de proveedores inline**: Los proveedores se pueden gestionar directamente en la página de edición de hojas de trabajo.

2. **Añadir/eliminar proveedores**: Se pueden añadir y eliminar proveedores directamente desde el panel integrado.

3. **Proveedor principal**: Se puede establecer un proveedor como principal directamente, lo que actualiza los campos del formulario.

4. **Cálculo de margen real**: El sistema calcula automáticamente el margen real basado en el precio del proveedor y el precio final.

## Scripts de automatización

1. **aplicar_mejoras_proveedores.bat**: Script para aplicar todas las mejoras al sistema.

2. **restaurar_antes_proveedores.bat**: Script para revertir los cambios en caso de problemas.

## Instrucciones de uso

1. Ejecutar `aplicar_mejoras_proveedores.bat` para aplicar los cambios.
2. Reiniciar la aplicación para que los cambios surtan efecto.
3. En la página de edición de hojas de trabajo, usar el botón "Proveedores" para gestionar los proveedores de cada partida.

## Solución de problemas

Si hay problemas con la nueva implementación, ejecutar `restaurar_antes_proveedores.bat` para volver al sistema anterior.

## Futuras mejoras

1. Implementar la posibilidad de añadir unidades y cantidades específicas por proveedor.
2. Mejorar la interfaz de usuario para la gestión de proveedores.
3. Implementar funcionalidad para exportar información de proveedores a PDFs y Excel.
