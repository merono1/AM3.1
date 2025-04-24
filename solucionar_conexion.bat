@echo off
echo ===== Solucionador de problemas de conexión a PostgreSQL en AM3.1 =====
echo.

REM Verificar que Python está instalado
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python no encontrado. Por favor, instala Python primero.
    pause
    exit /b 1
)

REM Verificar archivos del proyecto
if not exist app\__init__.py (
    echo ERROR: Estructura de proyecto no válida. Asegúrate de estar en el directorio correcto.
    pause
    exit /b 1
)

echo 1. Verificando variables de entorno...
python check_env.py
echo.

echo 2. Aplicando correcciones a la detección de PostgreSQL...
python fix_app_init.py
echo.

echo 3. Probando conexión a la base de datos Neon...
python test_neon_connection.py
echo.

echo 4. Si las pruebas anteriores han sido exitosas, ahora puedes ejecutar la aplicación.
echo    Selecciona una opción:
echo    1 - Ejecutar con modo diagnóstico (recomendado para solucionar problemas)
echo    2 - Ejecutar normalmente (si todo parece funcionar)
echo    3 - Salir sin ejecutar
echo.

set /p opcion="   Opción: "

if "%opcion%"=="1" (
    echo.
    echo Ejecutando en modo diagnóstico...
    python run_with_debug.py
) else if "%opcion%"=="2" (
    echo.
    echo Ejecutando normalmente...
    python run_fixed.py
) else (
    echo.
    echo Saliendo sin ejecutar la aplicación.
)

pause
