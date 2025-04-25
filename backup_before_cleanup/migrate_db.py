import os
import sys
import sqlite3

def run_migration(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Connected to database: {db_path}")
    
    # Verificar si ya existe la columna porcentaje_facturado en partidas
    cursor.execute("PRAGMA table_info(partidas)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    # Añadir columna porcentaje_facturado a la tabla partidas si no existe
    if 'porcentaje_facturado' not in column_names:
        print("Adding porcentaje_facturado column to partidas table...")
        cursor.execute("ALTER TABLE partidas ADD COLUMN porcentaje_facturado REAL DEFAULT 0")
    
    # Verificar si ya existe la columna id_presupuesto en facturas
    cursor.execute("PRAGMA table_info(facturas)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    # Añadir columna id_presupuesto a la tabla facturas si no existe
    if 'id_presupuesto' not in column_names:
        print("Adding id_presupuesto column to facturas table...")
        cursor.execute("ALTER TABLE facturas ADD COLUMN id_presupuesto INTEGER")
    
    # Verificar si ya existen las columnas id_partida y porcentaje_facturado en lineas_factura
    cursor.execute("PRAGMA table_info(lineas_factura)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    # Añadir columnas a lineas_factura si no existen
    if 'id_partida' not in column_names:
        print("Adding id_partida column to lineas_factura table...")
        cursor.execute("ALTER TABLE lineas_factura ADD COLUMN id_partida INTEGER")
    
    if 'porcentaje_facturado' not in column_names:
        print("Adding porcentaje_facturado column to lineas_factura table...")
        cursor.execute("ALTER TABLE lineas_factura ADD COLUMN porcentaje_facturado REAL DEFAULT 100")
    
    # Confirmar cambios
    conn.commit()
    
    # Verificar que todo está correcto
    print("\nVerifying database structure...")
    tables = [
        "partidas", 
        "facturas", 
        "lineas_factura"
    ]
    
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print(f"\n{table} table columns:")
        for column in columns:
            print(f"- {column[1]} ({column[2]})")
    
    conn.close()
    print("\nMigration completed successfully!")

if __name__ == "__main__":
    db_path = os.path.join(os.getcwd(), "app", "data", "app.db")
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        sys.exit(1)
    
    # Imprimir un mensaje para confirmar que empieza la migración
    print("\nIniciando migración de base de datos...")
    print(f"Base de datos: {db_path}")
    run_migration(db_path)
