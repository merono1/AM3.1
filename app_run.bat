@echo off
echo Ejecutando aplicacion AM3.1 (metodo alternativo)...
echo.

REM Verificar que python esté en el PATH
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python no encontrado. Asegurate que Python este instalado y agregado al PATH.
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

REM Ejecutar la aplicación con método alternativo
python app_run.py

pause