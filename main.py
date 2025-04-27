# main.py
import os
import sys
import logging
from dotenv import load_dotenv
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
load_dotenv()

# Variable para controlar si ya se ejecutó la inicialización
is_second_run = os.environ.get('FLASK_RUN_FROM_RELOAD') == '1'

# Verificar dependencias solo en la primera ejecución
if not is_second_run:
    # Ya no es necesario verificar psycopg2 porque solo usamos SQLite
    pass

# Ahora importamos y creamos la aplicación
from app import create_app

app = create_app(os.getenv('FLASK_ENV', 'default'))

# Agregar ruta de diagnóstico
@app.route('/check_db')
def check_db():
    from flask import render_template_string
    
    try:
        # Obtener las tablas disponibles utilizando SQLAlchemy
        from sqlalchemy import inspect
        from app import db as flask_db
        
        # Usar una función simple para obtener las tablas
        inspector = inspect(flask_db.engine)
        tables = inspector.get_table_names()
        tables_html = "\\n".join([f"<li>{table}</li>" for table in tables])
        
        # Obtener ruta de la base de datos SQLite
        db_path = os.environ.get('DB_PATH', 'instance/app.db')
        
        return render_template_string("""<!DOCTYPE html>
            <html>
            <head>
                <title>Verificación de Base de Datos</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body class="bg-light">
                <div class="container py-5">
                    <div class="card shadow">
                        <div class="card-header bg-success text-white">
                            <h4 class="mb-0">✅ Conexión a SQLite Exitosa</h4>
                        </div>
                        <div class="card-body">
                            <p class="lead">Se ha conectado correctamente a la base de datos SQLite local.</p>
                            <p><strong>Ruta:</strong> {{ db_path }}</p>
                            
                            <h5 class="mt-4">Tablas disponibles:</h5>
                            <ul>
                                {{ tables_html|safe }}
                            </ul>
                            
                            <div class="mt-4">
                                <a href="/" class="btn btn-primary">Volver al Inicio</a>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
        """, db_path=db_path, tables_html=tables_html)
    except Exception as e:
        logger.error(f"Error al verificar la base de datos: {e}")
        
        return render_template_string("""<!DOCTYPE html>
            <html>
            <head>
                <title>Error de Base de Datos</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body class="bg-light">
                <div class="container py-5">
                    <div class="card shadow">
                        <div class="card-header bg-danger text-white">
                            <h4 class="mb-0">❌ Error de Conexión a SQLite</h4>
                        </div>
                        <div class="card-body">
                            <p class="lead">No se ha podido conectar a la base de datos SQLite local.</p>
                            
                            <div class="alert alert-danger">
                                {{ error }}
                            </div>
                            
                            <h5 class="mt-4">Soluciones posibles:</h5>
                            <ol>
                                <li>Verifica que la variable DB_PATH en el archivo .env es correcta.</li>
                                <li>Asegúrate de que el directorio 'instance' existe y tiene permisos de escritura.</li>
                                <li>Comprueba si el archivo de base de datos tiene permisos correctos.</li>
                                <li>Reinicia la aplicación para crear la base de datos si no existe.</li>
                            </ol>
                            
                            <div class="mt-4">
                                <a href="/" class="btn btn-primary">Volver al Inicio</a>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
        """, error=str(e))

# Ruta para detener la aplicación (para reinicio manual)
@app.route('/stop', methods=['POST'])
def stop_app():
    from flask import jsonify
    import os
    import threading
    import time
    
    def delayed_stop():
        time.sleep(1)  # Esperar 1 segundo para que se envíe la respuesta
        os._exit(0)  # Forzar cierre de la aplicación
    
    # Ejecutar en un hilo separado para permitir enviar la respuesta
    stop_thread = threading.Thread(target=delayed_stop)
    stop_thread.daemon = True
    stop_thread.start()
    
    return jsonify({"success": True, "message": "Servidor detenido"})

if __name__ == '__main__':
    # Imprimir mensaje de inicio solo una vez
    if not is_second_run:
        print("\n=== Iniciando aplicación AM3.1 ===")
        print(f"Configuración: {os.getenv('FLASK_ENV', 'default')}")
        print(f"Escuchando en: http://localhost:{os.getenv('PORT', 5000)}")
        print(f"Modo reloader: {'Desactivado' if os.environ.get('DISABLE_RELOADER', 'false').lower() == 'true' else 'Activado'}")
    
    # Marcar que está ejecutándose para el reinicio
    os.environ['FLASK_RUN_FROM_RELOAD'] = '1'
    
    # Decidir si usar reloader basado en una variable de entorno
    # Esto permite desactivarlo fácilmente sin cambiar el código
    use_reloader = not (is_second_run or os.environ.get('DISABLE_RELOADER', 'false').lower() == 'true')
    
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), use_reloader=use_reloader)