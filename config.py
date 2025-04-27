"""
ARCHIVO DEPRECADO: 
Este archivo ha sido reemplazado por app/config.py para centralizar la configuración.
Se mantiene temporalmente para compatibilidad con código existente.
"""
import warnings
import os
from pathlib import Path
from app.config import BASE_DIR, STATIC_DIR, UPLOAD_DIR, TEMP_DIR, LOG_DIR
from app.config import ensure_dirs_exist, ensure_client_dir_exists

# Mostrar advertencia de deprecación
warnings.warn(
    "El archivo config.py en la raíz está deprecado. Utiliza app/config.py en su lugar.",
    DeprecationWarning, 
    stacklevel=2
)

# Re-exportar variables y funciones de app/config.py para mantener compatibilidad
from app.config import Config

# Configuración del entorno de la aplicación
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
DEBUG = FLASK_ENV == 'development'
PORT = int(os.environ.get('PORT', 5000))
SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_secreta_predeterminada')

# Función para obtener rutas absolutas
def get_abs_path(relative_path):
    """Convierte una ruta relativa a absoluta desde BASE_DIR"""
    if os.path.isabs(relative_path):
        return relative_path
    return os.path.join(BASE_DIR, relative_path)
