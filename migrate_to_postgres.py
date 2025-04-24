"""
Script para migrar la base de datos de SQLite a PostgreSQL (Neon)
"""
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
import sqlite3
import csv
import io
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Cargar variables de entorno
load_dotenv()

# Configuración básica
BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB_PATH = os.environ.get('DB_PATH') or str(BASE_DIR / 'app' / 'data' / 'app.db')
POSTGRES_URI = os.environ.get('DATABASE_URL')

if not POSTGRES_URI:
    print("❌ Error: Es necesario definir DATABASE_URL en el archivo .env")
    print("Formato esperado: postgresql://usuario:contraseña@ep-xxxxx.region.aws.neon.tech/nombre_db")
    sys.exit(1)

# Verificar que el archivo SQLite existe
if not Path(SQLITE_DB_PATH).exists():
    print(f"❌ Error: No se encontró la base de datos SQLite en {SQLITE_DB_PATH}")
    sys.exit(1)

print(f"🔍 Analizando base de datos SQLite: {SQLITE_DB_PATH}")

# Conectar a la base de datos SQLite
sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
sqlite_conn.row_factory = sqlite3.Row
sqlite_cursor = sqlite_conn.cursor()

# Obtener todas las tablas de SQLite
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row['name'] for row in sqlite_cursor.fetchall() if not row['name'].startswith('sqlite_')]

if not tables:
    print("⚠️ No se encontraron tablas en la base de datos SQLite")
    sys.exit(1)

print(f"📋 Tablas encontradas en SQLite: {', '.join(tables)}")

# Conectar a PostgreSQL
try:
    print(f"🔌 Conectando a PostgreSQL: {POSTGRES_URI}")
    pg_conn = psycopg2.connect(POSTGRES_URI)
    pg_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    pg_cursor = pg_conn.cursor()
except Exception as e:
    print(f"❌ Error al conectar a PostgreSQL: {e}")
    sys.exit(1)

print("✅ Conexión a PostgreSQL establecida")

# Crear las tablas en PostgreSQL usando modelos de SQLAlchemy
print("🔄 Creando tablas en PostgreSQL usando SQLAlchemy...")

# Modificar temporalmente el .env para usar PostgreSQL
env_backup = None
env_path = BASE_DIR / '.env'
if env_path.exists():
    with open(env_path, 'r') as f:
        env_backup = f.read()
    
    # Reemplazar SQLite con PostgreSQL en .env
    with open(env_path, 'w') as f:
        env_content = env_backup
        if 'DB_PATH=' in env_content:
            env_content = env_content.replace('DB_PATH=', '# DB_PATH=')
        if 'DATABASE_URL=' not in env_content:
            env_content += f"\nDATABASE_URL={POSTGRES_URI}"
        f.write(env_content)

# Importar modelos y crear tablas
try:
    # Modificamos temporalmente la configuración para usar PostgreSQL
    from app.config import Config
    original_uri = Config.SQLALCHEMY_DATABASE_URI
    Config.SQLALCHEMY_DATABASE_URI = POSTGRES_URI
    
    # Crear app y tablas
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    # Importar modelos
    from app.models.cliente import Cliente
    from app.models.proyecto import Proyecto
    from app.models.presupuesto import Presupuesto, Capitulo, Partida
    from app.models.proveedor import Proveedor
    from app.models.hoja_trabajo import HojaTrabajo, CapituloHoja, PartidaHoja
    from app.models.factura import Factura, LineaFactura
    
    with app.app_context():
        db.create_all()
    
    # Restaurar la configuración original
    Config.SQLALCHEMY_DATABASE_URI = original_uri
    print("✅ Tablas creadas en PostgreSQL")
except Exception as e:
    print(f"❌ Error al crear tablas en PostgreSQL: {e}")
    if env_backup:
        # Restaurar el .env original
        with open(env_path, 'w') as f:
            f.write(env_backup)
    sys.exit(1)

# Migrar datos tabla por tabla
print("\n📦 Migrando datos de SQLite a PostgreSQL...")

for table in tables:
    try:
        # Obtener datos de SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"  ℹ️ Tabla '{table}' vacía, omitiendo")
            continue
        
        # Obtener nombres de columnas
        column_names = [column[0] for column in sqlite_cursor.description]
        
        print(f"  🔄 Migrando tabla '{table}' ({len(rows)} filas)")
        
        # Preparar consulta de inserción para PostgreSQL
        columns_str = ', '.join([f'"{col}"' for col in column_names])
        placeholders = ', '.join(['%s' for _ in column_names])
        insert_query = f'INSERT INTO {table} ({columns_str}) VALUES ({placeholders})'
        
        # Insertar datos en PostgreSQL
        for row in rows:
            # Convertir row a lista de valores
            values = [row[col] for col in column_names]
            pg_cursor.execute(insert_query, values)
        
        print(f"  ✅ Datos migrados para tabla '{table}'")
    except Exception as e:
        print(f"  ❌ Error migrando tabla '{table}': {e}")

# Cerrar conexiones
sqlite_conn.close()
pg_conn.close()

# Restaurar .env si hicimos backup
if env_backup:
    with open(env_path, 'w') as f:
        f.write(env_backup)

# Actualizar .env.example para incluir DB_URL
env_example_path = BASE_DIR / '.env.example'
if env_example_path.exists():
    with open(env_example_path, 'r') as f:
        env_example = f.read()
    
    # Añadir DATABASE_URL si no existe
    if 'DATABASE_URL=' not in env_example:
        with open(env_example_path, 'w') as f:
            f.write(env_example + "\n# URL para PostgreSQL\nDATABASE_URL=postgresql://usuario:contraseña@host:puerto/nombre_db\n")

# Crear un nuevo archivo .env con ambas opciones
with open(BASE_DIR / '.env.postgres', 'w') as f:
    f.write(f"""FLASK_ENV=development
SECRET_KEY=tu_clave_secreta_de_desarrollo
PORT=5000
# SQLite (configuración anterior)
# DB_PATH={SQLITE_DB_PATH}
# PostgreSQL (configuración nueva)
DATABASE_URL={POSTGRES_URI}
""")

print("\n✅ Migración completada con éxito")
print("""
🔄 Próximos pasos:

1. Para usar PostgreSQL de forma permanente:
   - Actualiza tu archivo .env para incluir DATABASE_URL
   - Comenta o elimina la línea DB_PATH

2. Es recomendable modificar app/config.py para usar PostgreSQL de forma nativa:
   - Abre app/config.py
   - Actualiza la clase Config para usar DATABASE_URL si está disponible
   
3. Prueba tu aplicación con la nueva base de datos:
   - Ejecuta 'python main.py'
   - Verifica que todo funcione correctamente

Se ha creado un archivo '.env.postgres' con la configuración recomendada
para usar PostgreSQL. Puedes renombrarlo a '.env' cuando estés listo.
""")
