# app/routes/proveedor_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.proveedor import Proveedor
from app.services.db_service import get_all, get_by_id, create, update, delete
from app import db
from datetime import datetime
import re

proveedores_bp = Blueprint('proveedores', __name__, url_prefix='/proveedores')

@proveedores_bp.route('/')
def listar_proveedores():
    proveedores = get_all(Proveedor)
    return render_template('proveedores/lista.html', proveedores=proveedores)

@proveedores_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_proveedor():
    if request.method == 'POST':
        try:
            # Generar referencia automática
            año_actual = datetime.now().year
            ultimo_proveedor = Proveedor.query.filter(Proveedor.referencia.like(f"PROV-{año_actual}%")) \
                                 .order_by(Proveedor.id.desc()).first()
            
            if ultimo_proveedor:
                # Extraer el número secuencial y aumentarlo
                match = re.search(r'(\d+)$', ultimo_proveedor.referencia)
                if match:
                    num = int(match.group(1)) + 1
                else:
                    num = 1
            else:
                num = 1
                
            # Crear referencia en formato PROV-YYYY-XXX
            referencia = f"PROV-{año_actual}-{num:03d}"
            
            data = {
                'referencia': referencia,
                'tipo': request.form.get('tipo'),
                'nombre': request.form.get('nombre'),
                'razon_social': request.form.get('razon_social'),
                'direccion': request.form.get('direccion'),
                'codigo_postal': request.form.get('codigo_postal'),
                'localidad': request.form.get('localidad'),
                'provincia': request.form.get('provincia'),
                'pais': request.form.get('pais'),
                'telefono1': request.form.get('telefono1'),
                'telefono2': request.form.get('telefono2'),
                'telefono3': request.form.get('telefono3'),
                'telefono4': request.form.get('telefono4'),
                'email1': request.form.get('email1'),
                'email2': request.form.get('email2'),
                'contacto': request.form.get('contacto'),
                'contacto_telefono1': request.form.get('contacto_telefono1'),
                'contacto_telefono2': request.form.get('contacto_telefono2'),
                'contacto_email': request.form.get('contacto_email'),
                'fecha_alta': datetime.utcnow(),
                'fecha_modificacion': datetime.utcnow(),
                'especialidad': request.form.get('especialidad'),
                'notas': request.form.get('notas')
            }
            
            create(Proveedor, data)
            flash('Proveedor creado correctamente', 'success')
            return redirect(url_for('proveedores.listar_proveedores'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear proveedor: {str(e)}', 'danger')
    
    return render_template('proveedores/nuevo.html')

@proveedores_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_proveedor(id):
    proveedor = get_by_id(Proveedor, id)
    
    if not proveedor:
        flash('Proveedor no encontrado', 'danger')
        return redirect(url_for('proveedores.listar_proveedores'))
    
    if request.method == 'POST':
        try:
            data = {
                'tipo': request.form.get('tipo'),
                'nombre': request.form.get('nombre'),
                'razon_social': request.form.get('razon_social'),
                'direccion': request.form.get('direccion'),
                'codigo_postal': request.form.get('codigo_postal'),
                'localidad': request.form.get('localidad'),
                'provincia': request.form.get('provincia'),
                'pais': request.form.get('pais'),
                'telefono1': request.form.get('telefono1'),
                'telefono2': request.form.get('telefono2'),
                'telefono3': request.form.get('telefono3'),
                'telefono4': request.form.get('telefono4'),
                'email1': request.form.get('email1'),
                'email2': request.form.get('email2'),
                'contacto': request.form.get('contacto'),
                'contacto_telefono1': request.form.get('contacto_telefono1'),
                'contacto_telefono2': request.form.get('contacto_telefono2'),
                'contacto_email': request.form.get('contacto_email'),
                'fecha_modificacion': datetime.utcnow(),
                'especialidad': request.form.get('especialidad'),
                'notas': request.form.get('notas')
            }
            
            update(Proveedor, id, data)
            flash('Proveedor actualizado correctamente', 'success')
            return redirect(url_for('proveedores.listar_proveedores'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar proveedor: {str(e)}', 'danger')
    
    return render_template('proveedores/editar.html', proveedor=proveedor)

@proveedores_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_proveedor(id):
    try:
        delete(Proveedor, id)
        flash('Proveedor eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar proveedor: {str(e)}', 'danger')
    
    return redirect(url_for('proveedores.listar_proveedores'))

@proveedores_bp.route('/api/proveedores')
def api_listar_proveedores():
    proveedores = get_all(Proveedor)
    return jsonify([proveedor.to_dict() for proveedor in proveedores])
    
@proveedores_bp.route('/api/proveedores/listar')
def api_listar_proveedores_json():
    proveedores = get_all(Proveedor)
    proveedores_list = [{
        'id': p.id,
        'nombre': p.nombre,
        'especialidad': p.especialidad,
        'referencia': p.referencia
    } for p in proveedores]
    return jsonify({
        'success': True,
        'proveedores': proveedores_list
    })

@proveedores_bp.route('/api/proveedores/<int:id>')
def api_get_proveedor(id):
    proveedor = get_by_id(Proveedor, id)
    if proveedor:
        return jsonify(proveedor.to_dict())
    return jsonify({'error': 'Proveedor no encontrado'}), 404

@proveedores_bp.route('/api/proveedores/buscar')
def api_buscar_proveedores():
    termino = request.args.get('termino', '')
    if not termino:
        return jsonify([])
    
    proveedores = Proveedor.query.filter(
        (Proveedor.nombre.like(f'%{termino}%')) |
        (Proveedor.razon_social.like(f'%{termino}%')) |
        (Proveedor.especialidad.like(f'%{termino}%'))
    ).all()
    
    return jsonify([proveedor.to_dict() for proveedor in proveedores])