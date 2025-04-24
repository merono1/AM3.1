"""
Script para solucionar conflicto de nombres entre variables db
"""
import os
import sys

def main():
    print("Solucionando conflicto de nombres en el proyecto AM3.1...")
    
    # Verificar archivos necesarios
    required_files = [
        'config.py',
        'app/__init__.py',
        'main.py'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Error: No se encuentra el archivo {file}")
            return False
    
    # 1. Modificar config.py para renombrar la variable db_dir
    print("1. Modificando config.py...")
    with open('config.py', 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    # Cambiar db_dir a sqlite_db_dir para evitar conflictos
    if 'db_dir = ensure_db_dir_exists()' in config_content:
        config_content = config_content.replace(
            'db_dir = ensure_db_dir_exists()',
            'sqlite_db_dir = ensure_db_dir_exists()'
        )
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("   ✅ Variable db_dir renombrada a sqlite_db_dir en config.py")
    else:
        print("   ⚠️ No se encontró la variable db_dir en config.py")
    
    # 2. Modificar main.py para usar la nueva variable
    print("2. Modificando main.py...")
    with open('main.py', 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    if 'from app import db' in main_content:
        main_content = main_content.replace(
            'from app import db',
            'from app import db as flask_db'
        )
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(main_content)
        print("   ✅ Importación de db renombrada en main.py")
    
    # 3. Crear un archivo temporal que sirva como punto de entrada alternativo
    print("3. Creando punto de entrada alternativo...")
    with open('run_fixed.py', 'w', encoding='utf-8') as f:
        f.write("""# run_fixed.py - Punto de entrada con solución al conflicto de nombres
import os
import sys
import subprocess

# Establecer variable de entorno para evitar conflictos
os.environ['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))

try:
    # Importar directamente para verificar que no hay conflictos
    from app import create_app
    from app import db as flask_db  # Importar con nombre diferente
    
    print("✅ Importaciones verificadas correctamente")
    app = create_app(os.getenv('FLASK_ENV', 'default'))
    
    # Ejecutar la aplicación
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    
except Exception as e:
    print(f"❌ Error al iniciar la aplicación: {e}")
    # Si hay error, intentar ejecutar como subproceso con PYTHONPATH modificado
    print("Intentando método alternativo...")
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))
    
    subprocess.call([sys.executable, 'main.py'], env=env)
""")
    print("   ✅ Archivo run_fixed.py creado")
    
    print("\n✅ Solución aplicada correctamente.")
    print("""
Para iniciar la aplicación, ahora tienes dos opciones:
1. Usar el nuevo script: python run_fixed.py
2. Usar el script original (si la solución fue exitosa): python main.py

Si sigues teniendo problemas, por favor contacta al desarrollador.
""")

if __name__ == "__main__":
    main()
