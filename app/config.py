# app/config.py
import os
from pathlib import Path
import sys
import time
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

# Asegurar que los directorios necesarios existan
def ensure_dirs_exist():
    """Crea los directorios necesarios para la aplicación"""
    for directory in [STATIC_DIR, UPLOAD_DIR, TEMP_DIR, LOG_DIR]:
        directory.mkdir(exist_ok=True, parents=True)

# Aseguramos directorios al importar el módulo
ensure_dirs_exist()

# Configuración para conexión PostgreSQL
POSTGRES_CONNECT_ARGS = {
    'connect_timeout': int(os.environ.get('DB_CONNECT_TIMEOUT', 10)),
    'keepalives': 1,
    'keepalives_idle': 60,     # Reducido para ser más agresivo
    'keepalives_interval': 10,  # Reducido para ser más agresivo
    'keepalives_count': 10,    # Aumentado para más reintentos
    'application_name': 'AM3.1'  # Identificador para la aplicación
}

# Verificación centralizada de conexión a PostgreSQL
def verify_postgres_connection(db_url, timeout=5):
    """
    Verifica la conexión a PostgreSQL y maneja errores apropiadamente.
    
    Args:
        db_url: URL de conexión PostgreSQL
        timeout: Tiempo máximo de espera para la conexión
        
    Returns:
        tuple: (éxito, mensaje)
    """
    try:
        import psycopg2
        # Ocultar credenciales en logs usando solo el host
        safe_url_info = db_url.split('@')[1] if '@' in db_url else 'configurada'
        
        # Configurar opciones de conexión para mayor robustez
        connect_args = {
            'connect_timeout': timeout,
            'keepalives': 1,
            'keepalives_idle': 60,  # TCP Keepalive después de 60s de inactividad
            'sslmode': 'require'
        }
        
        start_time = time.time()
        conn = psycopg2.connect(db_url, **connect_args)
        elapsed = time.time() - start_time
        # Verificar que la conexión funciona con una consulta simple
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
        conn.close()
        
        logger.info(f"Conexión exitosa a PostgreSQL ({elapsed:.2f}s)")
        return True, f"✅ Usando PostgreSQL: {safe_url_info}"
    except ImportError:
        logger.error("Módulo psycopg2 no instalado")
        return False, "❌ Error: psycopg2 no está instalado. Instala psycopg2-binary con: pip install psycopg2-binary"
    except Exception as e:
        logger.error(f"Error al conectar a PostgreSQL: {e}")
        return False, f"❌ Error al conectar a PostgreSQL: {e}"

class Config:
    """Configuración base para la aplicación."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave_predeterminada_segura_para_desarrollo'
    
    # Configuración de base de datos
    DATABASE_URL = os.environ.get('DATABASE_URL')
    DB_PATH = os.environ.get('DB_PATH') or str(BASE_DIR / 'instance' / 'app.db')
    
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
    
    # Determinar URI de base de datos - solo PostgreSQL compatible
    if DATABASE_URL:
        # Verificar si se requiere verificación explícita
        if os.environ.get('CHECK_DB_CONNECTION', 'false').lower() == 'true':
            success, message = verify_postgres_connection(DATABASE_URL)
            print(message)
            if not success:
                sys.exit(1)
        
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        # Añadir connect_args solo para PostgreSQL
        SQLALCHEMY_ENGINE_OPTIONS['connect_args'] = POSTGRES_CONNECT_ARGS
    else:
        print("❌ Error: No se ha configurado DATABASE_URL en el archivo .env")
        print("   La aplicación está configurada para usar SOLO PostgreSQL.")
        print("   Asegúrate de que DATABASE_URL esté correctamente definida en el archivo .env")
        sys.exit(1)
    
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
