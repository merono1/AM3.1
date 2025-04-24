import os
import sqlite3
import shutil
from datetime import datetime

# Rutas
DB_DIR = 'app/data'
DB_PATH = os.path.join(DB_DIR, 'app.db')

def reset_database():
    print("Iniciando reconstrucción de la base de datos...")
    
    # Crear respaldo de la base de datos actual
    if os.path.exists(DB_PATH):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(DB_DIR, f'app_backup_{timestamp}.db')
        try:
            shutil.copy2(DB_PATH, backup_path)
            print(f"Se ha creado una copia de seguridad en: {backup_path}")
        except Exception as e:
            print(f"Error al crear copia de seguridad: {str(e)}")
    
    # Eliminar base de datos actual
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            print("Base de datos anterior eliminada.")
    except Exception as e:
        print(f"Error al eliminar la base de datos: {str(e)}")
        return False
    
    # Crear nueva base de datos con la estructura correcta
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Crear las tablas necesarias
        cursor.execute('''
        CREATE TABLE clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo_via TEXT,
            nombre_via TEXT,
            numero_via TEXT,
            puerta TEXT,
            codigo_postal TEXT,
            poblacion TEXT,
            cif_nif TEXT,
            telefono1 TEXT,
            telefono2 TEXT,
            telefono3 TEXT,
            telefono4 TEXT,
            mail1 TEXT,
            mail2 TEXT,
            tipo_cliente TEXT,
            categoria_cliente TEXT,
            notas TEXT,
            fecha_creacion TIMESTAMP,
            fecha_modificacion TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER,
            tipo_proyecto TEXT,
            tipo_via TEXT,
            calle TEXT,
            nombre_via TEXT,
            numero TEXT,
            puerta TEXT,
            codigo_postal TEXT,
            poblacion TEXT,
            nombre_proyecto TEXT,
            fecha_creacion TIMESTAMP,
            referencia TEXT UNIQUE,
            fecha_modificacion TIMESTAMP,
            estado TEXT,
            FOREIGN KEY (id_cliente) REFERENCES clientes (id) ON DELETE CASCADE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE presupuestos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_proyecto INTEGER NOT NULL,
            referencia TEXT NOT NULL,
            fecha TIMESTAMP NOT NULL,
            tipo_via TEXT,
            nombre_via TEXT,
            numero_via TEXT,
            puerta TEXT,
            codigo_postal TEXT,
            poblacion TEXT,
            titulo TEXT,
            notas TEXT,
            tecnico_encargado TEXT,
            aprobacion TEXT,
            fecha_aprobacion TIMESTAMP,
            estado TEXT,
            estado_workflow TEXT DEFAULT 'En estudio',
            fecha_modificacion TIMESTAMP,
            FOREIGN KEY (id_proyecto) REFERENCES proyectos (id) ON DELETE CASCADE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE capitulos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_presupuesto INTEGER NOT NULL,
            numero TEXT NOT NULL,
            descripcion TEXT,
            FOREIGN KEY (id_presupuesto) REFERENCES presupuestos (id) ON DELETE CASCADE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE partidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_presupuesto INTEGER NOT NULL,
            capitulo_numero TEXT NOT NULL,
            numero TEXT,
            descripcion TEXT,
            unitario TEXT,
            cantidad REAL,
            precio REAL,
            total REAL,
            margen REAL,
            final REAL,
            FOREIGN KEY (id_presupuesto) REFERENCES presupuestos (id) ON DELETE CASCADE
        )
        ''')
        
        # Añadir datos de muestra (cliente y proyecto)
        cursor.execute('''
        INSERT INTO clientes (nombre, tipo_via, nombre_via, numero_via, poblacion)
        VALUES ('Juan Vicente', 'Calle', 'Principal', '1', 'Madrid')
        ''')
        
        cliente_id = cursor.lastrowid
        
        cursor.execute('''
        INSERT INTO proyectos (id_cliente, tipo_proyecto, nombre_proyecto, referencia, fecha_creacion)
        VALUES (?, 'Reforma', 'Reforma del patio', '2025-0001', datetime('now'))
        ''', (cliente_id,))
        
        # Guardar cambios
        conn.commit()
        conn.close()
        
        print("Base de datos creada correctamente con la estructura actualizada.")
        return True
        
    except Exception as e:
        print(f"Error al crear la nueva base de datos: {str(e)}")
        return False

if __name__ == "__main__":
    if reset_database():
        print("Proceso completado con éxito.")
    else:
        print("El proceso no pudo completarse. Revise los errores.")