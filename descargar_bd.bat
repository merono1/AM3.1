@echo off
echo ====================================================
echo    DESCARGA DE BASE DE DATOS NEON A SQLITE LOCAL
echo ====================================================
echo.

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Entorno virtual activado.
) else (
    echo ADVERTENCIA: No se encontro entorno virtual. Usando Python del sistema.
)

echo.
echo Iniciando descarga...
echo.

python db_download.py

echo.
if %ERRORLEVEL% NEQ 0 (
    echo Descarga FALLIDA. Revise los mensajes de error.
) else (
    echo Descarga COMPLETADA exitosamente.
)
echo.

pause
