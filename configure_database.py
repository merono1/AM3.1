import os
from pathlib import Path
from dotenv import load_dotenv, set_key
import sys
import time

def main():
    print("=== Configuración de Base de Datos para AM3.1 ===")
    print("\nEste script te ayudará a configurar la base de datos para el proyecto.")
    print("Puedes elegir entre:")
    print("1. PostgreSQL en Neon (remoto)")
    print("2. SQLite local (desarrollo)")
    
    # Cargar .env actual
    env_path = Path('.env')
    load_dotenv(env_path)
    
    choice = input("\n¿Qué opción prefieres? [1/2]: ").strip()
    
    if choice == "1":
        configure_postgresql()
    elif choice == "2":
        configure_sqlite()
    else:
        print("Opción no válida. Vuelve a intentarlo.")
        return
    
    print("\n✅ Configuración guardada. Ahora puedes ejecutar: python main.py")
    
def configure_postgresql():
    print("\n=== Configuración de PostgreSQL en Neon ===")
    
    # Obtener URL actual si existe
    current_url = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_V9nz4xhHPfab@ep-delicate-salad-ab2eh0sf-pooler.eu-west-2.aws.neon.tech/neondb')
    
    print(f"URL actual: {current_url}")
    change = input("¿Quieres modificar la URL de conexión? [s/N]: ").strip().lower()
    
    if change == "s":
        new_url = input("Introduce la nueva URL de conexión: ").strip()
        if new_url:
            current_url = new_url
    
    # Guardar en .env
    with open('.env', 'w') as f:
        f.write(f"# Configuración general\n")
        f.write(f"SECRET_KEY=clave_secreta_desarrollo\n")
        f.write(f"FLASK_APP=main.py\n")
        f.write(f"FLASK_DEBUG=1\n")
        f.write(f"PORT=5000\n\n")
        f.write(f"# PostgreSQL (Neon)\n")
        f.write(f"DATABASE_URL={current_url}\n")
        f.write(f"# Habilitado fallback a SQLite si PostgreSQL falla\n")
        f.write(f"ENABLE_SQLITE_FALLBACK=false\n")
    
    print("\n✅ Configuración de PostgreSQL guardada correctamente.")
    
    # Probar conexión
    test = input("¿Quieres probar la conexión ahora? [S/n]: ").strip().lower()
    if test != "n":
        try:
            import psycopg2
            
            print(f"Intentando conectar a: {current_url.split('@')[1] if '@' in current_url else current_url}")
            print("(timeout de 10 segundos)")
            
            start_time = time.time()
            conn = psycopg2.connect(current_url, connect_timeout=10)
            elapsed = time.time() - start_time
            
            print(f"✅ ¡Conexión exitosa! (tiempo: {elapsed:.2f}s)")
            conn.close()
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            
            fallback = input("¿Quieres habilitar el fallback a SQLite? [s/N]: ").strip().lower()
            if fallback == "s":
                with open('.env', 'r') as f:
                    lines = f.readlines()
                
                with open('.env', 'w') as f:
                    for line in lines:
                        if line.strip().startswith('ENABLE_SQLITE_FALLBACK='):
                            f.write('ENABLE_SQLITE_FALLBACK=true\n')
                        else:
                            f.write(line)
                
                print("✅ Fallback a SQLite habilitado.")

def configure_sqlite():
    print("\n=== Configuración de SQLite Local ===")
    
    base_dir = Path(__file__).resolve().parent
    default_path = str(base_dir / 'app' / 'data' / 'app.db')
    
    current_path = os.environ.get('DB_PATH', default_path)
    
    print(f"Ruta actual: {current_path}")
    change = input("¿Quieres modificar la ruta de la base de datos SQLite? [s/N]: ").strip().lower()
    
    if change == "s":
        new_path = input("Introduce la nueva ruta: ").strip()
        if new_path:
            current_path = new_path
    
    # Crear directorio si no existe
    db_dir = Path(current_path).parent
    try:
        os.makedirs(db_dir, exist_ok=True)
        print(f"✅ Directorio {db_dir} creado/verificado")
    except Exception as e:
        print(f"❌ Error al crear directorio: {e}")
    
    # Guardar en .env
    with open('.env', 'w') as f:
        f.write(f"# Configuración general\n")
        f.write(f"SECRET_KEY=clave_secreta_desarrollo\n")
        f.write(f"FLASK_APP=main.py\n")
        f.write(f"FLASK_DEBUG=1\n")
        f.write(f"PORT=5000\n\n")
        f.write(f"# SQLite (local)\n")
        f.write(f"DB_PATH={current_path}\n")
        f.write(f"# PostgreSQL desactivado\n")
        f.write(f"# DATABASE_URL=\n")
    
    print("\n✅ Configuración de SQLite guardada correctamente.")

if __name__ == "__main__":
    main()
    input("\nPresiona Enter para salir...")
