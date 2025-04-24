#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para inicializar correctamente la base de datos.
Crea todas las tablas según los modelos definidos en la aplicación.
"""

import os
import shutil
import sqlite3
from datetime import datetime
from contextlib import closing

# Asegurar que exista el directorio de datos
def ensure_data_dir():
    data_dir = os.path.join('app', 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✓ Directorio creado: {data_dir}")
    return data_dir

# Crear backup de la base de datos si existe
def backup_database(db_path):
    if not os.path.exists(db_path):
        print(f"No hay base de datos para respaldar en: {db_path}")
        return

    backup_dir = os.path.dirname(db_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"app_backup_{timestamp}.db")
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✓ Backup creado: {backup_path}")
    except Exception as e:
        print(f"❌ Error al crear backup: {str(e)}")

# Crear las tablas con la estructura correcta
def create_tables(db_path):
    try:
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.cursor()
            
            # Tabla clientes
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                tipo_via VARCHAR(20),
                nombre_via VARCHAR(100),
                numero_via VARCHAR(10),
                puerta VARCHAR(10),
                codigo_postal VARCHAR(10),
                poblacion VARCHAR(100),
                cif_nif VARCHAR(20),
                telefono1 VARCHAR(20),
                telefono2 VARCHAR(20),
                telefono3 VARCHAR(20),
                telefono4 VARCHAR(20),
                mail1 VARCHAR(100),
                mail2 VARCHAR(100),
                tipo_cliente VARCHAR(50),
                categoria_cliente VARCHAR(50),
                notas TEXT,
                fecha_creacion TIMESTAMP,
                fecha_modificacion TIMESTAMP
            )
            ''')
            
            # Tabla proyectos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS proyectos (
                id INTEGER PRIMARY KEY,
                id_cliente INTEGER,
                tipo_proyecto VARCHAR(50),
                calle VARCHAR(100),
                nombre_via VARCHAR(100),
                numero VARCHAR(10),
                puerta VARCHAR(10),
                codigo_postal VARCHAR(10),
                poblacion VARCHAR(100),
                nombre_proyecto VARCHAR(200),
                fecha_creacion TIMESTAMP,
                referencia VARCHAR(50) UNIQUE,
                fecha_modificacion TIMESTAMP,
                estado VARCHAR(50),
                FOREIGN KEY (id_cliente) REFERENCES clientes (id) ON DELETE CASCADE
            )
            ''')
            
            # Tabla presupuestos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS presupuestos (
                id INTEGER PRIMARY KEY,
                id_proyecto INTEGER NOT NULL,
                referencia VARCHAR(50) NOT NULL,
                fecha TIMESTAMP NOT NULL,
                tipo_via VARCHAR(20),
                nombre_via VARCHAR(100),
                numero_via VARCHAR(10),
                puerta VARCHAR(10),
                codigo_postal VARCHAR(10),
                poblacion VARCHAR(100),
                titulo VARCHAR(200),
                notas TEXT,
                tecnico_encargado VARCHAR(100),
                aprobacion VARCHAR(100),
                fecha_aprobacion TIMESTAMP,
                estado VARCHAR(50),
                fecha_modificacion TIMESTAMP,
                FOREIGN KEY (id_proyecto) REFERENCES proyectos (id) ON DELETE CASCADE
            )
            ''')
            
            # Tabla capitulos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS capitulos (
                id INTEGER PRIMARY KEY,
                id_presupuesto INTEGER NOT NULL,
                numero VARCHAR(20) NOT NULL,
                descripcion TEXT,
                FOREIGN KEY (id_presupuesto) REFERENCES presupuestos (id) ON DELETE CASCADE
            )
            ''')
            
            # Tabla partidas
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS partidas (
                id INTEGER PRIMARY KEY,
                id_presupuesto INTEGER NOT NULL,
                capitulo_numero VARCHAR(20) NOT NULL,
                numero VARCHAR(20),
                descripcion TEXT,
                unitario VARCHAR(20),
                cantidad FLOAT,
                precio FLOAT,
                total FLOAT,
                margen FLOAT,
                final FLOAT,
                FOREIGN KEY (id_presupuesto) REFERENCES presupuestos (id) ON DELETE CASCADE
            )
            ''')
            
            # Tabla proveedores (basado en modelos.proveedor)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS proveedores (
                id INTEGER PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                direccion VARCHAR(200),
                telefono VARCHAR(20),
                email VARCHAR(100),
                notas TEXT,
                fecha_creacion TIMESTAMP,
                fecha_modificacion TIMESTAMP
            )
            ''')
            
            # Tabla hojas_trabajo (basado en modelos.hoja_trabajo)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS hojas_trabajo (
                id INTEGER PRIMARY KEY,
                id_proyecto INTEGER NOT NULL,
                fecha TIMESTAMP NOT NULL,
                asunto VARCHAR(200),
                contenido TEXT,
                tecnico VARCHAR(100),
                estado VARCHAR(50),
                fecha_modificacion TIMESTAMP,
                FOREIGN KEY (id_proyecto) REFERENCES proyectos (id) ON DELETE CASCADE
            )
            ''')
            
            # Tabla facturas (basado en modelos.factura)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS facturas (
                id INTEGER PRIMARY KEY,
                id_cliente INTEGER NOT NULL,
                numero VARCHAR(50) NOT NULL,
                fecha TIMESTAMP NOT NULL,
                concepto TEXT,
                importe FLOAT,
                impuesto FLOAT,
                total FLOAT,
                estado VARCHAR(50),
                fecha_vencimiento TIMESTAMP,
                fecha_pago TIMESTAMP,
                FOREIGN KEY (id_cliente) REFERENCES clientes (id) ON DELETE CASCADE
            )
            ''')
            
            conn.commit()
            print("✓ Tablas creadas correctamente")
            return True
    except sqlite3.Error as e:
        print(f"❌ Error al crear tablas: {str(e)}")
        return False

def main():
    print("=== Inicializando base de datos ===")
    
    # Asegurar que exista el directorio
    data_dir = ensure_data_dir()
    
    # Ruta al archivo de base de datos
    db_path = os.path.join(data_dir, 'app.db')
    
    # Crear backup si existe
    backup_database(db_path)
    
    # Crear las tablas
    if create_tables(db_path):
        print("\n✅ Base de datos inicializada correctamente")
        print(f"   Ubicación: {db_path}")
    else:
        print("\n❌ No se pudo inicializar la base de datos")
    
    print("\nPuede iniciar la aplicación normalmente.")

if __name__ == "__main__":
    main()
