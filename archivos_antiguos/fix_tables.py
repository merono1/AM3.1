#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import os
from contextlib import closing
from datetime import datetime

def backup_table(db_path, table_name):
    """Crea una copia de seguridad de una tabla específica."""
    backup_name = f"{table_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.cursor()
            
            # Verificar si la tabla existe
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                print(f"La tabla {table_name} no existe")
                return False
            
            # Obtener la estructura de la tabla
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            create_sql = cursor.fetchone()[0]
            
            # Crear tabla de backup
            cursor.execute(f"CREATE TABLE {backup_name} AS SELECT * FROM {table_name}")
            
            # Guardar la definición original para posible restauración
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            conn.commit()
            print(f"Backup de la tabla {table_name} creado como {backup_name}")
            return True
    except sqlite3.Error as e:
        print(f"Error al crear backup de la tabla: {e}")
        return False

def fix_proyecto_table(db_path):
    """Corrige la tabla proyecto haciendo campos opcionales."""
    table_name = "proyecto"
    temp_table = "proyecto_temp"
    
    try:
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.cursor()
            
            # Hacer backup
            if not backup_table(db_path, table_name):
                print("No se pudo hacer backup, operación cancelada")
                return False
            
            # Obtener datos actuales
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Obtener nombres de columnas
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Crear tabla temporal con campos opcionales
            cursor.execute(f'''
                CREATE TABLE {temp_table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    direccion TEXT,
                    fecha_inicio TEXT,
                    fecha_fin TEXT,
                    estado TEXT,
                    id_cliente INTEGER,
                    notas TEXT,
                    FOREIGN KEY (id_cliente) REFERENCES cliente (id)
                )
            ''')
            
            # Copiar datos a la tabla temporal
            for row in rows:
                placeholders = ', '.join(['?' for _ in row])
                cursor.execute(f"INSERT INTO {temp_table} VALUES ({placeholders})", row)
            
            # Eliminar tabla original
            cursor.execute(f"DROP TABLE {table_name}")
            
            # Renombrar tabla temporal a original
            cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")
            
            conn.commit()
            print(f"Tabla {table_name} reparada exitosamente")
            return True
    except sqlite3.Error as e:
        print(f"Error al reparar la tabla proyecto: {e}")
        return False

def fix_presupuesto_table(db_path):
    """Corrige la tabla presupuesto si es necesario."""
    table_name = "presupuesto"
    
    try:
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.cursor()
            
            # Verificar si la tabla existe
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                print(f"La tabla {table_name} no existe, creándola...")
                
                # Crear la tabla si no existe
                cursor.execute(f'''
                    CREATE TABLE {table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        fecha_creacion TEXT,
                        fecha_actualizacion TEXT,
                        estado TEXT,
                        monto REAL,
                        id_proyecto INTEGER,
                        notas TEXT,
                        FOREIGN KEY (id_proyecto) REFERENCES proyecto (id)
                    )
                ''')
                
                conn.commit()
                print(f"Tabla {table_name} creada exitosamente")
                return True
            
            # Si la tabla existe, verificar su estructura
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = {column[1]: column for column in cursor.fetchall()}
            
            # Verificar si faltan columnas necesarias
            required_columns = {
                'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
                'nombre': 'TEXT NOT NULL',
                'fecha_creacion': 'TEXT',
                'fecha_actualizacion': 'TEXT',
                'estado': 'TEXT',
                'monto': 'REAL',
                'id_proyecto': 'INTEGER',
                'notas': 'TEXT'
            }
            
            missing_columns = [col for col in required_columns.keys() if col not in columns]
            
            if missing_columns:
                print(f"Faltan columnas en la tabla {table_name}: {missing_columns}")
                print("Se recomienda usar rebuild_db.py para reconstruir completamente la tabla")
                return False
            
            print(f"La estructura de la tabla {table_name} es correcta")
            return True
    except sqlite3.Error as e:
        print(f"Error al verificar/reparar la tabla presupuesto: {e}")
        return False

def main():
    """Función principal que ejecuta las reparaciones de tablas."""
    db_path = "app.db"  # Ajusta esto a la ruta de tu base de datos
    
    print("=== Iniciando reparación de tablas específicas ===")
    
    # Verificar si existe la base de datos
    if not os.path.exists(db_path):
        print(f"La base de datos {db_path} no existe")
        return False
    
    # Reparar tabla proyecto
    print("\n--- Reparando tabla proyecto ---")
    fix_proyecto_table(db_path)
    
    # Reparar tabla presupuesto
    print("\n--- Verificando tabla presupuesto ---")
    fix_presupuesto_table(db_path)
    
    print("\n=== Reparación de tablas completada ===")
    return True

if __name__ == "__main__":
    main()
