#!/usr/bin/env python
# instalar_psycopg2.py
import sys
import subprocess
import os

def main():
    print("=== Instalación de psycopg2-binary ===")
    print("Este script instalará psycopg2-binary necesario para conectar con PostgreSQL en Neon")
    
    try:
        import psycopg2
        print("✅ psycopg2 ya está instalado. Versión:", psycopg2.__version__)
        return True
    except ImportError:
        print("❌ psycopg2 no está instalado. Intentando instalar...")
    
    # Determinar el ejecutable de Python
    python_exe = sys.executable
    
    try:
        # Instalar psycopg2-binary
        print(f"Ejecutando: {python_exe} -m pip install psycopg2-binary")
        subprocess.check_call([python_exe, '-m', 'pip', 'install', 'psycopg2-binary'])
        
        # Verificar la instalación
        import psycopg2
        print("✅ psycopg2 instalado correctamente. Versión:", psycopg2.__version__)
        return True
    except Exception as e:
        print(f"❌ Error al instalar psycopg2-binary: {e}")
        print("\nPasos alternativos de instalación:")
        print("1. Abre una terminal o CMD como administrador")
        print("2. Ejecuta: pip install psycopg2-binary")
        print("   - O si usas un entorno virtual: .\\venv\\Scripts\\pip install psycopg2-binary")
        print("3. Si hay errores, prueba instalar los prerrequisitos según tu sistema operativo")
        print("   - Windows: Asegúrate de tener instalado Visual C++ Build Tools")
        print("   - Linux: sudo apt-get install python3-dev libpq-dev")
        print("   - macOS: brew install postgresql")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Todo listo para usar PostgreSQL en Neon!")
        print("Ahora puedes ejecutar la aplicación con: python main.py")
    else:
        print("\n❌ No se ha podido instalar psycopg2-binary.")
        print("Resuelve los problemas de instalación e inténtalo de nuevo.")
        
    input("\nPresiona Enter para salir...")
