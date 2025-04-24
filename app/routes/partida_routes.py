# app/routes/partida_routes.py
from flask import Blueprint, request, jsonify, flash, redirect, url_for
from app.models.presupuesto import Partida
from app import db
import traceback

partidas_bp = Blueprint('partidas', __name__, url_prefix='/presupuestos/partidas')

@partidas_bp.route('/<int:id>/actualizar_descripcion', methods=['POST'])
def actualizar_descripcion(id):
    """Actualiza la descripción de una partida mediante AJAX"""
    try:
        # Obtener la partida
        partida = Partida.query.get(id)
        if not partida:
            return jsonify({'success': False, 'error': 'Partida no encontrada'}), 404
        
        # Obtener la nueva descripción
        descripcion = request.form.get('descripcion')
        if not descripcion:
            return jsonify({'success': False, 'error': 'Descripción no proporcionada'}), 400
        
        # Actualizar la descripción
        partida.descripcion = descripcion
        
        # Guardar en la base de datos
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Descripción actualizada correctamente',
            'partida': {
                'id': partida.id,
                'descripcion': partida.descripcion
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar descripción de partida {id}: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Error al actualizar descripción: {str(e)}'}), 500
