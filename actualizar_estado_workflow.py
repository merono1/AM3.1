# actualizar_estado_workflow.py
import os
import sqlite3
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
import sys

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de la base de datos
DB_PATH = os.environ.get('DB_PATH', 'app/data/app.db')
print(f"Ruta de la base de datos: {DB_PATH}")

def verificar_columna_workflow():
    """Verifica si la columna estado_workflow existe en la tabla presupuestos."""
    try:
        # Establecer conexión directa con SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Consultar información del esquema de la tabla presupuestos
        cursor.execute("PRAGMA table_info(presupuestos)")
        columnas = cursor.fetchall()
        
        # Buscar si existe la columna estado_workflow
        existe_columna = any(col[1] == 'estado_workflow' for col in columnas)
        
        conn.close()
        
        return existe_columna
    except Exception as e:
        print(f"Error al verificar la columna: {e}")
        return False

def agregar_columna_workflow():
    """Agrega la columna estado_workflow a la tabla presupuestos si no existe."""
    try:
        # Establecer conexión directa con SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Agregar la columna si no existe
        cursor.execute("ALTER TABLE presupuestos ADD COLUMN estado_workflow TEXT DEFAULT 'En estudio'")
        conn.commit()
        
        print("✅ Columna estado_workflow agregada correctamente a la tabla presupuestos")
        conn.close()
        return True
    except sqlite3.OperationalError as e:
        # Puede ocurrir si la columna ya existe
        if "duplicate column name" in str(e):
            print("⚠️ La columna estado_workflow ya existe en la tabla presupuestos")
            return True
        else:
            print(f"❌ Error al agregar la columna: {e}")
            return False
    except Exception as e:
        print(f"❌ Error general al agregar la columna: {e}")
        return False

def actualizar_valores_predeterminados():
    """Actualiza todos los registros estableciendo valor predeterminado para estado_workflow."""
    try:
        # Establecer conexión directa con SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Actualizar los valores existentes que sean NULL
        cursor.execute("UPDATE presupuestos SET estado_workflow = 'En estudio' WHERE estado_workflow IS NULL")
        conn.commit()
        
        # Verificar cuántas filas se actualizaron
        filas_actualizadas = cursor.rowcount
        print(f"✅ {filas_actualizadas} presupuestos actualizados con estado_workflow predeterminado")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error al actualizar valores predeterminados: {e}")
        return False

def main():
    """Función principal para verificar y actualizar la columna estado_workflow."""
    print("=== Actualización de la columna estado_workflow ===")
    
    # Verificar si existe la base de datos
    if not os.path.exists(DB_PATH):
        print(f"❌ La base de datos no existe en {DB_PATH}")
        return False
    
    # Verificar si existe la columna
    if verificar_columna_workflow():
        print("✅ La columna estado_workflow ya existe en la tabla presupuestos")
        
        # Aun así, asegurar que todos los registros tengan un valor
        actualizar_valores_predeterminados()
        return True
    else:
        print("❓ La columna estado_workflow no existe, se procederá a crearla")
        
        # Agregar la columna
        if agregar_columna_workflow():
            # Actualizar valores predeterminados
            actualizar_valores_predeterminados()
            return True
        else:
            return False

if __name__ == "__main__":
    try:
        if main():
            print("\n✅ Actualización completada con éxito")
            print("Ahora puede utilizar todas las funcionalidades del listado avanzado de presupuestos")
            sys.exit(0)
        else:
            print("\n❌ La actualización no se completó correctamente")
            print("Por favor, revise los mensajes de error e intente nuevamente")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
