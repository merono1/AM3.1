# Solución al problema de los PDFs de presupuestos

## Descripción del problema

El sistema de generación de PDFs presentaba un problema donde las variables no se procesaban correctamente, mostrando el texto sin procesar (ejemplo: `{presupuesto.referencia}` en lugar del valor real). Esto ocurría principalmente cuando fallaban los métodos principales de generación y se recurría al método de generación de "PDF mínimo" como fallback.

## Causa del problema

El problema estaba en la forma en que se generaban las cadenas de texto en el PDF mínimo:

1. Se usaban f-strings directamente dentro de un contenido PDF binario.
2. No se evaluaban las variables antes de formar el contenido PDF.
3. No había una separación clara entre la fase de creación de contenido y la fase de codificación a bytes.

## Solución implementada

Se ha corregido el archivo `app/services/pdf_service.py` con las siguientes mejoras:

1. **Evaluación previa de variables**: Ahora evaluamos todas las variables (referencia, nombre de cliente, fecha, etc.) antes de insertarlas en el contenido del PDF.

```python
# Evaluamos las variables antes de crear el contenido del PDF
ref = presupuesto.referencia
cli = cliente.nombre
fecha = presupuesto.fecha.strftime('%d/%m/%Y') if presupuesto.fecha else '-'
dir_tipo = presupuesto.tipo_via or ''
dir_nombre = presupuesto.nombre_via or ''
# ... y así con todas las variables
```

2. **Separación de la creación de contenido y codificación**: Primero se crea la cadena de texto completa y luego se codifica a bytes.

```python
# Primero creamos el contenido completo como cadena de texto
pdf_content = f'''%PDF-1.7
...
BT /F1 10 Tf 50 700 Td (Referencia: {ref}) Tj ET
...
'''

# Después codificamos a bytes y escribimos
minimal_pdf = pdf_content.encode('utf-8')
with open(temp_file.name, 'wb') as f:
    f.write(minimal_pdf)
```

3. **Manejo mejorado de errores**: Se implementaron varias capas de fallback para garantizar que siempre se genere un PDF válido.

4. **Enriquecimiento del PDF mínimo**: Se mejoró el contenido del PDF mínimo para que incluya:
   - Datos básicos del presupuesto (referencia, cliente, fecha, dirección)
   - Resumen de capítulos y sus importes
   - Muestra de las partidas más importantes
   - Total del presupuesto
   - Información de contacto

## Capas de generación de PDFs

El sistema ahora cuenta con tres niveles de generación, en orden de preferencia:

1. **HTML a PDF con pdfkit**: Genera PDFs completos y bien formateados si `wkhtmltopdf` está instalado.
2. **FPDF como alternativa**: Genera PDFs estructurados con toda la información usando la biblioteca FPDF si el método anterior falla.
3. **PDF mínimo mejorado**: Genera un PDF básico pero completo con la información esencial si los dos métodos anteriores fallan.

## Verificación de la solución

Se ha probado la solución con varios presupuestos y todas las variables se muestran correctamente. El PDF mínimo ahora incluye toda la información esencial y mantiene un formato legible.

## Script de prueba independiente

Se ha creado un script `test_pdf_minimo.py` que permite verificar la generación del PDF mínimo sin depender del framework Flask. Este script crea objetos simulados y genera un PDF de prueba para confirmar que las variables se procesan correctamente.

## Recomendaciones adicionales

1. **Instalación de wkhtmltopdf**: Para obtener PDFs de mejor calidad, se recomienda instalar wkhtmltopdf en el sistema.
2. **Verificación periódica**: Se recomienda ejecutar el script de prueba periódicamente para verificar que la generación de PDFs sigue funcionando correctamente.
3. **Mejoras futuras**: Considerar la implementación de una solución más moderna y mantenible para la generación de PDFs, como ReportLab o WeasyPrint.

## Conclusión

El problema de las variables no procesadas en los PDFs ha sido solucionado mediante una mejor separación entre la evaluación de variables y la creación del contenido del PDF. Ahora, incluso cuando se utiliza el "PDF mínimo" como último recurso, todas las variables se muestran correctamente con sus valores reales.
