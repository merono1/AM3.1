@echo off
echo ================================================================
echo         SOLUCION DE ERROR DE PROVEEDORES MULTIPLES
echo ================================================================
echo.

echo [1/5] Verificando aplicacion...
tasklist /FI "IMAGENAME eq python.exe" | find /i "python.exe" > nul
if %ERRORLEVEL% EQU 0 (
    echo Cerrando aplicacion actual...
    taskkill /f /im python.exe > nul 2>&1
    timeout /t 2 > nul
)

echo [2/5] Activando entorno virtual...
call venv\Scripts\activate.bat

echo [3/5] Ejecutando migracion...
call ejecutar_migracion_final_proveedores.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudo completar la migracion.
    pause
    exit /b 1
)

echo [4/5] Actualizando rutas de trabajo...
call actualizar_rutas_hoja_trabajo.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudo actualizar las rutas.
    pause
    exit /b 2
)

echo [5/5] Iniciando aplicacion...
start python main.py

echo.
echo ================================================================
echo      SOLUCION COMPLETADA EXITOSAMENTE
echo ================================================================
echo.
echo El error ha sido corregido. La aplicacion se ha reiniciado con
echo los cambios aplicados. Ya puede utilizar la nueva funcionalidad
echo de proveedores multiples.
echo.
echo Si encuentra algun otro problema, contacte con soporte tecnico.
echo.
pause
