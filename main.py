# main.py
import os
import sqlite3
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno desde .env
load_dotenv()

# Verificar tipo de base de datos y configuración
using_postgres = os.environ.get('DATABASE_URL') is not None

# Configuración para SQLite si no estamos usando PostgreSQL
db_path = os.environ.get('DB_PATH', 'app/data/app.db') if not using_postgres else None
db_dir = Path(db_path).parent if db_path else None

# Variable para controlar si ya se ejecutó la inicialización
is_second_run = os.environ.get('FLASK_RUN_FROM_RELOAD') == '1'

if not is_second_run:
    print("=== Verificación de base de datos ===")
    
    if using_postgres:
        print(f"✅ Usando PostgreSQL: {os.environ.get('DATABASE_URL', '').split('@')[1] if '@' in os.environ.get('DATABASE_URL', '') else 'configurada'}")
    else:
        print(f"Ruta de la base de datos SQLite: {db_path}")
        print(f"Directorio: {db_dir}")
        
        # Asegurar que el directorio existe para SQLite
        try:
            os.makedirs(db_dir, exist_ok=True)
            print(f"✅ Directorio verificado/creado")
        except Exception as e:
            print(f"❌ Error al crear directorio: {e}")
        
        # Verificar permisos para SQLite
        try:
            with open(db_path, 'a'):
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
    import os
    
    # Determinar si usamos PostgreSQL o SQLite
    using_postgres = os.environ.get('DATABASE_URL') is not None
    db_path_display = db_path if db_path else 'N/A (usando PostgreSQL)'
    
    try:
        # Obtener las tablas disponibles utilizando SQLAlchemy
        from flask import current_app
        from sqlalchemy import inspect
        from app import db
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        tables_html = "\n".join([f"<li>{table}</li>" for table in tables])
        
        connection_type = "PostgreSQL" if using_postgres else "SQLite"
        db_info = os.environ.get('DATABASE_URL', '').split('@')[1] if using_postgres and '@' in os.environ.get('DATABASE_URL', '') else db_path_display
        
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
        print("\n=== Iniciando aplicación AM3.1 ===")
        print(f"Configuración: {os.getenv('FLASK_ENV', 'default')}")
        print(f"Escuchando en: http://localhost:{os.getenv('PORT', 5000)}")
    
    # Marcar que está ejecutándose para el reinicio
    os.environ['FLASK_RUN_FROM_RELOAD'] = '1'
    
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))