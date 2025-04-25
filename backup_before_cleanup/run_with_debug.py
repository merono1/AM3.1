
"""
Script de ejecución con modo debug para diagnosticar problemas de conexión a PostgreSQL
"""
import os
import sys
from dotenv import load_dotenv
import traceback

# Cargar variables de entorno desde .env
print("1. Cargando variables de entorno...")
load_dotenv()

# Mostrar información de diagnóstico
print("\n=== Diagnóstico de Variables de Entorno ===")
print(f"DATABASE_URL = {os.environ.get('DATABASE_URL', 'No definida')}")
print(f"FLASK_ENV = {os.environ.get('FLASK_ENV', 'No definida')}")
print(f"PORT = {os.environ.get('PORT', '5000')}")
print(f"PYTHONPATH = {os.environ.get('PYTHONPATH', 'No definida')}")

# Establecer PYTHONPATH
os.environ['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))
print(f"PYTHONPATH ahora = {os.environ.get('PYTHONPATH', 'No definida')}")

# Verificar si la URL de PostgreSQL tiene el parámetro sslmode
db_url = os.environ.get('DATABASE_URL', '')
if db_url and 'postgresql' in db_url and 'sslmode' not in db_url:
    print("\n⚠️ ADVERTENCIA: La URL de PostgreSQL no contiene el parámetro sslmode=require")
    print("   Es posible que necesites añadir ?sslmode=require al final de la URL")
    print("   URL actual:", db_url)

# Verificar si psycopg2 está instalado
try:
    print("\nVerificando psycopg2...")
    import psycopg2
    print("✅ psycopg2 está instalado correctamente")
except ImportError:
    print("❌ psycopg2 no está instalado")
    print("   Instálalo con: pip install psycopg2-binary")
    sys.exit(1)

# Importar componentes de la aplicación
try:
    print("\nImportando módulos de la aplicación...")
    from app import create_app
    print("✅ Módulos importados correctamente")
except Exception as e:
    print(f"❌ Error al importar módulos: {e}")
    print("\nTraceback completo:")
    traceback.print_exc()
    sys.exit(1)

# Crear y ejecutar la aplicación
try:
    print("\nCreando aplicación Flask...")
    app = create_app(os.environ.get('FLASK_ENV', 'default'))
    
    print("\n✅ Aplicación creada correctamente")
    print("\nIniciando servidor...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
except Exception as e:
    print(f"\n❌ Error al iniciar la aplicación: {e}")
    print("\nTraceback completo:")
    traceback.print_exc()
