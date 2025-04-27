"""
Rutas para gestión de base de datos, permitiendo cambiar entre local y remota.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, make_response, Response
from flask_wtf.csrf import validate_csrf, generate_csrf
from wtforms.validators import ValidationError
import subprocess
import sys
import threading
import time
from app.services.db_backup_service import db_backup_service
from app.services.direct_db_backup import get_direct_transfer
import os
import logging
import time
import json

# Configurar logging
logger = logging.getLogger(__name__)

# Crear blueprint
db_manager = Blueprint('db_manager', __name__, url_prefix='/db-manager')

# Ruta para verificar si el servidor está activo (para polling)
@db_manager.route('/check-status', methods=['GET'])
def check_server_status():
    """Verifica si el servidor está activo (para polling)."""
    return jsonify({
        "success": True,
        "status": "running",
        "timestamp": time.time()
    })

@db_manager.route('/')
def index():
    """Página principal de gestión de base de datos."""
    db_info = db_backup_service.get_current_db_info()
    return render_template('db_manager/index.html', db_info=db_info)

@db_manager.route('/download', methods=['POST'])
def download_db():
    """Descargar base de datos de PostgreSQL a SQLite."""
    # Detectar si la petición es AJAX (usando método más robusto)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
              request.headers.get('Content-Type') == 'application/json' or \
              request.headers.get('Accept') == 'application/json' or \
              request.headers.get('Sec-Fetch-Mode') == 'cors'
              
    # Verificación adicional para depuración
    logger.info(f"Headers de solicitud: {dict(request.headers)}")
    logger.info(f"Formulario: {request.form}")
    logger.info(f"Es AJAX: {is_ajax}")
    
    # Validar CSRF manualmente
    csrf_token = request.form.get('csrf_token')
    if not csrf_token:
        csrf_token = request.headers.get('X-CSRFToken')
    
    # Si el token CSRF no está presente, devolver error
    if not csrf_token and is_ajax:
        logger.error("Error CSRF: Token no proporcionado")
        return jsonify({
            "success": False,
            "message": "Error de seguridad: Token CSRF faltante"
        }), 400
    
    # Validar el token si existe
    if csrf_token:
        try:
            validate_csrf(csrf_token)
        except ValidationError as e:
            logger.error(f"Error CSRF: {str(e)}")
            if is_ajax:
                return jsonify({
                    "success": False, 
                    "message": "Error de seguridad: Token CSRF inválido"
                }), 400
            else:
                flash("Error de seguridad: Token CSRF inválido", "danger")
                return redirect(url_for('db_manager.index'))
    
    try:
        start_time = time.time()
        
        # Log de información para diagnóstico
        logger.info(f"Iniciando descarga de base de datos")
        logger.info(f"Headers: {request.headers}")
        
        # Usar el método directo de transferencia en lugar del basado en SQLAlchemy
        direct_transfer = get_direct_transfer(current_app)
        success, message = direct_transfer.download_postgres_to_sqlite()
        
        elapsed_time = time.time() - start_time
        
        if success:
            result_message = f"Base de datos descargada correctamente en {elapsed_time:.2f} segundos."
            logger.info(result_message)
            
            if is_ajax:
                return jsonify({
                    "success": True,
                    "message": result_message
                })
            else:
                flash(result_message, "success")
                return redirect(url_for('db_manager.index'))
        else:
            error_message = f"Error al descargar la base de datos: {message}"
            logger.error(error_message)
            
            if is_ajax:
                return jsonify({
                    "success": False,
                    "message": error_message
                }), 500
            else:
                flash(error_message, "danger")
                return redirect(url_for('db_manager.index'))
    
    except Exception as e:
        logger.exception("Error al descargar base de datos")
        flash(f"Error inesperado: {str(e)}", "danger")
        return redirect(url_for('db_manager.index'))

@db_manager.route('/upload', methods=['POST'])
def upload_db():
    """Subir base de datos SQLite a PostgreSQL."""
    # Detectar si la petición es AJAX (usando método más robusto)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
              request.headers.get('Content-Type') == 'application/json' or \
              request.headers.get('Accept') == 'application/json' or \
              request.headers.get('Sec-Fetch-Mode') == 'cors'
              
    # Verificación adicional para depuración
    logger.info(f"Headers de solicitud: {dict(request.headers)}")
    logger.info(f"Formulario: {request.form}")
    logger.info(f"Es AJAX: {is_ajax}")
    
    # Validar CSRF manualmente
    csrf_token = request.form.get('csrf_token')
    if not csrf_token:
        csrf_token = request.headers.get('X-CSRFToken')
    
    # Si el token CSRF no está presente, devolver error
    if not csrf_token and is_ajax:
        logger.error("Error CSRF: Token no proporcionado")
        return jsonify({
            "success": False,
            "message": "Error de seguridad: Token CSRF faltante"
        }), 400
    
    # Validar el token si existe
    if csrf_token:
        try:
            validate_csrf(csrf_token)
        except ValidationError as e:
            logger.error(f"Error CSRF: {str(e)}")
            if is_ajax:
                return jsonify({
                    "success": False, 
                    "message": "Error de seguridad: Token CSRF inválido"
                }), 400
            else:
                flash("Error de seguridad: Token CSRF inválido", "danger")
                return redirect(url_for('db_manager.index'))
    
    try:
        start_time = time.time()
        
        # Log de información para diagnóstico
        logger.info(f"Iniciando subida de base de datos")
        logger.info(f"Headers: {request.headers}")
        
        # Usar el método directo de transferencia en lugar del basado en SQLAlchemy
        direct_transfer = get_direct_transfer(current_app)
        success, message = direct_transfer.upload_sqlite_to_postgres()
        
        elapsed_time = time.time() - start_time
        
        if success:
            result_message = f"Base de datos subida correctamente en {elapsed_time:.2f} segundos."
            logger.info(result_message)
            
            if is_ajax:
                return jsonify({
                    "success": True,
                    "message": result_message
                })
            else:
                flash(result_message, "success")
                return redirect(url_for('db_manager.index'))
        else:
            error_message = f"Error al subir la base de datos: {message}"
            logger.error(error_message)
            
            if is_ajax:
                return jsonify({
                    "success": False,
                    "message": error_message
                }), 500
            else:
                flash(error_message, "danger")
                return redirect(url_for('db_manager.index'))
    
    except Exception as e:
        logger.exception("Error al subir base de datos")
        flash(f"Error inesperado: {str(e)}", "danger")
        return redirect(url_for('db_manager.index'))

@db_manager.route('/switch-to-local', methods=['POST'])
def switch_to_local():
    """Cambiar a base de datos local."""
    try:
        # Verificar si es una petición AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
                  request.headers.get('Content-Type') == 'application/json' or \
                  request.headers.get('Accept') == 'application/json' or \
                  request.headers.get('Sec-Fetch-Mode') == 'cors'
                  
        # Verificación adicional para depuración
        logger.info(f"Headers de solicitud: {dict(request.headers)}")
        logger.info(f"Formulario: {request.form}")
        logger.info(f"Es AJAX: {is_ajax}")
        
        # Validar CSRF manualmente
        csrf_token = request.form.get('csrf_token')
        if not csrf_token:
            csrf_token = request.headers.get('X-CSRFToken')
        
        # Si el token CSRF no está presente, devolver error
        if not csrf_token and is_ajax:
            logger.error("Error CSRF: Token no proporcionado en switch_to_local")
            return jsonify({
                "success": False,
                "message": "Error de seguridad: Token CSRF faltante"
            }), 400
        
        # Validar el token si existe
        if csrf_token:
            try:
                validate_csrf(csrf_token)
            except ValidationError as e:
                logger.error(f"Error CSRF: {str(e)}")
                if is_ajax:
                    return jsonify({
                        "success": False, 
                        "message": "Error de seguridad: Token CSRF inválido"
                    }), 400
                else:
                    flash("Error de seguridad: Token CSRF inválido", "danger")
                    return redirect(url_for('db_manager.index'))
        success, message = db_backup_service.switch_to_local_db()
        
        if success:
            message = "Cambiado a base de datos local. Se requiere reiniciar la aplicación."
            logger.info(message)
            
            if is_ajax:
                return jsonify({
                    "success": True,
                    "message": message
                })
            else:
                flash(message, "warning")
                return redirect(url_for('db_manager.index'))
        else:
            error_message = f"Error al cambiar a base de datos local: {message}"
            logger.error(error_message)
            
            if is_ajax:
                return jsonify({
                    "success": False,
                    "message": error_message
                }), 500
            else:
                flash(error_message, "danger")
                return redirect(url_for('db_manager.index'))
    
    except Exception as e:
        logger.exception("Error al cambiar a base de datos local")
        error_message = f"Error inesperado: {str(e)}"
        
        if is_ajax:
            return jsonify({
                "success": False,
                "message": error_message
            }), 500
        else:
            flash(error_message, "danger")
            return redirect(url_for('db_manager.index'))

@db_manager.route('/switch-to-postgres', methods=['POST'])
def switch_to_postgres():
    """Cambiar a base de datos PostgreSQL."""
    try:
        # Verificar si es una petición AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
                  request.headers.get('Content-Type') == 'application/json' or \
                  request.headers.get('Accept') == 'application/json' or \
                  request.headers.get('Sec-Fetch-Mode') == 'cors'
                  
        # Verificación adicional para depuración
        logger.info(f"Headers de solicitud: {dict(request.headers)}")
        logger.info(f"Formulario: {request.form}")
        logger.info(f"Es AJAX: {is_ajax}")
        
        # Validar CSRF manualmente
        csrf_token = request.form.get('csrf_token')
        if not csrf_token:
            csrf_token = request.headers.get('X-CSRFToken')
        
        # Si el token CSRF no está presente, devolver error
        if not csrf_token and is_ajax:
            logger.error("Error CSRF: Token no proporcionado en switch_to_postgres")
            return jsonify({
                "success": False,
                "message": "Error de seguridad: Token CSRF faltante"
            }), 400
        
        # Validar el token si existe
        if csrf_token:
            try:
                validate_csrf(csrf_token)
            except ValidationError as e:
                logger.error(f"Error CSRF: {str(e)}")
                if is_ajax:
                    return jsonify({
                        "success": False, 
                        "message": "Error de seguridad: Token CSRF inválido"
                    }), 400
                else:
                    flash("Error de seguridad: Token CSRF inválido", "danger")
                    return redirect(url_for('db_manager.index'))
        success, message = db_backup_service.switch_to_postgres_db()
        
        if success:
            message = "Cambiado a base de datos PostgreSQL. Se requiere reiniciar la aplicación."
            logger.info(message)
            
            if is_ajax:
                return jsonify({
                    "success": True,
                    "message": message
                })
            else:
                flash(message, "warning")
                return redirect(url_for('db_manager.index'))
        else:
            error_message = f"Error al cambiar a PostgreSQL: {message}"
            logger.error(error_message)
            
            if is_ajax:
                return jsonify({
                    "success": False,
                    "message": error_message
                }), 500
            else:
                flash(error_message, "danger")
                return redirect(url_for('db_manager.index'))
    
    except Exception as e:
        logger.exception("Error al cambiar a PostgreSQL")
        error_message = f"Error inesperado: {str(e)}"
        
        if is_ajax:
            return jsonify({
                "success": False,
                "message": error_message
            }), 500
        else:
            flash(error_message, "danger")
            return redirect(url_for('db_manager.index'))

# Ruta API para verificar estado actual
@db_manager.route('/status', methods=['GET'])
def db_status():
    """Obtener información sobre la base de datos actual."""
    try:
        db_info = db_backup_service.get_current_db_info()
        # Añadir una indicación visual más clara sobre qué base de datos está en uso
        db_info['indicator_color'] = 'success' if 'SQLite' in db_info.get('type', '') else 'primary'
        return jsonify({"success": True, "db_info": db_info, "active_timestamp": time.time()})
    
    except Exception as e:
        logger.exception("Error al obtener estado de base de datos")
        return jsonify({"success": False, "error": str(e)}), 500
        
# Ruta para reiniciar la aplicación
@db_manager.route('/restart', methods=['POST'])
def restart_app():
    """Reiniciar la aplicación Flask."""
    try:
        # Registrar la intención de reinicio
        logger.info("Iniciando reinicio de la aplicación desde la interfaz web")
        
        # Comprobar si la petición es AJAX (usando método más robusto)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
                  request.headers.get('Content-Type') == 'application/json' or \
                  request.headers.get('Accept') == 'application/json' or \
                  request.headers.get('Sec-Fetch-Mode') == 'cors'
                  
        # Validar CSRF manualmente
        csrf_token = request.form.get('csrf_token')
        if not csrf_token:
            csrf_token = request.headers.get('X-CSRFToken')
        
        # Si el token CSRF no está presente, devolver error
        if not csrf_token and is_ajax:
            logger.error("Error CSRF: Token no proporcionado en restart_app")
            return jsonify({
                "success": False,
                "message": "Error de seguridad: Token CSRF faltante"
            }), 400
        
        # Validar el token si existe
        if csrf_token:
            try:
                validate_csrf(csrf_token)
            except ValidationError as e:
                logger.error(f"Error CSRF: {str(e)}")
                if is_ajax:
                    return jsonify({
                        "success": False, 
                        "message": "Error de seguridad: Token CSRF inválido"
                    }), 400
                else:
                    flash("Error de seguridad: Token CSRF inválido", "danger")
                    return redirect(url_for('db_manager.index'))
        
        # Verificación adicional para depuración
        logger.info(f"Headers de solicitud en restart: {dict(request.headers)}")
        logger.info(f"Formulario en restart: {request.form}")
        logger.info(f"Es AJAX en restart: {is_ajax}")
        
        # Función para reiniciar la aplicación después de un breve retraso
        def delayed_restart():
            logger.info("Programando reinicio con retraso de 1 segundo...")
            time.sleep(1)  # Esperar 1 segundo para que la respuesta HTTP se complete
            logger.info("Ejecutando reinicio de la aplicación...")
            try:
                # Obtener ruta completa del ejecutable Python actual
                python_exe = sys.executable
                logger.info(f"Usando Python: {python_exe}")
                
                # Usar rutas relativas para mayor portabilidad entre máquinas
                # Obtener la ruta base del proyecto - independiente del sistema
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                main_script = os.path.join(base_dir, 'main.py')
                logger.info(f"Ruta del script principal: {main_script}")
                
                # Verificar que el archivo main.py existe
                if not os.path.exists(main_script):
                    logger.error(f"Error: El archivo {main_script} no existe")
                    return
                
                # Ejecutar el comando para reiniciar con prioridad alta
                logger.info(f"Ejecutando comando: {python_exe} {main_script}")
                # Usar subprocess.run para capturar salida y errores
                try:
                    # En Windows, usar creationflags para dar prioridad alta
                    if os.name == 'nt':
                        process = subprocess.Popen(
                            [python_exe, main_script],
                            creationflags=subprocess.CREATE_NEW_CONSOLE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        logger.info(f"Proceso iniciado con PID: {process.pid}")
                    else:  # En Linux/Mac
                        process = subprocess.Popen(
                            [python_exe, main_script],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        logger.info(f"Proceso iniciado con PID: {process.pid}")
                    
                    # Esperar un máximo de 3 segundos para procesar salida inicial
                    stdout, stderr = process.communicate(timeout=3)
                    logger.info(f"Salida inicial: {stdout}")
                    if stderr:
                        logger.warning(f"Errores iniciales: {stderr}")
                    
                except subprocess.TimeoutExpired:
                    # Esto es normal, significa que el proceso sigue ejecutándose
                    logger.info("El proceso sigue ejecutándose (esperable)")
                except Exception as sub_e:
                    logger.error(f"Error al iniciar proceso: {sub_e}")
                
                logger.info("Comando de reinicio ejecutado, cerrando proceso actual...")
                # Esperar un momento para asegurar que se inicie el nuevo proceso
                time.sleep(2)
                # Finalizar el proceso actual
                logger.info("Saliendo con os._exit(0)")
                os._exit(0)
            except Exception as e:
                logger.error(f"Error al reiniciar la aplicación: {e}")
        
        # Iniciar el proceso de reinicio en un hilo separado
        logger.info("Creando hilo para reinicio...")
        restart_thread = threading.Thread(target=delayed_restart)
        restart_thread.daemon = True
        restart_thread.start()
        logger.info("Hilo de reinicio iniciado")
        
        # Enviar respuesta según el tipo de petición
        if is_ajax:
            return jsonify({
                "success": True,
                "message": "La aplicación se está reiniciando. La página se actualizará automáticamente."
            })
        else:
            flash("La aplicación se está reiniciando. Espere un momento...", "info")
            return redirect(url_for('db_manager.index'))
            
    except Exception as e:
        logger.exception("Error al reiniciar la aplicación")
        if is_ajax:
            return jsonify({
                "success": False,
                "message": f"Error al reiniciar la aplicación: {str(e)}"
            }), 500
        else:
            flash(f"Error al reiniciar la aplicación: {str(e)}", "danger")
            return redirect(url_for('db_manager.index'))

# Ruta alternativa para reiniciar (para mayor compatibilidad)
@db_manager.route('/restart_app', methods=['POST'])
def restart_app_alt():
    """Alias de la ruta restart para mayor compatibilidad."""
    logger.info("Usando ruta alternativa /restart_app")
    return restart_app()

# Ruta para verificación en tiempo real de la base de datos
@db_manager.route('/verify_db', methods=['GET'])
def verify_db():
    """Realizar una verificación real de la base de datos activa."""
    try:
        # Obtener información de la base de datos
        db_info = db_backup_service.get_current_db_info()
        
        # Realizar una consulta de verificación real
        verification_result = db_backup_service.perform_verification_query()
        
        return jsonify({
            "success": True,
            "db_info": db_info,
            "verification": verification_result
        })
    
    except Exception as e:
        logger.exception("Error al verificar la base de datos")
        return jsonify({"success": False, "error": str(e)}), 500
