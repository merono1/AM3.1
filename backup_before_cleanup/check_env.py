
"""
Script para verificar la carga de variables de entorno
"""
import os
from dotenv import load_dotenv

print("Verificando variables de entorno:")
print("1. Antes de cargar .env:")
print(f"   DATABASE_URL = {os.environ.get('DATABASE_URL', 'No definida')}")
print("")

print("2. Cargando .env...")
load_dotenv()

print("3. Después de cargar .env:")
print(f"   DATABASE_URL = {os.environ.get('DATABASE_URL', 'No definida')}")

print("\nRuta del archivo .env:")
import pathlib
env_path = pathlib.Path(".env")
print(f"   Ruta absoluta: {env_path.absolute()}")
print(f"   ¿Existe el archivo?: {env_path.exists()}")

if env_path.exists():
    print("\nContenido del archivo .env:")
    with open(".env", "r") as f:
        content = f.read()
        print(content)

print("\nVerificación completada.")
