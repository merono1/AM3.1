"""
Script para añadir la columna estado_workflow a la tabla presupuestos.
Este script utiliza SQLAlchemy directamente para garantizar compatibilidad
con el modelo y la estructura actual de la aplicación.
"""
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, String, inspect
from sqlalchemy.sql import text

# Obtener la ruta de la base de datos desde el archivo de configuración o usar la predeterminada
DB_PATH = os.path.join('app', 'data', 'app.db')
DB_URI = f"sqlite:///{DB_PATH}"

def fix_workflow_column():
    """Añade la columna estado_workflow a la tabla presupuestos usando SQLAlchemy"""
    print(f"Usando base de datos en: {os.path.abspath(DB_PATH)}")
    
    # Verificar que el archivo existe
    if not os.path.exists(DB_PATH):
        print(f"ERROR: No se encuentra la base de datos en {DB_PATH}")
        return False
    
    # Crear copia de seguridad
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join('app', 'data', f'app_backup_{timestamp}.db')
    
    try:
        # Crear copia de seguridad
        print(f"Creando copia de seguridad en {backup_path}...")
        with open(DB_PATH, 'rb') as source:
            with open(backup_path, 'wb') as dest:
                dest.write(source.read())
        print("Copia de seguridad creada.")
        
        # Conectar a la base de datos
        print("Conectando a la base de datos...")
        engine = create_engine(DB_URI)
        connection = engine.connect()
        
        # Verificar si la tabla presupuestos existe
        inspector = inspect(engine)
        if 'presupuestos' not in inspector.get_table_names():
            print("ERROR: La tabla 'presupuestos' no existe en la base de datos.")
            return False
        
        # Verificar si la columna ya existe
        columns = inspector.get_columns('presupuestos')
        column_names = [col['name'] for col in columns]
        
        if 'estado_workflow' in column_names:
            print("La columna 'estado_workflow' ya existe en la tabla presupuestos.")
            return True
        
        # Añadir la columna
        print("Añadiendo columna 'estado_workflow' a la tabla presupuestos...")
        connection.execute(text("ALTER TABLE presupuestos ADD COLUMN estado_workflow TEXT DEFAULT 'En estudio'"))
        connection.commit()
        
        # Verificar que la columna se agregó correctamente
        inspector = inspect(engine)
        columns_after = inspector.get_columns('presupuestos')
        column_names_after = [col['name'] for col in columns_after]
        
        if 'estado_workflow' in column_names_after:
            print("ÉXITO: La columna 'estado_workflow' se ha añadido correctamente.")
            return True
        else:
            print("ERROR: La columna no se añadió correctamente.")
            # Intentar restaurar desde backup
            print("Intentando restaurar desde backup...")
            connection.close()
            with open(backup_path, 'rb') as source:
                with open(DB_PATH, 'wb') as dest:
                    dest.write(source.read())
            print("Base de datos restaurada desde backup.")
            return False
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        # Intentar restaurar desde backup si existe
        if os.path.exists(backup_path):
            try:
                print("Intentando restaurar desde backup...")
                with open(backup_path, 'rb') as source:
                    with open(DB_PATH, 'wb') as dest:
                        dest.write(source.read())
                print("Base de datos restaurada desde backup.")
            except Exception as restore_error:
                print(f"Error al restaurar desde backup: {str(restore_error)}")
        return False
    finally:
        try:
            connection.close()
        except:
            pass

if __name__ == "__main__":
    print("Iniciando reparación de base de datos...")
    if fix_workflow_column():
        print("Operación completada con éxito.")
        sys.exit(0)
    else:
        print("La operación no se pudo completar correctamente.")
        sys.exit(1)
