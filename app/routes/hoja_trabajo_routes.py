from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.hoja_trabajo import HojaTrabajo, CapituloHoja, PartidaHoja
from app.models.proyecto import Proyecto
from app.models.presupuesto import Presupuesto
from app.services.db_service import db
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import logging

hojas_trabajo_bp = Blueprint('hojas_trabajo', __name__)
logger = logging.getLogger(__name__)

@hojas_trabajo_bp.route('/hojas_trabajo')
def listar_hojas_trabajo():
    try:
        hojas = HojaTrabajo.query.all()
        return render_template('hojas_trabajo/lista.html', hojas=hojas)
    except SQLAlchemyError as e:
        logger.error(f"Error al listar hojas de trabajo: {str(e)}")
        flash('Error al obtener las hojas de trabajo', 'danger')
        return render_template('hojas_trabajo/lista.html', hojas=[])

@hojas_trabajo_bp.route('/hojas_trabajo/por_presupuesto/<int:id_presupuesto>')
def hojas_por_presupuesto(id_presupuesto):
    try:
        hojas = HojaTrabajo.query.filter_by(id_presupuesto=id_presupuesto).all()
        presupuesto = Presupuesto.query.get_or_404(id_presupuesto)
        return render_template('hojas_trabajo/lista.html', hojas=hojas, id_presupuesto=id_presupuesto, presupuesto=presupuesto)
    except SQLAlchemyError as e:
        logger.error(f"Error al listar hojas de trabajo por presupuesto: {str(e)}")
        flash('Error al obtener las hojas de trabajo para este presupuesto', 'danger')
        return render_template('hojas_trabajo/lista.html', hojas=[], id_presupuesto=id_presupuesto)

@hojas_trabajo_bp.route('/hojas_trabajo/nueva/<int:id_presupuesto>')
def nueva_hoja(id_presupuesto):
    try:
        presupuesto = Presupuesto.query.get_or_404(id_presupuesto)
        return render_template('hojas_trabajo/nueva.html', presupuesto=presupuesto, id_presupuesto=id_presupuesto)
    except SQLAlchemyError as e:
        logger.error(f"Error al cargar formulario de nueva hoja de trabajo: {str(e)}")
        flash('Error al cargar el formulario de nueva hoja de trabajo', 'danger')
        return redirect(url_for('hojas_trabajo.hojas_por_presupuesto', id_presupuesto=id_presupuesto))

@hojas_trabajo_bp.route('/hojas_trabajo/nueva', methods=['GET', 'POST'])
def nueva_hoja_trabajo():
    if request.method == 'POST':
        try:
            proyecto_id = request.form.get('proyecto_id')
            numero = request.form.get('numero')
            fecha = datetime.strptime(request.form.get('fecha'), '%Y-%m-%d')
            descripcion = request.form.get('descripcion')
            
            # Validación básica
            if not proyecto_id or not numero or not fecha:
                flash('Todos los campos obligatorios deben ser completados', 'danger')
                proyectos = Proyecto.query.all()
                return render_template('hojas_trabajo/nueva.html', proyectos=proyectos)
            
            # Verificar si el número ya existe para ese proyecto
            existe = HojaTrabajo.query.filter_by(
                id_presupuesto=proyecto_id, 
                referencia=numero
            ).first()
            
            if existe:
                flash('Ya existe una hoja de trabajo con ese número para el proyecto seleccionado', 'danger')
                proyectos = Proyecto.query.all()
                return render_template('hojas_trabajo/nueva.html', proyectos=proyectos)
            
            # Crear la hoja de trabajo
            nueva_hoja = HojaTrabajo(
                id_presupuesto=proyecto_id,
                referencia=numero,
                fecha=fecha,
                titulo=descripcion
            )
            
            db.session.add(nueva_hoja)
            db.session.commit()
            
            flash('Hoja de trabajo creada correctamente', 'success')
            return redirect(url_for('hojas_trabajo.detalle_hoja_trabajo', id=nueva_hoja.id))
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al crear hoja de trabajo: {str(e)}")
            flash('Error al crear la hoja de trabajo', 'danger')
            proyectos = Proyecto.query.all()
            return render_template('hojas_trabajo/nueva.html', proyectos=proyectos)
    
    # GET request
    proyectos = Proyecto.query.all()
    return render_template('hojas_trabajo/nueva.html', proyectos=proyectos)

@hojas_trabajo_bp.route('/hojas_trabajo/<int:id>')
def detalle_hoja_trabajo(id):
    try:
        hoja = HojaTrabajo.query.get_or_404(id)
        capitulos = CapituloHoja.query.filter_by(id_hoja=id).all()
        partidas = PartidaHoja.query.filter_by(id_hoja=id).all()
        
        return render_template(
            'hojas_trabajo/detalle.html', 
            hoja=hoja,
            capitulos=capitulos,
            partidas=partidas
        )
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener detalle de hoja de trabajo: {str(e)}")
        flash('Error al obtener los detalles de la hoja de trabajo', 'danger')
        return redirect(url_for('hojas_trabajo.listar_hojas_trabajo'))

@hojas_trabajo_bp.route('/hojas_trabajo/editar/<int:id>', methods=['GET', 'POST'])
def editar_hoja(id):
    hoja = HojaTrabajo.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            numero = request.form.get('numero')
            fecha = datetime.strptime(request.form.get('fecha'), '%Y-%m-%d')
            descripcion = request.form.get('descripcion')
            
            # Validación básica
            if not numero or not fecha:
                flash('Todos los campos obligatorios deben ser completados', 'danger')
                return render_template('hojas_trabajo/editar.html', hoja=hoja)
            
            # Verificar si el número ya existe para ese proyecto (excluyendo esta hoja)
            existe = HojaTrabajo.query.filter(
                HojaTrabajo.id_presupuesto == hoja.id_presupuesto,
                HojaTrabajo.referencia == numero,
                HojaTrabajo.id != id
            ).first()
            
            if existe:
                flash('Ya existe otra hoja de trabajo con ese número para este proyecto', 'danger')
                return render_template('hojas_trabajo/editar.html', hoja=hoja)
            
            # Actualizar la hoja de trabajo
            hoja.referencia = numero
            hoja.fecha = fecha
            hoja.titulo = descripcion
            
            db.session.commit()
            
            flash('Hoja de trabajo actualizada correctamente', 'success')
            return redirect(url_for('hojas_trabajo.detalle_hoja_trabajo', id=hoja.id))
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al actualizar hoja de trabajo: {str(e)}")
            flash('Error al actualizar la hoja de trabajo', 'danger')
            return render_template('hojas_trabajo/editar.html', hoja=hoja)
    
    # GET request
    return render_template('hojas_trabajo/editar.html', hoja=hoja)

@hojas_trabajo_bp.route('/hojas_trabajo/eliminar/<int:id>', methods=['POST'])
def eliminar_hoja(id):
    try:
        hoja = HojaTrabajo.query.get_or_404(id)
        
        # Eliminar primero las relaciones
        CapituloHoja.query.filter_by(id_hoja=id).delete()
        PartidaHoja.query.filter_by(id_hoja=id).delete()
        
        db.session.delete(hoja)
        db.session.commit()
        
        flash('Hoja de trabajo eliminada correctamente', 'success')
        return redirect(url_for('hojas_trabajo.listar_hojas_trabajo'))
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error al eliminar hoja de trabajo: {str(e)}")
        flash('Error al eliminar la hoja de trabajo', 'danger')
        return redirect(url_for('hojas_trabajo.detalle_hoja_trabajo', id=id))

@hojas_trabajo_bp.route('/hojas_trabajo/ver_pdf/<int:id>')
def ver_pdf(id):
    # Implementar cuando se necesite
    flash('Funcionalidad de visualización de PDF no implementada aún', 'warning')
    return redirect(url_for('hojas_trabajo.listar_hojas_trabajo'))

@hojas_trabajo_bp.route('/hojas_trabajo/exportar_excel/<int:id>')
def exportar_excel(id):
    # Implementar cuando se necesite
    flash('Funcionalidad de exportación a Excel no implementada aún', 'warning')
    return redirect(url_for('hojas_trabajo.listar_hojas_trabajo'))

@hojas_trabajo_bp.route('/hojas_trabajo/agregar_capitulo/<int:hoja_id>', methods=['POST'])
def agregar_capitulo(hoja_id):
    try:
        numero = request.form.get('numero_capitulo')
        descripcion = request.form.get('descripcion_capitulo')
        
        # Validaciones básicas
        if not numero:
            flash('El número del capítulo es obligatorio', 'danger')
            return redirect(url_for('hojas_trabajo.detalle_hoja_trabajo', id=hoja_id))
        
        # Verificar si ya existe este capítulo
        existe = CapituloHoja.query.filter_by(
            id_hoja=hoja_id,
            numero=numero
        ).first()
        
        if existe:
            # Actualizar la descripción
            existe.descripcion = descripcion
        else:
            # Crear nuevo capítulo
            capitulo_hoja = CapituloHoja(
                id_hoja=hoja_id,
                numero=numero,
                descripcion=descripcion
            )
            db.session.add(capitulo_hoja)
        
        db.session.commit()
        flash('Capítulo agregado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al agregar capítulo a hoja: {str(e)}")
        flash('Error al agregar el capítulo', 'danger')
    
    return redirect(url_for('hojas_trabajo.detalle_hoja_trabajo', id=hoja_id))

@hojas_trabajo_bp.route('/hojas_trabajo/eliminar_capitulo/<int:hoja_id>/<int:capitulo_id>', methods=['POST'])
def eliminar_capitulo(hoja_id, capitulo_id):
    try:
        capitulo = CapituloHoja.query.get_or_404(capitulo_id)
        
        # Verificar que pertenece a la hoja correcta
        if capitulo.id_hoja != hoja_id:
            flash('El capítulo no pertenece a esta hoja de trabajo', 'danger')
            return redirect(url_for('hojas_trabajo.detalle_hoja_trabajo', id=hoja_id))
        
        db.session.delete(capitulo)
        db.session.commit()
        flash('Capítulo eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar capítulo de hoja: {str(e)}")
        flash('Error al eliminar el capítulo', 'danger')
    
    return redirect(url_for('hojas_trabajo.detalle_hoja_trabajo', id=hoja_id))

@hojas_trabajo_bp.route('/hojas_trabajo/agregar_partida/<int:hoja_id>', methods=['POST'])
def agregar_partida(hoja_id):
    try:
        capitulo_numero = request.form.get('capitulo_numero')
        descripcion = request.form.get('descripcion_partida')
        unitario = request.form.get('unitario')
        cantidad = float(request.form.get('cantidad', 0))
        precio = float(request.form.get('precio', 0))
        margen = float(request.form.get('margen', 0))
        
        # Validaciones básicas
        if not capitulo_numero or not descripcion:
            flash('El capítulo y la descripción son obligatorios', 'danger')
            return redirect(url_for('hojas_trabajo.detalle_hoja_trabajo', id=hoja_id))
        
        # Crear nueva partida
        partida = PartidaHoja(
            id_hoja=hoja_id,
            capitulo_numero=capitulo_numero,
            descripcion=descripcion,
            unitario=unitario,
            cantidad=cantidad,
            precio=precio,
            margen=margen
        )
        
        # Calcular totales
        partida.calcular_total()
        partida.calcular_final()
        
        db.session.add(partida)
        db.session.commit()
        flash('Partida agregada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al agregar partida a hoja: {str(e)}")
        flash('Error al agregar la partida', 'danger')
    
    return redirect(url_for('hojas_trabajo.detalle_hoja_trabajo', id=hoja_id))

@hojas_trabajo_bp.route('/hojas_trabajo/eliminar_partida/<int:hoja_id>/<int:partida_id>', methods=['POST'])
def eliminar_partida(hoja_id, partida_id):
    try:
        partida = PartidaHoja.query.get_or_404(partida_id)
        
        # Verificar que pertenece a la hoja correcta
        if partida.id_hoja != hoja_id:
            flash('La partida no pertenece a esta hoja de trabajo', 'danger')
            return redirect(url_for('hojas_trabajo.detalle_hoja_trabajo', id=hoja_id))
        
        db.session.delete(partida)
        db.session.commit()
        flash('Partida eliminada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar partida de hoja: {str(e)}")
        flash('Error al eliminar la partida', 'danger')
    
    return redirect(url_for('hojas_trabajo.detalle_hoja_trabajo', id=hoja_id))
