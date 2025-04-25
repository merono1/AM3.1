#!/usr/bin/env python
# configurar_neon.py
import os
from pathlib import Path
import sys
import re
from dotenv import load_dotenv, set_key

def main():
    print("=== Configuración de Conexión a Neon PostgreSQL ===")
    
    # Cargar .env actual
    env_path = Path('.env')
    load_dotenv(env_path)
    
    # Obtener URL actual si existe
    current_url = os.environ.get('DATABASE_URL', '')
    
    # Extraer componentes de la URL actual si existe
    username = "usuario"
    password = "password"
    host = "ep-delicate-salad-ab2eh0sf-pooler.eu-west-2.aws.neon.tech"
    dbname = "neondb"
    
    if current_url:
        # Intentar analizar la URL actual
        url_pattern = r'postgresql://([^:]+):([^@]+)@([^/]+)/(.+)'
        match = re.match(url_pattern, current_url)
        if match:
            username, password, host, dbname = match.groups()
    
    # Solicitar información
    print("\nPor favor, proporciona los datos de conexión a tu base de datos Neon:")
    print("(Presiona Enter para mantener los valores actuales)")
    
    new_username = input(f"Usuario [{username}]: ") or username
    new_password = input(f"Contraseña [{password}]: ") or password
    new_host = input(f"Host [{host}]: ") or host
    new_dbname = input(f"Nombre de la base de datos [{dbname}]: ") or dbname
    
    # Crear nueva URL
    new_url = f"postgresql://{new_username}:{new_password}@{new_host}/{new_dbname}"
    
    # Verificar si ha habido cambios
    if new_url == current_url:
        print("\nNo se han realizado cambios en la configuración.")
    else:
        print("\nNueva URL de conexión:")
        print(f"DATABASE_URL={new_url}")
        
        # Actualizar .env
        with open(env_path, 'r') as file:
            lines = file.readlines()
        
        with open(env_path, 'w') as file:
            for line in lines:
                if line.strip().startswith('DATABASE_URL='):
                    file.write(f'DATABASE_URL={new_url}\n')
                else:
                    file.write(line)
        
        print("\n✅ Archivo .env actualizado correctamente.")
    
    print("\nPara probar la conexión a PostgreSQL, ejecuta: python main.py")

if __name__ == "__main__":
    main()
    input("\nPresiona Enter para salir...")
