# update_constraint_hojas_trabajo.py
"""
Script para modificar la restricción NOT NULL de la columna id_proyecto
en la tabla hojas_trabajo.
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de base de datos
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    db_path = os.environ.get('DB_PATH', 'app/data/app.db')
    db_url = f'sqlite:///{db_path}'

# Crear conexión a la base de datos
print(f"Conectando a la base de datos: {db_url}")
engine = create_engine(db_url)

def main():
    """Función principal del script"""
    print("Modificando restricción NOT NULL en la columna id_proyecto...")
    
    try:
        # Usar AUTOCOMMIT para evitar problemas con transacciones
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            # Paso 1: Modificar la columna id_proyecto para permitir valores NULL
            print("Cambiando id_proyecto a nullable...")
            conn.execute(text("ALTER TABLE hojas_trabajo ALTER COLUMN id_proyecto DROP NOT NULL"))
            print("Restricción NOT NULL eliminada correctamente")
            
            # Paso 2: Verificar que id_presupuesto tiene la restricción NOT NULL
            print("Verificando restricción NOT NULL en id_presupuesto...")
            conn.execute(text("ALTER TABLE hojas_trabajo ALTER COLUMN id_presupuesto SET NOT NULL"))
            print("Restricción NOT NULL establecida en id_presupuesto")
        
        print("Modificación de restricciones completada con éxito")
        
    except Exception as e:
        print(f"Error al modificar restricciones: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
