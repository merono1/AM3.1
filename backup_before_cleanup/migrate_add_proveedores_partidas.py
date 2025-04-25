"""
Script para añadir soporte de proveedores a partidas en PostgreSQL Neon
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Cargar variables de entorno
load_dotenv()

# Obtener URL de conexión a PostgreSQL
POSTGRES_URI = os.environ.get('DATABASE_URL')

if not POSTGRES_URI:
    print("❌ Error: Es necesario definir DATABASE_URL en el archivo .env")
    print("Formato esperado: postgresql://usuario:contraseña@ep-xxxxx.region.aws.neon.tech/nombre_db")
    sys.exit(1)

# Conectar a PostgreSQL
try:
    print(f"🔌 Conectando a PostgreSQL Neon...")
    conn = psycopg2.connect(POSTGRES_URI)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    print("✅ Conexión a PostgreSQL establecida")
except Exception as e:
    print(f"❌ Error al conectar a PostgreSQL: {e}")
    sys.exit(1)

# Ejecutar las migraciones
print("🔄 Aplicando migraciones...")

try:
    # 1. Verificar si existen las columnas necesarias en la tabla partidas_hojas
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'partidas_hojas' AND column_name IN ('id_proveedor_principal', 'precio_proveedor');
    """)
    existing_columns = [col[0] for col in cursor.fetchall()]
    
    # 2. Añadir las columnas a partidas_hojas si no existen
    if 'id_proveedor_principal' not in existing_columns:
        print("➕ Añadiendo columna id_proveedor_principal a la tabla partidas_hojas...")
        cursor.execute("ALTER TABLE partidas_hojas ADD COLUMN id_proveedor_principal INTEGER;")
    else:
        print("✓ La columna id_proveedor_principal ya existe")
    
    if 'precio_proveedor' not in existing_columns:
        print("➕ Añadiendo columna precio_proveedor a la tabla partidas_hojas...")
        cursor.execute("ALTER TABLE partidas_hojas ADD COLUMN precio_proveedor FLOAT;")
    else:
        print("✓ La columna precio_proveedor ya existe")
    
    # 3. Verificar si existe la restricción de clave foránea
    cursor.execute("""
        SELECT constraint_name FROM information_schema.table_constraints
        WHERE table_name = 'partidas_hojas' AND constraint_name = 'fk_partida_proveedor';
    """)
    fk_exists = cursor.fetchone()
    
    if not fk_exists:
        print("➕ Añadiendo restricción de clave foránea fk_partida_proveedor...")
        cursor.execute("""
            ALTER TABLE partidas_hojas 
            ADD CONSTRAINT fk_partida_proveedor 
            FOREIGN KEY (id_proveedor_principal) REFERENCES proveedores(id);
        """)
    else:
        print("✓ La restricción fk_partida_proveedor ya existe")
    
    # 4. Verificar si existe la tabla proveedores_partidas
    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_name = 'proveedores_partidas';
    """)
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("➕ Creando tabla proveedores_partidas...")
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
        
        print("➕ Creando índices para la tabla proveedores_partidas...")
        cursor.execute("CREATE INDEX ix_proveedores_partidas_id_partida ON proveedores_partidas(id_partida);")
        cursor.execute("CREATE INDEX ix_proveedores_partidas_id_proveedor ON proveedores_partidas(id_proveedor);")
    else:
        print("✓ La tabla proveedores_partidas ya existe")

    print("\n✅ Migración completada con éxito")
    
except Exception as e:
    print(f"❌ Error durante la migración: {e}")
    sys.exit(1)
finally:
    cursor.close()
    conn.close()

print("\n🔄 Reinicia la aplicación para que los cambios tengan efecto")
