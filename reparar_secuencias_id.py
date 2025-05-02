#!/usr/bin/env python
"""
Script para reparar secuencias de ID en las tablas de hojas de trabajo.
Este script resuelve problemas con las secuencias de IDs en SQLite.
"""

import os
import sqlite3
import sys
from pathlib import Path
from dotenv import load_dotenv

def main():
    """Función principal para reparar la base de datos."""
    print("\n===== REPARACIÓN DE SECUENCIAS DE ID EN SQLITE =====\n")
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener la ruta de la base de datos desde .env
    db_path = os.environ.get('DB_PATH', 'instance/app.db')
    
    # Convertir a ruta absoluta si es relativa
    if not os.path.isabs(db_path):
        base_dir = Path(__file__).resolve().parent
        db_path = str(base_dir / db_path)
    
    print(f"Ruta de la base de datos: {db_path}")
    
    # Verificar si existe
    if not os.path.exists(db_path):
        print("La base de datos no existe. No es posible reparar.")
        return 1
    
    # Conectar a la base de datos
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar si las tablas existen
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('capitulos_hojas', 'partidas_hojas')")
        tables = cursor.fetchall()
        table_names = [t['name'] for t in tables]
        
        if 'capitulos_hojas' not in table_names or 'partidas_hojas' not in table_names:
            print("Error: No se encontraron las tablas necesarias.")
            return 1
        
        # Verificar el estado actual de las secuencias
        print("\n--- Estado actual de las tablas ---")
        
        for table in ['capitulos_hojas', 'partidas_hojas']:
            cursor.execute(f"SELECT COUNT(*) as count, MAX(id) as max_id FROM {table}")
            result = cursor.fetchone()
            print(f"Tabla {table}: {result['count']} registros, ID máximo: {result['max_id']}")
        
        # Comprobar si hay registros con valores NULL en id
        cursor.execute("SELECT COUNT(*) as null_count FROM capitulos_hojas WHERE id IS NULL")
        null_count = cursor.fetchone()['null_count']
        if null_count > 0:
            print(f"ADVERTENCIA: Se encontraron {null_count} registros con ID NULL en capitulos_hojas")
        
        cursor.execute("SELECT COUNT(*) as null_count FROM partidas_hojas WHERE id IS NULL")
        null_count = cursor.fetchone()['null_count']
        if null_count > 0:
            print(f"ADVERTENCIA: Se encontraron {null_count} registros con ID NULL en partidas_hojas")
        
        # Reparar sqlite_sequence
        print("\n--- Reparando secuencias ---")
        
        # Primero verificar si existe la tabla sqlite_sequence
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'")
        if not cursor.fetchone():
            print("Creando tabla sqlite_sequence...")
            cursor.execute("CREATE TABLE sqlite_sequence(name TEXT PRIMARY KEY, seq INTEGER)")
        
        # Actualizar secuencias para cada tabla
        for table in ['capitulos_hojas', 'partidas_hojas']:
            cursor.execute(f"SELECT MAX(id) as max_id FROM {table}")
            max_id = cursor.fetchone()['max_id'] or 0
            
            # Verificar si ya existe un registro para esta tabla en sqlite_sequence
            cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = ?", (table,))
            row = cursor.fetchone()
            
            if row:
                current_seq = row['seq']
                if current_seq < max_id:
                    cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = ?", (max_id, table))
                    print(f"Actualizada secuencia para {table}: {current_seq} -> {max_id}")
                else:
                    print(f"La secuencia para {table} ya está correcta: {current_seq}")
            else:
                cursor.execute("INSERT INTO sqlite_sequence VALUES (?, ?)", (table, max_id))
                print(f"Creada secuencia para {table} con valor {max_id}")
        
        # Eliminar registros con ID NULL si existen
        cursor.execute("DELETE FROM capitulos_hojas WHERE id IS NULL")
        deleted = cursor.rowcount
        if deleted > 0:
            print(f"Eliminados {deleted} registros con ID NULL de capitulos_hojas")
        
        cursor.execute("DELETE FROM partidas_hojas WHERE id IS NULL")
        deleted = cursor.rowcount
        if deleted > 0:
            print(f"Eliminados {deleted} registros con ID NULL de partidas_hojas")
        
        # Guardar cambios
        conn.commit()
        
        # Verificar que todo esté correcto
        print("\n--- Estado final de las tablas ---")
        for table in ['capitulos_hojas', 'partidas_hojas']:
            cursor.execute(f"SELECT COUNT(*) as count, MAX(id) as max_id FROM {table}")
            result = cursor.fetchone()
            print(f"Tabla {table}: {result['count']} registros, ID máximo: {result['max_id']}")
            
            cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = ?", (table,))
            row = cursor.fetchone()
            if row:
                print(f"Secuencia actual: {row['seq']}")
        
        print("\n¡Reparación completada con éxito!")
        return 0
        
    except sqlite3.Error as e:
        print(f"Error de base de datos: {e}")
        return 1
    except Exception as e:
        print(f"Error general: {e}")
        return 1
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    sys.exit(main())
