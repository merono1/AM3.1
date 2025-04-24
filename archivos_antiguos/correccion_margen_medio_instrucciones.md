# Instrucciones para corregir el cálculo del margen medio en AM3.1

Se ha corregido el problema con el cálculo del margen medio en presupuestos. El problema era que:

1. El margen medio no se calculaba correctamente - se hacía un promedio simple en lugar de un promedio ponderado.
2. El margen medio aplicado no se mostraba en el resumen del presupuesto (aparecía como 0.00%).
3. No se mantenía correctamente la relación entre las partidas y el margen aplicado.

## Cambios realizados

1. Se modificó el archivo `app/templates/presupuestos/editar_pres.html`:
   - Se actualizó la función JavaScript `calcularMargenMedio()` para calcular un margen medio ponderado por el valor final de cada partida.
   - Se mejoró la inicialización del valor del margen medio al cargar la página.

2. Se modificó el archivo `app/routes/presupuesto_routes.py`:
   - Se actualizó la función `editar_presupuesto()` para calcular el margen medio real en el backend y pasarlo a la plantilla.
   - Esto asegura que el valor mostrado en el resumen del presupuesto sea correcto incluso antes de ejecutar el JavaScript.

## Cómo se calcula ahora el margen medio

El margen medio ahora se calcula como un promedio ponderado, donde:
- El peso de cada partida es su valor final (precio con margen aplicado)
- El margen medio = Suma(margen × valor_final) / Suma(valor_final)

Esto refleja mejor el impacto real de cada margen en el presupuesto total, ya que las partidas con mayor valor tienen mayor impacto en el margen medio.

## Para usar la nueva funcionalidad

No se requiere ninguna acción adicional. Los cambios ya están aplicados y funcionarán automáticamente. Ahora cuando:

1. Visualices un presupuesto, verás el margen medio calculado correctamente en el resumen.
2. Apliques un margen a todas las partidas, todas se actualizarán correctamente.

## Errores conocidos resueltos

- Se ha corregido el problema donde el margen medio aplicado aparecía como 0.00% aunque las partidas tuvieran márgenes.
- Se ha mejorado el manejo de casos donde alguna partida no tiene valores de total/final calculados.
