## Solución a problemas con la generación de PDFs

### Error: PDFs vacíos o incorrectos

Si los PDFs generados están vacíos o no se muestran correctamente, puede deberse a las siguientes causas:

1. **Falta instalar wkhtmltopdf**: El sistema usa dos bibliotecas para generar PDFs:
   - `pdfkit`: Biblioteca de Python (ya instalada con requirements.txt)
   - `wkhtmltopdf`: Programa externo que debe instalarse manualmente

### Instalación de wkhtmltopdf

1. Descarga wkhtmltopdf desde la página oficial: https://wkhtmltopdf.org/downloads.html
2. Instala la versión adecuada para tu sistema operativo (Windows, Mac o Linux)
3. Asegúrate de que wkhtmltopdf está en el PATH del sistema

### Verificación de la instalación

Para verificar que wkhtmltopdf está instalado correctamente:

1. Abre una terminal o línea de comandos
2. Ejecuta `wkhtmltopdf --version`
3. Deberías ver la versión instalada

### Solución alternativa

Si no puedes instalar wkhtmltopdf, el sistema usará automáticamente la biblioteca FPDF como alternativa. Los PDFs generados con FPDF serán más simples pero contendrán la información esencial.

### Archivos HTML para diagnóstico

Cuando se produce un error, el sistema guarda automáticamente el HTML generado en archivos temporales:

- `last_presupuesto.html`: Para presupuestos
- `last_hoja_trabajo.html`: Para hojas de trabajo
- `last_factura.html`: Para facturas

Estos archivos se encuentran en la misma carpeta que los PDFs generados y pueden ser útiles para diagnóstico.

### Contacto para soporte

Si continúas teniendo problemas con la generación de PDFs, contacta con el equipo de soporte técnico.
# Solución de Problemas en AM3.1

Este documento proporciona instrucciones para solucionar los problemas comunes en la aplicación AM3.1.

## Problemas identificados y soluciones

### 0. Problema con la generación de PDFs de presupuestos

**Problema**: Los PDFs de presupuestos se generaban pero mostraban las variables sin procesar como `{presupuesto.referencia}` en lugar de sus valores reales. Esto ocurría principalmente en la generación del "PDF mínimo" que sirve como respaldo cuando fallan los métodos principales.

**Solución**:
1. Se ha corregido la función `generar_pdf_presupuesto` (y otras funciones relacionadas) en `app/services/pdf_service.py` para separar la creación del contenido de la cadena de texto y su posterior codificación a bytes.
2. Ahora se usa un enfoque de dos pasos:
   ```python
   # Primero se crea el contenido con f-string (para evaluar variables)
   pdf_content = f'%PDF-1.7\n... (Presupuesto: {presupuesto.referencia}) ...'
   # Luego se codifica a bytes
   minimal_pdf = pdf_content.encode('utf-8')
   ```
3. Se mantienen los dos métodos de generación de PDFs:
   - Usando `pdfkit` (con wkhtmltopdf) como primera opción para PDFs de alta calidad
   - Usando `FPDF` como alternativa cuando wkhtmltopdf no está disponible
   - El "PDF mínimo" como último recurso

4. Para probar la generación de PDFs, puedes usar el script actualizado:
   ```
   python generar_pdf_prueba.py
   ```
   Este script ahora muestra más información de diagnóstico para verificar que todo funcione correctamente.

5. Para más detalles técnicos, consulta el archivo `SOLUCION_PDF_PRESUPUESTOS.md`

### 1. Error de conexión a la base de datos SQLite

**Problema**: "unable to open database file"

**Solución**:
1. Ejecuta el script de verificación de base de datos:
   ```
   python check_db.py
   ```
   Este script verifica que:
   - El directorio de la base de datos existe
   - El archivo de la base de datos existe y tiene permisos correctos
   - Se puede establecer conexión con SQLite

2. Si todavía hay problemas, ejecuta:
   ```
   python reset_db.py
   ```
   Este script eliminará la base de datos existente y creará una nueva.

3. Inicializa la base de datos:
   ```
   python init_db.py
   ```

### 2. Error de sintaxis en plantillas Jinja2 con `**kwargs`

**Problema**: Error al usar `**kwargs` en macros de paginación

**Solución**:
- Se ha modificado la macro de paginación en `app/templates/layout/components.html` para usar `**(extra_params or {})` en lugar de `**extra_params`, lo que maneja correctamente el caso donde extra_params está vacío o es None.

### 3. Error con consultas SQL directas en SQLAlchemy

**Problema**: SQLAlchemy requiere el uso de `text()` para consultas SQL directas

**Solución**:
- Se ha importado `from sqlalchemy import text` en todos los archivos de rutas
- Se ha modificado las consultas SQL directas para usar `db.session.execute(text("SQL QUERY"))` en lugar de `db.session.execute("SQL QUERY")`

### 4. Problemas de compatibilidad entre versiones de paquetes

**Problema**: Conflictos entre versiones de SQLAlchemy, Flask y extensiones

**Solución**:
1. Ejecuta el script de configuración de entorno virtual con versiones compatibles:
   ```
   python setup_venv.py
   ```
   Este script creará un nuevo entorno virtual con las siguientes versiones:
   - Flask==2.2.3
   - Werkzeug==2.2.3
   - SQLAlchemy==1.4.46
   - Flask-SQLAlchemy==3.0.3
   - Flask-WTF==1.1.1
   - Flask-Migrate==4.0.4

2. En Windows, también puedes usar el archivo batch para activar el entorno:
   ```
   activate_venv.bat
   ```

## Pasos para ejecutar la aplicación tras las correcciones

1. Activa el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

2. Verifica la base de datos:
   ```
   python check_db.py
   ```

3. Inicializa la base de datos si es necesario:
   ```
   python init_db.py
   ```

4. Ejecuta la aplicación:
   ```
   python run.py
   ```

## Consejos adicionales para desarrollo

- No mezcles diferentes versiones de SQLAlchemy, Flask-SQLAlchemy y Flask
- Mantén un archivo de dependencias exacto con versiones específicas
- Usa entornos virtuales para cada proyecto
- Siempre verifica permisos y rutas para archivos de base de datos SQLite

## Comandos útiles para diagnóstico

- Ver versiones de paquetes instalados: `pip freeze`
- Ver log detallado de SQLAlchemy: añade `SQLALCHEMY_ECHO = True` en configuración
- Comprobar permisos de archivo en Linux/Mac: `ls -la app/data/app.db`
- Comprobar conectividad SQLite directa: `sqlite3 app/data/app.db ".tables"`
