"""
Script para verificar si la base de datos local existe y obtener su tamaño e información.
"""

import os
import sys
import datetime
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def main():
    """Verificar estado de la base de datos local."""
    try:
        # Obtener ruta de la base de datos
        base_dir = Path(__file__).resolve().parent
        instance_dir = base_dir / 'instance'
        
        db_path = os.environ.get('DB_PATH')
        if not db_path:
            db_path = instance_dir / 'app.db'
            print(f"ℹ️ Usando ruta predeterminada para SQLite: {db_path}")
        else:
            db_path = Path(db_path)
            print(f"ℹ️ Usando ruta configurada para SQLite: {db_path}")
        
        # Verificar si existe
        if not db_path.exists():
            print(f"❌ La base de datos local NO existe en {db_path}")
            return 1
        
        # Obtener información de la BD
        size_bytes = db_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        mod_time = datetime.datetime.fromtimestamp(db_path.stat().st_mtime)
        
        print(f"✅ Base de datos local encontrada en {db_path}")
        print(f"📊 Tamaño: {size_mb:.2f} MB ({size_bytes:,} bytes)")
        print(f"⏰ Última modificación: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Verificar si tiene tablas
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Obtener lista de tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if tables:
                print(f"📋 Número de tablas encontradas: {len(tables)}")
                print("📌 Primeras 10 tablas:")
                for i, table in enumerate(tables[:10]):
                    # Contar filas en cada tabla
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM '{table[0]}'")
                        count = cursor.fetchone()[0]
                        print(f"   - {table[0]}: {count} filas")
                    except sqlite3.Error:
                        print(f"   - {table[0]}: Error al contar filas")
            else:
                print("⚠️ No se encontraron tablas en la base de datos")
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Error al leer estructura de la base de datos: {e}")
        
        return 0
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
