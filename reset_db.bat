@echo off
echo ===== REINICIAR BASE DE DATOS =====
echo.
echo Este script eliminara la base de datos actual.
echo Al iniciar la aplicacion se creara una nueva base de datos en blanco.
echo.
echo Se creara una copia de seguridad automaticamente.
echo.
python reset_db_simple.py
echo.
pause
