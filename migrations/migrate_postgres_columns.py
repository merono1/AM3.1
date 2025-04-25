
# migrations/migrate_postgres_columns.py

import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path para poder importar app
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# Importar para permitir acceso directo a PostgreSQL
import psycopg2
from dotenv import load_dotenv

def get_connection_string():
    """Obtiene la cadena de conexión desde el archivo .env"""
    # Cargar variables de entorno
    dotenv_path = os.path.join(root_dir, '.env')
    load_dotenv(dotenv_path)
    
    # Obtener DATABASE_URL del entorno
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ Error: No se encontró DATABASE_URL en el archivo .env")
        return None
    
    return database_url

def run_migration():
    """
    Añade las columnas 'unitario' y 'cantidad' a la tabla proveedores_partidas en PostgreSQL
    usando psycopg2 directamente sin depender del contexto de la aplicación
    """
    try:
        # Obtener cadena de conexión
        conn_string = get_connection_string()
        if not conn_string:
            return False
        
        print(f"✅ Conectando a PostgreSQL con: {conn_string.split('@')[1] if '@' in conn_string else '***conexión protegida***'}")
        
        # Conectar a PostgreSQL
        conn = psycopg2.connect(conn_string)
        conn.autocommit = False  # Usaremos transacciones explícitamente
        
        # Crear cursor
        cur = conn.cursor()
        
        try:
            # Verificar si las columnas existen
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'proveedores_partidas' AND 
                (column_name = 'unitario' OR column_name = 'cantidad')
            """)
            
            existing_columns = [row[0] for row in cur.fetchall()]
            
            # Añadir columna 'unitario' si no existe
            if 'unitario' not in existing_columns:
                cur.execute("ALTER TABLE proveedores_partidas ADD COLUMN unitario VARCHAR(10)")
                print("Columna 'unitario' añadida correctamente a la tabla proveedores_partidas")
            else:
                print("La columna 'unitario' ya existe")
            
            # Añadir columna 'cantidad' si no existe
            if 'cantidad' not in existing_columns:
                cur.execute("ALTER TABLE proveedores_partidas ADD COLUMN cantidad FLOAT DEFAULT 1")
                print("Columna 'cantidad' añadida correctamente a la tabla proveedores_partidas")
            else:
                print("La columna 'cantidad' ya existe")
            
            # Actualizar valores por defecto
            cur.execute("UPDATE proveedores_partidas SET unitario = 'UD' WHERE unitario IS NULL")
            cur.execute("UPDATE proveedores_partidas SET cantidad = 1 WHERE cantidad IS NULL")
            print("Valores predeterminados establecidos")
            
            # Confirmar transacción
            conn.commit()
            print("Migración completada con éxito")
            
        except Exception as e:
            # Revertir cambios en caso de error
            conn.rollback()
            print(f"❌ Error durante la ejecución SQL: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Cerrar cursor y conexión
            cur.close()
            conn.close()
            
        return True
    except Exception as e:
        print(f"❌ Error durante la migración: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Iniciando migración para añadir columnas 'unitario' y 'cantidad' a la tabla proveedores_partidas en PostgreSQL...")
    success = run_migration()
    if success:
        print("✅ Migración completada correctamente")
    else:
        print("❌ La migración falló")
        sys.exit(1)
