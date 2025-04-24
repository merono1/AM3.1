
# app/routes/proveedor_partida_routes.py
from flask import Blueprint, request, jsonify, flash
from app.models.proveedor_partida import ProveedorPartida
from app.models.hoja_trabajo import PartidaHoja
from app.models.proveedor import Proveedor
from app.services.db_service import get_by_id
from app import db
from datetime import datetime
import traceback

proveedor_partida_bp = Blueprint('proveedor_partida', __name__, url_prefix='/api/proveedores-partidas')

@proveedor_partida_bp.route('/asignar', methods=['POST'])
def asignar_proveedor():
    """Asigna un proveedor a una partida"""
    try:
        # Obtener datos del formulario
        id_partida = request.form.get('id_partida')
        id_proveedor = request.form.get('id_proveedor')
        precio = float(request.form.get('precio') or 0)
        margen = float(request.form.get('margen') or 0)
        notas = request.form.get('notas', '')
        
        if not id_partida or not id_proveedor:
            return jsonify({'success': False, 'error': 'Faltan datos obligatorios'}), 400
        
        # Verificar si la partida y el proveedor existen
        partida = get_by_id(PartidaHoja, id_partida)
        proveedor = get_by_id(Proveedor, id_proveedor)
        
        if not partida:
            return jsonify({'success': False, 'error': 'Partida no encontrada'}), 404
            
        if not proveedor:
            return jsonify({'success': False, 'error': 'Proveedor no encontrado'}), 404
            
        # Verificar si ya existe esta asignación
        proveedor_existente = ProveedorPartida.query.filter_by(
            id_partida=id_partida, 
            id_proveedor=id_proveedor
        ).first()
        
        if proveedor_existente:
            # Actualizar la asignación existente
            proveedor_existente.precio = precio
            proveedor_existente.margen_proveedor = margen
            proveedor_existente.notas = notas
            proveedor_existente.fecha_asignacion = datetime.utcnow()
            
            # Calcular el final del proveedor
            proveedor_existente.calcular_final_proveedor()
            
            db.session.commit()
            return jsonify({
                'success': True, 
                'message': 'Proveedor actualizado correctamente',
                'proveedor_partida': {
                    'id': proveedor_existente.id,
                    'id_partida': proveedor_existente.id_partida,
                    'id_proveedor': proveedor_existente.id_proveedor,
                    'nombre_proveedor': proveedor.nombre,
                    'precio': proveedor_existente.precio,
                    'margen_proveedor': proveedor_existente.margen_proveedor,
                    'final_proveedor': proveedor_existente.final_proveedor,
                    'notas': proveedor_existente.notas,
                    'estado': proveedor_existente.estado
                }
            })
        
        # Crear una nueva asignación
        proveedor_partida = ProveedorPartida(
            id_partida=id_partida,
            id_proveedor=id_proveedor,
            precio=precio,
            margen_proveedor=margen,
            notas=notas,
            fecha_asignacion=datetime.utcnow(),
            estado='Pendiente'
        )
        
        # Calcular el final del proveedor
        proveedor_partida.calcular_final_proveedor()
        
        db.session.add(proveedor_partida)
        db.session.commit()
        
        # Si se marca como principal, actualizar la partida
        es_principal = request.form.get('es_principal') == 'true'
        if es_principal:
            partida.id_proveedor_principal = id_proveedor
            partida.precio_proveedor = precio
            db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Proveedor asignado correctamente',
            'proveedor_partida': {
                'id': proveedor_partida.id,
                'id_partida': proveedor_partida.id_partida,
                'id_proveedor': proveedor_partida.id_proveedor,
                'nombre_proveedor': proveedor.nombre,
                'precio': proveedor_partida.precio,
                'margen_proveedor': proveedor_partida.margen_proveedor,
                'final_proveedor': proveedor_partida.final_proveedor,
                'notas': proveedor_partida.notas,
                'estado': proveedor_partida.estado
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al asignar proveedor: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@proveedor_partida_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar_proveedor_partida(id):
    """Elimina la asignación de un proveedor a una partida"""
    try:
        proveedor_partida = get_by_id(ProveedorPartida, id)
        if not proveedor_partida:
            return jsonify({'success': False, 'error': 'Asignación no encontrada'}), 404
            
        # Comprobar si es el proveedor principal y actualizar partida
        partida = get_by_id(PartidaHoja, proveedor_partida.id_partida)
        if partida and partida.id_proveedor_principal == proveedor_partida.id_proveedor:
            partida.id_proveedor_principal = None
            partida.precio_proveedor = None
            
        # Eliminar asignación
        db.session.delete(proveedor_partida)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Asignación eliminada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar asignación: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@proveedor_partida_bp.route('/por-partida/<int:id_partida>', methods=['GET'])
def obtener_proveedores_partida(id_partida):
    """Obtiene todos los proveedores asignados a una partida"""
    try:
        # Verificar si la partida existe
        partida = get_by_id(PartidaHoja, id_partida)
        if not partida:
            return jsonify({'success': False, 'error': 'Partida no encontrada'}), 404
            
        # Obtener proveedores asignados
        proveedores = db.session.query(
            ProveedorPartida, Proveedor
        ).join(
            Proveedor, ProveedorPartida.id_proveedor == Proveedor.id
        ).filter(
            ProveedorPartida.id_partida == id_partida
        ).all()
        
        # Formatear respuesta
        result = []
        for pp, prov in proveedores:
            result.append({
                'id': pp.id,
                'id_proveedor': pp.id_proveedor,
                'nombre_proveedor': prov.nombre,
                'especialidad': prov.especialidad,
                'precio': pp.precio,
                'margen_proveedor': pp.margen_proveedor,
                'final_proveedor': pp.final_proveedor,
                'es_principal': partida.id_proveedor_principal == pp.id_proveedor,
                'fecha_asignacion': pp.fecha_asignacion.strftime('%d/%m/%Y') if pp.fecha_asignacion else None,
                'notas': pp.notas,
                'estado': pp.estado
            })
            
        return jsonify({
            'success': True, 
            'proveedores': result
        })
        
    except Exception as e:
        print(f"Error al obtener proveedores: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@proveedor_partida_bp.route('/establecer-principal', methods=['POST'])
def establecer_proveedor_principal():
    """Establece un proveedor como principal para una partida"""
    try:
        id_partida = request.form.get('id_partida')
        id_proveedor = request.form.get('id_proveedor')
        
        if not id_partida or not id_proveedor:
            return jsonify({'success': False, 'error': 'Faltan datos obligatorios'}), 400
            
        # Verificar si la partida existe
        partida = get_by_id(PartidaHoja, id_partida)
        if not partida:
            return jsonify({'success': False, 'error': 'Partida no encontrada'}), 404
            
        # Verificar si existe la asignación
        proveedor_partida = ProveedorPartida.query.filter_by(
            id_partida=id_partida, 
            id_proveedor=id_proveedor
        ).first()
        
        if not proveedor_partida:
            return jsonify({'success': False, 'error': 'No existe asignación para este proveedor'}), 404
            
        # Establecer como principal
        partida.id_proveedor_principal = id_proveedor
        partida.precio_proveedor = proveedor_partida.precio
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Proveedor establecido como principal correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al establecer proveedor principal: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@proveedor_partida_bp.route('/actualizar/<int:id>', methods=['POST'])
def actualizar_proveedor_partida(id):
    """Actualiza la información de un proveedor asignado a una partida"""
    try:
        proveedor_partida = get_by_id(ProveedorPartida, id)
        if not proveedor_partida:
            return jsonify({'success': False, 'error': 'Asignación no encontrada'}), 404
            
        # Actualizar datos
        if 'precio' in request.form:
            proveedor_partida.precio = float(request.form.get('precio') or 0)
            
        if 'margen_proveedor' in request.form:
            proveedor_partida.margen_proveedor = float(request.form.get('margen_proveedor') or 0)
            
        if 'notas' in request.form:
            proveedor_partida.notas = request.form.get('notas')
            
        if 'estado' in request.form:
            proveedor_partida.estado = request.form.get('estado')
            
        # Recalcular final_proveedor
        proveedor_partida.calcular_final_proveedor()
        
        # Si es proveedor principal, actualizar la partida
        partida = get_by_id(PartidaHoja, proveedor_partida.id_partida)
        if partida and partida.id_proveedor_principal == proveedor_partida.id_proveedor:
            partida.precio_proveedor = proveedor_partida.precio
            
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Información actualizada correctamente',
            'proveedor_partida': {
                'id': proveedor_partida.id,
                'precio': proveedor_partida.precio,
                'margen_proveedor': proveedor_partida.margen_proveedor,
                'final_proveedor': proveedor_partida.final_proveedor,
                'notas': proveedor_partida.notas,
                'estado': proveedor_partida.estado
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar proveedor: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
