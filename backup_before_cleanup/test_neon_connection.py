import psycopg2
import os
from dotenv import load_dotenv
import time

# Cargar variables de entorno
load_dotenv()

# Obtener la URL de conexión
db_url = os.environ.get('DATABASE_URL')

if not db_url:
    print("❌ ERROR: No se ha configurado DATABASE_URL en el archivo .env")
    exit(1)

print(f"Intentando conectar a: {db_url.split('@')[1]}")
print("Esto puede tardar unos segundos...")

try:
    # Establecer un tiempo límite para la conexión (10 segundos)
    start_time = time.time()
    conn = psycopg2.connect(db_url, connect_timeout=10)
    elapsed = time.time() - start_time
    
    print(f"✅ ¡Conexión exitosa! (tiempo: {elapsed:.2f}s)")
    
    # Obtener información sobre el servidor
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"Versión del servidor: {version}")
    
    # Listar tablas
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    
    if tables:
        print("\nTablas disponibles:")
        for table in tables:
            print(f" - {table[0]}")
    else:
        print("\nNo se encontraron tablas en la base de datos.")
    
    # Cerrar conexión
    cursor.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"❌ Error de conexión: {e}")
    print("\nPosibles soluciones:")
    print("1. Verifica que la cadena de conexión DATABASE_URL sea correcta")
    print("2. Comprueba si el servidor Neon está activo")
    print("3. Verifica si hay restricciones de IP (necesitas estar en una red permitida)")
    print("4. Tu contraseña puede haber expirado o cambiado")
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")

input("\nPresiona Enter para salir...")
