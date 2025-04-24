@echo off
echo Solucionando conflicto de nombre en la variable db...
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

REM Aplicar todas las soluciones posibles
echo 1. Corrigiendo config.py...
python fix_db_conflict.py

echo 2. Corrigiendo app/__init__.py...
python app/fix_app.py

echo 3. Ejecutando aplicacion con metodo alternativo...
python app_run.py

pause