# Corrección del Problema al Crear Nuevas Partidas en Presupuestos

## Problema detectado
Al intentar crear una nueva partida en la edición de presupuestos, el sistema no permitía guardar la partida correctamente debido a problemas en:

1. El manejo de la comunicación entre el editor CKEditor y el servidor
2. La forma en que se enviaban los datos del formulario
3. La gestión del evento onsubmit del formulario

## Archivos modificados

### 1. `app/static/js/presupuestos_edicion.js`
Se modificó la función `prepararEnvioNuevaPartida` para:
- Prevenir el envío tradicional del formulario con `event.preventDefault()`
- Recolectar todos los datos del formulario manualmente
- Utilizar la API Fetch para enviar los datos al servidor
- Manejar correctamente la respuesta (tanto éxito como error)
- Recargar la página cuando la operación se complete con éxito

### 2. `app/templates/presupuestos/editar_pres.html`
Se modificó el atributo `onsubmit` del formulario de nueva partida para asegurar que:
- Se ejecuta la función `prepararEnvioNuevaPartida`
- Se devuelve siempre `false` para evitar el envío normal del formulario

### 3. `app/routes/presupuesto_routes.py`
Se mejoró la función `nueva_partida` para:
- Añadir mensajes de diagnóstico más detallados
- Validar mejor los datos recibidos
- Establecer valores por defecto adecuados para campos faltantes
- Proporcionar un manejo diferenciado según si la solicitud es AJAX o normal
- Responder con JSON cuando se detecta una solicitud AJAX
- Mejorar los mensajes de error y seguimiento

## Cómo funciona ahora
1. Al hacer clic en "Guardar Partida" en el formulario:
   - JavaScript intercepta el evento submit
   - Recoge los datos del formulario, incluido el contenido del editor CKEditor
   - Envía los datos al servidor mediante AJAX (Fetch API)

2. El servidor:
   - Recibe y valida los datos
   - Crea la partida en la base de datos
   - Responde con un mensaje de éxito o error en formato JSON

3. De vuelta en el cliente:
   - Si la operación fue exitosa, se recarga la página para mostrar la nueva partida
   - Si hubo un error, se muestra un mensaje de alerta con el detalle del problema

## Ventajas de esta corrección
1. Mejor manejo de datos del editor CKEditor
2. Más información de diagnóstico en caso de problemas
3. Experiencia de usuario mejorada (sin recargas innecesarias)
4. Mayor fiabilidad en la creación de partidas
5. Mejor tratamiento de errores