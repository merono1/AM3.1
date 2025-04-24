# app/routes/factura_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from app.models.factura import Factura, LineaFactura
from app.models.proyecto import Proyecto
from app.models.cliente import Cliente
from app.models.hoja_trabajo import HojaTrabajo, PartidaHoja, CapituloHoja
from app.models.presupuesto import Presupuesto, Capitulo, Partida
from app.services.db_service import get_all, get_by_id, create, update, delete
from app.services.pdf_service import generar_pdf_factura
from app import db
from datetime import datetime, timedelta
import re
from sqlalchemy import text

facturas_bp = Blueprint('facturas', __name__, url_prefix='/facturas')

# Nuevas rutas para facturar desde presupuestos
@facturas_bp.route('/desde-presupuesto/<int:id_presupuesto>', methods=['GET'])
def facturar_desde_presupuesto(id_presupuesto):
    """Muestra una página para facturar partidas de un presupuesto"""
    presupuesto = get_by_id(Presupuesto, id_presupuesto)
    if not presupuesto:
        flash('Presupuesto no encontrado', 'danger')
        return redirect(url_for('presupuestos.listar_presupuestos'))
    
    proyecto = get_by_id(Proyecto, presupuesto.id_proyecto)
    cliente = get_by_id(Cliente, proyecto.id_cliente)
    
    # Buscar capítulos y partidas
    capitulos = Capitulo.query.filter_by(id_presupuesto=id_presupuesto).order_by(Capitulo.numero).all()
    partidas = Partida.query.filter_by(id_presupuesto=id_presupuesto).all()
    
    # Organizar partidas por capítulo
    partidas_por_capitulo = {}
    for partida in partidas:
        if partida.capitulo_numero not in partidas_por_capitulo:
            partidas_por_capitulo[partida.capitulo_numero] = []
        partidas_por_capitulo[partida.capitulo_numero].append(partida)
    
    return render_template('facturas/facturar_presupuesto.html',
                          presupuesto=presupuesto,
                          proyecto=proyecto,
                          cliente=cliente,
                          capitulos=capitulos,
                          partidas_por_capitulo=partidas_por_capitulo)

@facturas_bp.route('/desde-presupuesto/<int:id_presupuesto>', methods=['POST'])
def procesar_factura_presupuesto(id_presupuesto):
    """Procesa el formulario de facturación desde presupuesto"""
    presupuesto = get_by_id(Presupuesto, id_presupuesto)
    if not presupuesto:
        flash('Presupuesto no encontrado', 'danger')
        return redirect(url_for('presupuestos.listar_presupuestos'))
    
    proyecto = get_by_id(Proyecto, presupuesto.id_proyecto)
    cliente = get_by_id(Cliente, proyecto.id_cliente)
    
    try:
        # Comprobar si es facturación por bloque (porcentaje)
        facturar_por_bloque = request.form.get('facturar_por_bloque') == 'on'
        porcentaje_bloque = float(request.form.get('porcentaje_bloque') or 0) if facturar_por_bloque else 0
        
        # Generar número de factura automático (año-número secuencial)
        año_actual = datetime.now().year
        ultima_factura = Factura.query.filter(Factura.numero.like(f"F{año_actual}%")) \
                          .order_by(Factura.id.desc()).first()
        
        if ultima_factura:
            match = re.search(r'(\d+)$', ultima_factura.numero)
            if match:
                num = int(match.group(1)) + 1
            else:
                num = 1
        else:
            num = 1
        
        numero_factura = f"F{año_actual}-{num:04d}"
        
        # Crear la factura
        factura = Factura(
            numero=numero_factura,
            id_proyecto=proyecto.id,
            id_cliente=cliente.id,
            id_presupuesto=presupuesto.id,
            fecha_emision=datetime.utcnow(),
            fecha_vencimiento=datetime.utcnow() + timedelta(days=30),
            estado='Pendiente',
            concepto=f"Facturación de presupuesto {presupuesto.referencia}",
            base_imponible=0,
            iva_porcentaje=float(request.form.get('iva_porcentaje') or 21),
            forma_pago=request.form.get('forma_pago', 'Transferencia Bancaria'),
            datos_bancarios=request.form.get('datos_bancarios')
        )
        
        db.session.add(factura)
        db.session.flush()  # Para obtener el ID
        
        # Lista para almacenar partidas a actualizar
        partidas_actualizadas = []
        base_imponible = 0
        
        if facturar_por_bloque:
            # Facturar todas las partidas por el porcentaje indicado
            partidas = Partida.query.filter_by(id_presupuesto=id_presupuesto).all()
            for partida in partidas:
                # Verificar que todavía hay margen para facturar
                porcentaje_disponible = 100 - partida.porcentaje_facturado
                if porcentaje_disponible <= 0:
                    continue  # Esta partida ya está completamente facturada
                
                # Calcular el porcentaje a aplicar en esta factura (no exceder lo disponible)
                porcentaje_a_facturar = min(porcentaje_bloque, porcentaje_disponible)
                
                # Calcular el importe proporcional
                importe_proporcional = partida.final * (porcentaje_a_facturar / 100)
                
                # Crear línea de factura
                linea = LineaFactura(
                    id_factura=factura.id,
                    id_partida=partida.id,
                    porcentaje_facturado=porcentaje_a_facturar,
                    concepto=f"Capítulo {partida.capitulo_numero} - {porcentaje_a_facturar}% de facturación",
                    descripcion=partida.descripcion,
                    cantidad=partida.cantidad * (porcentaje_a_facturar / 100) if partida.cantidad else 1,
                    precio_unitario=partida.precio if partida.precio else importe_proporcional,
                    importe=importe_proporcional
                )
                db.session.add(linea)
                
                # Actualizar porcentaje facturado de la partida
                partida.porcentaje_facturado += porcentaje_a_facturar
                partidas_actualizadas.append(partida)
                
                # Sumar a la base imponible
                base_imponible += importe_proporcional
        else:
            # Facturar partidas seleccionadas individualmente
            partidas_ids = request.form.getlist('partidas[]')
            porcentajes = {}
            
            # Recoger porcentajes para cada partida
            for key in request.form:
                if key.startswith('porcentaje_'):
                    # Asegurarse de que el valor después del guion bajo sea un número válido
                    try:
                        partida_id = int(key.split('_')[1])
                        porcentajes[partida_id] = float(request.form[key] or 0)
                    except (ValueError, IndexError):
                        # Ignorar claves que no siguen el formato esperado
                        continue
            
            for partida_id in partidas_ids:
                partida_id = int(partida_id)
                partida = get_by_id(Partida, partida_id)
                
                if partida and partida.id_presupuesto == id_presupuesto:
                    # Verificar porcentaje disponible
                    porcentaje_disponible = 100 - partida.porcentaje_facturado
                    if porcentaje_disponible <= 0:
                        continue  # Esta partida ya está completamente facturada
                    
                    # Obtener el porcentaje solicitado (por defecto 100% o lo que quede disponible)
                    porcentaje_a_facturar = min(porcentajes.get(partida_id, 100), porcentaje_disponible)
                    
                    # Calcular el importe proporcional
                    importe_proporcional = partida.final * (porcentaje_a_facturar / 100)
                    
                    # Crear línea de factura
                    linea = LineaFactura(
                        id_factura=factura.id,
                        id_partida=partida.id,
                        porcentaje_facturado=porcentaje_a_facturar,
                        concepto=f"Capítulo {partida.capitulo_numero} - {porcentaje_a_facturar}% de facturación",
                        descripcion=partida.descripcion,
                        cantidad=partida.cantidad * (porcentaje_a_facturar / 100) if partida.cantidad else 1,
                        precio_unitario=partida.precio if partida.precio else importe_proporcional,
                        importe=importe_proporcional
                    )
                    db.session.add(linea)
                    
                    # Actualizar porcentaje facturado de la partida
                    partida.porcentaje_facturado += porcentaje_a_facturar
                    partidas_actualizadas.append(partida)
                    
                    # Sumar a la base imponible
                    base_imponible += importe_proporcional
        
        # Actualizar totales de la factura
        factura.base_imponible = base_imponible
        factura.iva_importe = base_imponible * (factura.iva_porcentaje / 100)
        factura.total = factura.base_imponible + factura.iva_importe
        
        db.session.commit()
        flash('Factura creada correctamente', 'success')
        return redirect(url_for('facturas.editar_factura', id=factura.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear factura: {str(e)}', 'danger')
        return redirect(url_for('facturas.facturar_desde_presupuesto', id_presupuesto=id_presupuesto))

@facturas_bp.route('/')
def listar_facturas():
    # Obtener todas las facturas con información de proyecto y cliente
    facturas = db.session.query(Factura, Proyecto, Cliente) \
                .join(Proyecto, Factura.id_proyecto == Proyecto.id) \
                .join(Cliente, Factura.id_cliente == Cliente.id) \
                .order_by(Factura.fecha_emision.desc()) \
                .all()
    return render_template('facturas/lista.html', facturas=facturas)

@facturas_bp.route('/por-proyecto/<int:id_proyecto>')
def facturas_por_proyecto(id_proyecto):
    proyecto = get_by_id(Proyecto, id_proyecto)
    if not proyecto:
        flash('Proyecto no encontrado', 'danger')
        return redirect(url_for('proyectos.listar_proyectos'))
    
    facturas = Factura.query.filter_by(id_proyecto=id_proyecto).all()
    return render_template('facturas/por_proyecto.html', 
                          facturas=facturas, 
                          proyecto=proyecto)

@facturas_bp.route('/nueva/<int:id_proyecto>', methods=['GET', 'POST'])
def nueva_factura(id_proyecto):
    proyecto = get_by_id(Proyecto, id_proyecto)
    if not proyecto:
        flash('Proyecto no encontrado', 'danger')
        return redirect(url_for('proyectos.listar_proyectos'))
    
    cliente = get_by_id(Cliente, proyecto.id_cliente)
    today = datetime.utcnow()
    
    if request.method == 'POST':
        try:
            # Generar número de factura automático (año-número secuencial)
            año_actual = datetime.now().year
            ultima_factura = Factura.query.filter(Factura.numero.like(f"F{año_actual}%")) \
                              .order_by(Factura.id.desc()).first()
            
            if ultima_factura:
                match = re.search(r'(\d+)$', ultima_factura.numero)
                if match:
                    num = int(match.group(1)) + 1
                else:
                    num = 1
            else:
                num = 1
            
            numero_factura = f"F{año_actual}-{num:04d}"
            
            # Calcular fecha de vencimiento (por defecto a 30 días)
            fecha_emision = datetime.strptime(request.form.get('fecha_emision'), '%Y-%m-%d') if request.form.get('fecha_emision') else datetime.utcnow()
            fecha_vencimiento = fecha_emision + timedelta(days=30)
            
            # Crear la factura
            factura = Factura(
                numero=numero_factura,
                id_proyecto=id_proyecto,
                id_cliente=cliente.id,
                fecha_emision=fecha_emision,
                fecha_vencimiento=fecha_vencimiento,
                estado='Pendiente',
                concepto=request.form.get('concepto'),
                base_imponible=0,  # Se calculará después
                iva_porcentaje=float(request.form.get('iva_porcentaje') or 21),
                forma_pago=request.form.get('forma_pago'),
                datos_bancarios=request.form.get('datos_bancarios'),
                notas=request.form.get('notas')
            )
            
            db.session.add(factura)
            db.session.flush()  # Para obtener el ID
            
            # Comprobar si hay que importar desde hoja de trabajo
            id_hoja = request.form.get('id_hoja')
            if id_hoja:
                hoja = get_by_id(HojaTrabajo, id_hoja)
                if hoja:
                    # Creamos una línea por cada capítulo de la hoja
                    partidas_por_capitulo = {}
                    partidas = PartidaHoja.query.filter_by(id_hoja=id_hoja).all()
                    
                    for partida in partidas:
                        if partida.capitulo_numero not in partidas_por_capitulo:
                            partidas_por_capitulo[partida.capitulo_numero] = []
                        partidas_por_capitulo[partida.capitulo_numero].append(partida)
                    
                    capitulos = CapituloHoja.query.filter_by(id_hoja=id_hoja).order_by(CapituloHoja.numero).all()
                    
                    for capitulo in capitulos:
                        if capitulo.numero in partidas_por_capitulo:
                            partidas = partidas_por_capitulo[capitulo.numero]
                            if partidas:
                                total_capitulo = sum(partida.final for partida in partidas)
                                
                                linea = LineaFactura(
                                    id_factura=factura.id,
                                    concepto=f"Capítulo {capitulo.numero}: {capitulo.descripcion}",
                                    descripcion=f"Trabajos según hoja de trabajo {hoja.referencia}",
                                    cantidad=1,
                                    precio_unitario=total_capitulo,
                                    importe=total_capitulo
                                )
                                db.session.add(linea)
            else:
                # Crear una línea por defecto
                linea = LineaFactura(
                    id_factura=factura.id,
                    concepto="Servicios profesionales",
                    descripcion=f"Trabajos realizados en proyecto {proyecto.referencia}",
                    cantidad=1,
                    precio_unitario=0,
                    importe=0
                )
                db.session.add(linea)
            
            # Calcular totales
            db.session.flush()
            factura.calcular_totales()
            db.session.commit()
            
            flash('Factura creada correctamente', 'success')
            return redirect(url_for('facturas.editar_factura', id=factura.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear factura: {str(e)}', 'danger')
    
    # Obtener hojas de trabajo para este proyecto
    hojas = HojaTrabajo.query.filter_by(id_proyecto=id_proyecto).all()
    
    return render_template('facturas/nueva.html', 
                          proyecto=proyecto, 
                          cliente=cliente,
                          hojas=hojas,
                          today=today)

@facturas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_factura(id):
    factura = get_by_id(Factura, id)
    if not factura:
        flash('Factura no encontrada', 'danger')
        return redirect(url_for('facturas.listar_facturas'))
    
    proyecto = get_by_id(Proyecto, factura.id_proyecto)
    cliente = get_by_id(Cliente, factura.id_cliente)
    
    if request.method == 'POST':
        try:
            # Actualizar campos básicos
            factura.concepto = request.form.get('concepto')
            factura.fecha_emision = datetime.strptime(request.form.get('fecha_emision'), '%Y-%m-%d') if request.form.get('fecha_emision') else factura.fecha_emision
            factura.fecha_vencimiento = datetime.strptime(request.form.get('fecha_vencimiento'), '%Y-%m-%d') if request.form.get('fecha_vencimiento') else factura.fecha_vencimiento
            factura.estado = request.form.get('estado')
            factura.iva_porcentaje = float(request.form.get('iva_porcentaje') or 21)
            factura.forma_pago = request.form.get('forma_pago')
            factura.datos_bancarios = request.form.get('datos_bancarios')
            factura.notas = request.form.get('notas')
            
            # Recalcular totales
            factura.calcular_totales()
            db.session.commit()
            
            flash('Factura actualizada correctamente', 'success')
            return redirect(url_for('facturas.editar_factura', id=id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar factura: {str(e)}', 'danger')
    
    lineas = LineaFactura.query.filter_by(id_factura=id).all()
    
    return render_template('facturas/editar.html', 
                          factura=factura,
                          proyecto=proyecto,
                          cliente=cliente,
                          lineas=lineas)

@facturas_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_factura(id):
    try:
        factura = get_by_id(Factura, id)
        id_proyecto = factura.id_proyecto
        delete(Factura, id)
        flash('Factura eliminada correctamente', 'success')
        return redirect(url_for('facturas.facturas_por_proyecto', id_proyecto=id_proyecto))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar factura: {str(e)}', 'danger')
        return redirect(url_for('facturas.listar_facturas'))

@facturas_bp.route('/linea/nueva/<int:id_factura>', methods=['POST'])
def nueva_linea(id_factura):
    try:
        cantidad = float(request.form.get('cantidad') or 1)
        precio = float(request.form.get('precio_unitario') or 0)
        importe = cantidad * precio
        
        linea = LineaFactura(
            id_factura=id_factura,
            concepto=request.form.get('concepto'),
            descripcion=request.form.get('descripcion'),
            cantidad=cantidad,
            precio_unitario=precio,
            importe=importe
        )
        db.session.add(linea)
        
        # Actualizar totales de la factura
        factura = get_by_id(Factura, id_factura)
        factura.calcular_totales()
        
        db.session.commit()
        flash('Línea añadida correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al añadir línea: {str(e)}', 'danger')
    
    return redirect(url_for('facturas.editar_factura', id=id_factura))

@facturas_bp.route('/linea/editar/<int:id>', methods=['POST'])
def editar_linea(id):
    try:
        linea = get_by_id(LineaFactura, id)
        if linea:
            cantidad = float(request.form.get('cantidad') or 1)
            precio = float(request.form.get('precio_unitario') or 0)
            importe = cantidad * precio
            
            linea.concepto = request.form.get('concepto')
            linea.descripcion = request.form.get('descripcion')
            linea.cantidad = cantidad
            linea.precio_unitario = precio
            linea.importe = importe
            
            # Actualizar totales de la factura
            factura = get_by_id(Factura, linea.id_factura)
            factura.calcular_totales()
            
            db.session.commit()
            flash('Línea actualizada correctamente', 'success')
        else:
            flash('Línea no encontrada', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar línea: {str(e)}', 'danger')
    
    return redirect(url_for('facturas.editar_factura', id=request.form.get('id_factura')))

@facturas_bp.route('/linea/eliminar/<int:id>', methods=['POST'])
def eliminar_linea(id):
    try:
        linea = get_by_id(LineaFactura, id)
        id_factura = linea.id_factura
        
        db.session.delete(linea)
        
        # Actualizar totales de la factura
        factura = get_by_id(Factura, id_factura)
        factura.calcular_totales()
        
        db.session.commit()
        flash('Línea eliminada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar línea: {str(e)}', 'danger')
    
    return redirect(url_for('facturas.editar_factura', id=id_factura))

@facturas_bp.route('/pdf/<int:id>')
def generar_pdf(id):
    factura = get_by_id(Factura, id)
    if not factura:
        flash('Factura no encontrada', 'danger')
        return redirect(url_for('facturas.listar_facturas'))
    
    proyecto = get_by_id(Proyecto, factura.id_proyecto)
    cliente = get_by_id(Cliente, factura.id_cliente)
    lineas = LineaFactura.query.filter_by(id_factura=id).all()
    
    # Generar PDF
    pdf_file = generar_pdf_factura(factura, proyecto, cliente, lineas)
    
    # Retornar el archivo PDF
    return send_file(
        pdf_file,
        as_attachment=True,
        download_name=f"Factura_{factura.numero}.pdf",
        mimetype='application/pdf'
    )

@facturas_bp.route('/api/facturas')
def api_listar_facturas():
    facturas = get_all(Factura)
    return jsonify([{
        'id': f.id,
        'numero': f.numero,
        'fecha_emision': f.fecha_emision.isoformat() if f.fecha_emision else None,
        'fecha_vencimiento': f.fecha_vencimiento.isoformat() if f.fecha_vencimiento else None,
        'estado': f.estado,
        'total': f.total,
        'id_proyecto': f.id_proyecto,
        'id_cliente': f.id_cliente
    } for f in facturas])

@facturas_bp.route('/api/facturas/<int:id>')
def api_get_factura(id):
    factura = get_by_id(Factura, id)
    if not factura:
        return jsonify({'error': 'Factura no encontrada'}), 404
    
    lineas = LineaFactura.query.filter_by(id_factura=id).all()
    
    return jsonify({
        'id': factura.id,
        'numero': factura.numero,
        'fecha_emision': factura.fecha_emision.isoformat() if factura.fecha_emision else None,
        'fecha_vencimiento': factura.fecha_vencimiento.isoformat() if factura.fecha_vencimiento else None,
        'estado': factura.estado,
        'concepto': factura.concepto,
        'base_imponible': factura.base_imponible,
        'iva_porcentaje': factura.iva_porcentaje,
        'iva_importe': factura.iva_importe,
        'total': factura.total,
        'forma_pago': factura.forma_pago,
        'datos_bancarios': factura.datos_bancarios,
        'notas': factura.notas,
        'id_proyecto': factura.id_proyecto,
        'id_cliente': factura.id_cliente,
        'lineas': [{
            'id': l.id,
            'concepto': l.concepto,
            'descripcion': l.descripcion,
            'cantidad': l.cantidad,
            'precio_unitario': l.precio_unitario,
            'importe': l.importe
        } for l in lineas]
    })