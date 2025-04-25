@echo off
echo =========================================
echo Actualizar Restricciones de Hojas de Trabajo
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
    copy app\data\app.db app\data\app.db.backup_constraints
    echo Copia de seguridad creada en app\data\app.db.backup_constraints
) else (
    echo No se encontró la base de datos en app\data\app.db
    echo Procediendo sin copia de seguridad local...
)

echo.
echo Ejecutando script para actualizar restricciones...
python update_constraint_hojas_trabajo.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo Actualización de restricciones completada exitosamente!
) else (
    echo Error durante la actualización. Revise los mensajes anteriores.
)

:end
echo.
echo Presione cualquier tecla para salir...
pause > nul