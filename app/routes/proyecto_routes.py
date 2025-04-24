# app/routes/proyecto_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.proyecto import Proyecto
from app.models.cliente import Cliente
from app.services.db_service import get_all, get_by_id, create, update, delete
from app import db
from datetime import datetime
import re
import sqlite3
import os
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

proyectos_bp = Blueprint('proyectos', __name__, url_prefix='/proyectos')

@proyectos_bp.route('/')
def listar_proyectos():
    try:
        # Verificar primero si podemos hacer una consulta simple
        from sqlalchemy import text
        db.session.execute(text("SELECT 1")).scalar()
        
        # Si llegamos aquí, la conexión a la BD funciona
        proyectos = Proyecto.query.join(Cliente, Proyecto.id_cliente == Cliente.id, isouter=True)\
                   .order_by(Proyecto.fecha_creacion.desc())\
                   .all()
        return render_template('proyectos/lista.html', proyectos=proyectos)
    except Exception as e:
        # Si hay un error de conexión, mostrar mensaje amigable
        flash(f'Error al conectar con la base de datos: {str(e)}', 'danger')
        # Intentar verificar directamente el archivo de base de datos
        db_path = os.environ.get('DB_PATH', 'app/data/app.db')
        try:
            # Intentar conectarse directamente a SQLite
            conn = sqlite3.connect(db_path)
            conn.close()
            mensaje = f"La base de datos existe pero SQLAlchemy no puede conectarse. Verifica la configuración."
        except:
            mensaje = f"No se puede acceder al archivo de base de datos en {db_path}. Asegúrate de que exista y tenga permisos."
        
        return render_template('errors/database.html', error=str(e), mensaje=mensaje, db_path=db_path)

@proyectos_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_proyecto():
    # Obtener id_cliente de los parámetros de la URL (si existe)
    id_cliente_preseleccionado = request.args.get('id_cliente', None)
    cliente_preseleccionado = None
    
    if id_cliente_preseleccionado:
        try:
            cliente_preseleccionado = get_by_id(Cliente, int(id_cliente_preseleccionado))
            if not cliente_preseleccionado:
                flash('Cliente no encontrado', 'warning')
        except (ValueError, TypeError):
            flash('ID de cliente inválido', 'warning')
    
    if request.method == 'POST':
        try:
            # Obtener el id_cliente del formulario
            id_cliente = request.form.get('id_cliente')
            if not id_cliente:
                flash('El cliente es obligatorio para generar la referencia del proyecto', 'danger')
                clientes = get_all(Cliente)
                return render_template('proyectos/nuevo_simple.html', 
                                    clientes=clientes, 
                                    cliente_preseleccionado=cliente_preseleccionado,
                                    id_cliente_preseleccionado=id_cliente_preseleccionado)
            
            # Obtener el tipo de proyecto
            tipo_proyecto = request.form.get('tipo_proyecto', 'Otro')
            
            # Extraer las letras del tipo de proyecto (primera y tercera)
            tipo_abreviado = ''
            if tipo_proyecto and len(tipo_proyecto) >= 3:
                tipo_abreviado = tipo_proyecto[0] + tipo_proyecto[2]
            elif tipo_proyecto and len(tipo_proyecto) >= 1:
                tipo_abreviado = tipo_proyecto[0] + 'X'  # Si el tipo es muy corto
            else:
                tipo_abreviado = 'XX'  # Valor por defecto
            
            tipo_abreviado = tipo_abreviado.upper()  # Convertir a mayúsculas
            
            # Formatear el número de cliente con tres dígitos
            try:
                num_cliente = int(id_cliente)
                cliente_formateado = f"{num_cliente:03d}"
            except (ValueError, TypeError):
                cliente_formateado = "000"
            
            # Obtener la fecha actual para el formato DDMMAA
            fecha_actual = datetime.now()
            fecha_formateada = fecha_actual.strftime("%d%m%y")
            
            # Crear la nueva referencia en formato PR001RF-DDMMAA
            nueva_referencia = f"PR{cliente_formateado}{tipo_abreviado}-{fecha_formateada}"
            
            # Verificar si ya existe un proyecto con esta referencia
            proyecto_existente = Proyecto.query.filter_by(referencia=nueva_referencia).first()
            if proyecto_existente:
                flash(f'Ya existe un proyecto con la referencia {nueva_referencia}. Por favor, modifique algún parámetro.', 'warning')
                clientes = get_all(Cliente)
                return render_template('proyectos/nuevo_simple.html', 
                                    clientes=clientes, 
                                    cliente_preseleccionado=cliente_preseleccionado,
                                    id_cliente_preseleccionado=id_cliente_preseleccionado)
            
            data = {
                'id_cliente': request.form.get('id_cliente'),
                'tipo_proyecto': request.form.get('tipo_proyecto'),
                'tipo_via': request.form.get('tipo_via'),
                'nombre_via': request.form.get('nombre_via'),
                'numero': request.form.get('numero_via'),
                'puerta': request.form.get('puerta'),
                'codigo_postal': request.form.get('codigo_postal'),
                'poblacion': request.form.get('poblacion'),
                'nombre_proyecto': request.form.get('nombre_proyecto'),
                'fecha_creacion': datetime.utcnow(),
                'referencia': nueva_referencia,
                'fecha_modificacion': datetime.utcnow(),
                'estado': 'Activo'
            }
            
            # Crear el proyecto
            proyecto = Proyecto(**data)
            db.session.add(proyecto)
            db.session.commit()
            
            flash('Proyecto creado correctamente', 'success')
            return redirect(url_for('proyectos.listar_proyectos'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear proyecto: {str(e)}', 'danger')
    
    try:
        clientes = get_all(Cliente)
        return render_template('proyectos/nuevo_simple.html', 
                              clientes=clientes, 
                              cliente_preseleccionado=cliente_preseleccionado,
                              id_cliente_preseleccionado=id_cliente_preseleccionado)
    except SQLAlchemyError:
        flash('Error al conectar con la base de datos', 'danger')
        return redirect(url_for('index'))

@proyectos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_proyecto(id):
    try:
        proyecto = get_by_id(Proyecto, id)
        
        if not proyecto:
            flash('Proyecto no encontrado', 'danger')
            return redirect(url_for('proyectos.listar_proyectos'))
        
        if request.method == 'POST':
            try:
                data = {
                    'id_cliente': request.form.get('id_cliente'),
                    'tipo_proyecto': request.form.get('tipo_proyecto'),
                    'tipo_via': request.form.get('tipo_via'),
                    'nombre_via': request.form.get('nombre_via'),
                    'numero': request.form.get('numero_via'),
                    'puerta': request.form.get('puerta'),
                    'codigo_postal': request.form.get('codigo_postal'),
                    'poblacion': request.form.get('poblacion'),
                    'nombre_proyecto': request.form.get('nombre_proyecto'),
                    'fecha_modificacion': datetime.utcnow(),
                    'estado': request.form.get('estado')
                }
                
                update(Proyecto, id, data)
                flash('Proyecto actualizado correctamente', 'success')
                return redirect(url_for('proyectos.listar_proyectos'))
            
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar proyecto: {str(e)}', 'danger')
        
        clientes = get_all(Cliente)
        return render_template('proyectos/editar.html', proyecto=proyecto, clientes=clientes)
    
    except SQLAlchemyError as e:
        flash(f'Error al conectar con la base de datos: {str(e)}', 'danger')
        return redirect(url_for('index'))

@proyectos_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_proyecto(id):
    try:
        delete(Proyecto, id)
        flash('Proyecto eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar proyecto: {str(e)}', 'danger')
    
    return redirect(url_for('proyectos.listar_proyectos'))

@proyectos_bp.route('/por-cliente/<int:id_cliente>')
def proyectos_por_cliente(id_cliente):
    try:
        # Usar el parámetro id_cliente pero con manejo de nulos
        proyectos = Proyecto.query.filter(Proyecto.id_cliente == id_cliente).all()
        return render_template('proyectos/por_cliente.html', 
                              proyectos=proyectos, 
                              cliente=get_by_id(Cliente, id_cliente))
    except SQLAlchemyError as e:
        flash(f'Error al conectar con la base de datos: {str(e)}', 'danger')
        return redirect(url_for('index'))

@proyectos_bp.route('/api/proyectos')
def api_listar_proyectos():
    try:
        proyectos = get_all(Proyecto)
        return jsonify([proyecto.to_dict() for proyecto in proyectos])
    except SQLAlchemyError as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500

@proyectos_bp.route('/api/proyectos/<int:id>')
def api_get_proyecto(id):
    try:
        proyecto = get_by_id(Proyecto, id)
        if proyecto:
            return jsonify(proyecto.to_dict())
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    except SQLAlchemyError as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500

@proyectos_bp.route('/api/proyectos/cliente/<int:id_cliente>')
def api_proyectos_por_cliente(id_cliente):
    try:
        proyectos = Proyecto.query.filter(Proyecto.id_cliente == id_cliente).all()
        return jsonify([proyecto.to_dict() for proyecto in proyectos])
    except SQLAlchemyError as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500