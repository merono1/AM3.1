# reset_db_simple.py
import os
import shutil
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DB_PATH = os.environ.get('DB_PATH', 'app/data/app.db')
print(f"Ruta de la base de datos: {os.path.abspath(DB_PATH)}")

def main():
    """Elimina la base de datos y deja que la aplicación la recree."""
    # Verificar si existe el archivo
    if os.path.exists(DB_PATH):
        # Crear directorio de backup si no existe
        backup_dir = os.path.join(os.path.dirname(DB_PATH), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Crear copia de seguridad con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f'app_backup_{timestamp}.db')
        
        try:
            # Copiar el archivo a la ubicación de backup
            shutil.copy2(DB_PATH, backup_path)
            print(f"✅ Copia de seguridad creada: {backup_path}")
            
            # Eliminar el archivo original
            os.remove(DB_PATH)
            print(f"✅ Base de datos eliminada: {DB_PATH}")
            print("Al iniciar la aplicación se creará una nueva base de datos en blanco.")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print(f"La base de datos no existe en {DB_PATH}.")
        print("Al iniciar la aplicación se creará una nueva base de datos en blanco.")

if __name__ == "__main__":
    confirm = input("Este script eliminará la base de datos. ¿Continuar? (s/N): ").lower()
    if confirm == 's':
        main()
    else:
        print("Operación cancelada.")
