"""
Una versión simplificada de la aplicación para pruebas.
"""
import os
import sqlite3
from flask import Flask, render_template, render_template_string, flash
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
load_dotenv()

# Crear una aplicación Flask simple
app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')

# Configuración básica
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave_de_prueba')
app.config['DEBUG'] = True

# Verificar conexión a la base de datos
DB_PATH = os.environ.get('DB_PATH', 'app/data/app.db')
db_dir = Path(DB_PATH).parent
os.makedirs(db_dir, exist_ok=True)

# Verificar que se puede acceder a la base de datos
@app.route('/check_db')
def check_db():
    try:
        # Intentar conectarse a la base de datos
        conn = sqlite3.connect(DB_PATH)
        conn.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)')
        conn.close()
        return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Verificación de Base de Datos</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body class="bg-light">
                <div class="container py-5">
                    <div class="card shadow">
                        <div class="card-body text-center">
                            <h1 class="card-title text-success">✅ Conexión a Base de Datos Exitosa</h1>
                            <p class="lead">Se ha conectado correctamente a la base de datos SQLite.</p>
                            <p>Ruta: {{ db_path }}</p>
                            <a href="/" class="btn btn-primary mt-3">Volver al Inicio</a>
                        </div>
                    </div>
                </div>
            </body>
            </html>
        """, db_path=DB_PATH)
    except Exception as e:
        return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error de Base de Datos</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body class="bg-light">
                <div class="container py-5">
                    <div class="card shadow">
                        <div class="card-body text-center">
                            <h1 class="card-title text-danger">❌ Error de Conexión a Base de Datos</h1>
                            <p class="lead">No se ha podido conectar a la base de datos SQLite.</p>
                            <p>Ruta: {{ db_path }}</p>
                            <div class="alert alert-danger">
                                {{ error }}
                            </div>
                            <h3>Soluciones posibles:</h3>
                            <ul class="text-start">
                                <li>Asegúrate de que el directorio <code>app/data</code> existe y tiene permisos de escritura.</li>
                                <li>Verifica que la variable <code>DB_PATH</code> en el archivo <code>.env</code> es correcta.</li>
                                <li>Si estás usando Windows, prueba ejecutar la aplicación como administrador.</li>
                            </ul>
                            <a href="/" class="btn btn-primary mt-3">Volver al Inicio</a>
                        </div>
                    </div>
                </div>
            </body>
            </html>
        """, db_path=DB_PATH, error=str(e))

# Ruta principal
@app.route('/')
def index():
    try:
        return render_template('home.html')
    except Exception as e:
        return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>AM3.1 - Bienvenido</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body class="bg-light">
                <div class="container py-5">
                    <div class="card shadow">
                        <div class="card-body">
                            <h1 class="card-title">AM3.1 - Sistema de Gestión</h1>
                            <p class="lead">La aplicación está funcionando en modo de prueba.</p>
                            
                            <div class="alert alert-warning">
                                <strong>Advertencia:</strong> No se pudo cargar la plantilla principal.
                                <br>Error: {{ error }}
                            </div>
                            
                            <h2>Herramientas de diagnóstico:</h2>
                            <div class="d-grid gap-2">
                                <a href="/test" class="btn btn-primary">Verificar Estructura del Proyecto</a>
                                <a href="/check_db" class="btn btn-info">Verificar Conexión a Base de Datos</a>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
        """, error=str(e))

# Página de prueba
@app.route('/test')
def test():
    try:
        # Verificar la estructura del proyecto
        app_dir = Path(__file__).parent / 'app'
        
        checks = {
            "Estructura general": os.path.isdir(app_dir),
            "Módulo de modelos": os.path.isdir(app_dir / 'models'),
            "Módulo de rutas": os.path.isdir(app_dir / 'routes'),
            "Módulo de servicios": os.path.isdir(app_dir / 'services'),
            "Plantillas": os.path.isdir(app_dir / 'templates'),
            "Archivos estáticos": os.path.isdir(app_dir / 'static'),
            "Archivo de configuración": os.path.isfile(app_dir / 'config.py')
        }
        
        return render_template_string(get_test_template(checks))
    except Exception as e:
        return f"Error en la página de prueba: {str(e)}"

def get_test_template(checks):
    """Genera una plantilla HTML con los resultados de las verificaciones."""
    results = ""
    all_passed = all(checks.values())
    
    for name, passed in checks.items():
        status = "✅ Correcto" if passed else "❌ Error"
        color = "text-success" if passed else "text-danger"
        results += f'<li><span class="{color}">{status}</span>: {name}</li>\n'
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AM3.1 - Verificación de Estructura</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container py-5">
            <div class="card shadow">
                <div class="card-body">
                    <h1 class="card-title">Verificación de Estructura AM3.1</h1>
                    <div class="alert {'alert-success' if all_passed else 'alert-warning'}">
                        {'✅ Todos los componentes están correctamente estructurados.' if all_passed else '⚠️ Hay problemas con algunos componentes.'}
                    </div>
                    <h2>Resultados:</h2>
                    <ul>
                        {results}
                    </ul>
                    <p>Esta página verifica que la estructura básica del proyecto sea correcta.</p>
                    <div class="mt-3 d-grid gap-2">
                        <a href="/" class="btn btn-primary">Volver al Inicio</a>
                        <a href="/check_db" class="btn btn-info">Verificar Conexión a Base de Datos</a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    print(f"Iniciando aplicación en modo de prueba...")
    print(f"Base de datos: {DB_PATH}")
    print(f"Accede a http://localhost:{os.environ.get('PORT', 5000)}")
    print(f"URL de diagnóstico: http://localhost:{os.environ.get('PORT', 5000)}/test")
    print(f"Verificación de BD: http://localhost:{os.environ.get('PORT', 5000)}/check_db")
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
