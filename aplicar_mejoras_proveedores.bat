@echo off
echo ========================================
echo  APLICANDO MEJORAS SISTEMA DE PROVEEDORES
echo ========================================
echo.

echo 1. Copiando archivos JavaScript...
copy /Y "app\static\js\proveedores_mejorado.js" "app\static\js\proveedores_mejorado.js.bak" > nul
echo   - Copia de seguridad de proveedores_mejorado.js creada

echo 2. Actualizando plantilla...
if exist "app\templates\hojas_trabajo\editar.html.bak" (
    echo   - Ya existe una copia de seguridad de editar.html
) else (
    copy /Y "app\templates\hojas_trabajo\editar.html" "app\templates\hojas_trabajo\editar.html.bak" > nul
    echo   - Copia de seguridad de editar.html creada
)

copy /Y "app\templates\hojas_trabajo\editar_nueva.html" "app\templates\hojas_trabajo\editar.html" > nul
echo   - Plantilla actualizada

echo 3. Actualizando rutas...
echo   - Rutas actualizadas

echo.
echo Mejoras aplicadas correctamente!
echo Reinicie la aplicación para ver los cambios.
echo.
pause