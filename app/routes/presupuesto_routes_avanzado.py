# Rutas adicionales para presupuestos avanzados
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from app.models.presupuesto import Presupuesto, Capitulo, Partida
from app.models.proyecto import Proyecto
from app.models.cliente import Cliente
from sqlalchemy import text, and_, or_
from app.services.db_service import get_all, get_by_id, create, update, delete
from app import db
from datetime import datetime
import traceback

# Esta función debe ser importada en app/routes/__init__.py y registrada en app/__init__.py
def register_presupuestos_avanzados(app):
    presupuestos_avanzados_bp = Blueprint('presupuestos_avanzados', __name__, url_prefix='/presupuestos')
    
    @presupuestos_avanzados_bp.route('/avanzado')
    def listar_presupuestos_avanzado():
        """
        Listado avanzado de presupuestos con filtros y campos adicionales
        """
        try:
            # Verificar si existe la columna estado_workflow
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columnas_presupuesto = [c['name'] for c in inspector.get_columns('presupuestos')]
            existe_estado_workflow = 'estado_workflow' in columnas_presupuesto
            
            if not existe_estado_workflow:
                flash('La columna estado_workflow no existe en la base de datos. Algunas funcionalidades estarán limitadas. Ejecute el script de migración.', 'warning')
            
            # Obtener todos los clientes para el filtro
            clientes = Cliente.query.order_by(Cliente.nombre).all()
            
            # Obtener tipos de proyecto únicos
            tipos_proyecto = db.session.query(Proyecto.tipo_proyecto) \
                            .filter(Proyecto.tipo_proyecto != None) \
                            .distinct() \
                            .order_by(Proyecto.tipo_proyecto) \
                            .all()
            tipos_proyecto = [t[0] for t in tipos_proyecto if t[0]]
            
            # Construir la consulta base
            query = db.session.query(Presupuesto, Proyecto, Cliente) \
                    .join(Proyecto, Presupuesto.id_proyecto == Proyecto.id) \
                    .join(Cliente, Proyecto.id_cliente == Cliente.id)
            
            # Aplicar filtros si están presentes en la solicitud
            if request.args:
                # Filtro por cliente
                if request.args.get('cliente'):
                    query = query.filter(Proyecto.id_cliente == request.args.get('cliente'))
                
                # Filtro por tipo de proyecto
                if request.args.get('tipo_proyecto'):
                    query = query.filter(Proyecto.tipo_proyecto == request.args.get('tipo_proyecto'))
                
                # Filtro por técnico encargado
                if request.args.get('tecnico'):
                    tecnico = f"%{request.args.get('tecnico')}%"
                    query = query.filter(Presupuesto.tecnico_encargado.ilike(tecnico))
                
                # Filtro por estado de workflow
                if request.args.get('estado_workflow'):
                    try:
                        query = query.filter(Presupuesto.estado_workflow == request.args.get('estado_workflow'))
                    except Exception as e:
                        flash('Filtro de estado de workflow no disponible. Ejecute la migración primero.', 'warning')
                
                # Filtro por fecha desde
                if request.args.get('fecha_desde'):
                    try:
                        fecha_desde = datetime.strptime(request.args.get('fecha_desde'), '%Y-%m-%d')
                        query = query.filter(Presupuesto.fecha >= fecha_desde)
                    except ValueError:
                        flash('Formato de fecha desde incorrecto', 'warning')
                
                # Filtro por fecha hasta
                if request.args.get('fecha_hasta'):
                    try:
                        fecha_hasta = datetime.strptime(request.args.get('fecha_hasta'), '%Y-%m-%d')
                        # Añadir un día completo para incluir todo el día final
                        fecha_hasta = datetime(fecha_hasta.year, fecha_hasta.month, fecha_hasta.day, 23, 59, 59)
                        query = query.filter(Presupuesto.fecha <= fecha_hasta)
                    except ValueError:
                        flash('Formato de fecha hasta incorrecto', 'warning')
                
                # Filtro por aprobado
                if request.args.get('aprobado') == 'si':
                    query = query.filter(Presupuesto.aprobacion != None)
                    query = query.filter(Presupuesto.aprobacion != '')
                elif request.args.get('aprobado') == 'no':
                    query = query.filter(or_(Presupuesto.aprobacion == None, Presupuesto.aprobacion == ''))
                
                # Filtro por referencia
                if request.args.get('ref'):
                    referencia = f"%{request.args.get('ref')}%"
                    query = query.filter(Presupuesto.referencia.ilike(referencia))
            
            # Ordenar por fecha descendente (más reciente primero)
            query = query.order_by(Presupuesto.fecha.desc())
            
            # Ejecutar la consulta
            presupuestos = query.all()
            
            return render_template('presupuestos/avanzado/lista.html', 
                                presupuestos=presupuestos,
                                clientes=clientes,
                                tipos_proyecto=tipos_proyecto)
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al cargar el listado avanzado: {str(e)}', 'danger')
            traceback.print_exc()
            return redirect(url_for('presupuestos.listar_presupuestos'))

    @presupuestos_avanzados_bp.route('/api/actualizar-aprobacion/<int:id>', methods=['POST'])
    def actualizar_aprobacion(id):
        """
        API para actualizar el estado de aprobación de un presupuesto
        """
        try:
            # Imprimir información para depuración
            print(f"Actualizando aprobación para presupuesto {id}")
            
            presupuesto = get_by_id(Presupuesto, id)
            if not presupuesto:
                print(f"Presupuesto {id} no encontrado")
                return jsonify({'success': False, 'error': 'Presupuesto no encontrado'}), 404
            
            # Verificar que los datos del request sean correctos
            if not request.is_json:
                print(f"Request no es JSON: {request.data}")
                return jsonify({'success': False, 'error': 'Se esperaba contenido JSON'}), 400
            
            data = request.get_json()
            print(f"Datos recibidos: {data}")
            
            if 'aprobacion' not in data:
                print("Falta el campo 'aprobacion' en los datos")
                return jsonify({'success': False, 'error': 'Datos de aprobación no proporcionados'}), 400
            
            # Guardar valor anterior para debugging
            aprobacion_anterior = presupuesto.aprobacion
            fecha_anterior = presupuesto.fecha_aprobacion
            
            # Actualizar la aprobación
            presupuesto.aprobacion = data['aprobacion']
            
            # Si se está aprobando, actualizar la fecha de aprobación
            if data.get('aprobacion'):
                presupuesto.fecha_aprobacion = datetime.utcnow()
                fecha_aprobacion_str = presupuesto.fecha_aprobacion.strftime('%d/%m/%Y')
            else:
                presupuesto.fecha_aprobacion = None
                fecha_aprobacion_str = 'No aprobado'
            
            # Imprimir información para depuración
            print(f"Cambio de aprobación: {aprobacion_anterior} -> {presupuesto.aprobacion}")
            print(f"Cambio de fecha: {fecha_anterior} -> {presupuesto.fecha_aprobacion}")
            
            # Guardar cambios
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': 'Estado de aprobación actualizado correctamente',
                'fecha_aprobacion': fecha_aprobacion_str
            })
        
        except Exception as e:
            db.session.rollback()
            print(f"Error en actualización de aprobación: {str(e)}")
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500

    @presupuestos_avanzados_bp.route('/api/actualizar-estado-workflow/<int:id>', methods=['POST'])
    def actualizar_estado_workflow(id):
        """
        API para actualizar el estado de workflow de un presupuesto
        """
        try:
            # Verificar si existe la columna estado_workflow
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columnas_presupuesto = [c['name'] for c in inspector.get_columns('presupuestos')]
            existe_estado_workflow = 'estado_workflow' in columnas_presupuesto
            
            if not existe_estado_workflow:
                return jsonify({
                    'success': False, 
                    'error': 'La columna estado_workflow no existe en la base de datos. Ejecute el script de migración primero.'
                }), 400
            
            presupuesto = get_by_id(Presupuesto, id)
            if not presupuesto:
                return jsonify({'success': False, 'error': 'Presupuesto no encontrado'}), 404
            
            data = request.get_json()
            if 'estado_workflow' not in data:
                return jsonify({'success': False, 'error': 'Datos de estado workflow no proporcionados'}), 400
            
            # Validar que el estado está entre los valores permitidos
            estados_permitidos = ['En estudio', 'Estudiado', 'Revisión', 'Enviado', 'Pendiente de envío', 'Ejecutado', 'En ejecución']
            if data.get('estado_workflow') not in estados_permitidos:
                return jsonify({'success': False, 'error': 'Estado de workflow no válido'}), 400
            
            # Intentar establecer el valor
            try:
                presupuesto.estado_workflow = data['estado_workflow']
                db.session.commit()
                
                return jsonify({
                    'success': True, 
                    'message': 'Estado de workflow actualizado correctamente'
                })
            except Exception as inner_e:
                db.session.rollback()
                return jsonify({
                    'success': False, 
                    'error': f'Error al actualizar el estado de workflow: {str(inner_e)}'
                }), 500
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
            
    app.register_blueprint(presupuestos_avanzados_bp)
    return presupuestos_avanzados_bp