# Corrección de problemas en el editor de presupuestos

Se han corregido varios problemas que afectaban a la funcionalidad de edición y visualización de presupuestos:

## Problemas corregidos

1. **TOTAL PRESUPUESTO muestra 0 €**: Se ha corregido el cálculo del total del presupuesto para que muestre el valor correcto (625.0 € en el ejemplo).

2. **Botones de editar no funcionan**: Se han corregido los problemas con los botones de editar partidas. El problema se debía a caracteres especiales y comillas en las descripciones de las partidas que causaban errores de JavaScript.

3. **Margen medio no se actualiza correctamente**: Se ha mejorado el cálculo y la visualización del margen medio para que refleje el valor real (25.0% en el ejemplo).

## Cambios realizados

1. En el backend (`presupuesto_routes.py`):
   - Se agregó código para calcular el total del presupuesto y pasarlo a la plantilla.
   - Se mejoró el cálculo del margen medio real.

2. En el frontend (`editar_pres.html`):
   - Se mejoró la función `editarPartida()` para manejar correctamente caracteres especiales y prevenir errores.
   - Se modificó la forma de pasar los parámetros a la función de edición de partidas.
   - Se agregó manejo de errores y mensajes de depuración para facilitar la resolución de problemas.

## Recomendaciones para el uso

- Si aún experimentas problemas con la edición de partidas, verifica en la consola del navegador (F12) si aparecen mensajes de error y compártelos para poder hacer ajustes adicionales.
- En caso de encontrar descripciones de partidas que no se puedan editar, considera simplificar los textos evitando caracteres especiales complejos.

## Otras mejoras

- El campo de margen medio ahora muestra el valor real calculado desde el principio.
- El botón "Aplicar" ahora funciona correctamente y aplica el margen a todas las partidas.
- El margen medio aplicado en el resumen ahora muestra el valor real.
