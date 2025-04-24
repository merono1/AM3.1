import sqlite3
import os
from datetime import datetime

# Ruta a la base de datos
DB_PATH = os.path.join('app', 'data', 'app.db')
print(f"Usando base de datos en: {os.path.abspath(DB_PATH)}")

def add_estado_workflow_column():
    print("Verificando si existe la columna estado_workflow en presupuestos...")
    
    # Crear una copia de seguridad antes de modificar
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join('app', 'data', f'app_backup_{timestamp}.db')
    
    try:
        # Conectarse a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar si la base de datos existe y tiene la tabla presupuestos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='presupuestos'")
        if not cursor.fetchone():
            print("La tabla 'presupuestos' no existe en la base de datos.")
            conn.close()
            return False
        
        # Verificar si ya existe la columna
        cursor.execute("PRAGMA table_info(presupuestos)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'estado_workflow' in column_names:
            print("La columna 'estado_workflow' ya existe en la tabla 'presupuestos'.")
            conn.close()
            return True
        
        # Hacer una copia de seguridad
        print(f"Creando copia de seguridad de la base de datos en {backup_path}...")
        with open(DB_PATH, 'rb') as source:
            with open(backup_path, 'wb') as dest:
                dest.write(source.read())
        
        # Añadir la columna a la tabla
        print("Añadiendo columna 'estado_workflow' a la tabla 'presupuestos'...")
        cursor.execute("ALTER TABLE presupuestos ADD COLUMN estado_workflow TEXT DEFAULT 'En estudio'")
        
        # Confirmar los cambios
        conn.commit()
        print("Columna 'estado_workflow' añadida correctamente.")
        
        # Cerrar la conexión
        conn.close()
        # Comprobar si se ha añadido la columna
        cursor.execute("PRAGMA table_info(presupuestos)")
        columns_after = cursor.fetchall()
        column_names_after = [column[1] for column in columns_after]
        
        if 'estado_workflow' in column_names_after:
            print("Verificación: La columna 'estado_workflow' se ha añadido correctamente.")
            return True
        else:
            print("ERROR: La columna 'estado_workflow' no se ha añadido correctamente.")
            return False
        
    except Exception as e:
        print(f"Error al modificar la base de datos: {str(e)}")
        # Intentar restaurar desde la copia de seguridad si hubo error
        if os.path.exists(backup_path):
            try:
                print("Intentando restaurar desde la copia de seguridad...")
                os.replace(backup_path, DB_PATH)
                print("Restauración completada.")
            except Exception as restore_error:
                print(f"Error al restaurar: {str(restore_error)}")
        return False

if __name__ == "__main__":
    if add_estado_workflow_column():
        print("Operación completada con éxito.")
    else:
        print("La operación no se pudo completar correctamente.")
