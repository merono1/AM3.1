"""
Script para agregar la columna 'numero' a la tabla partidas
"""
import sqlite3
import os
from pathlib import Path

# Ruta a la base de datos
db_path = os.path.join('app', 'data', 'app.db')

def add_column():
    """Añade la columna numero a la tabla partidas"""
    print(f"Intentando agregar columna a: {db_path}")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(partidas)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'numero' not in columns:
            print("La columna 'numero' no existe en la tabla partidas. Añadiéndola...")
            # Agregar la columna
            cursor.execute("ALTER TABLE partidas ADD COLUMN numero VARCHAR(20)")
            conn.commit()
            print("Columna 'numero' añadida correctamente.")
        else:
            print("La columna 'numero' ya existe en la tabla partidas.")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error al agregar columna: {str(e)}")
        return False

if __name__ == "__main__":
    add_column()
    print("Proceso completado. Intenta reiniciar la aplicación.")
