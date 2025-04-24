
"""
Script para añadir el campo 'final_proveedor' a la tabla ProveedorPartida
y permitir asignar varios proveedores a una partida
"""

import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Determinar si se usa PostgreSQL o SQLite
using_postgres = os.environ.get('DATABASE_URL') is not None

if using_postgres:
    from sqlalchemy import create_engine
    # Conectar a PostgreSQL
    engine = create_engine(os.environ.get('DATABASE_URL'), isolation_level="AUTOCOMMIT")
    print(f"✅ Conectado a PostgreSQL: {os.environ.get('DATABASE_URL').split('@')[1] if '@' in os.environ.get('DATABASE_URL') else 'configurada'}")
else:
    from sqlalchemy import create_engine
    # Conectar a SQLite
    db_path = os.environ.get('DB_PATH', 'app/data/app.db')
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
    engine = create_engine(f'sqlite:///{db_path}', isolation_level="AUTOCOMMIT")
    print(f"✅ Conectado a SQLite: {db_path}")

def ejecutar_migracion():
    """Ejecuta la migración para añadir final_proveedor y permitir múltiples proveedores"""
    try:
        # Verificar primero si la tabla proveedores_partidas existe
        try:
            with engine.connect() as conn:
                if using_postgres:
                    result = conn.execute(text(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'proveedores_partidas'
                        )
                        """
                    ))
                    tabla_existe = result.scalar()
                else:
                    result = conn.execute(text(
                        """
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='proveedores_partidas'
                        """
                    ))
                    tabla_existe = result.fetchone() is not None
                
                if not tabla_existe:
                    print(f"⚠️ La tabla 'proveedores_partidas' no existe. Creando la tabla...")
                    crear_tabla_proveedores_partidas(conn)
        except Exception as e:
            print(f"❌ Error al verificar si existe la tabla: {e}")
            return False
            
        # Paso 1: Añadir columna 'final_proveedor' a la tabla 'proveedores_partidas'
        # Esta columna almacenará el precio final aplicando margen específico por proveedor
        columna_ya_existe = False
        
        try:
            # Comprobar si la columna ya existe
            with engine.connect() as conn:
                if using_postgres:
                    result = conn.execute(text(
                        """
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'proveedores_partidas' 
                        AND column_name = 'final_proveedor'
                        """
                    ))
                    columna_ya_existe = result.fetchone() is not None
                else:
                    result = conn.execute(text(
                        """
                        PRAGMA table_info(proveedores_partidas)
                        """
                    ))
                    column_names = [row[1] for row in result.fetchall()]
                    columna_ya_existe = 'final_proveedor' in column_names
                    
        except Exception as e:
            print(f"Error al verificar si existe la columna: {e}")
            return False
        
        # Añadir la columna si no existe
        if not columna_ya_existe:
            try:
                with engine.connect() as conn:
                    conn.execute(text(
                        """
                        ALTER TABLE proveedores_partidas
                        ADD COLUMN final_proveedor FLOAT
                        """
                    ))
                print("✅ Columna 'final_proveedor' añadida correctamente")
            except Exception as e:
                print(f"❌ Error al añadir columna 'final_proveedor': {e}")
                return False
        else:
            print("✅ Columna 'final_proveedor' ya existe")
            
        # Paso 2: Añadir columna 'margen_proveedor' a la tabla 'proveedores_partidas'
        columna_ya_existe = False
        
        try:
            # Comprobar si la columna ya existe
            with engine.connect() as conn:
                if using_postgres:
                    result = conn.execute(text(
                        """
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'proveedores_partidas' 
                        AND column_name = 'margen_proveedor'
                        """
                    ))
                    columna_ya_existe = result.fetchone() is not None
                else:
                    result = conn.execute(text(
                        """
                        PRAGMA table_info(proveedores_partidas)
                        """
                    ))
                    column_names = [row[1] for row in result.fetchall()]
                    columna_ya_existe = 'margen_proveedor' in column_names
                    
        except Exception as e:
            print(f"Error al verificar si existe la columna: {e}")
            return False
        
        # Añadir la columna si no existe
        if not columna_ya_existe:
            try:
                with engine.connect() as conn:
                    conn.execute(text(
                        """
                        ALTER TABLE proveedores_partidas
                        ADD COLUMN margen_proveedor FLOAT
                        """
                    ))
                print("✅ Columna 'margen_proveedor' añadida correctamente")
            except Exception as e:
                print(f"❌ Error al añadir columna 'margen_proveedor': {e}")
                return False
        else:
            print("✅ Columna 'margen_proveedor' ya existe")
        
        # Opcional: Inicializar valores para las columnas añadidas
        try:
            with engine.connect() as conn:
                conn.execute(text(
                    """
                    UPDATE proveedores_partidas 
                    SET margen_proveedor = 0,
                        final_proveedor = precio
                    WHERE margen_proveedor IS NULL
                    """
                ))
            print("✅ Valores inicializados para las nuevas columnas")
        except Exception as e:
            print(f"⚠️ Advertencia al inicializar valores: {e}")
        
        print("✅ Migración completada con éxito")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando migración para añadir campo 'final_proveedor' a proveedores_partidas...")
    resultado = ejecutar_migracion()
    
    if resultado:
        print("\n✅ Migración completada exitosamente")
        print("\nAhora puedes usar la funcionalidad de múltiples proveedores y campo final_proveedor")
    else:
        print("\n❌ La migración ha fallado")
        sys.exit(1)
    
def crear_tabla_proveedores_partidas(conn):
    """Crea la tabla proveedores_partidas si no existe"""
    try:
        if using_postgres:
            conn.execute(text("""
            CREATE TABLE proveedores_partidas (
                id SERIAL PRIMARY KEY,
                id_partida INTEGER NOT NULL REFERENCES partidas_hojas(id) ON DELETE CASCADE,
                id_proveedor INTEGER NOT NULL REFERENCES proveedores(id) ON DELETE CASCADE,
                precio FLOAT,
                fecha_asignacion TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
                notas TEXT,
                estado VARCHAR(50) DEFAULT 'Pendiente',
                margen_proveedor FLOAT DEFAULT 0,
                final_proveedor FLOAT
            )
            """))
        else:
            conn.execute(text("""
            CREATE TABLE proveedores_partidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_partida INTEGER NOT NULL REFERENCES partidas_hojas(id) ON DELETE CASCADE,
                id_proveedor INTEGER NOT NULL REFERENCES proveedores(id) ON DELETE CASCADE,
                precio FLOAT,
                fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notas TEXT,
                estado VARCHAR(50) DEFAULT 'Pendiente',
                margen_proveedor FLOAT DEFAULT 0,
                final_proveedor FLOAT
            )
            """))
            
        print("✅ Tabla 'proveedores_partidas' creada correctamente")
        return True
    except Exception as e:
        print(f"❌ Error al crear tabla 'proveedores_partidas': {e}")
        return False
