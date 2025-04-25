"""
Script para habilitar el modo de fallback a SQLite cuando PostgreSQL no es accesible
"""
import os
from pathlib import Path
from dotenv import load_dotenv, set_key
import sys

def main():
    print("=== Habilitando modo de fallback a SQLite ===")
    
    # Verificar que existe el archivo .env
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ Error: No se encontró el archivo .env")
        print("   Crea un archivo .env en la raíz del proyecto")
        return False
    
    # Cargar variables de entorno actuales
    load_dotenv(env_path)
    
    # Verificar configuración actual
    current_fallback = os.environ.get('ENABLE_SQLITE_FALLBACK', 'false').lower()
    if current_fallback == 'true':
        print("ℹ️ El modo de fallback a SQLite ya está habilitado")
    else:
        # Modificar el archivo .env
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fallback_line_exists = False
        
        with open(env_path, 'w', encoding='utf-8') as f:
            for line in lines:
                if line.strip().startswith('ENABLE_SQLITE_FALLBACK='):
                    f.write('ENABLE_SQLITE_FALLBACK=true\n')
                    fallback_line_exists = True
                else:
                    f.write(line)
            
            # Añadir la línea si no existe
            if not fallback_line_exists:
                f.write('\n# Permitir fallback a SQLite si PostgreSQL falla\nENABLE_SQLITE_FALLBACK=true\n')
        
        print("✅ Modo de fallback a SQLite habilitado correctamente")
    
    # Verificar DB_PATH
    db_path = os.environ.get('DB_PATH')
    if not db_path:
        base_dir = Path(__file__).resolve().parent
        db_path = str(base_dir / 'app' / 'data' / 'app.db')
        
        # Añadir DB_PATH al archivo .env
        with open(env_path, 'a', encoding='utf-8') as f:
            f.write(f'\n# Ruta para SQLite en modo fallback\nDB_PATH={db_path}\n')
        
        print(f"✅ Ruta de SQLite configurada: {db_path}")
    else:
        print(f"ℹ️ Ruta de SQLite ya configurada: {db_path}")
    
    # Asegurar que el directorio para la base de datos SQLite existe
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Directorio para SQLite creado: {db_dir}")
    
    # Modificar app/config.py para asegurar que el fallback funciona
    try:
        config_path = Path('app') / 'config.py'
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # Verificar si ya tiene el código necesario
            if 'ENABLE_SQLITE_FALLBACK' not in config_content:
                print("\n⚠️ El archivo app/config.py necesita ser modificado para soportar fallback")
                print("   Esta operación debe ser realizada manualmente o por un desarrollador")
            else:
                print("✅ El archivo app/config.py ya soporta el modo fallback")
    except Exception as e:
        print(f"⚠️ Error al analizar app/config.py: {e}")
    
    print("\n=== Configuración completa ===")
    print("Ahora puedes ejecutar la aplicación con: python main.py")
    print("Si PostgreSQL no está disponible, la aplicación utilizará SQLite automáticamente.")

if __name__ == "__main__":
    main()
    input("\nPresiona Enter para salir...")
