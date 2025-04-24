"""
Script para probar la conexión a Neon PostgreSQL con timeout y manejo de errores.
Utiliza las mismas credenciales que la aplicación para asegurar coherencia.
"""
import os
import sys
import time
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def clear_screen():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_db_url():
    """Obtiene la URL de conexión a PostgreSQL desde .env"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        # Si no hay DATABASE_URL en el entorno, buscar en .env
        env_path = Path('.env')
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('DATABASE_URL='):
                        database_url = line.split('=', 1)[1].strip()
                        break
    
    return database_url

def test_connection_with_timeout(connection_string, timeout=10):
    """
    Prueba la conexión a PostgreSQL con timeout
    
    Args:
        connection_string: Cadena de conexión a PostgreSQL
        timeout: Tiempo máximo de espera para la conexión en segundos
        
    Returns:
        tuple: (éxito, mensaje)
    """
    print(f"🔄 Probando conexión a PostgreSQL (timeout: {timeout}s)...")
    start_time = time.time()
    
    try:
        # Conexión con timeout explícito
        conn = psycopg2.connect(
            connection_string,
            connect_timeout=timeout,
            application_name="AM3.1-TestConnection"
        )
        
        # Obtener información del servidor
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        # Probar consulta simple para asegurar que la conexión funciona
        cursor.execute("SELECT 1;")
        cursor.fetchone()
        
        # Medir tiempo de respuesta
        elapsed_time = time.time() - start_time
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        return True, f"Versión PostgreSQL: {version}\nTiempo de respuesta: {elapsed_time:.2f}s"
    
    except psycopg2.OperationalError as e:
        error_msg = str(e).strip()
        elapsed_time = time.time() - start_time
        
        # Analizar el error para dar mensaje más amigable
        if "timeout expired" in error_msg:
            return False, f"Timeout de conexión después de {elapsed_time:.2f}s. La base de datos podría estar en modo sleep."
        elif "password authentication failed" in error_msg:
            return False, "Error de autenticación. Verifique usuario y contraseña."
        elif "could not translate host" in error_msg or "could not connect to server" in error_msg:
            return False, f"No se pudo conectar al servidor. Verifique el host y que la base de datos esté activa.\nError: {error_msg}"
        else:
            return False, f"Error operacional: {error_msg}\nTiempo transcurrido: {elapsed_time:.2f}s"
    
    except Exception as e:
        elapsed_time = time.time() - start_time
        return False, f"Error inesperado: {str(e)}\nTiempo transcurrido: {elapsed_time:.2f}s"

def wake_up_database(connection_string, max_attempts=3, delay=2):
    """
    Intenta despertar la base de datos si está en modo sleep
    
    Args:
        connection_string: Cadena de conexión a PostgreSQL
        max_attempts: Número máximo de intentos
        delay: Tiempo de espera entre intentos en segundos
        
    Returns:
        bool: True si se logró despertar, False en caso contrario
    """
    print(f"🔄 Intentando despertar la base de datos (max {max_attempts} intentos)...")
    
    for attempt in range(1, max_attempts + 1):
        print(f"  Intento {attempt}/{max_attempts}...")
        success, _ = test_connection_with_timeout(connection_string, timeout=15)
        
        if success:
            print("✅ ¡Base de datos despertada con éxito!")
            return True
        
        if attempt < max_attempts:
            print(f"  Esperando {delay} segundos antes del siguiente intento...")
            time.sleep(delay)
            # Incrementar el tiempo de espera en cada intento
            delay *= 1.5
    
    return False

def main():
    """Función principal"""
    clear_screen()
    print("""
    ╔════════════════════════════════════════════════════╗
    ║    Test de Conexión a Neon PostgreSQL (AM3.1)      ║
    ╚════════════════════════════════════════════════════╝
    """)
    
    # Verificar que psycopg2 está instalado
    try:
        import psycopg2
    except ImportError:
        print("❌ No se encontró el paquete psycopg2-binary")
        print("Ejecuta: pip install psycopg2-binary")
        return
    
    # Obtener URL de conexión
    connection_string = get_db_url()
    if not connection_string:
        print("❌ No se encontró la URL de conexión a PostgreSQL")
        print("Asegúrese de que DATABASE_URL esté definido en el archivo .env")
        return
    
    # Mostrar URL parcial (ocultar contraseña)
    display_url = connection_string
    if '@' in connection_string:
        pre, post = connection_string.split('@', 1)
        if ':' in pre:
            user_part, _ = pre.rsplit(':', 1)
            display_url = f"{user_part}:******@{post}"
    
    print(f"📌 Usando conexión: {display_url}")
    
    # Probar conexión con timeout
    success, message = test_connection_with_timeout(connection_string)
    
    if success:
        print(f"✅ Conexión exitosa a PostgreSQL")
        print(f"   {message}")
    else:
        print(f"❌ Error al conectar: {message}")
        
        # Preguntar si desea intentar despertar la base de datos
        choice = input("\n¿Intentar despertar la base de datos? (S/n): ").lower()
        if choice != 'n':
            if wake_up_database(connection_string):
                print("\n✅ La base de datos está ahora activa y lista para usar")
                print("   Puede iniciar la aplicación normalmente")
            else:
                print("\n❌ No se pudo despertar la base de datos")
                print("""
    Posibles soluciones:
    1. Acceda al panel de control de Neon y reactive el proyecto manualmente
    2. Espere unos minutos y vuelva a intentarlo
    3. Verifique sus credenciales de conexión en el archivo .env
                """)
    
    # Información adicional
    print("""
    Nota sobre Neon PostgreSQL:
    - La base de datos Neon puede entrar en modo 'sleep' después de un período de inactividad
    - Al iniciar la aplicación, puede tardar unos segundos en activarse
    - Si la aplicación muestra error de timeout, ejecute este script para activar la BD
    - Para más información, visite: https://neon.tech/docs/connect/connection-pooling
    """)

if __name__ == "__main__":
    main()
