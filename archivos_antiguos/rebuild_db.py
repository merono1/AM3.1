#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3
import shutil
from datetime import datetime
from contextlib import closing

def backup_database(db_path):
    """Crea una copia de seguridad de la base de datos antes de modificarla."""
    if not os.path.exists(db_path):
        print(f"No se puede hacer backup: El archivo {db_path} no existe")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"Backup creado exitosamente: {backup_path}")
        return True
    except Exception as e:
        print(f"Error al crear backup: {e}")
        return False

def export_data(db_path):
    """Exporta los datos actuales de las tablas principales."""
    data = {
        'cliente': [],
        'proyecto': [],
        'presupuesto': []
    }
    
    try:
        with closing(sqlite3.connect(db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Exportar datos de clientes
            cursor.execute("SELECT * FROM cliente")
            data['cliente'] = [dict(row) for row in cursor.fetchall()]
            print(f"Exportados {len(data['cliente'])} clientes")
            
            # Exportar datos de proyectos
            cursor.execute("SELECT * FROM proyecto")
            data['proyecto'] = [dict(row) for row in cursor.fetchall()]
            print(f"Exportados {len(data['proyecto'])} proyectos")
            
            # Exportar datos de presupuestos
            cursor.execute("SELECT * FROM presupuesto")
            data['presupuesto'] = [dict(row) for row in cursor.fetchall()]
            print(f"Exportados {len(data['presupuesto'])} presupuestos")
            
            return data
    except sqlite3.Error as e:
        print(f"Error al exportar datos: {e}")
        return None

def recreate_database(db_path):
    """Recrea la estructura de la base de datos."""
    try:
        # Si existe, eliminar la base de datos actual
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Base de datos eliminada: {db_path}")
        
        # Crear nueva base de datos
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.cursor()
            
            # Crear tabla cliente
            cursor.execute('''
                CREATE TABLE cliente (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    direccion TEXT,
                    telefono TEXT,
                    email TEXT,
                    notas TEXT
                )
            ''')
            
            # Crear tabla proyecto con campos opcionales
            cursor.execute('''
                CREATE TABLE proyecto (
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
            
            # Crear tabla presupuesto
            cursor.execute('''
                CREATE TABLE presupuesto (
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
            print("Estructura de base de datos recreada exitosamente")
            return True
    except sqlite3.Error as e:
        print(f"Error al recrear la base de datos: {e}")
        return False

def import_data(db_path, data):
    """Importa los datos previamente exportados a la nueva estructura."""
    if not data:
        print("No hay datos para importar")
        return False
    
    try:
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.cursor()
            
            # Importar clientes
            for cliente in data['cliente']:
                # Preparar los valores y las columnas dinámicamente
                columns = ', '.join(cliente.keys())
                placeholders = ', '.join(['?' for _ in cliente])
                values = list(cliente.values())
                
                # Ejecutar la inserción
                cursor.execute(
                    f"INSERT INTO cliente ({columns}) VALUES ({placeholders})",
                    values
                )
            
            # Importar proyectos
            for proyecto in data['proyecto']:
                columns = ', '.join(proyecto.keys())
                placeholders = ', '.join(['?' for _ in proyecto])
                values = list(proyecto.values())
                
                cursor.execute(
                    f"INSERT INTO proyecto ({columns}) VALUES ({placeholders})",
                    values
                )
            
            # Importar presupuestos
            for presupuesto in data['presupuesto']:
                columns = ', '.join(presupuesto.keys())
                placeholders = ', '.join(['?' for _ in presupuesto])
                values = list(presupuesto.values())
                
                cursor.execute(
                    f"INSERT INTO presupuesto ({columns}) VALUES ({placeholders})",
                    values
                )
            
            conn.commit()
            print(f"Datos importados: {len(data['cliente'])} clientes, {len(data['proyecto'])} proyectos, {len(data['presupuesto'])} presupuestos")
            return True
    except sqlite3.Error as e:
        print(f"Error al importar datos: {e}")
        return False

def main():
    """Función principal que ejecuta la reconstrucción de la base de datos."""
    db_path = "app.db"  # Ajusta esto a la ruta de tu base de datos
    
    print("=== Iniciando reconstrucción de la base de datos ===")
    
    # Hacer backup
    if not backup_database(db_path):
        response = input("No se pudo hacer backup. ¿Desea continuar de todos modos? (s/n): ")
        if response.lower() != 's':
            print("Operación cancelada por el usuario")
            return False
    
    # Exportar datos actuales
    data = export_data(db_path)
    if data is None:
        response = input("No se pudieron exportar los datos. ¿Desea continuar y crear una base de datos vacía? (s/n): ")
        if response.lower() != 's':
            print("Operación cancelada por el usuario")
            return False
    
    # Recrear estructura
    if not recreate_database(db_path):
        print("Error al recrear la estructura de la base de datos")
        return False
    
    # Importar datos
    if data and not import_data(db_path, data):
        print("Error al importar los datos")
        return False
    
    print("=== Reconstrucción de la base de datos completada ===")
    return True

if __name__ == "__main__":
    main()
