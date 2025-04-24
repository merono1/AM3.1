#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3
from contextlib import closing

def check_database_file(db_path):
    """Verifica si el archivo de base de datos existe y es accesible."""
    if not os.path.exists(db_path):
        print(f"ERROR: El archivo de base de datos no existe: {db_path}")
        return False
    
    if not os.access(db_path, os.R_OK | os.W_OK):
        print(f"ERROR: No se tienen permisos de lectura/escritura para: {db_path}")
        return False
    
    return True

def check_database_connection(db_path):
    """Intenta conectarse a la base de datos para verificar si es válida."""
    try:
        with closing(sqlite3.connect(db_path)) as conn:
            conn.execute("SELECT 1")
        print(f"✓ Conexión exitosa a la base de datos: {db_path}")
        return True
    except sqlite3.Error as e:
        print(f"ERROR de conexión a la base de datos: {e}")
        return False

def check_table_structure(db_path):
    """Verifica la estructura de las tablas principales."""
    tables_to_check = [
        "clientes", 
        "proyectos", 
        "presupuestos"
    ]
    
    try:
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.cursor()
            
            # Obtener todas las tablas en la base de datos
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            # Verificar si existen las tablas necesarias
            for table in tables_to_check:
                if table not in existing_tables:
                    print(f"ERROR: Falta la tabla '{table}' en la base de datos")
                    return False
                
                # Verificar la estructura de cada tabla
                cursor.execute(f"PRAGMA table_info({table});")
                columns = cursor.fetchall()
                
                if not columns:
                    print(f"ERROR: La tabla '{table}' existe pero no tiene columnas")
                    return False
                
                print(f"✓ Tabla '{table}' encontrada con {len(columns)} columnas")
            
            return True
    except sqlite3.Error as e:
        print(f"ERROR al verificar la estructura de las tablas: {e}")
        return False

def verify_relationships(db_path):
    """Verifica las relaciones entre tablas."""
    try:
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.cursor()
            
            # Verificar proyectos sin cliente válido
            cursor.execute("""
                SELECT p.id, p.nombre_proyecto
                FROM proyectos p
                LEFT JOIN clientes c ON p.id_cliente = c.id
                WHERE p.id_cliente IS NOT NULL AND c.id IS NULL
            """)
            
            invalid_projects = cursor.fetchall()
            if invalid_projects:
                print(f"ADVERTENCIA: Se encontraron {len(invalid_projects)} proyectos con cliente inválido")
                for proj in invalid_projects:
                    print(f"  - Proyecto ID: {proj[0]}, Nombre: {proj[1]}")
            else:
                print("✓ Todos los proyectos tienen clientes válidos")
            
            # Verificar presupuestos sin proyecto válido
            cursor.execute("""
                SELECT pr.id, pr.referencia
                FROM presupuestos pr
                LEFT JOIN proyectos p ON pr.id_proyecto = p.id
                WHERE pr.id_proyecto IS NOT NULL AND p.id IS NULL
            """)
            
            invalid_budgets = cursor.fetchall()
            if invalid_budgets:
                print(f"ADVERTENCIA: Se encontraron {len(invalid_budgets)} presupuestos con proyecto inválido")
                for budget in invalid_budgets:
                    print(f"  - Presupuesto ID: {budget[0]}, Nombre: {budget[1]}")
            else:
                print("✓ Todos los presupuestos tienen proyectos válidos")
            
            return True
    except sqlite3.Error as e:
        print(f"ERROR al verificar relaciones: {e}")
        return False

def repair_nullable_fields(db_path):
    """Actualiza la estructura de las tablas para hacer campos opcionales."""
    try:
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.cursor()
            
            # Hacer campos opcionales en la tabla proyecto
            # Nota: SQLite no permite ALTER COLUMN directamente, por lo que haremos esto en rebuild_db.py
            print("Para hacer campos opcionales se requiere reconstruir la tabla. Use rebuild_db.py para esto.")
            
            # Verificamos si hay datos NULL en campos que deberían ser opcionales
            cursor.execute("""
                SELECT COUNT(*) FROM proyectos 
                WHERE nombre_proyecto IS NULL OR calle IS NULL OR nombre_via IS NULL
            """)
            
            null_projects = cursor.fetchone()[0]
            if null_projects > 0:
                print(f"ADVERTENCIA: Se encontraron {null_projects} proyectos con campos NULL")
            
            return True
    except sqlite3.Error as e:
        print(f"ERROR al intentar reparar campos opcionales: {e}")
        return False

def main():
    """Función principal que ejecuta todas las verificaciones."""
    db_path = "app/data/app.db"  # Ruta correcta a la base de datos
    
    print("=== Iniciando verificación de la base de datos ===")
    
    if not check_database_file(db_path):
        print("La verificación de archivo falló. Revise los permisos o cree una nueva base de datos.")
        return False
    
    if not check_database_connection(db_path):
        print("La conexión a la base de datos falló. La base de datos podría estar corrupta.")
        return False
    
    if not check_table_structure(db_path):
        print("La estructura de tablas es incorrecta. Considere usar rebuild_db.py.")
        return False
    
    verify_relationships(db_path)
    repair_nullable_fields(db_path)
    
    print("=== Verificación completada ===")
    print("Para reparar problemas estructurales, use rebuild_db.py")
    return True

if __name__ == "__main__":
    main()
