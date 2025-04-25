"""
Script para crear las tablas de la base de datos directamente.
"""
import os
import sqlite3
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
load_dotenv()

# Configuración básica
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.environ.get('DB_PATH') or str(BASE_DIR / 'app' / 'data' / 'app.db')
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"

# Asegurarse de que el directorio de la base de datos existe
db_directory = Path(DB_PATH).parent
os.makedirs(db_directory, exist_ok=True)

# Probar conexión directa a SQLite para verificar permisos
print(f"Comprobando permisos de escritura en: {DB_PATH}")
try:
    conn = sqlite3.connect(DB_PATH)
    conn.close()
    print("✅ Prueba de conexión a SQLite exitosa")
except Exception as e:
    print(f"❌ Error conectando directamente a SQLite: {e}")
    print("Intentando resolver problema de permisos...")
    # Intentar crear un archivo vacío
    try:
        with open(DB_PATH, 'w') as f:
            pass
        print(f"✅ Archivo de base de datos creado manualmente en: {DB_PATH}")
    except Exception as e:
        print(f"❌ No se pudo crear el archivo manualmente: {e}")
        exit(1)

# Ahora que hemos verificado la conexión, importamos Flask y SQLAlchemy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Crear una aplicación básica
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DB_PATH'] = DB_PATH

# Inicializar la base de datos
db = SQLAlchemy(app)

# Importar modelos
try:
    print("Importando modelos...")
    from app.models.cliente import Cliente
    from app.models.proyecto import Proyecto
    from app.models.presupuesto import Presupuesto, Capitulo, Partida
    from app.models.proveedor import Proveedor
    from app.models.hoja_trabajo import HojaTrabajo, CapituloHoja, PartidaHoja
    from app.models.factura import Factura, LineaFactura
    print("✅ Modelos importados correctamente")
    
    # Asegurarse de que todas las columnas necesarias estén definidas en los modelos
    # Nota: Esto es muy importante para evitar problemas con la migración y la creación de tablas
    print("Verificando atributos en modelos...")
    # Las columnas estado_workflow, tipo_via y numero deben existir en sus respectivos modelos
    if not hasattr(Presupuesto, 'estado_workflow'):
        print("⚠️ La columna 'estado_workflow' no está definida en el modelo Presupuesto.")
    if not hasattr(Proyecto, 'tipo_via'):
        print("⚠️ La columna 'tipo_via' no está definida en el modelo Proyecto.")
    if not hasattr(Partida, 'numero'):
        print("⚠️ La columna 'numero' no está definida en el modelo Partida.")
    print("✅ Verificación de atributos completada")
except Exception as e:
    print(f"❌ Error al importar modelos: {e}")
    exit(1)

# Crear el contexto de aplicación
with app.app_context():
    # Crear las tablas directamente
    print("Creando tablas de la base de datos...")
    try:
        db.create_all()
        print("✅ Tablas creadas correctamente.")
        
        # Mostrar información de las tablas creadas
        print("\nTablas creadas:")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        for table_name in inspector.get_table_names():
            print(f" - {table_name}")
            
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        exit(1)
        
if __name__ == "__main__":
    print("\n✅ ¡Base de datos inicializada con éxito!")
    print(f"Ruta de la base de datos: {DB_PATH}")
