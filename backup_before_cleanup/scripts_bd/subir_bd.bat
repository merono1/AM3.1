@echo off
echo ====================================================
echo    SUBIDA DE BASE DE DATOS SQLITE A NEON POSTGRES
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
echo Iniciando subida...
echo.

python db_upload.py

echo.
if %ERRORLEVEL% NEQ 0 (
    echo Subida FALLIDA. Revise los mensajes de error.
) else (
    echo Subida COMPLETADA exitosamente.
)
echo.

pause
