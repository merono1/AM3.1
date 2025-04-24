"""
Script avanzado para probar diferentes configuraciones de conexión a Neon
"""
import os
import time
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener la URL de conexión
db_url = os.environ.get('DATABASE_URL')

if not db_url:
    print("❌ ERROR: No se ha configurado DATABASE_URL en el archivo .env")
    sys.exit(1)

print("=== Test avanzado de conexión a Neon PostgreSQL ===")
print(f"URL de conexión: {db_url.split('@')[1] if '@' in db_url else 'configurada'}")

# Verificar si psycopg2 está instalado
try:
    import psycopg2
except ImportError:
    print("❌ ERROR: No se ha encontrado el módulo 'psycopg2'")
    print("   Instálalo con: pip install psycopg2-binary")
    sys.exit(1)

# Extraer componentes de la URL
if 'postgresql://' in db_url:
    db_url = db_url.replace('postgresql://', '')
    user_pass, host_db = db_url.split('@', 1)
    
    # Manejar posibles parámetros en la URL
    if '?' in host_db:
        host_db_parts = host_db.split('?', 1)
        host_db = host_db_parts[0]
        params = host_db_parts[1]
    else:
        params = ''
    
    host, db = host_db.split('/', 1)
    user, password = user_pass.split(':', 1)
    
    print("\nDetalles de conexión:")
    print(f"- Host: {host}")
    print(f"- Base de datos: {db}")
    print(f"- Usuario: {user}")
    print(f"- Parámetros: {params}")
    
    # Probar diferentes configuraciones
    configurations = [
        {"name": "Estándar (timeout: 10s)", "params": {"connect_timeout": 10}},
        {"name": "Timeout extendido (30s)", "params": {"connect_timeout": 30}},
        {"name": "Sin SSL", "params": {"connect_timeout": 15, "sslmode": "disable"}},
        {"name": "SSL requerido", "params": {"connect_timeout": 15, "sslmode": "require"}},
    ]
    
    for config in configurations:
        print(f"\n=== Probando configuración: {config['name']} ===")
        try:
            start_time = time.time()
            print(f"Conectando...")
            
            # Construir parámetros de conexión
            conn_params = {
                "dbname": db,
                "user": user,
                "password": password,
                "host": host,
                **config["params"]
            }
            
            conn = psycopg2.connect(**conn_params)
            elapsed = time.time() - start_time
            
            print(f"✅ Conexión exitosa: {elapsed:.2f} segundos")
            
            # Obtener información sobre el servidor
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"Versión: {version}")
            
            # Probar una consulta simple
            cursor.execute("SELECT current_timestamp;")
            timestamp = cursor.fetchone()[0]
            print(f"Hora del servidor: {timestamp}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Error: {e}")
            print(f"   Tiempo transcurrido: {elapsed:.2f} segundos")
else:
    print("❌ ERROR: La URL de conexión no parece ser una URL de PostgreSQL válida")
    print("   Debe comenzar con 'postgresql://'")

print("\n=== Prueba completada ===")
input("Presiona Enter para salir...")
