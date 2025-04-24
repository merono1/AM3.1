@echo off
echo Actualizando rutas de hojas de trabajo...

rem Hacer copia de seguridad del archivo original
copy "app\routes\hoja_trabajo_routes.py" "app\routes\hoja_trabajo_routes.py.bak"
if %ERRORLEVEL% NEQ 0 (
    echo Error al hacer copia de seguridad.
    exit /b 1
)

rem Copiar el nuevo archivo
copy "app\routes\hoja_trabajo_routes.py.new" "app\routes\hoja_trabajo_routes.py"
if %ERRORLEVEL% NEQ 0 (
    echo Error al reemplazar el archivo.
    exit /b 2
)

echo Rutas actualizadas correctamente!
pause
