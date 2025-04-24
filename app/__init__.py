import os
import sqlite3
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from pathlib import Path
import sys

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
    
    # Verifica si usamos PostgreSQL
    using_postgres = 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']
    
    if using_postgres:
        print(f"✅ Usando PostgreSQL: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else 'configurada'}")
        
        # Verificar conexión a PostgreSQL antes de inicializar SQLAlchemy
        try:
            import psycopg2
            # Extraer datos de la URI de SQLAlchemy
            pg_uri = app.config['SQLALCHEMY_DATABASE_URI']
            pg_uri = pg_uri.replace('postgresql://', '')
            user_pass, host_db = pg_uri.split('@', 1)
            host, db = host_db.split('/', 1)
            user, password = user_pass.split(':', 1)
            
            # Conectar con un timeout de 15 segundos
            print("Conectando a PostgreSQL (timeout: 15s)...")
            conn = psycopg2.connect(
                dbname=db,
                user=user,
                password=password,
                host=host,
                connect_timeout=15
            )
            conn.close()
            print("✅ Conexión a PostgreSQL verificada")
        except ImportError:
            print("❌ Error: psycopg2 no está instalado")
            print("   Instala psycopg2-binary con: pip install psycopg2-binary")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error al conectar a PostgreSQL: {e}")
            print("   La aplicación está configurada para usar únicamente PostgreSQL.")
            print("   Verifica que la base de datos en Neon esté activa y las credenciales sean correctas.")
            print("   Si el problema persiste, contacta al soporte de Neon.")
            sys.exit(1)
    else:
        # La aplicación debe usar PostgreSQL exclusivamente
        print("❌ Error: La aplicación está configurada para usar únicamente PostgreSQL")
        print("   Configura DATABASE_URL en el archivo .env")
        sys.exit(1)
    
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
            print("   Verifica que la base de datos esté correctamente configurada.")
            sys.exit(1)
    
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