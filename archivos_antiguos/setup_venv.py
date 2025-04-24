"""
Script para configurar un nuevo entorno virtual con versiones compatibles de las dependencias.
"""
import os
import sys
import subprocess
import platform

def run_command(command, cwd=None):
    """Ejecuta un comando y muestra su salida en tiempo real."""
    print(f"Ejecutando: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        cwd=cwd
    )
    
    # Mostrar la salida en tiempo real
    for line in process.stdout:
        print(line.strip())
    
    # Esperar a que el proceso termine y obtener su código de salida
    return_code = process.wait()
    
    if return_code != 0:
        print(f"❌ El comando falló con código de salida {return_code}")
        return False
    return True

def setup_venv():
    """Configura un nuevo entorno virtual con las dependencias correctas."""
    print("Configurando un nuevo entorno virtual para AM3.1...")
    
    # Determinar el sistema operativo
    is_windows = platform.system() == "Windows"
    venv_dir = "venv"
    activate_cmd = f"{venv_dir}\\Scripts\\activate" if is_windows else f"source {venv_dir}/bin/activate"
    
    # Crear el entorno virtual
    print("\n1. Creando el entorno virtual...")
    if os.path.exists(venv_dir):
        print(f"Se encontró un entorno virtual existente en '{venv_dir}'.")
        choice = input("¿Desea eliminarlo y crear uno nuevo? (s/n): ").strip().lower()
        if choice == 's':
            import shutil
            print(f"Eliminando entorno virtual existente '{venv_dir}'...")
            shutil.rmtree(venv_dir, ignore_errors=True)
        else:
            print("Usando el entorno virtual existente.")
            goto_activate = True
    
    # Si no existe o se decidió recrearlo
    if not os.path.exists(venv_dir):
        if not run_command(f"{sys.executable} -m venv {venv_dir}"):
            print("❌ No se pudo crear el entorno virtual.")
            return False
    
    print("\n2. Activando el entorno virtual...")
    print(f"Para activar el entorno virtual manualmente, ejecuta:\n\t{activate_cmd}")
    
    # Determinamos el comando pip según el sistema operativo
    pip_cmd = f"{venv_dir}\\Scripts\\pip" if is_windows else f"{venv_dir}/bin/pip"
    
    # Actualizar pip
    print("\n3. Actualizando pip...")
    if not run_command(f"{pip_cmd} install --upgrade pip"):
        print("❌ No se pudo actualizar pip.")
    
    # Instalar dependencias con versiones específicas
    print("\n4. Instalando dependencias con versiones compatibles...")
    dependencies = [
        "flask==2.2.3",
        "werkzeug==2.2.3",
        "sqlalchemy==1.4.46",
        "flask-sqlalchemy==3.0.3",
        "flask-wtf==1.1.1",
        "flask-migrate==4.0.4",
        "python-dotenv==1.0.0",
        "PyPDF2==3.0.1",
        "pdfkit==1.0.0",
        "email-validator==2.0.0.post2",
        "pytest==7.3.1",
        "gunicorn==20.1.0"
    ]
    
    # Instalar dependencias una por una para identificar mejor los problemas
    for dep in dependencies:
        print(f"Instalando {dep}...")
        if not run_command(f"{pip_cmd} install {dep}"):
            print(f"❌ Error al instalar {dep}")
    
    # Generar/actualizar requirements.txt
    print("\n5. Actualizando requirements.txt...")
    if run_command(f"{pip_cmd} freeze > requirements.txt"):
        print("✅ Archivo requirements.txt actualizado correctamente.")
    
    print("\n✅ Entorno virtual configurado correctamente.")
    print(f"\nPara activar el entorno virtual, ejecuta: {activate_cmd}")
    print("Después de activar el entorno virtual, ejecuta: python check_db.py")
    return True

if __name__ == "__main__":
    setup_venv()
