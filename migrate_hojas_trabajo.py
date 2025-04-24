# migrate_hojas_trabajo.py
"""
Script para migrar las hojas de trabajo de estar vinculadas a proyectos 
a estar vinculadas directamente a presupuestos.
"""
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
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
Session = sessionmaker(bind=engine)
session = Session()

def check_column_exists(table, column):
    """Verifica si una columna existe en una tabla"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT {column} FROM {table} LIMIT 1"))
            return True
    except Exception:
        return False

def main():
    """Función principal del script de migración"""
    print("Iniciando migración de hojas de trabajo...")
    
    # Verificar si la columna id_presupuesto ya existe
    if check_column_exists('hojas_trabajo', 'id_presupuesto'):
        print("La columna id_presupuesto ya existe en la tabla hojas_trabajo")
    else:
        print("Añadiendo columna id_presupuesto a la tabla hojas_trabajo...")
        try:
            # Agregar la nueva columna con una nueva conexión
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE hojas_trabajo ADD COLUMN id_presupuesto INTEGER"))
                conn.commit()
            print("Columna id_presupuesto añadida correctamente")
        except Exception as e:
            print(f"Error al añadir columna id_presupuesto: {str(e)}")
            if "duplicate column name" in str(e).lower():
                print("La columna ya existe, continuando con la migración...")
            else:
                sys.exit(1)
    
    # Obtener todas las hojas de trabajo
    print("Obteniendo todas las hojas de trabajo...")
    hojas = []
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, id_proyecto, referencia FROM hojas_trabajo"))
            hojas = result.fetchall()
        print(f"Se encontraron {len(hojas)} hojas de trabajo")
    except Exception as e:
        print(f"Error al obtener hojas de trabajo: {str(e)}")
        sys.exit(1)
    
    # Para cada hoja, buscar un presupuesto que pertenezca al mismo proyecto
    # y actualizar la referencia con formato "XxxxHT"
    print("Asociando hojas de trabajo con presupuestos...")
    actualizaciones = []

    with engine.connect() as conn:
        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
        
        for hoja in hojas:
            hoja_id = hoja[0]
            proyecto_id = hoja[1]
            hoja_ref = hoja[2]
            
            # Buscar un presupuesto asociado al proyecto
            try:
                result = conn.execute(
                    text("SELECT id, referencia FROM presupuestos WHERE id_proyecto = :proyecto_id ORDER BY id DESC LIMIT 1"),
                    {"proyecto_id": proyecto_id}
                )
                presupuesto = result.fetchone()
                
                if presupuesto:
                    presupuesto_id = presupuesto[0]
                    presupuesto_ref = presupuesto[1]
                    nueva_ref = f"{presupuesto_ref}HT"
                    
                    # Actualizar la hoja de trabajo
                    print(f"Actualizando hoja ID {hoja_id}: {hoja_ref} -> {nueva_ref}")
                    conn.execute(
                        text("UPDATE hojas_trabajo SET id_presupuesto = :presupuesto_id, referencia = :nueva_ref WHERE id = :hoja_id"),
                        {"presupuesto_id": presupuesto_id, "nueva_ref": nueva_ref, "hoja_id": hoja_id}
                    )
                    actualizaciones.append(f"Hoja {hoja_id} vinculada a presupuesto {presupuesto_id}")
                else:
                    print(f"ADVERTENCIA: No se encontró presupuesto para la hoja ID {hoja_id} (Proyecto ID {proyecto_id})")
            except Exception as e:
                print(f"Error al procesar hoja ID {hoja_id}: {str(e)}")
    
    # Confirmar cambios
    try:
        session.commit()
        print("Migración completada con éxito")
    except Exception as e:
        session.rollback()
        print(f"Error al guardar los cambios: {str(e)}")
        sys.exit(1)
    
    # Crear índice para la nueva columna
    try:
        session.execute(text("CREATE INDEX IF NOT EXISTS idx_hojas_trabajo_presupuesto ON hojas_trabajo (id_presupuesto)"))
        session.commit()
        print("Índice creado correctamente para la columna id_presupuesto")
    except Exception as e:
        session.rollback()
        print(f"Error al crear índice: {str(e)}")
    
    print("Proceso de migración finalizado")

if __name__ == "__main__":
    main()
