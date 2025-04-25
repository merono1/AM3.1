
# migrations/add_unitario_cantidad_postgres.py

import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path para poder importar app
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# Importar la app y crear el contexto de aplicación
from app import create_app, db
from sqlalchemy import text

def run_migration():
    """
    Añade las columnas 'unitario' y 'cantidad' a la tabla proveedores_partidas en PostgreSQL
    """
    # Crear e inicializar la aplicación
    app = create_app()
    
    try:
        # Usar el contexto de la aplicación
        with app.app_context():
            # Verificar el tipo de base de datos
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            if 'postgresql' not in db_uri.lower():
                print(f"⚠️ No estás utilizando PostgreSQL. Esta migración es solo para PostgreSQL.")
                print(f"URI actual: {db_uri}")
                return False
            
            print(f"✅ Usando PostgreSQL: {db_uri}")
            
            # Usar transacción para permitir rollback automático en caso de error
            with db.engine.begin() as conn:
                # Verificar si las columnas existen
                check_query = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'proveedores_partidas' AND 
                    (column_name = 'unitario' OR column_name = 'cantidad')
                """)
                
                result = conn.execute(check_query)
                existing_columns = [row[0] for row in result]
                
                # Añadir columna 'unitario' si no existe
                if 'unitario' not in existing_columns:
                    conn.execute(text("ALTER TABLE proveedores_partidas ADD COLUMN unitario VARCHAR(10)"))
                    print("Columna 'unitario' añadida correctamente a la tabla proveedores_partidas")
                else:
                    print("La columna 'unitario' ya existe")
                
                # Añadir columna 'cantidad' si no existe
                if 'cantidad' not in existing_columns:
                    conn.execute(text("ALTER TABLE proveedores_partidas ADD COLUMN cantidad FLOAT DEFAULT 1"))
                    print("Columna 'cantidad' añadida correctamente a la tabla proveedores_partidas")
                else:
                    print("La columna 'cantidad' ya existe")
                
                # Actualizar valores por defecto
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
    print("Iniciando migración para añadir columnas 'unitario' y 'cantidad' a la tabla proveedores_partidas en PostgreSQL...")
    success = run_migration()
    if success:
        print("Migración completada correctamente")
    else:
        print("La migración falló")
        sys.exit(1)
