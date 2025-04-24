# main.py
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno desde .env
load_dotenv()

# Verificar que DATABASE_URL esté configurado
if not os.environ.get('DATABASE_URL'):
    print("❌ ERROR: No se ha configurado DATABASE_URL en el archivo .env")
    print("   La aplicación está configurada para usar SOLO PostgreSQL en Neon.")
    print("   Asegúrate de que DATABASE_URL esté correctamente definida en el archivo .env")
    sys.exit(1)

# Verificar que psycopg2 esté instalado
try:
    import psycopg2
except ImportError:
    print("❌ ERROR: No se ha encontrado el módulo 'psycopg2'")
    print("   Este módulo es necesario para conectarse a PostgreSQL.")
    print("   Instálalo con: pip install psycopg2-binary")
    sys.exit(1)

# Variable para controlar si ya se ejecutó la inicialización
is_second_run = os.environ.get('FLASK_RUN_FROM_RELOAD') == '1'

if not is_second_run:
    print("=== Verificación de base de datos ===")
    print(f"✅ Usando PostgreSQL: {os.environ.get('DATABASE_URL', '').split('@')[1] if '@' in os.environ.get('DATABASE_URL', '') else 'configurada'}")

# Ahora importamos y creamos la aplicación
from app import create_app

app = create_app(os.getenv('FLASK_ENV', 'default'))

# Agregar ruta de diagnóstico
@app.route('/check_db')
def check_db():
    from flask import render_template_string
    import os
    
    try:
        # Obtener las tablas disponibles utilizando SQLAlchemy
        from flask import current_app
        from sqlalchemy import inspect
        from app import db as flask_db
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        tables_html = "\n".join([f"<li>{table}</li>" for table in tables])
        
        db_info = os.environ.get('DATABASE_URL', '').split('@')[1] if '@' in os.environ.get('DATABASE_URL', '') else 'configurada'
        
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
                            <h4 class="mb-0">✅ Conexión a PostgreSQL Exitosa</h4>
                        </div>
                        <div class="card-body">
                            <p class="lead">Se ha conectado correctamente a la base de datos PostgreSQL en Neon.</p>
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
        """, db_info=db_info, tables_html=tables_html)
    except Exception as e:
        database_info = os.environ.get('DATABASE_URL', '').split('@')[1] if '@' in os.environ.get('DATABASE_URL', '') else 'configurada'
        
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
                            <h4 class="mb-0">❌ Error de Conexión a PostgreSQL</h4>
                        </div>
                        <div class="card-body">
                            <p class="lead">No se ha podido conectar a la base de datos PostgreSQL en Neon.</p>
                            <p><strong>Conexión:</strong> {{ db_info }}</p>
                            
                            <div class="alert alert-danger">
                                {{ error }}
                            </div>
                            
                            <h5 class="mt-4">Soluciones posibles:</h5>
                            <ol>
                                <li>Verifica que la cadena de conexión DATABASE_URL en el archivo .env es correcta.</li>
                                <li>Asegúrate de que el módulo psycopg2-binary está instalado.</li>
                                <li>Comprueba si hay restricciones de IP o si necesitas VPN para acceder al servidor.</li>
                                <li>Verifica que las credenciales (usuario/contraseña) son correctas.</li>
                            </ol>
                            
                            <div class="mt-4">
                                <a href="/" class="btn btn-primary">Volver al Inicio</a>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
        """, db_info=database_info, error=str(e))

if __name__ == '__main__':
    if not is_second_run:
        print("\n=== Iniciando aplicación AM3.1 ===")
        print(f"Configuración: {os.getenv('FLASK_ENV', 'default')}")
        print(f"Escuchando en: http://localhost:{os.getenv('PORT', 5000)}")
    
    # Marcar que está ejecutándose para el reinicio
    os.environ['FLASK_RUN_FROM_RELOAD'] = '1'
    
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))