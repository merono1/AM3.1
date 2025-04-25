
"""
Script para corregir el módulo app/__init__.py y permitir la conexión a PostgreSQL
"""
import os
import sys

def main():
    print("Corrigiendo app/__init__.py para mejorar compatibilidad con PostgreSQL...")
    
    # Verificar que existe el archivo
    app_init_path = os.path.join('app', '__init__.py')
    if not os.path.exists(app_init_path):
        print(f"❌ Error: No se encontró el archivo {app_init_path}")
        return False
    
    # Leer el contenido del archivo
    with open(app_init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Hacer los cambios necesarios para mejorar la detección de la conexión PostgreSQL
    if 'using_postgres = \'postgresql\' in app.config[\'SQLALCHEMY_DATABASE_URI\']' in content:
        print("1. Mejorando la detección de PostgreSQL...")
        content = content.replace(
            'using_postgres = \'postgresql\' in app.config[\'SQLALCHEMY_DATABASE_URI\']',
            'using_postgres = app.config[\'SQLALCHEMY_DATABASE_URI\'].startswith(\'postgresql\')'
        )
    
    # Escribir los cambios
    with open(app_init_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Correcciones aplicadas correctamente.")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\nAhora puedes intentar ejecutar la aplicación con: python run_fixed.py")
    input("\nPresiona Enter para salir...")
