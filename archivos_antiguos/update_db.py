#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para actualizar la estructura de la base de datos.
Añade las columnas que faltan en las tablas existentes.
"""
import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener la ruta de la base de datos
DB_PATH = os.environ.get('DB_PATH', 'app/data/app.db')

def check_column_exists(conn, table, column):
    """Verifica si una columna existe en una tabla."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    return any(col[1] == column for col in columns)

def add_column(conn, table, column, type):
    """Agrega una columna a una tabla si no existe."""
    if not check_column_exists(conn, table, column):
        print(f"Añadiendo columna '{column}' a la tabla '{table}'...")
        try:
            cursor = conn.cursor()
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type}")
            conn.commit()
            print(f"✅ Columna '{column}' añadida correctamente")
            return True
        except Exception as e:
            print(f"❌ Error al añadir columna: {e}")
            return False
    else:
        print(f"✅ La columna '{column}' ya existe en la tabla '{table}'")
        return True

def update_partidas(conn):
    """Actualiza las partidas existentes con numeración automática."""
    if not check_column_exists(conn, 'partidas', 'numero'):
        print("La columna 'numero' no existe, no se pueden actualizar las partidas")
        return False
    
    try:
        cursor = conn.cursor()
        # Obtener presupuestos
        cursor.execute("SELECT id FROM presupuestos")
        presupuestos = cursor.fetchall()
        
        for presupuesto_id in presupuestos:
            id_presupuesto = presupuesto_id[0]
            # Obtener capítulos del presupuesto
            cursor.execute("SELECT numero FROM capitulos WHERE id_presupuesto = ?", (id_presupuesto,))
            capitulos = cursor.fetchall()
            
            for capitulo in capitulos:
                capitulo_numero = capitulo[0]
                # Obtener partidas del capítulo
                cursor.execute(
                    "SELECT id FROM partidas WHERE id_presupuesto = ? AND capitulo_numero = ? ORDER BY id",
                    (id_presupuesto, capitulo_numero)
                )
                partidas = cursor.fetchall()
                
                # Actualizar numeración de partidas
                for i, partida in enumerate(partidas, 1):
                    partida_id = partida[0]
                    nuevo_numero = f"{capitulo_numero}.{i}"
                    cursor.execute(
                        "UPDATE partidas SET numero = ? WHERE id = ?",
                        (nuevo_numero, partida_id)
                    )
        
        conn.commit()
        print("✅ Partidas actualizadas correctamente con numeración automática")
        return True
    except Exception as e:
        print(f"❌ Error al actualizar partidas: {e}")
        return False

def main():
    """Función principal del script."""
    print("=== Actualización de estructura de base de datos ===")
    print(f"Usando base de datos: {DB_PATH}")
    
    # Verificar que el archivo existe
    if not os.path.exists(DB_PATH):
        print(f"❌ El archivo de base de datos no existe: {DB_PATH}")
        return False
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        
        # Añadir columna 'numero' a la tabla 'partidas'
        if add_column(conn, 'partidas', 'numero', 'TEXT'):
            # Actualizar partidas existentes con numeración automática
            update_partidas(conn)
        
        conn.close()
        print("✅ Actualización completada con éxito")
        return True
    except Exception as e:
        print(f"❌ Error durante la actualización: {e}")
        return False

if __name__ == "__main__":
    main()
