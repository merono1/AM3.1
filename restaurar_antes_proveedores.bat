@echo off
echo ========================================
echo  RESTAURANDO SISTEMA ANTERIOR DE PROVEEDORES
echo ========================================
echo.

echo 1. Restaurando plantilla...
if exist "app\templates\hojas_trabajo\editar.html.bak" (
    copy /Y "app\templates\hojas_trabajo\editar.html.bak" "app\templates\hojas_trabajo\editar.html" > nul
    echo   - Plantilla editar.html restaurada
) else (
    echo   - No se encontró copia de seguridad de editar.html
)

echo.
echo Restauración completada!
echo Reinicie la aplicación para ver los cambios.
echo.
pause