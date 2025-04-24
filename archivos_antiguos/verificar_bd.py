"""
Script para verificar el estado de la base de datos y comprobar si la columna estado_workflow existe.
"""
import os
import sqlite3
from sqlalchemy import create_engine, inspect

# Ruta a la base de datos
DB_PATH = os.path.join('app', 'data', 'app.db')
DB_URI = f"sqlite:///{DB_PATH}"

def verificar_estructura_db():
    """Verifica la estructura de la base de datos y muestra información detallada."""
    print(f"Verificando base de datos en: {os.path.abspath(DB_PATH)}")
    
    # Verificar que el archivo existe
    if not os.path.exists(DB_PATH):
        print(f"ERROR: No se encuentra la base de datos en {DB_PATH}")
        return False
    
    try:
        # Método 1: Verificar con SQLite directamente
        print("\n=== Verificación con SQLite ===")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Obtener lista de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = cursor.fetchall()
        print(f"Tablas en la base de datos ({len(tablas)}):")
        for tabla in tablas:
            print(f"  - {tabla[0]}")
        
        # Verificar si existe la tabla presupuestos
        if ('presupuestos',) not in tablas:
            print("ERROR: La tabla 'presupuestos' no existe")
        else:
            print("\nColumnas en la tabla 'presupuestos':")
            cursor.execute("PRAGMA table_info(presupuestos)")
            columnas = cursor.fetchall()
            for col in columnas:
                print(f"  - {col[1]} ({col[2]}){' PRIMARY KEY' if col[5] == 1 else ''}")
            
            # Verificar si existe la columna estado_workflow
            columna_existe = any(col[1] == 'estado_workflow' for col in columnas)
            if columna_existe:
                print("\nEstado: La columna 'estado_workflow' SÍ existe en la tabla 'presupuestos'")
            else:
                print("\nEstado: La columna 'estado_workflow' NO existe en la tabla 'presupuestos'")
        
        conn.close()
        
        # Método 2: Verificar con SQLAlchemy
        print("\n=== Verificación con SQLAlchemy ===")
        engine = create_engine(DB_URI)
        inspector = inspect(engine)
        
        # Verificar tablas
        tablas_alchemy = inspector.get_table_names()
        print(f"Tablas detectadas por SQLAlchemy ({len(tablas_alchemy)}):")
        for tabla in tablas_alchemy:
            print(f"  - {tabla}")
        
        # Verificar columnas de presupuestos
        if 'presupuestos' in tablas_alchemy:
            columns = inspector.get_columns('presupuestos')
            print("\nColumnas en 'presupuestos' según SQLAlchemy:")
            for col in columns:
                print(f"  - {col['name']} ({col['type']})")
            
            # Verificar si existe la columna estado_workflow
            column_names = [col['name'] for col in columns]
            if 'estado_workflow' in column_names:
                print("\nEstado: La columna 'estado_workflow' SÍ existe según SQLAlchemy")
            else:
                print("\nEstado: La columna 'estado_workflow' NO existe según SQLAlchemy")
        
        print("\n=== Resumen ===")
        print("La base de datos existe y se puede acceder.")
        print(f"Total de tablas: {len(tablas)}")
        if ('presupuestos',) in tablas:
            print("La tabla 'presupuestos' existe.")
            if columna_existe:
                print("La columna 'estado_workflow' existe y todo parece correcto.")
                return True
            else:
                print("La columna 'estado_workflow' NO existe. Ejecute el script de actualización.")
                return False
        else:
            print("La tabla 'presupuestos' NO existe. Hay un problema con la estructura de la BD.")
            return False
        
    except Exception as e:
        print(f"ERROR al verificar la base de datos: {str(e)}")
        return False

if __name__ == "__main__":
    print("Iniciando verificación de base de datos...")
    resultado = verificar_estructura_db()
    if resultado:
        print("\nLa estructura de la base de datos es correcta.")
    else:
        print("\nHay problemas con la estructura de la base de datos.")
