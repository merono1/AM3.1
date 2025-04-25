@echo off
echo Ejecutando migracion para proveedores_partidas en PostgreSQL...
python migrations\migrate_postgres_columns.py
if %ERRORLEVEL% NEQ 0 (
  echo Error en la migracion. Presione cualquier tecla para salir...
  pause > nul
  exit /b %ERRORLEVEL%
)

echo.
echo Migracion completada exitosamente!
echo Presione cualquier tecla para salir...
pause > nul
