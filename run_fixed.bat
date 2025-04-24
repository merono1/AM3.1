@echo off
echo Aplicando solución para conflicto de nombres y ejecutando la aplicación...
echo.

REM Verificar que python esté en el PATH
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python no encontrado. Asegúrate que Python esté instalado y agregado al PATH.
    echo.
    pause
    exit /b
)

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Aplicar solución de conflicto
python fix_db_conflict.py

REM Ejecutar versión fija
echo.
echo Ejecutando aplicación con configuración corregida...
echo.
python run_fixed.py

pause