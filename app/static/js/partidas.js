/**
 * Archivo JavaScript para la gestión de partidas en presupuestos
 */

// Variables globales para edición in-line de partidas
let datosOriginales = {}; // Almacena los datos originales de la partida en edición

// Función para insertar la edición in-line de una partida
function editarPartidaInline(id, capitulo_numero, numero, descripcion, unitario, cantidad, precio, margen) {
    // Guardar datos originales para cancelar
    datosOriginales = {descripcion, unitario, cantidad, precio, margen};
    
    // Seleccionar las filas de la partida
    const fila1 = document.querySelector(`.partida-fila-1-${id}`);
    const fila2 = document.querySelector(`.partida-fila-2-${id}`);
    
    if (fila1 && fila2) {
        // Reemplazar contenido con campos editables
        fila1.querySelector('td:nth-child(2)').innerHTML = `
            <textarea class="form-control" id="editar-descripcion-${id}">${descripcion}</textarea>
        `;
        
        // Crear contenedor para datos numéricos
        let datosNumericos = `
            <div class="row mb-2">
                <div class="col">
                    <label for="editar-unitario-${id}">Unidad:</label>
                    <input type="text" class="form-control" id="editar-unitario-${id}" value="${unitario}">
                </div>
                <div class="col">
                    <label for="editar-cantidad-${id}">Cantidad:</label>
                    <input type="number" step="0.01" class="form-control" id="editar-cantidad-${id}" value="${cantidad}" onchange="calcularTotalInline(${id})">
                </div>
                <div class="col">
                    <label for="editar-precio-${id}">Precio:</label>
                    <input type="number" step="0.01" class="form-control" id="editar-precio-${id}" value="${precio}" onchange="calcularTotalInline(${id})">
                </div>
            </div>
            <div class="row">
                <div class="col">
                    <label for="editar-total-${id}">Total:</label>
                    <input type="number" step="0.01" class="form-control" id="editar-total-${id}" value="${(cantidad * precio).toFixed(2)}" readonly>
                </div>
                <div class="col">
                    <label for="editar-margen-${id}">Margen (%):</label>
                    <input type="number" step="0.01" class="form-control" id="editar-margen-${id}" value="${margen}" onchange="calcularFinalInline(${id})">
                </div>
                <div class="col">
                    <label for="editar-final-${id}">Total + Margen:</label>
                    <input type="number" step="0.01" class="form-control" id="editar-final-${id}" value="${((cantidad * precio) * (1 + margen/100)).toFixed(2)}" readonly>
                </div>
            </div>
        `;
        
        fila2.querySelector('td:nth-child(1)').colSpan = 3;
        fila2.querySelector('td:nth-child(1)').innerHTML = datosNumericos;
        
        // Cambiar botones por guardar/cancelar
        fila1.querySelector('td:nth-child(3)').innerHTML = `
            <button type="button" class="btn btn-sm btn-success" onclick="guardarPartidaInline(${id})">
                <i class="fas fa-save"></i>
            </button>
            <button type="button" class="btn btn-sm btn-secondary" onclick="cancelarEdicionInline(${id})">
                <i class="fas fa-times"></i>
            </button>
        `;
    }
}

// Función para calcular el total en edición in-line
function calcularTotalInline(id) {
    const cantidad = parseFloat(document.getElementById(`editar-cantidad-${id}`).value) || 0;
    const precio = parseFloat(document.getElementById(`editar-precio-${id}`).value) || 0;
    const total = cantidad * precio;
    document.getElementById(`editar-total-${id}`).value = total.toFixed(2);
    calcularFinalInline(id);
}

// Función para calcular el precio final en edición in-line
function calcularFinalInline(id) {
    const total = parseFloat(document.getElementById(`editar-total-${id}`).value) || 0;
    const margen = parseFloat(document.getElementById(`editar-margen-${id}`).value) || 0;
    const final = total * (1 + margen / 100);
    document.getElementById(`editar-final-${id}`).value = final.toFixed(2);
}

// Función para guardar los cambios de edición in-line
function guardarPartidaInline(id) {
    const descripcion = document.getElementById(`editar-descripcion-${id}`).value;
    const unitario = document.getElementById(`editar-unitario-${id}`).value;
    const cantidad = document.getElementById(`editar-cantidad-${id}`).value;
    const precio = document.getElementById(`editar-precio-${id}`).value;
    const margen = document.getElementById(`editar-margen-${id}`).value;
    
    // Aquí se enviarían los datos al servidor mediante Ajax
    // Por ahora solo actualizamos la vista
    actualizarVistaPartida(id, {
        descripcion,
        unitario,
        cantidad,
        precio,
        margen
    });
}

// Función para cancelar la edición in-line
function cancelarEdicionInline(id) {
    actualizarVistaPartida(id, datosOriginales);
}

// Función para actualizar la vista de una partida después de editar
function actualizarVistaPartida(id, datos) {
    const {descripcion, unitario, cantidad, precio, margen} = datos;
    const total = (parseFloat(cantidad) * parseFloat(precio)).toFixed(2);
    const final = (parseFloat(total) * (1 + parseFloat(margen)/100)).toFixed(2);
    
    // Restaurar vista normal de la partida
    const fila1 = document.querySelector(`.partida-fila-1-${id}`);
    const fila2 = document.querySelector(`.partida-fila-2-${id}`);
    
    if (fila1 && fila2) {
        // Actualizar datos visibles
        fila1.querySelector('td:nth-child(2)').textContent = descripcion;
        
        // Restaurar visualización de datos numéricos
        const datosNumericos = `
            <div class="row datos-numericos">
                <div class="col">
                    <span><strong>Unidad:</strong> ${unitario}</span>
                </div>
                <div class="col">
                    <span><strong>Cantidad:</strong> ${parseFloat(cantidad).toFixed(2)}</span>
                </div>
                <div class="col">
                    <span><strong>Precio:</strong> ${parseFloat(precio).toFixed(2)} €</span>
                </div>
                <div class="col">
                    <span><strong>Total:</strong> ${total} €</span>
                </div>
                <div class="col">
                    <span><strong>Margen %:</strong> ${margen} %</span>
                </div>
                <div class="col">
                    <span><strong>Total + Margen:</strong> ${final} €</span>
                </div>
            </div>
        `;
        
        // Restaurar estructura de la tabla
        fila2.querySelector('td').colSpan = 3;
        fila2.querySelector('td').innerHTML = datosNumericos;
        
        // Restaurar botones originales
        fila1.querySelector('td:nth-child(3)').innerHTML = `
            <button type="button" class="btn btn-sm btn-info" 
                    onclick="editarPartida(
                        '${id}', 
                        '${fila1.dataset.capitulo}',
                        '${fila1.dataset.numero}',
                        '${descripcion}',
                        '${unitario}',
                        '${cantidad}',
                        '${precio}',
                        '${margen}'
                    )">
                <i class="fas fa-edit"></i>
            </button>
            <button type="button" class="btn btn-sm btn-danger" 
                    data-bs-toggle="modal" data-bs-target="#eliminarPartidaModal${id}">
                <i class="fas fa-trash"></i>
            </button>
        `;
    }
}

// Función para aplicar un margen a todas las partidas
function aplicarMargen() {
    const margen = document.getElementById('margen-medio').value;
    
    // Enviar mediante AJAX para que no se recargue la página
    fetch("/presupuestos/aplicar-margen-todas/" + window.presupuestoId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
        },
        body: JSON.stringify({
            margen: margen
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Recargar la página para ver los cambios
            location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        alert('Error: ' + error);
    });
}

// Calcular total para nueva partida
function calcularTotal() {
    const cantidad = parseFloat(document.getElementById('cantidad').value) || 0;
    const precio = parseFloat(document.getElementById('precio').value) || 0;
    const total = cantidad * precio;
    document.getElementById('total').value = total.toFixed(2);
    calcularFinal();
}

// Calcular precio final para nueva partida
function calcularFinal() {
    const total = parseFloat(document.getElementById('total').value) || 0;
    const margen = parseFloat(document.getElementById('margen').value) || 0;
    const final = total * (1 + margen / 100);
    document.getElementById('final').value = final.toFixed(2);
}

// Calcular total para edición de partida
function calcularTotalEditar() {
    const cantidad = parseFloat(document.getElementById('editar_partida_cantidad').value) || 0;
    const precio = parseFloat(document.getElementById('editar_partida_precio').value) || 0;
    const total = cantidad * precio;
    document.getElementById('editar_partida_total').value = total.toFixed(2);
    calcularFinalEditar();
}

// Calcular precio final para edición de partida
function calcularFinalEditar() {
    const total = parseFloat(document.getElementById('editar_partida_total').value) || 0;
    const margen = parseFloat(document.getElementById('editar_partida_margen').value) || 0;
    const final = total * (1 + margen / 100);
    document.getElementById('editar_partida_final').value = final.toFixed(2);
}

// Seleccionar capítulo para nueva partida
function seleccionarCapitulo(numero) {
    document.getElementById('capitulo_numero').value = numero;
}

// Preparar datos para el modal de edición de capítulo
function editarCapitulo(id, numero, descripcion) {
    document.getElementById('formEditarCapitulo').action = `/presupuestos/capitulo/editar/${id}`;
    document.getElementById('editar_descripcion').value = descripcion;
    
    const modal = new bootstrap.Modal(document.getElementById('editarCapituloModal'));
    modal.show();
}

// Preparar datos para el modal de edición de partida
function editarPartida(id, capitulo_numero, numero, descripcion, unitario, cantidad, precio, margen) {
    document.getElementById('formEditarPartida').action = `/presupuestos/partida/editar/${id}`;
    document.getElementById('editar_partida_capitulo').value = capitulo_numero;
    
    // Mostrar el número real de la partida
    document.getElementById('editar_partida_numero_display').value = numero || (capitulo_numero + '.?');
    document.getElementById('editar_partida_numero').value = numero;
    
    document.getElementById('editar_partida_descripcion').value = descripcion;
    document.getElementById('editar_partida_unitario').value = unitario;
    document.getElementById('editar_partida_cantidad').value = cantidad;
    document.getElementById('editar_partida_precio').value = precio;
    document.getElementById('editar_partida_margen').value = margen;
    
    // Calcular el total y final
    calcularTotalEditar();
    
    const modal = new bootstrap.Modal(document.getElementById('editarPartidaModal'));
    modal.show();
}
