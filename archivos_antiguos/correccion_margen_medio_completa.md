# Corrección del problema con el margen medio en AM3.1

Se han corregido los problemas relacionados con el cálculo y aplicación del margen medio en los presupuestos:

## Problemas corregidos

1. **Cálculo incorrecto del margen medio**: Anteriormente se calculaba como un promedio simple, ahora se calcula como un promedio ponderado por el valor final de cada partida.

2. **Valor incorrecto en la interfaz**:
   - El campo de "Margen medio" en la cabecera (junto al botón "Nuevo Capítulo") ahora muestra el valor real calculado.
   - El valor de "Margen medio aplicado" en el resumen del presupuesto ahora muestra el valor real.

3. **Aplicación incorrecta del margen a todas las partidas**: Al hacer clic en "Aplicar", ahora se aplica correctamente el margen elegido a todas las partidas.

## Cambios realizados

1. En el backend (`presupuesto_routes.py`):
   - Se agregó código para calcular el margen medio real y pasarlo a la plantilla.
   - Se mejoró la función `aplicar_margen_todas` para manejar casos donde el total es nulo.

2. En el frontend (`editar_pres.html`):
   - Se modificó el cálculo del margen medio en JavaScript para usar un promedio ponderado.
   - Se actualizó el valor inicial del campo "Margen medio" para mostrar el valor real calculado.
   - Se simplificó la función `aplicarMargenProporcional` para aplicar directamente el valor digitado.
   - Se modificó la función `aplicarMargenMedio` para aceptar el nuevo margen como parámetro.

## Cómo funciona ahora

1. Al cargar un presupuesto:
   - El campo "Margen medio" muestra el valor real calculado en el backend (ej: 25.0% si todas las partidas tienen 25.0%)
   - El "Margen medio aplicado" en el resumen también muestra este valor

2. Al editar el valor en el campo "Margen medio" y hacer clic en "Aplicar":
   - Se envía el nuevo valor al backend
   - Se aplica este valor a todas las partidas
   - La página se recarga mostrando los cambios

## Para usar la nueva funcionalidad

1. Simplemente cargue un presupuesto y verá que los valores de margen medio son correctos.
2. Para cambiar el margen de todas las partidas:
   - Ingrese el nuevo valor en el campo "Margen medio"
   - Haga clic en "Aplicar"
   - Confirme en el diálogo que aparece

La función ahora es mucho más intuitiva y proporciona un cálculo preciso del margen medio que refleja la ponderación real por valor de cada partida.
