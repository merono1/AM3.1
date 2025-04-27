@echo off
echo Activando entorno virtual de AM3.1...

IF NOT EXIST venv (
    echo No se encontro el entorno virtual. Crealo primero con:
    echo python -m venv venv
    exit /b
)

call venv\Scripts\activate

IF %ERRORLEVEL% NEQ 0 (
    echo Error al activar el entorno virtual.
    echo Por favor, ejecuta manualmente: venv\Scripts\activate
) ELSE (
    echo Entorno virtual activado correctamente!
    echo.
    echo Puedes ejecutar los siguientes comandos:
    echo - python check_db.py      : Verificar la base de datos
    echo - python init_db.py       : Inicializar la base de datos
    echo - python main.py          : Ejecutar la aplicacion
    echo - app_run.bat             : Metodo alternativo para ejecutar la aplicacion
)
