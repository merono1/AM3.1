@echo off
echo ===== REPARACION DE BASE DE DATOS AM3.1 =====
echo.
echo Este script reparara la estructura de la base de datos
echo Se creara una copia de seguridad automaticamente.
echo.
echo Presiona CTRL+C para cancelar o...
pause

python fix_database_complete.py

echo.
echo Proceso completado.
pause
