"""
Script corregido para agregar el campo numero a la tabla partidas y actualizar las partidas existentes
con el formato de numeración automática (capítulo.secuencia).
Este script maneja correctamente el contexto de la aplicación Flask.
"""
import os
import sqlite3
from contextlib import closing

def add_numero_column():
    """Añade la columna numero a la tabla partidas si no existe usando SQLite directo"""
    db_path = os.path.join('app', 'data', 'app.db')
    
    try:
        # Conectar directamente a SQLite
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.cursor()
            
            # Verificar si la columna ya existe
            cursor.execute("PRAGMA table_info(partidas)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'numero' not in columns:
                print("Agregando columna 'numero' a la tabla partidas...")
                cursor.execute("ALTER TABLE partidas ADD COLUMN numero VARCHAR(20)")
                conn.commit()
                print("Columna agregada exitosamente.")
            else:
                print("La columna 'numero' ya existe en la tabla partidas.")
            
            return True
    except Exception as e:
        print(f"Error al agregar columna: {str(e)}")
        return False

def update_partidas_numeros():
    """Actualiza los números de partidas existentes con el formato capítulo.secuencia"""
    db_path = os.path.join('app', 'data', 'app.db')
    
    try:
        with closing(sqlite3.connect(db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Obtener todos los presupuestos
            cursor.execute("SELECT id, referencia FROM presupuestos")
            presupuestos = cursor.fetchall()
            
            for presupuesto in presupuestos:
                print(f"Procesando presupuesto: {presupuesto['referencia']}")
                
                # Obtener capítulos de este presupuesto
                cursor.execute(
                    "SELECT DISTINCT capitulo_numero FROM partidas WHERE id_presupuesto = ?",
                    (presupuesto['id'],)
                )
                capitulos_nums = [row[0] for row in cursor.fetchall()]
                
                for cap_num in capitulos_nums:
                    # Obtener partidas para este capítulo ordenadas por ID
                    cursor.execute(
                        "SELECT id FROM partidas WHERE id_presupuesto = ? AND capitulo_numero = ? ORDER BY id",
                        (presupuesto['id'], cap_num)
                    )
                    partidas = cursor.fetchall()
                    
                    # Asignar números en formato x.y
                    for i, partida in enumerate(partidas, 1):
                        nuevo_numero = f"{cap_num}.{i}"
                        cursor.execute(
                            "UPDATE partidas SET numero = ? WHERE id = ?",
                            (nuevo_numero, partida['id'])
                        )
                        print(f"  Asignando número {nuevo_numero} a partida {partida['id']}")
            
            # Guardar cambios
            conn.commit()
            print("Actualización de números de partidas completada.")
            return True
    except Exception as e:
        print(f"Error al actualizar números de partidas: {str(e)}")
        return False

if __name__ == "__main__":
    print("Iniciando actualización de la estructura de la base de datos...")
    
    # Agregar columna si no existe
    if add_numero_column():
        # Actualizar números de partidas existentes
        update_partidas_numeros()
    
    print("Proceso completado.")
