"""
Script para subir la base de datos desde SQLite a PostgreSQL.
Se puede ejecutar directamente desde la línea de comandos.
"""

import os
import sys
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

def main():
    """Función principal para subir base de datos."""
    try:
        # Obtener rutas y configuración
        base_dir = Path(__file__).resolve().parent
        instance_dir = base_dir / 'instance'
        
        # Obtener URL de PostgreSQL
        pg_url = os.environ.get('DATABASE_URL')
        if not pg_url:
            print("❌ Error: No se ha configurado DATABASE_URL en el archivo .env")
            sys.exit(1)
        
        # Ruta para SQLite
        sqlite_path = os.environ.get('DB_PATH')
        if not sqlite_path:
            sqlite_path = instance_dir / 'app.db'
            print(f"ℹ️ Usando ruta predeterminada para SQLite: {sqlite_path}")
        else:
            sqlite_path = Path(sqlite_path)
            print(f"ℹ️ Usando ruta configurada para SQLite: {sqlite_path}")
        
        # Verificar que existe la base de datos local
        if not sqlite_path.exists():
            print(f"❌ Error: No se encontró la base de datos local en {sqlite_path}")
            return 1
        
        # Importar la clase de transferencia directa
        sys.path.append(str(base_dir))
        from app.services.direct_db_backup import DirectDatabaseTransfer
        
        # Crear instancia
        transfer = DirectDatabaseTransfer(pg_url=pg_url, sqlite_path=sqlite_path)
        
        # Confirmar con el usuario
        if not '--force' in sys.argv:
            print("⚠️ ADVERTENCIA: Esta operación sobrescribirá todos los datos en PostgreSQL.")
            print("⚠️ Asegúrese de tener una copia de seguridad si es necesario.")
            response = input("¿Desea continuar? (s/N): ").strip().lower()
            if response != 's':
                print("Operación cancelada por el usuario.")
                return 0
        
        # Subir base de datos
        print("🔄 Iniciando subida de base de datos...")
        start_time = time.time()
        
        success, message = transfer.upload_sqlite_to_postgres()
        
        elapsed_time = time.time() - start_time
        
        if success:
            print(f"✅ {message}")
            print(f"⏱️ Tiempo total: {elapsed_time:.2f} segundos")
            return 0
        else:
            print(f"❌ {message}")
            return 1
    
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        logger.exception("Error en subida directa de base de datos")
        return 1

if __name__ == "__main__":
    sys.exit(main())
