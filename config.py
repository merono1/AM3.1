"""
Configuración centralizada para rutas y variables de entorno.
Este archivo contiene todas las configuraciones de rutas y ubicaciones
para asegurar que la aplicación funcione correctamente en diferentes equipos.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Determinar la ruta base de la aplicación
def get_base_dir():
    """Obtiene el directorio base de la aplicación de forma robusta"""
    if getattr(sys, 'frozen', False):
        # Si es una aplicación empaquetada (PyInstaller)
        return Path(sys.executable).parent
    else:
        # Si es código fuente
        return Path(__file__).resolve().parent

# Directorio base de la aplicación
BASE_DIR = get_base_dir()

# Configuración de la base de datos
DB_TYPE = "sqlite" if os.environ.get('DATABASE_URL') is None else "postgres"
DB_PATH = os.environ.get('DB_PATH', os.path.join(BASE_DIR, 'app', 'data', 'app.db'))
DATABASE_URL = os.environ.get('DATABASE_URL')

# Asegurar que el directorio de la base de datos SQLite exista
def ensure_db_dir_exists():
    """Crea el directorio para la base de datos SQLite si no existe"""
    if DB_TYPE == "sqlite":
        db_dir = Path(DB_PATH).parent
        os.makedirs(db_dir, exist_ok=True)
        return db_dir
    return None

# Rutas para archivos estáticos
STATIC_DIR = os.path.join(BASE_DIR, 'app', 'static')
UPLOAD_DIR = os.path.join(STATIC_DIR, 'uploads')
TEMP_DIR = os.path.join(BASE_DIR, 'temp')
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Asegurar que existan los directorios necesarios
def ensure_dirs_exist():
    """Crea los directorios necesarios para la aplicación"""
    for directory in [STATIC_DIR, UPLOAD_DIR, TEMP_DIR, LOG_DIR]:
        os.makedirs(directory, exist_ok=True)

# Configuración del entorno de la aplicación
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
DEBUG = FLASK_ENV == 'development'
PORT = int(os.environ.get('PORT', 5000))
SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_secreta_predeterminada')

# Parámetros de configuración específicos del sistema
CONFIG = {
    'clientes_dir': os.environ.get('CLIENTES_DIR', os.path.join(os.path.expanduser('~'), 'Documentos', 'Clientes')),
    'logo_path': os.environ.get('LOGO_PATH', os.path.join(STATIC_DIR, 'img', 'logo.jpg')),
    'report_templates': os.path.join(BASE_DIR, 'app', 'templates', 'reports'),
}

# Asegurar que exista el directorio de clientes
def ensure_client_dir_exists():
    """Crea el directorio de clientes si no existe"""
    os.makedirs(CONFIG['clientes_dir'], exist_ok=True)

# Inicialización al importar el módulo
ensure_dirs_exist()
ensure_client_dir_exists()
db_dir = ensure_db_dir_exists()

# Función para obtener rutas absolutas
def get_abs_path(relative_path):
    """Convierte una ruta relativa a absoluta desde BASE_DIR"""
    if os.path.isabs(relative_path):
        return relative_path
    return os.path.join(BASE_DIR, relative_path)
