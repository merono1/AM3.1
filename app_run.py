"""
Script de ejecución alternativo (DEPRECADO)
Se recomienda usar main.py para iniciar la aplicación.
Este script se mantiene temporalmente para compatibilidad con código existente.
"""
import os
import sys
import warnings
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mostrar advertencia de deprecación
warnings.warn(
    "app_run.py está deprecado. Utiliza 'python main.py' para iniciar la aplicación.",
    DeprecationWarning,
    stacklevel=2
)

# Establecer variables de entorno
os.environ['FLASK_ENV'] = os.environ.get('FLASK_ENV', 'development')
os.environ['PORT'] = os.environ.get('PORT', '5000')

print("\n⚠️ AVISO: Este método de inicio está deprecado.")
print("   Se recomienda usar 'python main.py' en su lugar.\n")

try:
    # Importar directamente desde main.py
    from main import app
    
    # Ejecutar la aplicación
    port = int(os.environ.get('PORT', 5000))
    print(f"Iniciando servidor en http://localhost:{port}")
    app.run(host='0.0.0.0', port=port)
    
except Exception as e:
    logger.error(f"Error al iniciar la aplicación: {e}")
    print(f"❌ Error al iniciar la aplicación: {e}")
    import traceback
    traceback.print_exc()
