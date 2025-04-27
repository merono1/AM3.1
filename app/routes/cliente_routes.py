# app/routes/cliente_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.cliente import Cliente
from app.services.db_service import get_all, get_by_id, create, update, delete
from app import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import os
import sqlite3

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@clientes_bp.route('/')
def listar_clientes():
    try:
        # Verificar la conexión a la base de datos
        from sqlalchemy import text
        db.session.execute(text("SELECT 1")).scalar()
        
        # Si llegamos aquí, la conexión funciona
        clientes = get_all(Cliente)
        return render_template('clientes/lista.html', clientes=clientes)
    
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

@clientes_bp.route('/debug')
def listar_clientes_debug():
    try:
        # Verificar la conexión a la base de datos
        from sqlalchemy import text
        db.session.execute(text("SELECT 1")).scalar()
        
        # Si llegamos aquí, la conexión funciona
        clientes = get_all(Cliente)
        return render_template('clientes/lista_simplificada.html', clientes=clientes)
    
    except Exception as e:
        # Si hay un error de conexión, mostrar mensaje amigable
        flash(f'Error al conectar con la base de datos: {str(e)}', 'danger')
        db_path = os.environ.get('DB_PATH', 'app/data/app.db')
        return render_template('errors/database.html', error=str(e), mensaje="Error en vista simplificada", db_path=db_path)

@clientes_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    if request.method == 'POST':
        try:
            data = {
                'nombre': request.form.get('nombre'),
                'tipo_via': request.form.get('tipo_via'),
                'nombre_via': request.form.get('nombre_via'),
                'numero_via': request.form.get('numero_via'),
                'puerta': request.form.get('puerta'),
                'codigo_postal': request.form.get('codigo_postal'),
                'poblacion': request.form.get('poblacion'),
                'cif_nif': request.form.get('cif_nif'),
                'telefono1': request.form.get('telefono1'),
                'telefono2': request.form.get('telefono2'),
                'telefono3': request.form.get('telefono3'),
                'telefono4': request.form.get('telefono4'),
                'mail1': request.form.get('mail1'),
                'mail2': request.form.get('mail2'),
                'tipo_cliente': request.form.get('tipo_cliente'),
                'categoria_cliente': request.form.get('categoria_cliente'),
                'notas': request.form.get('notas'),
                'fecha_creacion': datetime.utcnow(),
                'fecha_modificacion': datetime.utcnow()
            }
            
            create(Cliente, data)
            flash('Cliente creado correctamente', 'success')
            return redirect(url_for('clientes.listar_clientes'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear cliente: {str(e)}', 'danger')
    
    try:
        return render_template('clientes/nuevo.html')
    except Exception as e:
        flash(f'Error al cargar la plantilla: {str(e)}', 'danger')
        return redirect(url_for('index'))

@clientes_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    try:
        cliente = get_by_id(Cliente, id)
        
        if not cliente:
            flash('Cliente no encontrado', 'danger')
            return redirect(url_for('clientes.listar_clientes'))
        
        if request.method == 'POST':
            try:
                data = {
                    'nombre': request.form.get('nombre'),
                    'tipo_via': request.form.get('tipo_via'),
                    'nombre_via': request.form.get('nombre_via'),
                    'numero_via': request.form.get('numero_via'),
                    'puerta': request.form.get('puerta'),
                    'codigo_postal': request.form.get('codigo_postal'),
                    'poblacion': request.form.get('poblacion'),
                    'cif_nif': request.form.get('cif_nif'),
                    'telefono1': request.form.get('telefono1'),
                    'telefono2': request.form.get('telefono2'),
                    'telefono3': request.form.get('telefono3'),
                    'telefono4': request.form.get('telefono4'),
                    'mail1': request.form.get('mail1'),
                    'mail2': request.form.get('mail2'),
                    'tipo_cliente': request.form.get('tipo_cliente'),
                    'categoria_cliente': request.form.get('categoria_cliente'),
                    'notas': request.form.get('notas'),
                    'fecha_modificacion': datetime.utcnow()
                }
                
                update(Cliente, id, data)
                flash('Cliente actualizado correctamente', 'success')
                return redirect(url_for('clientes.listar_clientes'))
            
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar cliente: {str(e)}', 'danger')
        
        return render_template('clientes/editar.html', cliente=cliente)
    
    except SQLAlchemyError as e:
        flash(f'Error al conectar con la base de datos: {str(e)}', 'danger')
        return redirect(url_for('index'))

@clientes_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_cliente(id):
    try:
        delete(Cliente, id)
        flash('Cliente eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar cliente: {str(e)}', 'danger')
    
    return redirect(url_for('clientes.listar_clientes'))

@clientes_bp.route('/notas/<int:id>', methods=['POST'])
def actualizar_nota(id):
    try:
        cliente = get_by_id(Cliente, id)
        if cliente:
            cliente.notas = request.form.get('nueva_nota')
            cliente.fecha_modificacion = datetime.utcnow()
            db.session.commit()
            flash('Nota actualizada correctamente', 'success')
        else:
            flash('Cliente no encontrado', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar nota: {str(e)}', 'danger')
    
    return redirect(url_for('clientes.listar_clientes'))

@clientes_bp.route('/api/clientes')
def api_listar_clientes():
    try:
        clientes = get_all(Cliente)
        return jsonify([cliente.to_dict() for cliente in clientes if hasattr(cliente, 'to_dict')])
    except SQLAlchemyError as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500

@clientes_bp.route('/api/clientes/<int:id>')
def api_get_cliente(id):
    try:
        cliente = get_by_id(Cliente, id)
        if cliente and hasattr(cliente, 'to_dict'):
            return jsonify(cliente.to_dict())
        return jsonify({'error': 'Cliente no encontrado'}), 404
    except SQLAlchemyError as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500