@echo off
echo ================================================================
echo       MIGRACION PARA ANADIR CAMPOS DE PROVEEDORES MULTIPLES
echo ================================================================
echo.

echo [1/3] Activando entorno virtual...
call venv\Scripts\activate.bat

echo [2/3] Verificando base de datos...
python -c "from app import create_app; app = create_app(); print('Base de datos verificada correctamente')"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: No se pudo conectar a la base de datos.
    echo Asegurese de que la base de datos este configurada correctamente.
    pause
    exit /b 1
)

echo [3/3] Ejecutando migracion...
python migrate_add_final_proveedores.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Hubo un problema durante la migracion.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ================================================================
echo      MIGRACION COMPLETADA EXITOSAMENTE
echo ================================================================
echo.
echo Ya puede utilizar la nueva funcionalidad de proveedores adicionales.
echo.
echo ACCIONES RECOMENDADAS:
echo 1. Reinicie la aplicacion para aplicar los cambios
echo 2. Si encuentra algun error, contacte con soporte tecnico
echo.
pause
