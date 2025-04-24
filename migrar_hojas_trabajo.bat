@echo off
echo =========================================
echo Migrar Hojas de Trabajo hacia Presupuestos
echo =========================================
echo.

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
) else (
    echo No se encontro entorno virtual, continuando sin activar...
)

echo.
echo Creando copia de seguridad de la base de datos...
if exist app\data\app.db (
    copy app\data\app.db app\data\app.db.backup
    echo Copia de seguridad creada en app\data\app.db.backup
) else (
    echo No se encontró la base de datos en app\data\app.db
    echo Verifique la ubicación de la base de datos antes de continuar
    goto end
)

echo.
echo Ejecutando script de migracion de hojas de trabajo...
python migrate_hojas_trabajo_v2.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo Migracion completada exitosamente!
) else (
    echo Error durante la migracion. Revise los mensajes anteriores.
)

:end
echo.
echo Presione cualquier tecla para salir...
pause > nul