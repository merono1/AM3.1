import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def run_migration():
    # Obtener información de conexión desde variables de entorno o usar valores predeterminados
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'app_db')
    db_user = os.environ.get('DB_USER', 'postgres')
    db_pass = os.environ.get('DB_PASS', 'postgres')
    
    # Conectar a la base de datos
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_pass
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        print(f"Conectado a la base de datos: {db_name} en {db_host}:{db_port}")
    except psycopg2.Error as e:
        print(f"Error de conexión a la base de datos: {e}")
        sys.exit(1)
    
    try:
        # Verificar si existen las columnas necesarias en la tabla partidas_hojas
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'partidas_hojas' AND column_name IN ('id_proveedor_principal', 'precio_proveedor');
        """)
        existing_columns = [col[0] for col in cursor.fetchall()]
        
        # Añadir las columnas a partidas_hojas si no existen
        if 'id_proveedor_principal' not in existing_columns:
            print("Añadiendo columna id_proveedor_principal a la tabla partidas_hojas...")
            cursor.execute("ALTER TABLE partidas_hojas ADD COLUMN id_proveedor_principal INTEGER;")
        
        if 'precio_proveedor' not in existing_columns:
            print("Añadiendo columna precio_proveedor a la tabla partidas_hojas...")
            cursor.execute("ALTER TABLE partidas_hojas ADD COLUMN precio_proveedor FLOAT;")
        
        # Verificar si existe la restricción de clave foránea
        cursor.execute("""
            SELECT constraint_name FROM information_schema.table_constraints
            WHERE table_name = 'partidas_hojas' AND constraint_name = 'fk_partida_proveedor';
        """)
        fk_exists = cursor.fetchone()
        
        if not fk_exists:
            print("Añadiendo restricción de clave foránea fk_partida_proveedor...")
            cursor.execute("""
                ALTER TABLE partidas_hojas 
                ADD CONSTRAINT fk_partida_proveedor 
                FOREIGN KEY (id_proveedor_principal) REFERENCES proveedores(id);
            """)
        
        # Verificar si existe la tabla proveedores_partidas
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_name = 'proveedores_partidas';
        """)
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Creando tabla proveedores_partidas...")
            cursor.execute("""
                CREATE TABLE proveedores_partidas (
                    id SERIAL PRIMARY KEY,
                    id_partida INTEGER NOT NULL,
                    id_proveedor INTEGER NOT NULL,
                    precio FLOAT,
                    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notas TEXT,
                    estado VARCHAR(50) DEFAULT 'Pendiente',
                    CONSTRAINT fk_provpart_partida FOREIGN KEY (id_partida) 
                        REFERENCES partidas_hojas(id) ON DELETE CASCADE,
                    CONSTRAINT fk_provpart_proveedor FOREIGN KEY (id_proveedor) 
                        REFERENCES proveedores(id) ON DELETE CASCADE
                );
            """)
            
            print("Creando índices para la tabla proveedores_partidas...")
            cursor.execute("CREATE INDEX ix_proveedores_partidas_id_partida ON proveedores_partidas(id_partida);")
            cursor.execute("CREATE INDEX ix_proveedores_partidas_id_proveedor ON proveedores_partidas(id_proveedor);")
        
        # Confirmar cambios
        conn.commit()
        
        # Verificar la estructura final
        print("\nVerificando estructura de la base de datos...")
        
        # Verificar columnas de partidas_hojas
        cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'partidas_hojas';")
        columns = cursor.fetchall()
        print("\nColumnas de la tabla partidas_hojas:")
        for column in columns:
            print(f"- {column[0]} ({column[1]})")
        
        # Verificar columnas de proveedores_partidas si existe
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_name = 'proveedores_partidas';
        """)
        if cursor.fetchone():
            cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'proveedores_partidas';")
            columns = cursor.fetchall()
            print("\nColumnas de la tabla proveedores_partidas:")
            for column in columns:
                print(f"- {column[0]} ({column[1]})")
        
        print("\nMigración completada exitosamente!")
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error durante la migración: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("\nIniciando migración para añadir soporte de proveedores a partidas...")
    run_migration()
