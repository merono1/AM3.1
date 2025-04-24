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