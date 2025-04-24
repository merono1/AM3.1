"""
Script para agregar la columna tipo_via a la tabla proyectos
"""
import sqlite3
import os
from contextlib import closing

# Ruta de la base de datos
db_path = os.path.join('app', 'data', 'app.db')
backup_path = os.path.join('app', 'data', f"app_backup_tipovia.db")

def backup_database():
    """Crear una copia de seguridad de la base de datos"""
    try:
        if os.path.exists(db_path):
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"✅ Copia de seguridad creada en {backup_path}")
            return True
        else:
            print(f"❌ No se encontró la base de datos en {db_path}")
            return False
    except Exception as e:
        print(f"❌ Error al crear copia de seguridad: {str(e)}")
        return False

def add_tipo_via_column():
    """Añadir la columna tipo_via a la tabla proyectos"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la tabla proyectos existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='proyectos'")
        if not cursor.fetchone():
            print("❌ La tabla 'proyectos' no existe en la base de datos")
            return False
        
        # Verificar si la columna tipo_via ya existe
        cursor.execute("PRAGMA table_info(proyectos)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'tipo_via' in columns:
            print("ℹ️ La columna 'tipo_via' ya existe en la tabla proyectos")
            return True
            
        # Añadir la columna
        print("Añadiendo columna 'tipo_via' a la tabla proyectos...")
        cursor.execute("ALTER TABLE proyectos ADD COLUMN tipo_via VARCHAR(20)")
        conn.commit()
        
        # Verificar que se haya añadido correctamente
        cursor.execute("PRAGMA table_info(proyectos)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'tipo_via' in columns:
            print("✅ Columna 'tipo_via' añadida correctamente")
            result = True
        else:
            print("❌ No se pudo añadir la columna 'tipo_via'")
            result = False
            
        conn.close()
        return result
    
    except Exception as e:
        print(f"❌ Error al modificar la base de datos: {str(e)}")
        return False

def check_database():
    """Verificar el estado de la base de datos"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ver columnas de la tabla proyectos
        cursor.execute("PRAGMA table_info(proyectos)")
        columns = cursor.fetchall()
        print("\nColumnas en la tabla 'proyectos':")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"❌ Error al verificar la base de datos: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Añadiendo columna 'tipo_via' a la tabla proyectos ===")
    
    # Crear copia de seguridad
    print("\n[1/3] Creando copia de seguridad...")
    if not backup_database():
        respuesta = input("No se pudo crear copia de seguridad. ¿Desea continuar? (s/n): ")
        if respuesta.lower() != 's':
            print("Operación cancelada.")
            exit()
    
    # Verificar estado actual
    print("\n[2/3] Verificando estado actual de la base de datos...")
    check_database()
    
    # Añadir columna
    print("\n[3/3] Intentando agregar la columna 'tipo_via'...")
    if add_tipo_via_column():
        print("\n✅ Operación completada con éxito")
        print("Ahora puede reiniciar la aplicación para que los cambios surtan efecto.")
    else:
        print("\n❌ No se pudo completar la operación")
    
    print("\nVerificación final de la base de datos:")
    check_database()
