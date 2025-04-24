# run_fixed.py - Punto de entrada con solución al conflicto de nombres
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
