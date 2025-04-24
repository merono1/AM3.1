# fix_clientes_table.py
import os
import sqlite3
from datetime import datetime
from pathlib import Path

# Cargar variables de entorno desde .env
from dotenv import load_dotenv
load_dotenv()

# Ruta a la base de datos
DB_PATH = os.environ.get('DB_PATH', 'app/data/app.db')
print(f"Usando base de datos en: {os.path.abspath(DB_PATH)}")

def verificar_tablas():
    """Verifica las tablas existentes en la base de datos."""
    try:
        # Asegurar que el directorio existe
        db_dir = Path(DB_PATH).parent
        os.makedirs(db_dir, exist_ok=True)
        
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = cursor.fetchall()
        
        print("Tablas encontradas en la base de datos:")
        for tabla in tablas:
            print(f"- {tabla[0]}")
        
        # Verificar si existe la tabla clientes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clientes'")
        existe_clientes = cursor.fetchone() is not None
        
        if existe_clientes:
            print("\n✅ La tabla 'clientes' existe.")
        else:
            print("\n❌ La tabla 'clientes' NO existe.")
        
        conn.close()
        return tablas, existe_clientes
    
    except Exception as e:
        print(f"Error al verificar tablas: {str(e)}")
        return [], False

def crear_tabla_clientes():
    """Crea la tabla clientes si no existe."""
    try:
        # Crear copia de seguridad antes
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join('app', 'data', f'app_backup_{timestamp}.db')
        
        # Verificar si el archivo existe antes de hacer backup
        if os.path.exists(DB_PATH):
            print(f"Creando copia de seguridad en {backup_path}...")
            with open(DB_PATH, 'rb') as source:
                with open(backup_path, 'wb') as dest:
                    dest.write(source.read())
        
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Crear la tabla clientes
        print("Creando tabla 'clientes'...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo_via TEXT,
            nombre_via TEXT,
            numero_via TEXT,
            puerta TEXT,
            codigo_postal TEXT,
            poblacion TEXT,
            cif_nif TEXT,
            telefono1 TEXT,
            telefono2 TEXT,
            telefono3 TEXT,
            telefono4 TEXT,
            mail1 TEXT,
            mail2 TEXT,
            tipo_cliente TEXT,
            categoria_cliente TEXT,
            notas TEXT,
            fecha_creacion TIMESTAMP,
            fecha_modificacion TIMESTAMP
        )
        ''')
        
        # Confirmar los cambios
        conn.commit()
        
        # Verificar que la tabla se creó
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clientes'")
        existe_clientes = cursor.fetchone() is not None
        
        conn.close()
        
        if existe_clientes:
            print("✅ Tabla 'clientes' creada correctamente.")
            return True
        else:
            print("❌ No se pudo crear la tabla 'clientes'.")
            return False
        
    except Exception as e:
        print(f"Error al crear tabla clientes: {str(e)}")
        return False

if __name__ == "__main__":
    # Verificar las tablas existentes
    tablas, existe_clientes = verificar_tablas()
    
    # Si no existe la tabla clientes, crearla
    if not existe_clientes:
        if crear_tabla_clientes():
            print("\nOperación completada con éxito. La tabla 'clientes' ha sido creada.")
        else:
            print("\nNo se pudo completar la operación.")
    else:
        print("\nNo es necesario crear la tabla 'clientes' porque ya existe.")