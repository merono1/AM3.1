"""
Script para reparar la base de datos y agregar la columna numero a la tabla partidas
"""
import sqlite3
import os

# Configuración
db_path = os.path.join('app', 'data', 'app.db')
backup_path = os.path.join('app', 'data', 'app_backup.db')

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

def add_column():
    """Añadir la columna numero a la tabla partidas"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la tabla partidas existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='partidas'")
        if not cursor.fetchone():
            print("❌ La tabla 'partidas' no existe en la base de datos")
            return False
        
        # Verificar si la columna numero ya existe
        cursor.execute("PRAGMA table_info(partidas)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'numero' in columns:
            print("ℹ️ La columna 'numero' ya existe en la tabla partidas")
            return True
            
        # Añadir la columna
        print("Añadiendo columna 'numero' a la tabla partidas...")
        cursor.execute("ALTER TABLE partidas ADD COLUMN numero VARCHAR(20)")
        conn.commit()
        
        # Verificar que se haya añadido correctamente
        cursor.execute("PRAGMA table_info(partidas)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'numero' in columns:
            print("✅ Columna 'numero' añadida correctamente")
            result = True
        else:
            print("❌ No se pudo añadir la columna 'numero'")
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
        
        # Listar todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("\nTablas en la base de datos:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Ver columnas de la tabla partidas
        cursor.execute("PRAGMA table_info(partidas)")
        columns = cursor.fetchall()
        print("\nColumnas en la tabla 'partidas':")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"❌ Error al verificar la base de datos: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Utilidad de reparación de la base de datos ===")
    
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
    print("\n[3/3] Intentando agregar la columna 'numero'...")
    if add_column():
        print("\n✅ Operación completada con éxito")
        print("Ahora puede reiniciar la aplicación para que los cambios surtan efecto.")
    else:
        print("\n❌ No se pudo completar la operación")
        print("Puede intentar usar la versión alternativa de las rutas para crear partidas.")
        print("Instrucciones en el archivo README.md")
    
    print("\nVerificación final de la base de datos:")
    check_database()
