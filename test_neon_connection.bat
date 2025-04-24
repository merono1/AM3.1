@echo off
echo Probando conexion a Neon PostgreSQL...
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

REM Verificar si psycopg2 está instalado
python -c "import psycopg2" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Instalando psycopg2-binary...
    pip install psycopg2-binary
    if %ERRORLEVEL% NEQ 0 (
        echo Error al instalar psycopg2-binary. Por favor, instalalo manualmente:
        echo pip install psycopg2-binary
        echo.
        pause
        exit /b
    )
)

REM Verificar si python-dotenv está instalado
python -c "import dotenv" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Instalando python-dotenv...
    pip install python-dotenv
    if %ERRORLEVEL% NEQ 0 (
        echo Error al instalar python-dotenv. Por favor, instalalo manualmente:
        echo pip install python-dotenv
        echo.
        pause
        exit /b
    )
)

REM Ejecutar script de prueba
python test_neon_connection.py

echo.
pause