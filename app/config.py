# app/config.py
import os
from pathlib import Path

# Obtener el directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    """Configuración base para la aplicación."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave_predeterminada_segura_para_desarrollo'
    
    # Configuración de base de datos
    # Prioridad a PostgreSQL si está configurado, sino usar SQLite
    DATABASE_URL = os.environ.get('DATABASE_URL')
    DB_PATH = os.environ.get('DB_PATH') or str(BASE_DIR / 'app' / 'data' / 'app.db')
    
    # Usar PostgreSQL si está configurado, sino usar SQLite
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de timeouts para PostgreSQL
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_timeout': 30,  # 30 segundos
        'pool_recycle': 1800,  # 30 minutos
        'pool_pre_ping': True,  # Verificación de conexión antes de usarla
        'pool_size': 5,  # Tamaño del pool
        'max_overflow': 10,  # Conexiones adicionales si es necesario
        'connect_args': {
            'connect_timeout': 10,  # 10 segundos para timeout de conexión
            'application_name': 'AM3.1'  # Nombre de la aplicación en el servidor
        }
    }
    
    # Asegurar que el directorio de la base de datos existe
    @staticmethod
    def init_app(app):
        db_dir = Path(app.config['DB_PATH']).parent
        db_dir.mkdir(exist_ok=True)
    
class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo."""
    DEBUG = True
    
    # En desarrollo, usar SQLite por defecto si no hay DATABASE_URL
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        print(f"🔧 Modo desarrollo: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
class ProductionConfig(Config):
    """Configuración para entorno de producción."""
    DEBUG = False
    
    # Configuraciones específicas para producción
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_timeout': 60,  # Timeout más largo en producción
        'pool_recycle': 3600,  # Reciclar conexiones cada hora
        'pool_pre_ping': True,
        'pool_size': 10,  # Mayor pool en producción
        'max_overflow': 20,
        'connect_args': {
            'connect_timeout': 15,
            'application_name': 'AM3.1-Production'
        }
    }
    
    # En producción, recomendar usar PostgreSQL
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        if not app.config.get('DATABASE_URL'):
            print("⚠️ Advertencia: Se recomienda usar PostgreSQL en producción")
        print(f"🔧 Modo producción: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
class TestingConfig(Config):
    """Configuración para entorno de pruebas."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}