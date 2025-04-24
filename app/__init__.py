# app/__init__.py
import os
import sqlite3
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

from app.config import config

# Inicialización de extensiones
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_name='default'):
    """
    Crea y configura la aplicación Flask.
    
    Args:
        config_name: Nombre de la configuración a usar (default, development, production, testing)
        
    Returns:
        app: Aplicación Flask configurada
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Determinar tipo de base de datos
    using_postgres = 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']
    
    if using_postgres:
        print(f"✅ Usando PostgreSQL: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else 'configurada'}")
        
        # Configurar opciones específicas para PostgreSQL (timeout, pool, etc)
        postgres_uri = app.config['SQLALCHEMY_DATABASE_URI']
        
        # Personalizar el motor de SQLAlchemy para PostgreSQL con timeout
        engine = create_engine(
            postgres_uri,
            connect_args={
                "connect_timeout": 10,  # Timeout de conexión en segundos
                "application_name": "AM3.1",  # Identificador de la aplicación
            },
            poolclass=QueuePool,
            pool_size=5,  # Tamaño del pool de conexiones
            max_overflow=10,  # Máximo número de conexiones adicionales
            pool_timeout=30,  # Timeout para obtener una conexión del pool
            pool_recycle=1800,  # Reciclar conexiones después de 30 minutos
        )
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'engine': engine
        }
        
        # Verificar si la base de datos está en modo sleep
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
                print("✅ Conexión a PostgreSQL establecida correctamente")
        except Exception as e:
            print(f"⚠️ Error al conectar a PostgreSQL: {e}")
            print("La base de datos podría estar en modo sleep. Intente realizar una operación para activarla.")
    else:
        # Para SQLite, asegurar que existe el directorio de datos y el archivo de base de datos
        db_path = Path(app.config['DB_PATH'])
        os.makedirs(db_path.parent, exist_ok=True)
        
        # Verificar acceso a la base de datos SQLite antes de inicializar SQLAlchemy
        try:
            # Intentar crear/acceder al archivo de SQLite directamente
            sqlite_conn = sqlite3.connect(db_path)
            sqlite_conn.close()
            print(f"✅ Conexión a SQLite verificada: {db_path}")
        except Exception as e:
            print(f"❌ Error al conectar a SQLite: {e}")
            print(f"Intentando crear directorio: {db_path.parent}")
            try:
                # Intento más agresivo de crear el directorio y el archivo
                db_path.parent.mkdir(parents=True, exist_ok=True)
                # Intentar crear el archivo manualmente
                with open(db_path, 'a'):
                    pass
                print(f"✅ Archivo de base de datos creado manualmente")
            except Exception as e:
                print(f"❌ Error al crear archivo de base de datos: {e}")
    
    # Inicializar extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Añadir funciones útiles a los globales de Jinja2
    app.jinja_env.globals['hasattr'] = hasattr
    
    # Filtro personalizado para sanitizar HTML
    def sanitize_html(text):
        if text is None:
            return ''
        import re
        return re.sub(r'<[^>]*>', '', text)
    
    app.jinja_env.filters['sanitize_html'] = sanitize_html
    
    # Inicializar la base de datos dentro del contexto de la aplicación
    with app.app_context():
        try:
            # Importar todos los modelos para asegurar que SQLAlchemy los conozca
            from app.models.cliente import Cliente
            from app.models.proyecto import Proyecto
            from app.models.presupuesto import Presupuesto, Capitulo, Partida
            from app.models.proveedor import Proveedor
            from app.models.hoja_trabajo import HojaTrabajo, CapituloHoja, PartidaHoja
            from app.models.factura import Factura, LineaFactura
            
            # Crear todas las tablas
            db.create_all()
            print("✅ Tablas de base de datos creadas correctamente")
            
            # Verificar las tablas creadas
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            created_tables = inspector.get_table_names()
            
            print("Tablas verificadas en la base de datos:")
            for table in created_tables:
                print(f" - {table}")
        except Exception as e:
            print(f"❌ Error al crear tablas: {e}")
            if using_postgres:
                print("🔄 La base de datos PostgreSQL podría estar en modo sleep.")
                print("   Espere un momento e intente nuevamente para activarla.")
    
    # Registrar blueprints
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # Página de inicio
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Manejador de error 404
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    # Manejador de error 500
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    return app