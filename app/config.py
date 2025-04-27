# app/config.py
import os
from pathlib import Path
import sys
import logging

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Obtener el directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Directorios importantes
STATIC_DIR = BASE_DIR / 'app' / 'static'
UPLOAD_DIR = STATIC_DIR / 'uploads'
TEMP_DIR = BASE_DIR / 'temp'
LOG_DIR = BASE_DIR / 'logs'
INSTANCE_DIR = BASE_DIR / 'instance'

# Asegurar que los directorios necesarios existan
def ensure_dirs_exist():
    """Crea los directorios necesarios para la aplicación"""
    for directory in [STATIC_DIR, UPLOAD_DIR, TEMP_DIR, LOG_DIR, INSTANCE_DIR]:
        directory.mkdir(exist_ok=True, parents=True)

# Aseguramos directorios al importar el módulo
ensure_dirs_exist()

class Config:
    """Configuración base para la aplicación."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave_predeterminada_segura_para_desarrollo'
    
    # Configuración de base de datos
    DB_PATH = os.environ.get('DB_PATH')
    if not DB_PATH:
        DB_PATH = str(BASE_DIR / 'instance' / 'app.db')
    elif not os.path.isabs(DB_PATH):
        # Si es una ruta relativa, hacerla absoluta relativa al BASE_DIR
        DB_PATH = str(BASE_DIR / DB_PATH)
    logger.info(f"Ruta de base de datos: {DB_PATH}")
    
    # Configuración común para SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración del pool de conexiones para SQLAlchemy
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,      # Verifica la conexión antes de usarla
        'pool_recycle': 1800,       # Recicla conexiones después de 30 minutos
        'pool_timeout': 30,         # Tiempo límite para obtener una conexión del pool
        'pool_size': 5,             # Tamaño del pool de conexiones
        'max_overflow': 10          # Máximo de conexiones adicionales
    }
    
    # URI de base de datos SQLite local
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    logger.info(f"Usando base de datos local: {SQLALCHEMY_DATABASE_URI}")
    
    # Parámetros de configuración específicos del sistema
    CONFIG = {
        'clientes_dir': os.environ.get('CLIENTES_DIR', os.path.join(os.path.expanduser('~'), 'Documentos', 'Clientes')),
        'logo_path': os.environ.get('LOGO_PATH', str(STATIC_DIR / 'img' / 'logo.jpg')),
        'report_templates': str(BASE_DIR / 'app' / 'templates' / 'reports'),
    }
    
    @staticmethod
    def init_app(app):
        # Configuración específica para la aplicación
        pass

class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo."""
    DEBUG = True
    
class ProductionConfig(Config):
    """Configuración para entorno de producción."""
    DEBUG = False
    
class TestingConfig(Config):
    """Configuración para entorno de pruebas."""
    TESTING = True
    # Para pruebas usamos una base de datos PostgreSQL de prueba
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or os.environ.get('DATABASE_URL')
    WTF_CSRF_ENABLED = False

# Configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Asegurar que exista el directorio de clientes
def ensure_client_dir_exists():
    """Crea el directorio de clientes si no existe"""
    client_dir = Path(Config.CONFIG['clientes_dir'])
    client_dir.mkdir(exist_ok=True, parents=True)

# Inicialización al importar el módulo
ensure_client_dir_exists()
