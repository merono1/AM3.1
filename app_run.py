"""
Script de ejecución alternativo para evitar conflictos de nombres
"""
import os
import sys
import importlib.util

# Eliminar cualquier módulo conflictivo que ya esté cargado
for mod in list(sys.modules.keys()):
    if mod.startswith('app.') or mod == 'app' or mod == 'config':
        sys.modules.pop(mod, None)

# Establecer variables de entorno
os.environ['FLASK_ENV'] = os.environ.get('FLASK_ENV', 'development')
os.environ['PORT'] = os.environ.get('PORT', '5000')

def load_module(name, path):
    """Carga un módulo Python de forma segura"""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

print("Iniciando aplicación AM3.1 (método alternativo)...")

try:
    # Cargar el módulo app/__init__.py
    print("Cargando módulos...")
    app_init = load_module('app', os.path.join('app', '__init__.py'))
    
    # Extraer la función create_app
    create_app = getattr(app_init, 'create_app')
    
    # Crear la aplicación
    print("Creando aplicación Flask...")
    app = create_app(os.environ.get('FLASK_ENV', 'default'))
    
    # Ejecutar la aplicación
    port = int(os.environ.get('PORT', 5000))
    print(f"Iniciando servidor en http://localhost:{port}")
    app.run(host='0.0.0.0', port=port)
    
except Exception as e:
    print(f"Error al iniciar la aplicación: {e}")
    import traceback
    traceback.print_exc()
