# Solución a problemas con los PDFs de presupuestos

## Descripción del problema
Se identificó un problema con la generación de PDFs de presupuestos donde los documentos se generaban pero mostraban las variables sin procesar como `{presupuesto.referencia}` en lugar de sus valores reales. Esto ocurría especialmente en la generación del "PDF mínimo" cuando fallaban los métodos principales de generación.

## Solución implementada
Se ha corregido y mejorado la función `generar_pdf_presupuesto` (y otras funciones relacionadas) en el archivo `app/services/pdf_service.py` para:

1. Corregir el procesamiento de f-strings en la generación del PDF mínimo de respaldo
2. Separar la creación del contenido del PDF y su codificación a bytes
3. Implementar un PDF mínimo mejorado con más información sobre el presupuesto
4. Asegurar que todas las variables se evalúen correctamente antes de generar el archivo
5. Mantener el soporte para tres métodos de generación de PDFs:
   - Usando `pdfkit` (con wkhtmltopdf) como primera opción
   - Usando `FPDF` como alternativa cuando wkhtmltopdf no está disponible
   - Usando un "PDF mínimo mejorado" que muestra información básica pero completa

## Cómo funcionan los PDFs ahora

### Método principal (pdfkit)
Si `wkhtmltopdf` está instalado en el sistema, el programa usará `pdfkit` para generar PDFs de alta calidad a partir de HTML. Este método permite documentos con mejor formato, tipografía y soporte para CSS.

### Método alternativo (FPDF)
Si `wkhtmltopdf` no está instalado o falla por alguna razón, el programa utilizará `FPDF` como alternativa. Este método es más simple pero genera PDFs con buena estructura y toda la información del presupuesto.

### Método alternativo de emergencia (PDF mínimo mejorado)
Si tanto `wkhtmltopdf` como `FPDF` fallan o no están disponibles, el sistema generará un PDF mínimo pero con información completa y legible. Este PDF incluye:

1. Los datos básicos del presupuesto (referencia, cliente, fecha, dirección, título)
2. Un resumen de los capítulos y sus importes
3. Una muestra de las partidas más importantes
4. El total del presupuesto
5. Información de contacto de la empresa

Este método, si bien es más simple visualmente, garantiza que siempre se genere un PDF útil y con toda la información esencial del presupuesto.

## Instalación de wkhtmltopdf (recomendado)

Para obtener PDFs de mejor calidad, recomendamos instalar wkhtmltopdf:

1. Descarga la versión adecuada para tu sistema desde [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html)
2. Instala siguiendo las instrucciones del instalador
3. Asegúrate de que el ejecutable esté en el PATH del sistema

## Solución de problemas comunes

### El PDF no muestra datos o muestra variables sin procesar
- Si ves texto como `{presupuesto.referencia}` en lugar del valor real, verifica que estés usando la versión corregida del archivo `pdf_service.py`
- Verifica que el presupuesto tenga datos asociados en la base de datos
- Comprueba que el presupuesto esté asociado a un cliente y proyecto válidos
- Verifica que los capítulos y partidas estén correctamente creados

### El PDF no se genera
- Verifica que exista el directorio `app/static/pdfs` (se debería crear automáticamente)
- Comprueba que el usuario tenga permisos de escritura en ese directorio
- Revisa los logs para ver si hay errores específicos

### Problemas con caracteres especiales (acentos, ñ, etc.)
- Asegúrate de que todos los archivos estén guardados con codificación UTF-8
- Verifica que los datos se estén guardando correctamente en la base de datos

### El PDF no tiene el formato correcto
- Si estás usando el método alternativo (FPDF), el formato será más simple
- Para obtener un mejor formato, instala wkhtmltopdf

## Mejoras adicionales posibles

En el futuro, se podrían implementar las siguientes mejoras:

1. Refactorizar completamente el código de generación de PDFs para hacerlo más modular y mantenible
2. Añadir soporte para incluir logotipos e imágenes en los PDFs
3. Permitir personalizar el formato de los PDFs desde la interfaz
4. Agregar la posibilidad de incluir firmas digitales
5. Implementar múltiples plantillas de presupuestos
6. Implementar pruebas automatizadas para la generación de PDFs

## Referencia de la estructura de datos
Para que el PDF se genere correctamente, se necesitan los siguientes datos:

- **Presupuesto**: referencia, fecha, titulo, datos de dirección
- **Cliente**: nombre y otros datos de contacto
- **Proyecto**: referencia, nombre
- **Capítulos**: numero, descripción
- **Partidas**: capitulo_numero, numero, descripción, unitario, cantidad, precio, total, margen, final
