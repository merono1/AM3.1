@echo off
echo ====================================================
echo    VERIFICACION DE BASE DE DATOS LOCAL SQLITE
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
echo Verificando base de datos local...
echo.

python check_local_db.py

echo.
if %ERRORLEVEL% NEQ 0 (
    echo RESULTADO: La base de datos local NO esta disponible o tiene problemas.
) else (
    echo RESULTADO: Verificacion completada.
)
echo.

pause
