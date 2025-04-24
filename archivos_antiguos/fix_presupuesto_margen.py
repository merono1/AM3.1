"""
Script para añadir la función de aplicar margen a todas las partidas en presupuesto_routes.py
"""

import os

def actualizar_archivo():
    # Archivo a modificar
    ruta_archivo = os.path.join('app', 'routes', 'presupuesto_routes.py')
    
    # Leer el contenido actual
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Código a añadir al final del archivo
    codigo_nuevo = """

@presupuestos_bp.route('/aplicar-margen-todas/<int:id>', methods=['POST'])
def aplicar_margen_todas(id):
    """Aplica un margen determinado a todas las partidas de un presupuesto"""
    try:
        # Verificar que el presupuesto existe
        presupuesto = get_by_id(Presupuesto, id)
        if not presupuesto:
            return jsonify({'success': False, 'error': 'Presupuesto no encontrado'}), 404
        
        # Obtener los datos del request
        data = request.get_json()
        if not data or 'margen' not in data:
            return jsonify({'success': False, 'error': 'Datos inválidos'}), 400
        
        # Obtener el nuevo margen
        nuevo_margen = float(data['margen'])
        
        # Aplicar el margen a todas las partidas
        partidas = Partida.query.filter_by(id_presupuesto=id).all()
        for partida in partidas:
            partida.margen = nuevo_margen
            partida.final = partida.total * (1 + nuevo_margen / 100)
        
        # Guardar los cambios
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Margen aplicado correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
"""
    
    # Añadir el código nuevo al final del archivo
    with open(ruta_archivo, 'a', encoding='utf-8') as f:
        f.write(codigo_nuevo)
    
    print(f"✅ Archivo {ruta_archivo} actualizado correctamente")

if __name__ == "__main__":
    actualizar_archivo()
    print("Para que los cambios surtan efecto, reinicia la aplicación.")
