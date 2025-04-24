"""
Script alternativo para ejecutar la aplicación directamente
"""
import os
import sys
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Verificar DATABASE_URL
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("❌ ERROR: No se ha configurado DATABASE_URL en el archivo .env")
    print("   Configura la variable DATABASE_URL con la conexión a PostgreSQL")
    sys.exit(1)

# Verificar psycopg2
try:
    import psycopg2
    # Probar conexión a PostgreSQL
    print("Conectando a PostgreSQL...")
    start_time = time.time()
    conn = psycopg2.connect(database_url, connect_timeout=10)
    conn.close()
    elapsed = time.time() - start_time
    print(f"✅ Conexión exitosa ({elapsed:.2f}s)")
except ImportError:
    print("❌ Error: psycopg2 no está instalado")
    print("   Instala psycopg2-binary con: pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error al conectar a PostgreSQL: {e}")
    print("   Intenta ejecutar test_neon_connection.py primero para activar la base de datos")
    sys.exit(1)

# Crear aplicación Flask
app = Flask(__name__, 
            template_folder='app/templates', 
            static_folder='app/static')

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave_desarrollo_segura')

# Inicializar extensiones
db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# Importar modelos (después de inicializar db)
from app.models.cliente import Cliente
from app.models.proyecto import Proyecto
from app.models.presupuesto import Presupuesto, Capitulo, Partida
from app.models.proveedor import Proveedor
from app.models.hoja_trabajo import HojaTrabajo, CapituloHoja, PartidaHoja
from app.models.factura import Factura, LineaFactura

# Importar rutas
from app.routes import register_blueprints
register_blueprints(app)

# Página principal
@app.route('/')
def index():
    from flask import render_template
    return render_template('index.html')

# Ejecutar la aplicación
if __name__ == '__main__':
    print(f"\n=== Iniciando aplicación AM3.1 (modo directo) ===")
    print(f"Configuración: desarrollo directo")
    print(f"Escuchando en: http://localhost:{os.getenv('PORT', 5000)}")
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))