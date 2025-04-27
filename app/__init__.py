import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
import sys
from pathlib import Path

from app.config import config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialización de extensiones con opciones optimizadas para SQLite
db = SQLAlchemy(engine_options={
    'pool_pre_ping': True,     # Verifica la conexión antes de usarla
    'pool_recycle': 3600,      # Recicla conexiones después de 1 hora
    'pool_size': 5,            # Tamaño del pool para SQLite
    'echo': False,            # Desactiva el logging de SQL para mejorar rendimiento
    'echo_pool': False        # Desactiva el logging de pool para mejorar rendimiento
})
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
    
    # Aplicar optimizaciones ANTES de usar la BD
    # IMPORTANTE: Debe estar dentro del app context
    with app.app_context():
        from app.services.db_service import setup_db_optimizations
        setup_db_optimizations(app)
    
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
            logger.info("Tablas de base de datos creadas correctamente")
            
            # Verificar las tablas creadas
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            created_tables = inspector.get_table_names()
            
            logger.info("Tablas verificadas en la base de datos:")
            for table in created_tables:
                logger.info(f" - {table}")
        except Exception as e:
            logger.error(f"Error al crear tablas: {e}")
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