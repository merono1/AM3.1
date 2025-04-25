"""
Script para diagnosticar problemas de conexión a Neon PostgreSQL con detalle
"""
import os
import sys
import time
import traceback
from dotenv import load_dotenv

print("=== Diagnóstico detallado de conexión a PostgreSQL en Neon ===")

# Cargar variables de entorno
print("1. Cargando variables de entorno...")
load_dotenv()

# Verificar datos de conexión
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("❌ ERROR: No se ha configurado DATABASE_URL en el archivo .env")
    sys.exit(1)

print(f"2. URL de conexión encontrada: {db_url.split('@')[1] if '@' in db_url else 'configurada'}")

# Verificar si tiene el parámetro sslmode
if '?sslmode=' not in db_url and 'sslmode=' not in db_url:
    print("⚠️ ADVERTENCIA: La URL no contiene el parámetro sslmode (requerido por Neon)")
else:
    print("✅ Parámetro SSL configurado correctamente")

# Verificar instalación de psycopg2
print("\n3. Verificando módulo psycopg2...")
try:
    import psycopg2
    print("✅ psycopg2 instalado correctamente")
except ImportError:
    print("❌ ERROR: psycopg2 no está instalado")
    print("   Ejecuta: pip install psycopg2-binary")
    sys.exit(1)

# Intentar conexión básica
print("\n4. Intentando conexión básica (timeout: 15s)...")
try:
    start_time = time.time()
    conn = psycopg2.connect(db_url, connect_timeout=15)
    elapsed = time.time() - start_time
    print(f"✅ Conexión básica exitosa ({elapsed:.2f}s)")
    conn.close()
except Exception as e:
    elapsed = time.time() - start_time
    print(f"❌ Error en conexión básica ({elapsed:.2f}s): {e}")
    
    # Extraer componentes para hacer pruebas alternativas
    try:
        # Obtener componentes de la URL
        if 'postgresql://' in db_url:
            db_url_clean = db_url.replace('postgresql://', '')
            user_pass, host_db = db_url_clean.split('@', 1)
            
            if '/' in host_db:
                host_db_parts = host_db.split('/', 1)
                host = host_db_parts[0]
                db_with_params = host_db_parts[1]
                
                if '?' in db_with_params:
                    db, params = db_with_params.split('?', 1)
                else:
                    db = db_with_params
                    params = ""
                
                user, password = user_pass.split(':', 1)
                
                print("\n5. Detalles de conexión:")
                print(f"   Host: {host}")
                print(f"   Base de datos: {db}")
                print(f"   Usuario: {user}")
                print(f"   Parámetros: {params}")
                
                # Probar conexión alternativa
                print("\n6. Intentando conexión alternativa...")
                try:
                    conn_params = {
                        "dbname": db,
                        "user": user,
                        "password": password,
                        "host": host,
                        "connect_timeout": 15
                    }
                    
                    # Añadir sslmode explícitamente
                    conn_params["sslmode"] = "require"
                    
                    print("   Conectando con parámetros explícitos...")
                    start_time = time.time()
                    alt_conn = psycopg2.connect(**conn_params)
                    elapsed = time.time() - start_time
                    print(f"✅ Conexión alternativa exitosa ({elapsed:.2f}s)")
                    alt_conn.close()
                except Exception as alt_e:
                    elapsed = time.time() - start_time
                    print(f"❌ Error en conexión alternativa ({elapsed:.2f}s): {alt_e}")
                    
                    # Probar sin SSL
                    print("\n7. Intentando sin SSL (sólo para diagnóstico)...")
                    try:
                        no_ssl_params = conn_params.copy()
                        no_ssl_params["sslmode"] = "disable"
                        start_time = time.time()
                        no_ssl_conn = psycopg2.connect(**no_ssl_params)
                        elapsed = time.time() - start_time
                        print(f"✅ Conexión sin SSL exitosa ({elapsed:.2f}s) - PERO Neon requiere SSL")
                        no_ssl_conn.close()
                    except Exception as no_ssl_e:
                        elapsed = time.time() - start_time
                        print(f"❌ Error al intentar sin SSL ({elapsed:.2f}s): {no_ssl_e}")
    except Exception as parse_e:
        print(f"\n❌ Error al analizar la URL de conexión: {parse_e}")

print("\n=== Comprobación de red ===")
import socket
try:
    # Extraer host para prueba de red
    if 'postgresql://' in db_url:
        db_url_clean = db_url.replace('postgresql://', '')
        _, host_part = db_url_clean.split('@', 1)
        host = host_part.split('/')[0]
        
        print(f"Comprobando conexión de red a: {host} (puerto 5432)...")
        start_time = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        result = s.connect_ex((host, 5432))
        elapsed = time.time() - start_time
        s.close()
        
        if result == 0:
            print(f"✅ Puerto 5432 abierto y accesible ({elapsed:.2f}s)")
        else:
            print(f"❌ No se puede conectar al puerto 5432 ({elapsed:.2f}s)")
            print("   Esto indica un problema de red o firewall.")
            
except Exception as sock_e:
    print(f"❌ Error al verificar la conexión de red: {sock_e}")

print("\n=== Verificación del entorno ===")
# Verificar variables importantes
env_vars = ['SECRET_KEY', 'FLASK_APP', 'FLASK_DEBUG', 'PORT', 'DATABASE_URL', 'CHECK_DB_CONNECTION', 'ENABLE_SQLITE_FALLBACK']
for var in env_vars:
    value = os.environ.get(var)
    if value:
        if var == 'DATABASE_URL':
            # Ocultar contraseña
            parts = value.split('@')
            if len(parts) > 1:
                user_pass = parts[0].split(':')
                if len(user_pass) > 1:
                    hidden = f"{user_pass[0]}:****@{parts[1]}"
                    print(f"✅ {var}: {hidden}")
                else:
                    print(f"✅ {var}: [configurado pero formato inválido]")
            else:
                print(f"✅ {var}: [configurado pero formato inválido]")
        else:
            print(f"✅ {var}: {value}")
    else:
        print(f"❌ {var}: No configurado")

print("\n=== Diagnóstico completo ===")
print("Recomendaciones:")
print("1. Verifica que la base de datos en Neon esté activa y no suspendida")
print("2. Comprueba si hay restricciones de red o firewall")
print("3. Verifica que las credenciales no hayan expirado o cambiado")
print("4. Como último recurso, habilita el fallback a SQLite modificando ENABLE_SQLITE_FALLBACK=true en .env")

input("\nPresiona Enter para salir...")
