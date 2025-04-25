
# migrations/add_unitario_cantidad_proveedores_partidas.py

import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path para poder importar app
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from app import db
from sqlalchemy import Column, String, Float
from sqlalchemy.sql import text

def run_migration():
    """
    Añade las columnas 'unitario' y 'cantidad' a la tabla proveedores_partidas
    """
    try:
        # Usar transacción para permitir rollback automático en caso de error
        with db.engine.begin() as conn:
            # Verificar si la columna 'unitario' ya existe
            unitario_exists = False
            cantidad_exists = False
            
            # Consultar las columnas existentes
            result = conn.execute(text("PRAGMA table_info(proveedores_partidas)"))
            for row in result:
                if row[1] == 'unitario':
                    unitario_exists = True
                if row[1] == 'cantidad':
                    cantidad_exists = True
            
            # Añadir columna 'unitario' si no existe
            if not unitario_exists:
                conn.execute(text("ALTER TABLE proveedores_partidas ADD COLUMN unitario STRING(10)"))
                print("Columna 'unitario' añadida correctamente a la tabla proveedores_partidas")
            
            # Añadir columna 'cantidad' si no existe
            if not cantidad_exists:
                conn.execute(text("ALTER TABLE proveedores_partidas ADD COLUMN cantidad FLOAT DEFAULT 1"))
                print("Columna 'cantidad' añadida correctamente a la tabla proveedores_partidas")
            
            # Actualizar valores por defecto
            if not unitario_exists or not cantidad_exists:
                conn.execute(text("UPDATE proveedores_partidas SET unitario = 'UD' WHERE unitario IS NULL"))
                conn.execute(text("UPDATE proveedores_partidas SET cantidad = 1 WHERE cantidad IS NULL"))
                print("Valores predeterminados establecidos")
            
            print("Migración completada con éxito")
        
        return True
    except Exception as e:
        print(f"Error durante la migración: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Iniciando migración para añadir columnas 'unitario' y 'cantidad' a la tabla proveedores_partidas...")
    success = run_migration()
    if success:
        print("Migración completada correctamente")
    else:
        print("La migración falló")
        sys.exit(1)
