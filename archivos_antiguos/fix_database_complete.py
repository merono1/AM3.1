# fix_database_complete.py
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

# Configuración básica
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.environ.get('DB_PATH') or str(BASE_DIR / 'app' / 'data' / 'app.db')
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"

print("=== Diagnóstico y Reparación de Base de Datos ===")
print(f"Ruta actual de la base de datos: {DB_PATH}")

# Hacer una copia de seguridad de la base de datos si existe
def backup_database():
    if os.path.exists(DB_PATH):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(os.path.dirname(DB_PATH), f'app_backup_{timestamp}.db')
        try:
            shutil.copy2(DB_PATH, backup_path)
            print(f"✅ Copia de seguridad creada en: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Error al crear copia de seguridad: {e}")
            return None
    return None

# Verificar el estado actual de la base de datos
def check_database_state():
    try:
        # Verificar si el archivo existe
        if not os.path.exists(DB_PATH):
            print(f"❌ La base de datos no existe en la ruta: {DB_PATH}")
            db_directory = Path(DB_PATH).parent
            os.makedirs(db_directory, exist_ok=True)
            print(f"✅ Directorio creado: {db_directory}")
            return False, []
        
        # Verificar si se puede conectar
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]
            conn.close()
            
            print("Tablas encontradas en la base de datos:")
            if tables:
                for table in tables:
                    print(f" - {table}")
            else:
                print(" - No se encontraron tablas")
            
            required_tables = ['clientes', 'proyectos', 'presupuestos', 'capitulos', 'partidas', 
                              'proveedores', 'hojas_trabajo', 'capitulos_hoja', 'partidas_hoja',
                              'facturas', 'lineas_factura']
            
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print("\nTablas requeridas que faltan:")
                for table in missing_tables:
                    print(f" - {table}")
                return False, tables
            
            return True, tables
            
        except Exception as e:
            print(f"❌ Error al conectar a la base de datos: {e}")
            return False, []
            
    except Exception as e:
        print(f"❌ Error al verificar la base de datos: {e}")
        return False, []

# Recrear la base de datos desde cero
def recreate_database():
    try:
        # Crear la aplicación Flask y configurarla
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Inicializar SQLAlchemy
        db = SQLAlchemy(app)
        
        # Importar todos los modelos
        from app.models.cliente import Cliente
        from app.models.proyecto import Proyecto
        from app.models.presupuesto import Presupuesto, Capitulo, Partida
        from app.models.proveedor import Proveedor
        from app.models.hoja_trabajo import HojaTrabajo, CapituloHoja, PartidaHoja
        from app.models.factura import Factura, LineaFactura
        
        # Crear todas las tablas
        with app.app_context():
            db.create_all()
            
            # Verificar las tablas creadas
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            created_tables = inspector.get_table_names()
            
            print("\nTablas creadas correctamente:")
            for table in created_tables:
                print(f" - {table}")
            
            return True, created_tables
            
    except Exception as e:
        print(f"❌ Error al recrear la base de datos: {e}")
        return False, []

# Proceso principal
def main():
    # Paso 1: Verificar el estado actual
    db_ok, current_tables = check_database_state()
    
    if db_ok:
        print("\n✅ La base de datos parece estar en buen estado.")
        choice = input("¿Desea recrear la base de datos de todos modos? (s/N): ").lower()
        if choice != 's':
            print("Operación cancelada. No se realizaron cambios.")
            return
    
    # Paso 2: Hacer copia de seguridad
    backup_path = backup_database()
    
    # Paso 3: Recrear la base de datos
    print("\nRecreando la base de datos...")
    success, created_tables = recreate_database()
    
    if success:
        print("\n✅ Base de datos recreada exitosamente.")
        if backup_path:
            print(f"Se ha guardado una copia de seguridad en: {backup_path}")
    else:
        print("\n❌ Error al recrear la base de datos.")
        if backup_path:
            restore = input(f"¿Desea restaurar desde la copia de seguridad? (s/N): ").lower()
            if restore == 's':
                try:
                    shutil.copy2(backup_path, DB_PATH)
                    print(f"✅ Base de datos restaurada desde: {backup_path}")
                except Exception as e:
                    print(f"❌ Error al restaurar la copia de seguridad: {e}")

if __name__ == "__main__":
    main()
