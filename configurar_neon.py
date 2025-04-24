"""
Script para configurar y probar la conexión a Neon PostgreSQL
"""
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
import psycopg2

def clear_screen():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def check_required_packages():
    """Verifica que los paquetes necesarios estén instalados"""
    try:
        import psycopg2
        return True
    except ImportError:
        print("❌ No se encontró el paquete psycopg2-binary")
        print("Ejecuta: pip install psycopg2-binary")
        return False

def test_connection(connection_string):
    """Prueba la conexión a PostgreSQL"""
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        conn.close()
        return True, version[0]
    except Exception as e:
        return False, str(e)

def main():
    """Función principal"""
    if not check_required_packages():
        return

    clear_screen()
    print("""
    ╔════════════════════════════════════════════════════╗
    ║         Configuración de Neon PostgreSQL           ║
    ╚════════════════════════════════════════════════════╝
    """)
    
    # Cargar variables de entorno existentes
    load_dotenv()
    
    # Directorio base
    BASE_DIR = Path(__file__).resolve().parent
    ENV_PATH = BASE_DIR / '.env'
    
    # Verificar si ya existe DATABASE_URL
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        print(f"📁 Se encontró una conexión existente a PostgreSQL:")
        print(f"   {database_url}")
        
        print("\n🔄 Probando conexión existente...")
        success, message = test_connection(database_url)
        
        if success:
            print(f"✅ Conexión exitosa a PostgreSQL")
            print(f"   {message}")
            
            choice = input("\n¿Deseas configurar una nueva conexión? (s/N): ").lower()
            if choice != 's':
                print("\n✅ Manteniendo configuración actual")
                print("""
    Para migrar tus datos de SQLite a PostgreSQL, ejecuta:
    python migrate_to_postgres.py
                """)
                return
        else:
            print(f"❌ Error al conectar: {message}")
            print("Configuremos una nueva conexión...")
    
    # Solicitar detalles de conexión
    print("\n📝 Ingresa los detalles de conexión a Neon PostgreSQL:")
    print("   (Los puedes encontrar en el panel de control de Neon)")
    
    host = input("Host (ej: ep-cool-tree-123456.eu-central-1.aws.neon.tech): ")
    database = input("Base de datos (ej: neondb): ")
    user = input("Usuario (ej: tu_usuario): ")
    password = input("Contraseña: ")
    
    # Construir cadena de conexión
    connection_string = f"postgresql://{user}:{password}@{host}/{database}"
    
    # Probar conexión
    print("\n🔄 Probando conexión...")
    success, message = test_connection(connection_string)
    
    if success:
        print(f"✅ Conexión exitosa a PostgreSQL")
        print(f"   {message}")
        
        # Guardar en .env
        save = input("\n¿Guardar esta configuración en el archivo .env? (S/n): ").lower()
        if save != 'n':
            # Leer .env existente
            env_content = ""
            if ENV_PATH.exists():
                with open(ENV_PATH, 'r') as f:
                    env_content = f.read()
            
            # Modificar o añadir DATABASE_URL
            if 'DATABASE_URL=' in env_content:
                # Reemplazar línea existente
                lines = env_content.split('\n')
                new_lines = []
                for line in lines:
                    if line.startswith('DATABASE_URL='):
                        new_lines.append(f"DATABASE_URL={connection_string}")
                    else:
                        new_lines.append(line)
                env_content = '\n'.join(new_lines)
            else:
                # Añadir nueva línea
                env_content += f"\n# PostgreSQL Neon\nDATABASE_URL={connection_string}\n"
            
            # Comentar DB_PATH si existe
            if 'DB_PATH=' in env_content and '# DB_PATH=' not in env_content:
                env_content = env_content.replace('DB_PATH=', '# DB_PATH=')
            
            # Guardar cambios
            with open(ENV_PATH, 'w') as f:
                f.write(env_content)
            
            print("✅ Configuración guardada en .env")
            
            # Preguntar si desea migrar datos
            migrate = input("\n¿Deseas migrar los datos de SQLite a PostgreSQL ahora? (S/n): ").lower()
            if migrate != 'n':
                print("\n🔄 Ejecutando migración...")
                os.system('python migrate_to_postgres.py')
            else:
                print("""
    Para migrar tus datos más tarde, ejecuta:
    python migrate_to_postgres.py
                """)
    else:
        print(f"❌ Error al conectar: {message}")
        print("""
    Posibles soluciones:
    1. Verifica que los datos de conexión sean correctos
    2. Asegúrate de que la IP desde la que te conectas esté permitida en Neon
    3. Verifica que el servidor de Neon esté activo
        """)

if __name__ == "__main__":
    main()
