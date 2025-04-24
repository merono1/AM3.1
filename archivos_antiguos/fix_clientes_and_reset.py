# fix_clientes_and_reset.py
import os
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DB_PATH = os.environ.get('DB_PATH', 'app/data/app.db')
print(f"Usando base de datos en: {os.path.abspath(DB_PATH)}")

def backup_database():
    """Crea una copia de seguridad de la base de datos actual."""
    if os.path.exists(DB_PATH):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{os.path.splitext(DB_PATH)[0]}_backup_{timestamp}.db"
        try:
            shutil.copy2(DB_PATH, backup_path)
            print(f"✅ Copia de seguridad creada en: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Error al crear copia de seguridad: {e}")
    else:
        print("⚠️ No existe archivo de base de datos para hacer copia de seguridad.")
    
    return None

def check_tables():
    """Verifica las tablas existentes en la base de datos."""
    try:
        # Verificar si el archivo existe
        if not os.path.exists(DB_PATH):
            print(f"❌ El archivo de base de datos no existe en: {DB_PATH}")
            return False, []
        
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        conn.close()
        
        print("Tablas existentes en la base de datos:")
        for table in tables:
            print(f" - {table}")
        
        return len(tables) > 0, tables
    
    except Exception as e:
        print(f"❌ Error al verificar tablas: {e}")
        return False, []

def drop_all_tables():
    """Elimina todas las tablas de la base de datos."""
    try:
        # Verificar si el archivo existe
        if not os.path.exists(DB_PATH):
            print(f"❌ El archivo de base de datos no existe en: {DB_PATH}")
            return False
        
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        
        # Desactivar restricciones de clave foránea
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Eliminar cada tabla
        for table in tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"✅ Tabla '{table}' eliminada")
            except Exception as e:
                print(f"❌ Error al eliminar tabla '{table}': {e}")
        
        # Activar restricciones de clave foránea
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Confirmar cambios
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"❌ Error al eliminar tablas: {e}")
        return False

def initialize_database():
    """Inicializa la base de datos con todas las tablas usando SQLAlchemy."""
    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        
        # Crear la aplicación
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Inicializar SQLAlchemy
        db = SQLAlchemy(app)
        
        # Importar todos los modelos
        try:
            print("Importando modelos...")
            # Esto es importante para que SQLAlchemy conozca los modelos
            from app.models.cliente import Cliente
            from app.models.proyecto import Proyecto
            from app.models.presupuesto import Presupuesto, Capitulo, Partida
            from app.models.proveedor import Proveedor
            from app.models.hoja_trabajo import HojaTrabajo, CapituloHoja, PartidaHoja
            from app.models.factura import Factura, LineaFactura
            print("✅ Modelos importados correctamente")
        except Exception as e:
            print(f"❌ Error al importar modelos: {e}")
            return False
        
        # Crear todas las tablas
        with app.app_context():
            try:
                db.create_all()
                print("✅ Tablas creadas correctamente")
                
                # Listar las tablas creadas
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                created_tables = inspector.get_table_names()
                
                print("\nTablas creadas:")
                for table in created_tables:
                    print(f" - {table}")
                
                return True
            except Exception as e:
                print(f"❌ Error al crear tablas: {e}")
                return False
    
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        return False

def main():
    print("===== REPARACIÓN DE BASE DE DATOS =====")
    
    # Verificar la estructura de directorios
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        print(f"Creando directorio para la base de datos: {db_dir}")
        os.makedirs(db_dir, exist_ok=True)
    
    # Verificar tablas actuales
    tables_exist, tables = check_tables()
    
    # Determinar si la tabla clientes existe
    clientes_exists = 'clientes' in tables
    
    if clientes_exists:
        print("✅ La tabla 'clientes' existe en la base de datos.")
        choice = input("¿Desea reinicializar completamente la base de datos? (s/N): ").lower()
        if choice != 's':
            print("No se realizaron cambios.")
            return
    else:
        print("❌ La tabla 'clientes' NO existe en la base de datos.")
        print("Se procederá a reinicializar la base de datos.")
    
    # Crear copia de seguridad
    backup_path = backup_database()
    
    # Eliminar todas las tablas
    if tables_exist:
        print("\nEliminando todas las tablas existentes...")
        if not drop_all_tables():
            print("❌ Error al eliminar tablas, abortando.")
            return
    
    # Inicializar base de datos
    print("\nCreando nuevas tablas con SQLAlchemy...")
    if initialize_database():
        print("\n✅ Base de datos inicializada correctamente.")
        if backup_path:
            print(f"Se ha creado una copia de seguridad en: {backup_path}")
    else:
        print("\n❌ Error al inicializar la base de datos.")
        if backup_path:
            restore = input(f"¿Desea restaurar la copia de seguridad? (s/N): ").lower()
            if restore == 's':
                try:
                    shutil.copy2(backup_path, DB_PATH)
                    print(f"✅ Base de datos restaurada desde: {backup_path}")
                except Exception as e:
                    print(f"❌ Error al restaurar: {e}")

if __name__ == "__main__":
    main()
