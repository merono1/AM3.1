@echo off
echo Ejecutando actualización de base de datos para lista avanzada...

echo Intentando con el primer método...
python add_estado_workflow.py

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo Primer método falló, intentando método alternativo...
    python fix_add_workflow_column.py
)

echo.
echo Actualización completada. Pulse cualquier tecla para continuar...
pause > nul