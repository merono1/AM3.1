"""
Script para reiniciar completamente la base de datos.
Este script elimina la base de datos existente y crea una nueva vacía.
"""
import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def reset_database():
    """Elimina y recrea la base de datos desde cero."""
    # Obtener la ruta de la base de datos
    db_path = os.environ.get('DB_PATH', 'app/data/app.db')
    db_path_obj = Path(db_path)
    
    print(f"Reiniciando base de datos en: {db_path_obj.absolute()}")
    
    # Verificar si existe el archivo de base de datos
    if db_path_obj.exists():
        print(f"Eliminando base de datos existente...")
        try:
            db_path_obj.unlink()
            print(f"✅ Base de datos eliminada correctamente")
        except Exception as e:
            print(f"❌ Error al eliminar la base de datos: {str(e)}")
            return False
    
    # Asegurar que el directorio existe
    db_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # Crear una nueva base de datos vacía
    try:
        conn = sqlite3.connect(db_path_obj)
        conn.close()
        print(f"✅ Nueva base de datos creada correctamente en {db_path_obj.absolute()}")
    except Exception as e:
        print(f"❌ Error al crear nueva base de datos: {str(e)}")
        return False
    
    print("\nBase de datos reiniciada exitosamente.")
    print("Ahora debes ejecutar 'python init_db.py' para inicializar las tablas.")
    return True

if __name__ == "__main__":
    confirm = input("⚠️ ¡ADVERTENCIA! Este script eliminará todos los datos de la base de datos. ¿Estás seguro? (s/n): ")
    if confirm.lower() == 's':
        reset_database()
    else:
        print("Operación cancelada.")
