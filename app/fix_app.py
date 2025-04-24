"""
Corrección directa a la variable db en el módulo app
"""
import os
import sys

def fix_init_file():
    """Corrige el archivo __init__.py para evitar conflictos con 'db'"""
    init_path = os.path.join('app', '__init__.py')
    
    if not os.path.exists(init_path):
        print(f"❌ No se encontró el archivo {init_path}")
        return False
    
    # Leer el contenido del archivo
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si ya contiene el comentario de seguridad
    if "# Asegurar que db es un objeto SQLAlchemy y no una cadena" in content:
        print("✅ El archivo __init__.py ya ha sido arreglado")
        return True
    
    # Añadir comprobación de seguridad después de la definición de db
    if "db = SQLAlchemy()" in content:
        modified = content.replace(
            "db = SQLAlchemy()",
            """db = SQLAlchemy()

# Asegurar que db es un objeto SQLAlchemy y no una cadena
if not hasattr(db, 'init_app'):
    # Si db es una cadena, redefine la variable
    import sys
    this_module = sys.modules[__name__]
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()  # Reemplazar con un nuevo objeto SQLAlchemy"""
        )
        
        # Guardar el archivo modificado
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write(modified)
        
        print("✅ Archivo __init__.py corregido")
        return True
    else:
        print("❌ No se encontró la definición de db en __init__.py")
        return False

if __name__ == "__main__":
    fix_init_file()
