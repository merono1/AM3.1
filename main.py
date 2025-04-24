# main.py
import os
import sqlite3

# Importar la configuración centralizada
from config import (
    BASE_DIR, DB_PATH, DATABASE_URL, DB_TYPE, PORT,
    ensure_db_dir_exists, ensure_dirs_exist
)

# Variable para controlar si ya se ejecutó la inicialización
is_second_run = os.environ.get('FLASK_RUN_FROM_RELOAD') == '1'

if not is_second_run:
    print("=== Verificación de base de datos ===")
    
    using_postgres = DB_TYPE == "postgres"
    if using_postgres:
        print(f"✅ Usando PostgreSQL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configurada'}")
    else:
        db_dir = ensure_db_dir_exists()
        print(f"Ruta de la base de datos SQLite: {DB_PATH}")
        print(f"Directorio: {db_dir}")
        print(f"✅ Directorio verificado/creado")
        
        # Verificar permisos para SQLite
        try:
            with open(DB_PATH, 'a'):
                pass
            print(f"✅ Archivo de base de datos accesible/creado")
        except Exception as e:
            print(f"❌ Error al acceder al archivo de base de datos: {e}")

# Ahora importamos y creamos la aplicación
from app import create_app

app = create_app(os.getenv('FLASK_ENV', 'default'))

# Agregar ruta de diagnóstico
@app.route('/check_db')
def check_db():
    from flask import render_template_string
    
    # Determinar si usamos PostgreSQL o SQLite
    using_postgres = DB_TYPE == "postgres"
    db_path_display = DB_PATH if not using_postgres else 'N/A (usando PostgreSQL)'
    
    try:
        # Obtener las tablas disponibles utilizando SQLAlchemy
        from flask import current_app
        from sqlalchemy import inspect
        from app import db
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        tables_html = "\\n".join([f"<li>{table}</li>" for table in tables])
        
        connection_type = "PostgreSQL" if using_postgres else "SQLite"
        db_info = DATABASE_URL.split('@')[1] if using_postgres and '@' in DATABASE_URL else db_path_display
        
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
                            <h4 class="mb-0">✅ Conexión a Base de Datos Exitosa</h4>
                        </div>
                        <div class="card-body">
                            <p class="lead">Se ha conectado correctamente a la base de datos {{ connection_type }}.</p>
                            <p><strong>Conexión:</strong> {{ db_info }}</p>
                            
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
        """, connection_type=connection_type, db_info=db_info, tables_html=tables_html)
    except Exception as e:
        connection_type = "PostgreSQL" if using_postgres else "SQLite"
        
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
                            <h4 class="mb-0">❌ Error de Conexión a Base de Datos</h4>
                        </div>
                        <div class="card-body">
                            <p class="lead">No se ha podido conectar a la base de datos {{ connection_type }}.</p>
                            <p><strong>Conexión:</strong> {{ db_info }}</p>
                            
                            <div class="alert alert-danger">
                                {{ error }}
                            </div>
                            
                            <h5 class="mt-4">Soluciones posibles:</h5>
                            <ol>
                                {% if using_postgres %}
                                <li>Verifica que la cadena de conexión DATABASE_URL en el archivo .env es correcta.</li>
                                <li>Asegúrate de que el servidor PostgreSQL está en funcionamiento.</li>
                                <li>Comprueba si hay restricciones de IP o si necesitas VPN para acceder al servidor.</li>
                                <li>Ejecuta <code>python reset_db.bat</code> para recrear la base de datos.</li>
                                {% else %}
                                <li>Verifica que el directorio existe y tiene permisos de escritura.</li>
                                <li>Ejecuta <code>python reset_db_simple.py</code> para recrear la base de datos desde cero.</li>
                                <li>Asegúrate de que la variable <code>DB_PATH</code> en el archivo <code>.env</code> es correcta.</li>
                                {% endif %}
                            </ol>
                            
                            <div class="mt-4">
                                <a href="/" class="btn btn-primary">Volver al Inicio</a>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
        """, connection_type=connection_type, db_info=db_info, using_postgres=using_postgres, error=str(e))

if __name__ == '__main__':
    if not is_second_run:
        print("\\n=== Iniciando aplicación AM3.1 ===")
        print(f"Configuración: {os.getenv('FLASK_ENV', 'default')}")
        print(f"Escuchando en: http://localhost:{PORT}")
    
    # Marcar que está ejecutándose para el reinicio
    os.environ['FLASK_RUN_FROM_RELOAD'] = '1'
    
    app.run(host='0.0.0.0', port=PORT)
