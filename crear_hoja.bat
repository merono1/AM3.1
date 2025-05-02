@echo off
set /p id_presupuesto="Introduce el ID del presupuesto: "
python crear_hoja_trabajo.py %id_presupuesto%
echo.
echo Proceso finalizado.
pause
