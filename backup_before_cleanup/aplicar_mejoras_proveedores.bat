@echo off
echo ========================================================
echo    APLICANDO MEJORAS DE PROVEEDORES MULTIPLES
echo ========================================================
echo.

echo 1. Ejecutando migracion para campos final_proveedor...
call ejecutar_migracion_final_proveedores.bat

echo.
echo 2. Reiniciando aplicacion...
taskkill /f /im python.exe 2>NUL
start python main.py

echo.
echo Mejoras de proveedores aplicadas correctamente!
echo.
echo Para usar la nueva funcionalidad:
echo 1. Acceda a una hoja de trabajo
echo 2. Use el boton "Proveedores Adicionales" en cada partida
echo 3. Agregue los proveedores que necesite
echo.
echo NOTA: Cada proveedor puede tener un precio y margen diferentes,
echo lo que permite comparar entre varios proveedores.
echo.
pause
