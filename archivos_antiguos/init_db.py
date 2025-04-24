"""
Script para inicializar la base de datos.
"""
import os
from flask_migrate import Migrate, init, migrate, upgrade
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from app import create_app, db

app = create_app(os.getenv('FLASK_ENV', 'default'))

# Configurar Flask Migrate
migrate_instance = Migrate(app, db)

# Crear el contexto de aplicación
with app.app_context():
    # Inicializar la base de datos
    print("Inicializando la base de datos...")
    
    # Asegurarse de que existe el directorio para la base de datos
    db_dir = os.path.dirname(app.config['DB_PATH'])
    os.makedirs(db_dir, exist_ok=True)
    
    # Inicializar el repositorio de migraciones
    init()
    
    # Crear la migración inicial
    migrate(message="Migración inicial")
    
    # Aplicar la migración
    upgrade()
    
    print("Base de datos inicializada correctamente.")
