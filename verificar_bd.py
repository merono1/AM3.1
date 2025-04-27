#!/usr/bin/env python
"""
Script para verificar el estado de la base de datos SQLite local.
Muestra información sobre las tablas y realiza verificaciones básicas.
"""

import os
import sys
import sqlite3
import datetime
from pathlib import Path

def get_db_path():
    """Obtiene la ruta de la base de datos desde .env o usa la predeterminada."""
    # Intentar leer .env
    db_path = None
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('DB_PATH='):
                    db_path = line.split('=', 1)[1].strip()
                    break
    except Exception as e:
        print(f"No se pudo leer .env: {e}")
    
    # Usar ruta predeterminada si no se encontró en .env
    if not db_path:
        db_path = 'instance/app.db'
        print(f"Usando ruta predeterminada: {db_path}")
    else:
        print(f"Usando ruta desde .env: {db_path}")
        
    return db_path

def get_file_info(file_path):
    """Obtiene información del archivo de base de datos."""
    path = Path(file_path)
    
    if not path.exists():
        return {
            'exists': False,
            'message': f"El archivo no existe: {path}"
        }
    
    size_bytes = path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    mod_time = datetime.datetime.fromtimestamp(path.stat().st_mtime)
    
    return {
        'exists': True,
        'path': str(path.absolute()),
        'size_bytes': size_bytes,
        'size_mb': f"{size_mb:.2f} MB",
        'last_modified': mod_time.strftime("%Y-%m-%d %H:%M:%S"),
    }

def check_db_tables(db_path):
    """Verifica las tablas existentes en la base de datos."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener lista de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Obtener conteo de filas por tabla
        table_counts = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM '{table}'")
            count = cursor.fetchone()[0]
            table_counts[table] = count
        
        conn.close()
        
        return {
            'success': True,
            'tables': tables,
            'table_counts': table_counts,
            'total_tables': len(tables),
        }
    except sqlite3.Error as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """Función principal."""
    print("\n===== VERIFICACIÓN DE BASE DE DATOS LOCAL SQLITE =====\n")
    
    # Obtener ruta de la base de datos
    db_path = get_db_path()
    
    # Verificar existencia y obtener info del archivo
    file_info = get_file_info(db_path)
    
    if not file_info['exists']:
        print(f"❌ Error: {file_info['message']}")
        return 1
    
    # Mostrar información del archivo
    print("\n>> INFORMACIÓN DEL ARCHIVO:")
    print(f"   Ruta: {file_info['path']}")
    print(f"   Tamaño: {file_info['size_mb']}")
    print(f"   Última modificación: {file_info['last_modified']}")
    
    # Verificar tablas
    db_info = check_db_tables(db_path)
    
    if not db_info['success']:
        print(f"\n❌ Error al verificar tablas: {db_info['error']}")
        return 1
    
    # Mostrar información de tablas
    print(f"\n>> TABLAS ENCONTRADAS: {db_info['total_tables']}")
    
    if db_info['total_tables'] == 0:
        print("\n⚠️ Advertencia: No se encontraron tablas en la base de datos.")
        print("   Esto puede indicar que la base de datos está vacía o no inicializada.")
        print("   Prueba a iniciar la aplicación para crear las tablas automáticamente.")
        return 0
    
    # Mostrar tablas y conteos
    print("\n   TABLA                      | REGISTROS")
    print("   ---------------------------|----------")
    for table, count in db_info['table_counts'].items():
        print(f"   {table:27} | {count:10}")
    
    print("\n✅ Verificación completada correctamente!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
