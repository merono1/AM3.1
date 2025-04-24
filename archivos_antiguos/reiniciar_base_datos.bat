@echo off
echo ===== REINICIALIZACION DE BASE DE DATOS AM3.1 =====
echo.
echo Este script ELIMINARA todas las tablas de la base de datos
echo y creara una nueva estructura desde cero.
echo.
echo Se creara una copia de seguridad automaticamente.
echo.
echo ADVERTENCIA: Todos los datos seran eliminados!
echo.
echo Presiona CTRL+C para cancelar o...
pause

python fix_clientes_and_reset.py

echo.
echo Proceso completado.
pause
