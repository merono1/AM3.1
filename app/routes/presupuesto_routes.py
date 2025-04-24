# app/routes/presupuesto_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, abort
from app.models.presupuesto import Presupuesto, Capitulo, Partida
from app.models.proyecto import Proyecto
from app.models.cliente import Cliente
from sqlalchemy import text, and_, or_
from app.services.db_service import get_all, get_by_id, create, update, delete
from app.services.pdf_service import generar_pdf_presupuesto
from app import db
from datetime import datetime
import re
import tempfile
import os
import traceback

presupuestos_bp = Blueprint('presupuestos', __name__, url_prefix='/presupuestos')

@presupuestos_bp.route('/')
def listar_presupuestos():
    # Redirigir al listado avanzado
    return redirect(url_for('presupuestos_avanzados.listar_presupuestos_avanzado'))

@presupuestos_bp.route('/por-proyecto/<int:id_proyecto>')
def presupuestos_por_proyecto(id_proyecto):
    try:
        proyecto = get_by_id(Proyecto, id_proyecto)
        if not proyecto:
            flash('Proyecto no encontrado', 'danger')
            return redirect(url_for('proyectos.listar_proyectos'))
        
        # Seleccionar solo columnas específicas para evitar errores con columnas que puedan no existir
        presupuestos = db.session.query(
            Presupuesto.id,
            Presupuesto.id_proyecto,
            Presupuesto.referencia,
            Presupuesto.fecha,
            Presupuesto.titulo,
            Presupuesto.estado,
            Presupuesto.tecnico_encargado,
            Presupuesto.aprobacion,
            Presupuesto.fecha_aprobacion
        ).filter(Presupuesto.id_proyecto == id_proyecto).all()
        
        # Convertir resultados a objetos tipo Presupuesto para usar en plantillas
        presupuestos_formateados = []
        for p in presupuestos:
            presupuesto = type('Presupuesto', (), {
                'id': p.id,
                'id_proyecto': p.id_proyecto,
                'referencia': p.referencia,
                'fecha': p.fecha,
                'titulo': p.titulo,
                'estado': p.estado,
                'tecnico_encargado': p.tecnico_encargado,
                'aprobacion': p.aprobacion,
                'fecha_aprobacion': p.fecha_aprobacion
            })
            presupuestos_formateados.append(presupuesto)
        
        # Verificar si es una solicitud para el modal o para la vista completa
        if request.args.get('modal') == 'true':
            # Renderizar solo el contenido para el modal
            return render_template('presupuestos/listado_modal.html', 
                                presupuestos=presupuestos_formateados, 
                                proyecto=proyecto)
        else:
            # Renderizar la vista completa
            return render_template('presupuestos/por_proyecto.html', 
                                presupuestos=presupuestos_formateados, 
                                proyecto=proyecto)
    except Exception as e:
        print(f"Error al listar presupuestos por proyecto: {str(e)}")
        traceback.print_exc()
        flash(f"Error al cargar los presupuestos del proyecto. {str(e)}", 'danger')
        return redirect(url_for('proyectos.listar_proyectos'))

@presupuestos_bp.route('/nuevo', defaults={'id_proyecto': None}, methods=['GET', 'POST'])
@presupuestos_bp.route('/nuevo/<int:id_proyecto>', methods=['GET', 'POST'])
def nuevo_presupuesto(id_proyecto=None):
    # Si no se proporciona en la ruta, intenta obtenerlo desde los parámetros de consulta
    if id_proyecto is None:
        id_proyecto_str = request.args.get('id_proyecto')
        if id_proyecto_str:
            try:
                id_proyecto = int(id_proyecto_str)
            except ValueError:
                flash('ID de proyecto inválido', 'danger')
                return redirect(url_for('proyectos.listar_proyectos'))
    
    # Si aún no tenemos id_proyecto, redirigir a listado de proyectos
    if id_proyecto is None:
        flash('Debe seleccionar un proyecto para crear un presupuesto', 'warning')
        return redirect(url_for('proyectos.listar_proyectos'))
    
    proyecto = get_by_id(Proyecto, id_proyecto)
    if not proyecto:
        flash('Proyecto no encontrado', 'danger')
        return redirect(url_for('proyectos.listar_proyectos'))
    
    if request.method == 'POST':
        try:
            # Generar referencia automática basada en la referencia del proyecto
            ultimo_presupuesto = Presupuesto.query \
                .filter_by(id_proyecto=id_proyecto) \
                .order_by(Presupuesto.id.desc()).first()
            
            if ultimo_presupuesto:
                # Extraer el número secuencial y aumentarlo
                match = re.search(r'(\d+)$', ultimo_presupuesto.referencia)
                if match:
                    num = int(match.group(1)) + 1
                else:
                    num = 1
            else:
                num = 1
                
            # Crear referencia en formato PRJ-XXXX (proyecto-numero)
            referencia = f"{proyecto.referencia}-P{num:02d}"
            
            data = {
                'id_proyecto': id_proyecto,
                'referencia': referencia,
                'fecha': datetime.utcnow(),
                'tipo_via': request.form.get('tipo_via'),
                'nombre_via': request.form.get('nombre_via'),
                'numero_via': request.form.get('numero_via'),
                'puerta': request.form.get('puerta'),
                'codigo_postal': request.form.get('codigo_postal'),
                'poblacion': request.form.get('poblacion'),
                'titulo': request.form.get('titulo'),
                'notas': request.form.get('notas'),
                'tecnico_encargado': request.form.get('tecnico_encargado'),
                'aprobacion': None,
                'fecha_aprobacion': None,
                'estado': 'Borrador'
            }
            
            presupuesto = Presupuesto(**data)
            db.session.add(presupuesto)
            db.session.commit()
            
            flash('Presupuesto creado correctamente', 'success')
            return redirect(url_for('presupuestos.editar_presupuesto', id=presupuesto.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear presupuesto: {str(e)}', 'danger')
    
    cliente = get_by_id(Cliente, proyecto.id_cliente)
    return render_template('presupuestos/nuevo.html', 
                          proyecto=proyecto, 
                          cliente=cliente)

@presupuestos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_presupuesto(id):
    presupuesto = get_by_id(Presupuesto, id)
    if not presupuesto:
        flash('Presupuesto no encontrado', 'danger')
        return redirect(url_for('presupuestos.listar_presupuestos'))
    
    proyecto = get_by_id(Proyecto, presupuesto.id_proyecto)
    cliente = get_by_id(Cliente, proyecto.id_cliente)
    
    if request.method == 'POST':
        try:
            data = {
                'tipo_via': request.form.get('tipo_via'),
                'nombre_via': request.form.get('nombre_via'),
                'numero_via': request.form.get('numero_via'),
                'puerta': request.form.get('puerta'),
                'codigo_postal': request.form.get('codigo_postal'),
                'poblacion': request.form.get('poblacion'),
                'titulo': request.form.get('titulo'),
                'notas': request.form.get('notas'),
                'tecnico_encargado': request.form.get('tecnico_encargado'),
                'estado': request.form.get('estado')
            }
            
            if request.form.get('aprobacion'):
                data['aprobacion'] = request.form.get('aprobacion')
                data['fecha_aprobacion'] = datetime.utcnow()
            
            update(Presupuesto, id, data)
            flash('Presupuesto actualizado correctamente', 'success')
            return redirect(url_for('presupuestos.editar_presupuesto', id=id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar presupuesto: {str(e)}', 'danger')
    
    capitulos = Capitulo.query.filter_by(id_presupuesto=id).order_by(Capitulo.numero).all()
    
    # Obtener todas las partidas normalmente
    partidas = Partida.query.filter_by(id_presupuesto=id).all()
    
    # Organizar partidas por capítulo
    partidas_por_capitulo = {}
    for partida in partidas:
        if partida.capitulo_numero not in partidas_por_capitulo:
            partidas_por_capitulo[partida.capitulo_numero] = []
        partidas_por_capitulo[partida.capitulo_numero].append(partida)
    
    # Ordenar las partidas de cada capítulo por número
    for capitulo_numero, lista_partidas in partidas_por_capitulo.items():
        try:
            # Función para convertir número de partida a flotante para ordenar
            def numero_a_flotante(partida):
                if not partida.numero or '.' not in partida.numero:
                    return float('inf')  # Poner al final si no tiene formato correcto
                try:
                    return float(partida.numero.replace(',', '.'))
                except:
                    return float('inf')
            
            # Ordenar las partidas
            lista_partidas.sort(key=numero_a_flotante)
            print(f"Partidas del capítulo {capitulo_numero} ordenadas por número")
        except Exception as e:
            print(f"Error al ordenar partidas del capítulo {capitulo_numero}: {str(e)}")
    
    # Calcular el total del presupuesto (suma de finales)
    total_presupuesto = round(sum(partida.final for partida in partidas if partida.final is not None), 2)
    
    # Calcular el subtotal (suma de totales sin margen)
    subtotal = round(sum(partida.total for partida in partidas if partida.total is not None), 2)
    
    # Calcular el valor del margen
    valor_margen = round(total_presupuesto - subtotal, 2)
    
    # Calcular el margen medio real para mostrarlo en la plantilla
    margen_medio_real = 0
    if subtotal > 0:
        margen_medio_real = round((valor_margen / subtotal) * 100, 2)
    
    # Garantizar que el número se redondea exactamente a 2 decimales
    margen_medio_real_str = '{:.2f}'.format(margen_medio_real)
    
    return render_template('presupuestos/editar_pres.html', 
                          presupuesto=presupuesto,
                          proyecto=proyecto,
                          cliente=cliente,
                          capitulos=capitulos,
                          partidas_por_capitulo=partidas_por_capitulo,
                          margen_medio_real=margen_medio_real,
                          margen_medio_real_str=margen_medio_real_str,
                          total_presupuesto=total_presupuesto,
                          subtotal=subtotal,
                          valor_margen=valor_margen)

@presupuestos_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_presupuesto(id):
    try:
        presupuesto = get_by_id(Presupuesto, id)
        id_proyecto = presupuesto.id_proyecto
        delete(Presupuesto, id)
        flash('Presupuesto eliminado correctamente', 'success')
        return redirect(url_for('presupuestos.presupuestos_por_proyecto', id_proyecto=id_proyecto))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar presupuesto: {str(e)}', 'danger')
        return redirect(url_for('presupuestos.listar_presupuestos'))

@presupuestos_bp.route('/capitulo/nuevo/<int:id_presupuesto>', methods=['POST'])
def nuevo_capitulo(id_presupuesto):
    try:
        # Obtener el último capítulo para asignar número automáticamente
        ultimo_capitulo = Capitulo.query \
            .filter_by(id_presupuesto=id_presupuesto) \
            .order_by(Capitulo.numero.desc()) \
            .first()
        
        if ultimo_capitulo:
            # Extraer el número y aumentarlo en 1
            try:
                ultimo_numero = int(ultimo_capitulo.numero)
                nuevo_numero = str(ultimo_numero + 1)
            except ValueError:
                # Si el número no es un entero válido, empezar con 1
                nuevo_numero = "1"
        else:
            nuevo_numero = "1"
            
        capitulo = Capitulo(
            id_presupuesto=id_presupuesto,
            numero=nuevo_numero,
            descripcion=request.form.get('descripcion')
        )
        db.session.add(capitulo)
        db.session.commit()
        flash('Capítulo creado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear capítulo: {str(e)}', 'danger')
    
    return redirect(url_for('presupuestos.editar_presupuesto', id=id_presupuesto))

@presupuestos_bp.route('/capitulo/editar/<int:id>', methods=['POST'])
def editar_capitulo(id):
    try:
        capitulo = get_by_id(Capitulo, id)
        if capitulo:
            # Solo modificamos la descripción, no el número
            capitulo.descripcion = request.form.get('descripcion')
            db.session.commit()
            flash('Capítulo actualizado correctamente', 'success')
        else:
            flash('Capítulo no encontrado', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar capítulo: {str(e)}', 'danger')
    
    return redirect(url_for('presupuestos.editar_presupuesto', id=request.form.get('id_presupuesto')))

@presupuestos_bp.route('/capitulo/eliminar/<int:id>', methods=['POST'])
def eliminar_capitulo(id):
    try:
        capitulo = get_by_id(Capitulo, id)
        id_presupuesto = capitulo.id_presupuesto
        
        # Eliminar todas las partidas asociadas
        Partida.query.filter_by(id_presupuesto=id_presupuesto, capitulo_numero=capitulo.numero).delete()
        
        db.session.delete(capitulo)
        db.session.commit()
        flash('Capítulo y sus partidas eliminados correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar capítulo: {str(e)}', 'danger')
    
    return redirect(url_for('presupuestos.editar_presupuesto', id=id_presupuesto))

@presupuestos_bp.route('/partida/nueva/<int:id_presupuesto>', methods=['POST'])
def nueva_partida(id_presupuesto):
    try:
        print("\n===== NUEVA PARTIDA =====\nDatos recibidos:")
        print(f"Content-Type: {request.content_type}")
        print(f"Datos del form: {request.form.to_dict()}")
        print(f"Headers: {dict(request.headers)}")
        print(f"Cuerpo de la solicitud: {request.get_data(as_text=True)}")
        
        # Verificar que existe el presupuesto
        presupuesto = get_by_id(Presupuesto, id_presupuesto)
        if not presupuesto:
            error_msg = f"ERROR: Presupuesto con ID {id_presupuesto} no encontrado"
            print(error_msg)
            return error_response(error_msg, id_presupuesto)
        
        # Obtener y validar el número de capítulo
        capitulo_numero = request.form.get('capitulo_numero')
        if not capitulo_numero:
            error_msg = "ERROR: Número de capítulo no proporcionado"
            print(error_msg)
            return error_response(error_msg, id_presupuesto)
        
        # Verificar que el capítulo existe
        capitulo = Capitulo.query.filter_by(
            id_presupuesto=id_presupuesto,
            numero=capitulo_numero
        ).first()
        
        if not capitulo:
            error_msg = f"ERROR: Capítulo {capitulo_numero} no encontrado en el presupuesto {id_presupuesto}"
            print(error_msg)
            return error_response(error_msg, id_presupuesto)
        
        # Verificar si es una inserción intercalada
        partida_anterior_id = request.form.get('partida_anterior_id')
        intercalando = partida_anterior_id is not None and partida_anterior_id.strip() != ''
        
        # Obtener las partidas del capítulo ordenadas por número
        partidas = Partida.query.filter_by(
            id_presupuesto=id_presupuesto,
            capitulo_numero=capitulo_numero
        ).all()
        
        # Ordenar partidas por número para asegurar inserción correcta
        try:
            # Función para convertir número de partida a flotante para ordenar
            def numero_a_flotante(partida):
                if not partida.numero or '.' not in partida.numero:
                    return float('inf')  # Poner al final si no tiene formato correcto
                try:
                    return float(partida.numero.replace(',', '.'))
                except:
                    return float('inf')
            
            # Ordenar las partidas
            partidas.sort(key=numero_a_flotante)
            print(f"Partidas ordenadas correctamente por número")
            
            # Log para debugging
            print("Orden de partidas después de ordenar:")
            for i, p in enumerate(partidas):
                print(f"  {i+1}. Número: {p.numero}, ID: {p.id}")
                
        except Exception as e:
            print(f"Error al ordenar partidas por número: {str(e)}")
            # Si falla el ordenamiento, dejamos como están
        
        if intercalando:
            print(f"Insertando partida intercalada después de la partida ID: {partida_anterior_id}")
            # Buscar la posición de la partida anterior
            posicion_insercion = None
            for i, partida in enumerate(partidas):
                if str(partida.id) == partida_anterior_id:
                    posicion_insercion = i
                    break
            
            if posicion_insercion is None:
                error_msg = f"ERROR: Partida anterior con ID {partida_anterior_id} no encontrada"
                print(error_msg)
                return error_response(error_msg, id_presupuesto)
            
            # Determinar el número de la nueva partida
            partida_anterior = partidas[posicion_insercion]
            
            # Determinar el número de la nueva partida y renumerar las siguientes
            # Para inserción intercalada, queremos una secuencia lógica (1.1, 1.2, 1.3...)
            
            # Si la partida anterior es la última, simplemente añadir al final con número incremental
            if posicion_insercion + 1 >= len(partidas):
                # Extraer el número secuencial de la última partida
                try:
                    partes = partida_anterior.numero.split('.')
                    if len(partes) == 2 and partes[1].isdigit():
                        last_seq = int(partes[1])
                        numero_partida = f"{capitulo_numero}.{last_seq + 1}"
                    else:
                        numero_partida = f"{capitulo_numero}.1" # Default si hay un problema con el formato
                except (ValueError, IndexError, AttributeError):
                    numero_partida = f"{capitulo_numero}.1" # Default si hay un problema 
                print(f"Añadiendo al final, número asignado: {numero_partida}")
            else:
                # Estamos insertando en medio - necesitamos renumerar todas las partidas siguientes
                # La nueva partida tomará el número de la siguiente, y todas las demás se incrementan
                partida_siguiente = partidas[posicion_insercion + 1]
                
                # Extraer los componentes del número
                try:
                    partes = partida_siguiente.numero.split('.')
                    if len(partes) == 2 and partes[1].isdigit():
                        # Usamos el mismo número de la siguiente partida para la nueva
                        insert_seq = int(partes[1])
                        numero_partida = f"{capitulo_numero}.{insert_seq}"
                        
                        # Renumerar todas las partidas siguientes incrementando en 1
                        print(f"Renumerando partidas a partir de la posición {posicion_insercion + 1}")
                        for idx in range(posicion_insercion + 1, len(partidas)):
                            part = partidas[idx]
                            try:
                                part_partes = part.numero.split('.')
                                if len(part_partes) == 2 and part_partes[1].isdigit():
                                    old_num = part.numero
                                    new_seq = int(part_partes[1]) + 1
                                    part.numero = f"{capitulo_numero}.{new_seq}"
                                    print(f"  Renumerando: {old_num} -> {part.numero}")
                            except Exception as e:
                                print(f"  Error al renumerar partida {part.id}: {str(e)}")
                    else:
                        # Si hay un problema con el formato, asignar un número por defecto
                        numero_partida = f"{capitulo_numero}.{posicion_insercion + 1}"
                except (ValueError, IndexError, AttributeError) as e:
                    print(f"Error al procesar número para intercalar: {str(e)}")
                    numero_partida = f"{capitulo_numero}.{posicion_insercion + 1}"
                
                print(f"Insertando en medio, número asignado: {numero_partida}")
            
            print(f"Número final asignado a la partida intercalada: {numero_partida}")
        else:
            # Comportamiento normal (añadir al final)
            numero_secuencial = len(partidas) + 1
            numero_partida = f"{capitulo_numero}.{numero_secuencial}"
            print(f"Número asignado a la partida: {numero_partida}")
        
        # Obtener y validar descripción
        descripcion = request.form.get('descripcion')
        if not descripcion or descripcion.strip() == '':
            descripcion = "<p>Sin descripción</p>"
            
        # Registrar en logs para debug
        print(f"Descripción recibida: {descripcion[:100]}..." if len(descripcion) > 100 else descripcion)
        
        # Asegurarnos de que la descripción tenga formato HTML adecuado
        if not descripcion.startswith('<p>') and not descripcion.startswith('<div>') and not descripcion.startswith('<ul>'):
            descripcion = f"<p>{descripcion}</p>"
            print("Formateando descripción con <p>")
        
        print(f"Longitud de la descripción: {len(descripcion)} caracteres")
        
        # Obtener unidad de medida
        unitario = request.form.get('unitario', 'Ud')
        print(f"Unidad de medida: {unitario}")
        
        # Procesar y validar datos numéricos
        cantidad_str = request.form.get('cantidad', '1')
        precio_str = request.form.get('precio', '0')
        margen_str = request.form.get('margen', '40')
        
        print(f"Valores recibidos: cantidad={cantidad_str}, precio={precio_str}, margen={margen_str}")
        
        try:
            cantidad = float(cantidad_str)
            if cantidad < 0:
                cantidad = 0
        except (ValueError, TypeError):
            cantidad = 1
        
        try:
            precio = float(precio_str)
            if precio < 0:
                precio = 0
        except (ValueError, TypeError):
            precio = 0
        
        try:
            margen = float(margen_str)
            if margen < 0:
                margen = 0
        except (ValueError, TypeError):
            margen = 40
        
        # Calcular valores derivados
        total = round(cantidad * precio, 2)
        final = round(total * (1 + margen / 100), 2)
        
        print(f"Valores calculados: cantidad={cantidad}, precio={precio}, margen={margen}, total={total}, final={final}")
        
        # Crear la partida
        partida = Partida(
            id_presupuesto=id_presupuesto,
            capitulo_numero=capitulo_numero,
            numero=numero_partida,
            descripcion=descripcion,
            unitario=unitario,
            cantidad=cantidad,
            precio=precio,
            total=total,
            margen=margen,
            final=final
        )
        
        # Log para debugging
        print(f"Partida creada con los siguientes datos:")
        print(f"  - ID Presupuesto: {id_presupuesto}")
        print(f"  - Capítulo: {capitulo_numero}")
        print(f"  - Número: {numero_partida}")
        print(f"  - ¿Es intercalada?: {'Sí' if intercalando else 'No'}")
        
        # Guardar en la base de datos
        db.session.add(partida)
        db.session.commit()
        
        # Confirmar los valores guardados
        print(f"Partida creada correctamente: ID={partida.id}, Total={partida.total}, Margen={partida.margen}, Final={partida.final}")
        print("===== FIN NUEVA PARTIDA =====\n")
        
        # Responder según el tipo de solicitud
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            return jsonify({
                'success': True,
                'message': 'Partida creada correctamente',
                'partida': {
                    'id': partida.id,
                    'capitulo_numero': partida.capitulo_numero,
                    'numero': partida.numero,
                    'descripcion': partida.descripcion,
                    'unitario': partida.unitario,
                    'cantidad': partida.cantidad,
                    'precio': partida.precio,
                    'total': partida.total,
                    'margen': partida.margen,
                    'final': partida.final
                }
            })
        else:
            flash('Partida creada correctamente', 'success')
            return redirect(url_for('presupuestos.editar_presupuesto', id=id_presupuesto))
            
    except Exception as e:
        db.session.rollback()
        error_msg = f"ERROR al crear partida: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return error_response(error_msg, id_presupuesto)

# Función auxiliar para generar respuestas de error
def error_response(message, id_presup=None):
    # Si no se proporciona un ID de presupuesto, intentar obtenerlo de la URL
    if id_presup is None:
        try:
            id_presup = request.view_args.get('id_presupuesto')
        except:
            # Si no se puede obtener, redirigir al listado general
            id_presup = None
    
    # Verificar si es una solicitud AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
        return jsonify({
            'success': False,
            'error': message
        }), 400
    else:
        flash(message, 'danger')
        if id_presup:
            return redirect(url_for('presupuestos.editar_presupuesto', id=id_presup))
        else:
            return redirect(url_for('presupuestos.listar_presupuestos'))

@presupuestos_bp.route('/partida/editar/<int:id>', methods=['POST'])
def editar_partida(id):
    try:
        partida = get_by_id(Partida, id)
        if partida:
            # Convertir y validar cantidad y precio
            try:
                cantidad = float(request.form.get('cantidad') or 0)
            except (ValueError, TypeError):
                cantidad = 0
                
            try:
                precio = float(request.form.get('precio') or 0)
            except (ValueError, TypeError):
                precio = 0
                
            # Calcular total
            total = round(cantidad * precio, 2)
            
            # Convertir y validar margen
            try:
                margen = float(request.form.get('margen') or 40)  # Valor por defecto 40%
            except (ValueError, TypeError):
                margen = 40
            
            # Calcular final
            final = round(total * (1 + margen / 100), 2)
            
            # Actualizar los valores de la partida
            partida.capitulo_numero = request.form.get('capitulo_numero')
            partida.descripcion = request.form.get('descripcion')
            partida.unitario = request.form.get('unitario')
            partida.cantidad = cantidad
            partida.precio = precio
            partida.total = total
            partida.margen = margen
            partida.final = final
            
            # Guardar en la base de datos
            db.session.commit()
            
            # Confirmar los valores que se han guardado
            print(f"Partida editada: ID={partida.id}, Total={partida.total}, Margen={partida.margen}, Final={partida.final}")
            
            flash('Partida actualizada correctamente', 'success')
        else:
            flash('Partida no encontrada', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar partida: {str(e)}', 'danger')
    
    return redirect(url_for('presupuestos.editar_presupuesto', id=request.form.get('id_presupuesto')))

@presupuestos_bp.route('/partida/eliminar/<int:id>', methods=['POST'])
def eliminar_partida(id):
    try:
        partida = get_by_id(Partida, id)
        id_presupuesto = partida.id_presupuesto
        db.session.delete(partida)
        db.session.commit()
        flash('Partida eliminada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar partida: {str(e)}', 'danger')
    
    return redirect(url_for('presupuestos.editar_presupuesto', id=id_presupuesto))

@presupuestos_bp.route('/pdf/<int:id>')
def generar_pdf(id):
    presupuesto = get_by_id(Presupuesto, id)
    if not presupuesto:
        flash('Presupuesto no encontrado', 'danger')
        return redirect(url_for('presupuestos.listar_presupuestos'))
    
    proyecto = get_by_id(Proyecto, presupuesto.id_proyecto)
    cliente = get_by_id(Cliente, proyecto.id_cliente)
    
    capitulos = Capitulo.query.filter_by(id_presupuesto=id).order_by(Capitulo.numero).all()
    partidas = Partida.query.filter_by(id_presupuesto=id).all()
    
    # Organizar partidas por capítulo
    partidas_por_capitulo = {}
    for partida in partidas:
        if partida.capitulo_numero not in partidas_por_capitulo:
            partidas_por_capitulo[partida.capitulo_numero] = []
        partidas_por_capitulo[partida.capitulo_numero].append(partida)
    
    # Generar PDF
    pdf_file = generar_pdf_presupuesto(presupuesto, proyecto, cliente, capitulos, partidas_por_capitulo)
    
    # Retornar el archivo PDF
    return send_file(
        pdf_file,
        as_attachment=True,
        download_name=f"Presupuesto_{presupuesto.referencia}.pdf",
        mimetype='application/pdf'
    )
    
@presupuestos_bp.route('/api/presupuestos/partida/<int:id>')
def api_get_partida(id):
    """Endpoint API para obtener datos de una partida específica"""
    try:
        partida = get_by_id(Partida, id)
        if not partida:
            return jsonify({'error': 'Partida no encontrada'}), 404
            
        # Devolver información detallada de la partida
        return jsonify({
            'id': partida.id,
            'id_presupuesto': partida.id_presupuesto,
            'capitulo_numero': partida.capitulo_numero,
            'numero': partida.numero,
            'descripcion': partida.descripcion,
            'unitario': partida.unitario,
            'cantidad': partida.cantidad,
            'precio': partida.precio,
            'total': partida.total,
            'margen': partida.margen,
            'final': partida.final
        })
    except Exception as e:
        print(f"Error al obtener partida {id}: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener datos de la partida: {str(e)}'}), 500

@presupuestos_bp.route('/api/partida/editar/<int:id>', methods=['POST'])
@presupuestos_bp.route('/presupuestos/api/partida/editar/<int:id>', methods=['POST'])
def api_editar_partida(id):
    """Endpoint API para editar una partida mediante AJAX"""
    try:
        partida = get_by_id(Partida, id)
        if not partida:
            return jsonify({'success': False, 'error': 'Partida no encontrada'}), 404
            
        # Procesar los datos recibidos
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
        
        print(f"Datos recibidos para editar partida {id}: {data}")
        
        # Actualizar los campos de la partida
        if 'descripcion' in data:
            # Guardar el contenido HTML sin alteraciones
            partida.descripcion = data['descripcion']
            print(f"Descripción actualizada (HTML): {data['descripcion'][:100]}...")
            
        if 'unitario' in data:
            partida.unitario = data['unitario']
            
        # Actualizar campos numéricos con cálculos asociados
        updated_cantidad = False
        updated_precio = False
        updated_margen = False
        
        if 'cantidad' in data:
            try:
                cantidad = float(data['cantidad'])
                partida.cantidad = cantidad
                updated_cantidad = True
            except (ValueError, TypeError):
                pass
                
        if 'precio' in data:
            try:
                precio = float(data['precio'])
                partida.precio = precio
                updated_precio = True
            except (ValueError, TypeError):
                pass
                
        # Recalcular total si se actualizó cantidad o precio
        if updated_cantidad or updated_precio:
            partida.total = round(partida.cantidad * partida.precio, 2)
            
        if 'margen' in data:
            try:
                margen = float(data['margen'])
                partida.margen = margen
                updated_margen = True
            except (ValueError, TypeError):
                pass
                
        # Recalcular final si se actualizó total o margen
        if updated_cantidad or updated_precio or updated_margen:
            partida.final = round(partida.total * (1 + partida.margen / 100), 2)
            
        # Guardar cambios en la base de datos
        db.session.commit()
        
        print(f"Partida {id} actualizada: total={partida.total}, margen={partida.margen}, final={partida.final}")
        
        # Devolver los datos actualizados
        return jsonify({
            'success': True,
            'partida': {
                'id': partida.id,
                'capitulo_numero': partida.capitulo_numero,
                'numero': partida.numero,
                'descripcion': partida.descripcion, # Devolvemos el HTML completo
                'unitario': partida.unitario,
                'cantidad': partida.cantidad,
                'precio': partida.precio,
                'total': partida.total,
                'margen': partida.margen,
                'final': partida.final
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al editar partida {id} vía API: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Error al actualizar partida: {str(e)}'}), 500

@presupuestos_bp.route('/clonar/<int:id>', methods=['GET', 'POST'])
def clonar_presupuesto(id):
    try:
        presupuesto_orig = get_by_id(Presupuesto, id)
        if not presupuesto_orig:
            flash('Presupuesto no encontrado', 'danger')
            return redirect(url_for('presupuestos.listar_presupuestos'))
        
        # Generar nueva referencia
        ultimo_presupuesto = Presupuesto.query \
            .filter_by(id_proyecto=presupuesto_orig.id_proyecto) \
            .order_by(Presupuesto.id.desc()).first()
        
        if ultimo_presupuesto:
            # Buscar referencias con formato "V" + números
            match = re.search(r'V(\d+)$', ultimo_presupuesto.referencia)
            if match:
                num = int(match.group(1)) + 1
            else:
                # Si no hay presupuestos con prefijo V, empezamos con 1
                num = 1
        else:
            num = 1
        
        proyecto = get_by_id(Proyecto, presupuesto_orig.id_proyecto)
        # Nueva referencia con formato {proyecto.referencia}-V{num:02d}
        nueva_referencia = f"{proyecto.referencia}-V{num:02d}"
        
        # Crear nuevo presupuesto como copia del original
        nuevo_presupuesto = Presupuesto(
            id_proyecto=presupuesto_orig.id_proyecto,
            referencia=nueva_referencia,
            fecha=datetime.utcnow(),
            tipo_via=presupuesto_orig.tipo_via,
            nombre_via=presupuesto_orig.nombre_via,
            numero_via=presupuesto_orig.numero_via,
            puerta=presupuesto_orig.puerta,
            codigo_postal=presupuesto_orig.codigo_postal,
            poblacion=presupuesto_orig.poblacion,
            titulo=f"Copia de {presupuesto_orig.titulo}" if presupuesto_orig.titulo else "Copia de presupuesto",
            notas=presupuesto_orig.notas,
            tecnico_encargado=presupuesto_orig.tecnico_encargado,
            estado='Borrador'  # Siempre comienza como borrador
        )
        
        db.session.add(nuevo_presupuesto)
        db.session.flush()  # Para obtener el ID
        
        # Copiar capítulos
        capitulos_orig = Capitulo.query.filter_by(id_presupuesto=id).all()
        for cap_orig in capitulos_orig:
            nuevo_cap = Capitulo(
                id_presupuesto=nuevo_presupuesto.id,
                numero=cap_orig.numero,
                descripcion=cap_orig.descripcion
            )
            db.session.add(nuevo_cap)
        
        # Copiar partidas
        partidas_orig = Partida.query.filter_by(id_presupuesto=id).all()
        for part_orig in partidas_orig:
            nueva_part = Partida(
                id_presupuesto=nuevo_presupuesto.id,
                capitulo_numero=part_orig.capitulo_numero,
                descripcion=part_orig.descripcion,
                unitario=part_orig.unitario,
                cantidad=part_orig.cantidad,
                precio=part_orig.precio,
                total=part_orig.total,
                margen=part_orig.margen,
                final=part_orig.final
            )
            db.session.add(nueva_part)
        
        db.session.commit()
        flash(f'Presupuesto clonado correctamente con referencia {nueva_referencia}', 'success')
        return redirect(url_for('presupuestos.editar_presupuesto', id=nuevo_presupuesto.id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error al clonar presupuesto: {str(e)}', 'danger')
        return redirect(url_for('presupuestos.editar_presupuesto', id=id))

@presupuestos_bp.route('/api/presupuestos')
def api_listar_presupuestos():
    presupuestos = get_all(Presupuesto)
    return jsonify([{
        'id': p.id,
        'referencia': p.referencia,
        'id_proyecto': p.id_proyecto,
        'fecha': p.fecha.isoformat() if p.fecha else None,
        'titulo': p.titulo,
        'estado': p.estado,
        'total': p.total
    } for p in presupuestos])

@presupuestos_bp.route('/api/presupuestos/<int:id>')
def api_get_presupuesto(id):
    presupuesto = get_by_id(Presupuesto, id)
    if not presupuesto:
        return jsonify({'error': 'Presupuesto no encontrado'}), 404
    
    # Obtener capitulos y partidas
    capitulos = Capitulo.query.filter_by(id_presupuesto=id).order_by(Capitulo.numero).all()
    partidas = Partida.query.filter_by(id_presupuesto=id).all()
    
    # Organizar partidas por capítulo
    partidas_por_capitulo = {}
    for partida in partidas:
        if partida.capitulo_numero not in partidas_por_capitulo:
            partidas_por_capitulo[partida.capitulo_numero] = []
        partidas_por_capitulo[partida.capitulo_numero].append({
            'id': partida.id,
            'descripcion': partida.descripcion,
            'unitario': partida.unitario,
            'cantidad': partida.cantidad,
            'precio': partida.precio,
            'total': partida.total,
            'margen': partida.margen,
            'final': partida.final
        })
    
    return jsonify({
        'id': presupuesto.id,
        'referencia': presupuesto.referencia,
        'id_proyecto': presupuesto.id_proyecto,
        'fecha': presupuesto.fecha.isoformat() if presupuesto.fecha else None,
        'direccion': presupuesto.direccion_completa,
        'titulo': presupuesto.titulo,
        'notas': presupuesto.notas,
        'tecnico_encargado': presupuesto.tecnico_encargado,
        'aprobacion': presupuesto.aprobacion,
        'fecha_aprobacion': presupuesto.fecha_aprobacion.isoformat() if presupuesto.fecha_aprobacion else None,
        'estado': presupuesto.estado,
        'total': presupuesto.total,
        'capitulos': [{
            'id': c.id,
            'numero': c.numero,
            'descripcion': c.descripcion,
            'partidas': partidas_por_capitulo.get(c.numero, [])
        } for c in capitulos]
    })

@presupuestos_bp.route('/aplicar-margen-todas/<int:id>', methods=['POST'])
def aplicar_margen_todas(id):
    """Aplica un margen determinado a todas las partidas de un presupuesto"""
    try:
        print("\n\n-------------- INICIO APLICAR MARGEN ---------------")
        print(f"Procesando petición para presupuesto {id}")
        
        # Verificar que el presupuesto existe
        presupuesto = get_by_id(Presupuesto, id)
        if not presupuesto:
            print("Presupuesto no encontrado")
            flash('Presupuesto no encontrado', 'danger')
            return redirect(url_for('presupuestos.listar_presupuestos'))
        
        # Comprobar el tipo de contenido de la petición
        content_type = request.content_type or ''
        print(f"Content-Type de la petición: {content_type}")
        
        # Comprobar si la petición es JSON
        if 'application/json' in content_type:
            print("Procesando petición JSON")
            # Obtener y mostrar los datos raw recibidos
            raw_data = request.get_data(as_text=True)
            print(f"Datos raw recibidos: {raw_data}")
            
            # Parsear los datos JSON
            data = request.get_json()
            print(f"Datos JSON parseados: {data}")
            
            if not data or 'margen' not in data:
                print("Error: Datos de margen no proporcionados")
                return jsonify({'success': False, 'error': 'Datos de margen no proporcionados'}), 400
                
            try:
                nuevo_margen = float(data['margen'])
                aplicar_proporcionalmente = data.get('aplicar_proporcionalmente', False)
                print(f"Margen: {nuevo_margen}, Aplicar proporcionalmente: {aplicar_proporcionalmente}")
            except (ValueError, TypeError) as e:
                print(f"Error al procesar valores: {e}")
                return jsonify({'success': False, 'error': 'Valor de margen inválido'}), 400
                
            # Obtener todas las partidas
            partidas = Partida.query.filter_by(id_presupuesto=id).all()
            print(f"Total de partidas encontradas: {len(partidas)}")
            
            if aplicar_proporcionalmente and 'factor_escalado' in data:
                # Aplicar el margen proporcionalmente usando el factor de escalado
                factor_escalado = float(data['factor_escalado'])
                print(f"Aplicando márgenes proporcionalmente con factor {factor_escalado}")
                
                for i, partida in enumerate(partidas):
                    if partida.margen is not None:
                        margen_anterior = partida.margen
                        # Aplicar el factor de escalado al margen actual
                        partida.margen = round(partida.margen * factor_escalado, 2)
                        
                        # Recalcular el precio final
                        if partida.total is not None:
                            final_anterior = partida.final
                            partida.final = round(partida.total * (1 + partida.margen / 100), 2)
                            print(f"Partida {i+1}: ID={partida.id}, Margen: {margen_anterior} -> {partida.margen}, Final: {final_anterior} -> {partida.final}")
                        else:
                            print(f"Partida {i+1}: ID={partida.id}, Total es None")
                    else:
                        print(f"Partida {i+1}: ID={partida.id}, Margen es None")
            else:
                # Aplicar el mismo margen a todas las partidas
                print(f"Aplicando margen {nuevo_margen}% a todas las partidas")
                
                for i, partida in enumerate(partidas):
                    margen_anterior = partida.margen
                    final_anterior = partida.final
                    
                    partida.margen = nuevo_margen
                    if partida.total is not None:
                        partida.final = round(partida.total * (1 + nuevo_margen / 100), 2)
                        print(f"Partida {i+1}: ID={partida.id}, Margen: {margen_anterior} -> {partida.margen}, Final: {final_anterior} -> {partida.final}")
                    else:
                        print(f"Partida {i+1}: ID={partida.id}, Total es None")
            
            # Guardar los cambios
            print("Guardando cambios en la base de datos...")
            db.session.commit()
            print("Cambios guardados. Enviando respuesta de éxito.")
            
            return jsonify({'success': True, 'message': 'Margen aplicado correctamente'})
        else:
            # Petición normal de formulario
            print("Procesando petición de formulario")
            margen_str = request.form.get('margen')
            if not margen_str:
                print("Error: Datos de margen no proporcionados en el formulario")
                flash('Datos de margen no proporcionados', 'danger')
                return redirect(url_for('presupuestos.editar_presupuesto', id=id))
            
            try:
                nuevo_margen = float(margen_str)
                print(f"Margen del formulario: {nuevo_margen}")
            except (ValueError, TypeError) as e:
                print(f"Error al procesar margen del formulario: {e}")
                flash('Valor de margen inválido', 'danger')
                return redirect(url_for('presupuestos.editar_presupuesto', id=id))
            
            # Aplicar el margen a todas las partidas
            partidas = Partida.query.filter_by(id_presupuesto=id).all()
            print(f"Total de partidas encontradas: {len(partidas)}")
            
            for i, partida in enumerate(partidas):
                margen_anterior = partida.margen
                final_anterior = partida.final
                
                partida.margen = nuevo_margen
                if partida.total is not None:
                    partida.final = round(partida.total * (1 + nuevo_margen / 100), 2)
                    print(f"Partida {i+1}: ID={partida.id}, Margen: {margen_anterior} -> {partida.margen}, Final: {final_anterior} -> {partida.final}")
                else:
                    print(f"Partida {i+1}: ID={partida.id}, Total es None")
            
            # Guardar los cambios
            print("Guardando cambios en la base de datos...")
            db.session.commit()
            print("Cambios guardados. Redirigiendo al usuario.")
            
            flash('Margen aplicado correctamente a todas las partidas', 'success')
            return redirect(url_for('presupuestos.editar_presupuesto', id=id))
            
    except Exception as e:
        db.session.rollback()
        print(f"\nERROR al aplicar margen: {str(e)}")
        traceback.print_exc()
        print("-------------- FIN APLICAR MARGEN (ERROR) ---------------\n")
        
        # Verificar si la solicitud fue AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in (request.content_type or ''):
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            flash(f'Error al aplicar margen: {str(e)}', 'danger')
            return redirect(url_for('presupuestos.editar_presupuesto', id=id))
            
    print("-------------- FIN APLICAR MARGEN (ÉXITO) ---------------\n")
