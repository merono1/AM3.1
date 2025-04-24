# Corrección del Error de Escape en Plantillas

Se ha corregido un error importante que impedía cargar la página de edición de presupuestos. El problema era:

## Error original
```
jinja2.exceptions.TemplateSyntaxError: unexpected char '\\' at 11573
```

El error se produjo en la línea donde intentábamos escapar caracteres especiales en la descripción de las partidas.

## Solución aplicada

1. Se ha reemplazado el código problemático:
   ```html
   `{{ partida.descripcion|replace('\', '\\')|replace("'", "\'") }}`,
   ```
   por la versión correcta:
   ```html
   "{{ partida.descripcion|e('js') }}",
   ```

2. Se ha simplificado la función `editarPartida()` eliminando el código de reemplazo manual que causaba problemas:
   ```javascript
   // Se eliminó esta línea problemática
   descripcion = descripcion.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
   ```

## Explicación

El error se debía a un problema con las secuencias de escape en Jinja2. En lugar de intentar manejar manualmente el escape de caracteres especiales, ahora estamos usando el filtro `e('js')` de Jinja2, que está diseñado específicamente para escapar correctamente cadenas para su uso en JavaScript.

## Qué hacer si persisten los problemas

Si encuentras algún otro error relacionado con caracteres especiales en las descripciones de las partidas, considera:

1. Utilizar descripciones más sencillas sin caracteres especiales complejos
2. Revisar la consola del navegador (F12) para identificar cualquier error de JavaScript
3. Consultar los registros del servidor para ver errores detallados

Esta corrección debería resolver el problema de carga de la página y permitir la edición correcta de las partidas.
