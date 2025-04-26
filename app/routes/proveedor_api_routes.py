# app/routes/proveedor_api_routes.py
from flask import Blueprint, request, jsonify
from app.models.proveedor import Proveedor
from app.models.proveedor_partida import ProveedorPartida
from app.models.hoja_trabajo import PartidaHoja
from app.services.db_service import get_all, get_by_id
from app import db
import traceback

# Crear un Blueprint específico para la API de proveedores
proveedor_api_bp = Blueprint('api_proveedor', __name__, url_prefix='/api/proveedores')

@proveedor_api_bp.route('/listar', methods=['GET'])
def listar_proveedores():
    """Retorna lista de proveedores en formato JSON"""
    try:
        proveedores = get_all(Proveedor)
        return jsonify({
            'success': True,
            'proveedores': [
                {
                    'id': p.id,
                    'nombre': p.nombre,
                    'especialidad': p.especialidad,
                    'telefono': p.telefono1
                } for p in proveedores
            ]
        })
    except Exception as e:
        print(f"Error al listar proveedores: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@proveedor_api_bp.route('/buscar', methods=['GET'])
def buscar_proveedores():
    """Busca proveedores por nombre o especialidad"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'success': True,
                'proveedores': []
            })
        
        proveedores = Proveedor.query.filter(
            db.or_(
                Proveedor.nombre.ilike(f'%{query}%'),
                Proveedor.especialidad.ilike(f'%{query}%')
            )
        ).all()
        
        return jsonify({
            'success': True,
            'proveedores': [
                {
                    'id': p.id,
                    'nombre': p.nombre,
                    'especialidad': p.especialidad,
                    'telefono': p.telefono1
                } for p in proveedores
            ]
        })
    except Exception as e:
        print(f"Error al buscar proveedores: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@proveedor_api_bp.route('/obtener/<int:id>', methods=['GET'])
def obtener_proveedor(id):
    """Obtiene detalles de un proveedor específico"""
    try:
        proveedor = get_by_id(Proveedor, id)
        if not proveedor:
            return jsonify({
                'success': False,
                'error': 'Proveedor no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'proveedor': proveedor.to_dict()
        })
    except Exception as e:
        print(f"Error al obtener proveedor: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@proveedor_api_bp.route('/partidas/<int:id_proveedor>', methods=['GET'])
def listar_partidas_proveedor(id_proveedor):
    """Lista las partidas asociadas a un proveedor"""
    try:
        proveedor = get_by_id(Proveedor, id_proveedor)
        if not proveedor:
            return jsonify({
                'success': False,
                'error': 'Proveedor no encontrado'
            }), 404
        
        # Obtener las asignaciones de partidas
        asignaciones = ProveedorPartida.query.filter_by(id_proveedor=id_proveedor).all()
        
        # Obtener detalles de cada partida
        partidas = []
        for asignacion in asignaciones:
            partida = get_by_id(PartidaHoja, asignacion.id_partida)
            if partida:
                # Obtener la hoja de trabajo asociada para más contexto
                hoja = get_by_id(db.models.hoja_trabajo.HojaTrabajo, partida.id_hoja)
                partidas.append({
                    'id_asignacion': asignacion.id,
                    'id_partida': partida.id,
                    'descripcion': partida.descripcion,
                    'hoja_referencia': hoja.referencia if hoja else 'Desconocida',
                    'precio_proveedor': asignacion.precio,
                    'margen_proveedor': asignacion.margen_proveedor,
                    'final_proveedor': asignacion.final_proveedor,
                    'es_principal': (partida.id_proveedor_principal == id_proveedor),
                    'estado': asignacion.estado
                })
        
        return jsonify({
            'success': True,
            'partidas': partidas
        })
    except Exception as e:
        print(f"Error al listar partidas: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_api_routes(app):
    """Registra las rutas API en la aplicación"""
    app.register_blueprint(proveedor_api_bp)
