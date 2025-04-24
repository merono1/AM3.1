@echo off
echo Reconstruyendo la base de datos completamente...
python reset_and_fix_db.py
echo.
echo Proceso finalizado. Pulse cualquier tecla para continuar.
pause > nul