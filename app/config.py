# app/config.py
import os
from pathlib import Path
import sys
import time

# Control de duplicación de mensajes
CONNECTION_VERIFIED = False
DB_INFO_PRINTED = False

# Obtener el directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    """Configuración base para la aplicación."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave_predeterminada_segura_para_desarrollo'
    
    # Configuración de base de datos
    DATABASE_URL = os.environ.get('DATABASE_URL')
    DB_PATH = os.environ.get('DB_PATH') or str(BASE_DIR / 'app' / 'data' / 'app.db')
    ENABLE_SQLITE_FALLBACK = os.environ.get('ENABLE_SQLITE_FALLBACK', 'false').lower() == 'true'
    
    # Determinar URI de base de datos
    if DATABASE_URL:
        # Configurar para usar PostgreSQL
        try:
            # Importar psycopg2 para verificar que está instalado
            import psycopg2
            
            # Verificar conexión SOLO si estamos en modo verbose y es la primera vez
            global CONNECTION_VERIFIED
            if os.environ.get('CHECK_DB_CONNECTION', 'false').lower() == 'true' and not CONNECTION_VERIFIED:
                print(f"Verificando conexión a PostgreSQL...")
                start_time = time.time()
                conn = psycopg2.connect(DATABASE_URL, connect_timeout=5)
                elapsed = time.time() - start_time
                print(f"✅ Conexión exitosa a PostgreSQL ({elapsed:.2f}s)")
                conn.close()
                # Marcar que ya verificamos la conexión
                CONNECTION_VERIFIED = True
            
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
            # Solo imprimir mensaje si no se ha verificado antes
            global DB_INFO_PRINTED
            if not DB_INFO_PRINTED:
                print(f"✅ Usando PostgreSQL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configurada'}")
                DB_INFO_PRINTED = True
        except Exception as e:
            # Si fallback está habilitado, usar SQLite
            if ENABLE_SQLITE_FALLBACK:
                print(f"⚠️ Error al conectar a PostgreSQL: {e}")
                print(f"⚠️ Usando SQLite como fallback: {DB_PATH}")
                SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
            else:
                print(f"❌ Error al conectar a PostgreSQL: {e}")
                print("Si quieres habilitar el fallback a SQLite, configura ENABLE_SQLITE_FALLBACK=true en .env")
                sys.exit(1)
    else:
        # Usar SQLite directamente
        print(f"✅ Usando SQLite: {DB_PATH}")
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def init_app(app):
        # Asegurar que el directorio existe para SQLite
        if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
            db_dir = Path(app.config.get('DB_PATH', 'app/data/app.db')).parent
            db_dir.mkdir(exist_ok=True)
    
class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo."""
    DEBUG = True
    
class ProductionConfig(Config):
    """Configuración para entorno de producción."""
    DEBUG = False
    
class TestingConfig(Config):
    """Configuración para entorno de pruebas."""
    TESTING = True
    # Para pruebas, puede usar SQLite en memoria
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}