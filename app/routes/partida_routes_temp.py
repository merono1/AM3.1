"""
Archivo temporal con funciones alternativas para manejar partidas
sin el campo numero hasta que se actualice la base de datos.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.presupuesto import Presupuesto, Capitulo, Partida
from app.services.db_service import get_by_id
from app import db

# Función alternativa para crear partida (sin usar el campo numero)
def crear_partida_temp(id_presupuesto):
    try:
        capitulo_numero = request.form.get('capitulo_numero')
        
        cantidad = float(request.form.get('cantidad') or 0)
        precio = float(request.form.get('precio') or 0)
        total = cantidad * precio
        margen = float(request.form.get('margen') or 0)
        final = total * (1 + margen / 100)
        
        # Crea un diccionario con los datos para insertar manualmente
        data = {
            'id_presupuesto': id_presupuesto,
            'capitulo_numero': capitulo_numero,
            'descripcion': request.form.get('descripcion'),
            'unitario': request.form.get('unitario'),
            'cantidad': cantidad,
            'precio': precio,
            'total': total,
            'margen': margen,
            'final': final
        }
        
        # Inserta usando SQL directo sin el campo numero
        conn = db.engine.connect()
        query = """
        INSERT INTO partidas (id_presupuesto, capitulo_numero, descripcion, 
                            unitario, cantidad, precio, total, margen, final)
        VALUES (:id_presupuesto, :capitulo_numero, :descripcion, 
                :unitario, :cantidad, :precio, :total, :margen, :final)
        """
        conn.execute(query, data)
        conn.close()
        
        flash('Partida creada correctamente (modo alternativo)', 'success')
        return True
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear partida (modo alternativo): {str(e)}', 'danger')
        return False
