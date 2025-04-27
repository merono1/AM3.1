#!/usr/bin/env python
"""
Script para resetear la base de datos SQLite.
Este script elimina la base de datos existente y deja que la aplicación la vuelva a crear.
"""

import os
import sys
import shutil
import datetime
from pathlib import Path

def main():
    """Función principal para resetear la base de datos."""
    print("\n===== RESET DE BASE DE DATOS SQLITE =====\n")
    
    # Obtener la ruta de la base de datos desde .env
    db_path = 'instance/app.db'  # Valor predeterminado
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('DB_PATH='):
                    db_path = line.split('=', 1)[1].strip()
                    break
    except Exception as e:
        print(f"Advertencia: No se pudo leer .env: {e}")
    
    # Convertir a ruta absoluta si es relativa
    if not os.path.isabs(db_path):
        base_dir = Path(__file__).resolve().parent
        db_path = str(base_dir / db_path)
    
    print(f"Ruta de la base de datos: {db_path}")
    
    # Verificar si existe
    if not os.path.exists(db_path):
        print("La base de datos no existe. No es necesario resetearla.")
        print("La aplicación creará una nueva base de datos al iniciar.")
        return 0
    
    # Crear copia de seguridad antes de eliminar
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"app_db_backup_before_reset_{timestamp}.db"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"Copia de seguridad creada: {backup_path}")
    except Exception as e:
        print(f"Advertencia: No se pudo crear copia de seguridad: {e}")
        
        # Preguntar si desea continuar sin copia de seguridad
        response = input("¿Desea continuar sin copia de seguridad? (s/N): ").lower()
        if response != 's':
            print("Operación cancelada.")
            return 1
    
    # Eliminar la base de datos
    try:
        os.remove(db_path)
        print("Base de datos eliminada correctamente.")
        print("La aplicación creará una nueva base de datos al iniciar.")
        return 0
    except Exception as e:
        print(f"Error: No se pudo eliminar la base de datos: {e}")
        print("Sugerencias:")
        print(" 1. Verifique que no hay otras aplicaciones usando la base de datos")
        print(" 2. Verifique que tiene permisos para eliminar archivos en esa carpeta")
        return 1

if __name__ == "__main__":
    sys.exit(main())
