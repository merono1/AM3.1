"""
Script de inicio rápido para la aplicación AM3.1
Este script permite iniciar la aplicación en diferentes modos y realizar acciones de mantenimiento.
"""
import os
import sys
import subprocess
from pathlib import Path

def clear_screen():
    """Limpia la pantalla de la consola."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Muestra el encabezado de la aplicación."""
    print("\n" + "=" * 60)
    print("                 AM3.1 - SISTEMA DE GESTIÓN")
    print("=" * 60)
    print("        Aplicación reorganizada con patrón MVC")
    print("-" * 60 + "\n")

def show_menu():
    """Muestra el menú principal."""
    print_header()
    print("OPCIONES DISPONIBLES:")
    print("  1. Iniciar en modo prueba (simple_app.py)")
    print("  2. Iniciar en modo normal (main.py)")
    print("  3. Crear/actualizar tablas de la base de datos")
    print("  4. Ver estructura de directorios")
    print("  5. Verificar dependencias")
    print("  0. Salir")
    print("\n" + "-" * 60)

def run_command(command):
    """Ejecuta un comando y espera a que termine."""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al ejecutar el comando: {e}")
    
    input("\nPresiona Enter para continuar...")

def show_directory_structure():
    """Muestra la estructura de directorios del proyecto."""
    print_header()
    print("ESTRUCTURA DE DIRECTORIOS DEL PROYECTO:")
    root_dir = Path(__file__).parent
    
    def print_tree(directory, prefix=""):
        """Imprime recursivamente el árbol de directorios."""
        items = sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name))
        
        for i, path in enumerate(items):
            is_last = i == len(items) - 1
            print(f"{prefix}{'└── ' if is_last else '├── '}{path.name}")
            
            if path.is_dir() and not path.name.startswith('__pycache__'):
                ext_prefix = f"{prefix}{'    ' if is_last else '│   '}"
                print_tree(path, ext_prefix)
    
    print_tree(root_dir)
    
    input("\nPresiona Enter para continuar...")

def check_dependencies():
    """Verifica que las dependencias necesarias estén instaladas."""
    print_header()
    print("VERIFICANDO DEPENDENCIAS INSTALADAS:")
    
    try:
        import pkg_resources
        
        with open('requirements.txt', 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        installed = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
        
        for requirement in requirements:
            package = requirement.split('==')[0].split('>=')[0].split('<=')[0].strip()
            if package.lower() in installed:
                print(f"✅ {package}: Instalado (versión {installed[package.lower()]})")
            else:
                print(f"❌ {package}: No instalado")
        
    except Exception as e:
        print(f"❌ Error al verificar dependencias: {str(e)}")
    
    input("\nPresiona Enter para continuar...")

def main():
    """Función principal del script."""
    while True:
        clear_screen()
        show_menu()
        
        try:
            option = input("\nSelecciona una opción (0-5): ").strip()
            
            if option == '0':
                clear_screen()
                print_header()
                print("¡Gracias por usar AM3.1! Hasta pronto.")
                sys.exit(0)
            
            elif option == '1':
                run_command("python simple_app.py")
            
            elif option == '2':
                run_command("python main.py")
            
            elif option == '3':
                run_command("python create_tables.py")
            
            elif option == '4':
                show_directory_structure()
            
            elif option == '5':
                check_dependencies()
            
            else:
                print("⚠️ Opción no válida. Por favor, selecciona una opción del 0 al 5.")
                input("\nPresiona Enter para continuar...")
        
        except KeyboardInterrupt:
            clear_screen()
            print_header()
            print("Operación cancelada por el usuario.")
            sys.exit(0)
        
        except Exception as e:
            print(f"\n❌ Error inesperado: {str(e)}")
            input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()
