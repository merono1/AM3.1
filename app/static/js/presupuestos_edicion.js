// Función para preparar el modal de nueva partida
function prepararModalNuevaPartida(capitulo_numero) {
    console.log('Preparando modal para nueva partida del capítulo:', capitulo_numero);
    
    // Establecer el capítulo seleccionado
    document.getElementById('nueva_partida_capitulo_numero').value = capitulo_numero;
    
    // Inicializar o limpiar el editor
    const modalDescripcion = document.getElementById('modal_descripcion');
    if (modalDescripcion && modalDescripcion._ckeditor) {
        modalDescripcion._ckeditor.setData('');
    }
    
    // Restablecer valores por defecto
    document.getElementById('modal_unitario').value = 'Ud';
    document.getElementById('modal_cantidad').value = '1';
    document.getElementById('modal_precio').value = '0';
    document.getElementById('modal_margen').value = '40';
    
    // Calcular valores iniciales
    calcularTotalModal();
    calcularFinalModal();
}

// Función para calcular el total en el modal
function calcularTotalModal() {
    const cantidad = parseFloat(document.getElementById('modal_cantidad').value) || 0;
    const precio = parseFloat(document.getElementById('modal_precio').value) || 0;
    const total = cantidad * precio;
    
    // Actualizar el elemento que muestra el total
    const totalCalc = document.getElementById('modal_total_calc');
    if (totalCalc) {
        totalCalc.innerHTML = `<strong>Total calculado:</strong> ${total.toFixed(2).replace('.', ',')} €`;
    }
    
    // Calcular también el final
    calcularFinalModal();
}

// Función para calcular el precio final en el modal
function calcularFinalModal() {
    const cantidad = parseFloat(document.getElementById('modal_cantidad').value) || 0;
    const precio = parseFloat(document.getElementById('modal_precio').value) || 0;
    const margen = parseFloat(document.getElementById('modal_margen').value) || 40;
    
    const total = cantidad * precio;
    const final = total * (1 + margen / 100);
    
    // Actualizar el elemento que muestra el precio final
    const finalCalc = document.getElementById('modal_final_calc');
    if (finalCalc) {
        finalCalc.innerHTML = `<strong>Precio final:</strong> ${final.toFixed(2).replace('.', ',')} €`;
    }
}/**
 * Archivo JavaScript específico para la edición de presupuestos
 */

// Variables globales para edición in-line
let partidaEnEdicion = null;
let datosOriginales = {};
let presupuestoId = null;
let csrfToken = null;

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando módulo de edición de presupuestos...');
    
    // Obtener el ID del presupuesto y CSRF token del contexto global si están disponibles
    if (window.presupuestoId) presupuestoId = window.presupuestoId;
    
    // Buscar token CSRF en el formulario
    const csrfInput = document.querySelector('input[name="csrf_token"]');
    if (csrfInput) csrfToken = csrfInput.value;
    
    console.log('Presupuesto ID:', presupuestoId);
    console.log('CSRF token disponible:', csrfToken ? 'Sí' : 'No');
    
    // Inicializar CKEditor 5 en los formularios de nueva partida
    document.querySelectorAll('.nuevo-partida-form textarea.nueva-descripcion').forEach(textarea => {
        ClassicEditor
            .create(textarea, {
                toolbar: {
                    items: [
                        'bold', 'italic', 'underline', 'strikethrough',
                        '|', 'numberedList', 'bulletedList', 'outdent', 'indent', 'blockQuote',
                        '|', 'alignment',
                        '|', 'heading'
                    ]
                },
                placeholder: 'Escriba la descripción aquí...',
                height: '150px'
            })
            .then(editor => {
                // Almacenar la instancia del editor para poder acceder posteriormente
                textarea._ckeditor = editor;
                console.log(`CKEditor 5 inicializado para el textarea ${textarea.id}`);
            })
            .catch(error => {
                console.error(`Error al inicializar CKEditor para ${textarea.id}:`, error);
            });
    });

    // Inicializar CKEditor para el modal de nueva partida
    // Ya no inicializamos el editor para modal_descripcion aquí 
    // porque ahora se hace en presupuestos_modal.js

    // Ocultar todos los formularios de nueva partida al inicio
    document.querySelectorAll('.nuevo-partida-form').forEach(form => {
        form.style.display = 'none';
        
        // Inicializar cálculos para los formularios de nuevas partidas
        const capituloNumero = form.getAttribute('data-capitulo');
        if (capituloNumero) {
            // Conectar los eventos a los campos
            const cantidadInput = form.querySelector('.nueva-cantidad');
            const precioInput = form.querySelector('.nueva-precio');
            const margenInput = form.querySelector('.nueva-margen');
            
            if (cantidadInput) {
                cantidadInput.addEventListener('input', function() {
                    calcularTotalNueva(capituloNumero);
                });
            }
            
            if (precioInput) {
                precioInput.addEventListener('input', function() {
                    calcularTotalNueva(capituloNumero);
                });
            }
            
            if (margenInput) {
                margenInput.addEventListener('input', function() {
                    calcularFinalNueva(capituloNumero);
                });
            }
        }
    });
    
    // Inicializar token CSRF
    csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
    
    // Conectar eventos para el modal
    const modalCantidad = document.getElementById('modal_cantidad');
    if (modalCantidad) {
        modalCantidad.addEventListener('input', calcularTotalModal);
    }
    
    const modalPrecio = document.getElementById('modal_precio');
    if (modalPrecio) {
        modalPrecio.addEventListener('input', calcularTotalModal);
    }
    
    const modalMargen = document.getElementById('modal_margen');
    if (modalMargen) {
        modalMargen.addEventListener('input', calcularFinalModal);
    }
});

// Función para mostrar/ocultar el formulario de nueva partida
function toggleNuevaPartidaForm(capitulo_numero) {
    console.log('Toggling formulario para capítulo:', capitulo_numero);
    const form = document.querySelector(`.nuevo-partida-form[data-capitulo="${capitulo_numero}"]`);
    if (form) {
        // Si el formulario está visible, ocultarlo, si está oculto, mostrarlo
        if (form.style.display === 'none' || form.style.display === '') {
            // Primero ocultar todos los formularios
            document.querySelectorAll('.nuevo-partida-form').forEach(f => {
                f.style.display = 'none';
            });
            // Luego mostrar solo el solicitado
            form.style.display = 'block';
            
            // Inicializar CKEditor 5 si no lo está ya
            const textareaId = `descripcion_${capitulo_numero}`;
            const textareaElement = document.getElementById(textareaId);
            
            if (textareaElement && !textareaElement._ckeditor) {
                ClassicEditor
                    .create(textareaElement, {
                        toolbar: {
                            items: [
                                'bold', 'italic', 'underline', 'strikethrough',
                                '|', 'numberedList', 'bulletedList', 'outdent', 'indent', 'blockQuote',
                                '|', 'alignment',
                                '|', 'heading'
                            ]
                        },
                        placeholder: 'Escriba la descripción aquí...'
                    })
                    .then(editor => {
                        textareaElement._ckeditor = editor;
                        console.log(`CKEditor 5 inicializado para el textarea ${textareaId}`);
                        // Hacer focus cuando el editor está listo
                        editor.focus();
                    })
                    .catch(error => {
                        console.error(`Error al inicializar CKEditor para ${textareaId}:`, error);
                    });
            } else if (textareaElement && textareaElement._ckeditor) {
                // Focus en el editor existente
                textareaElement._ckeditor.focus();
            }
            
            // Calcular los valores iniciales
            calcularTotalNueva(capitulo_numero);
            calcularFinalNueva(capitulo_numero);
        } else {
            // Destruir la instancia de CKEditor 5 si existe
            const textareaId = `descripcion_${capitulo_numero}`;
            const textareaElement = document.getElementById(textareaId);
            
            if (textareaElement && textareaElement._ckeditor) {
                textareaElement._ckeditor.destroy()
                    .then(() => {
                        console.log(`CKEditor 5 para ${textareaId} destruido`);
                        textareaElement._ckeditor = null;
                    })
                    .catch(error => {
                        console.error(`Error al destruir CKEditor para ${textareaId}:`, error);
                    });
            }
            form.style.display = 'none';
        }
    } else {
        console.error(`No se encontró el formulario para el capítulo ${capitulo_numero}`);
    }
}

// Función para iniciar la edición in-line de una partida
function iniciarEdicionPartida(idPartida) {
    // Si ya hay una partida en edición, cancelamos primero
    if (partidaEnEdicion) {
        cancelarEdicionPartida();
    }
    
    console.log('Iniciando edición de partida ID:', idPartida);
    partidaEnEdicion = idPartida;
    
    // Obtener las filas de la partida
    const fila1 = document.querySelector(`.partida-fila-1[data-partida-id="${idPartida}"]`);
    const fila2 = document.querySelector(`.partida-fila-2[data-partida-id="${idPartida}"]`);
    
    if (!fila1 || !fila2) {
        console.error('No se encontraron las filas de la partida');
        return;
    }
    
    // Añadir clase de edición para destacar visualmente
    fila1.classList.add('partida-edicion');
    fila2.classList.add('partida-edicion');
    
    // Guardar datos originales para poder cancelar
    const descripcionCelda = fila1.querySelector('.descripcion-celda');
    const unitarioSpan = fila2.querySelector('.unitario-span');
    const cantidadSpan = fila2.querySelector('.cantidad-span');
    const precioSpan = fila2.querySelector('.precio-span');
    const margenSpan = fila2.querySelector('.margen-span');
    const totalSpan = fila2.querySelector('.total-span');
    const finalSpan = fila2.querySelector('.final-span');
    
    // Guardar el contenido HTML completo para no perder el formato
    datosOriginales = {
        descripcion: descripcionCelda.innerHTML,
        unitario: unitarioSpan.textContent.trim(),
        cantidad: cantidadSpan.textContent.trim().replace(',', '.'),
        precio: precioSpan.textContent.trim().replace('€', '').trim().replace(',', '.'),
        margen: margenSpan ? margenSpan.textContent.trim().replace('%', '').trim().replace(',', '.') : '40',
        total: totalSpan.textContent.trim().replace('EUR', '').trim().replace(',', '.'),
        final: finalSpan ? finalSpan.textContent.trim().replace('EUR', '').trim().replace(',', '.') : '0'
    };
    
    console.log('Datos originales:', datosOriginales);
    
    // Reemplazar contenido con campos editables
    descripcionCelda.innerHTML = `
        <div class="campo-edicion" style="width: 100%;">
            <textarea id="editor_${idPartida}" class="edit-descripcion" style="width: 100%; min-height: 100px;">${datosOriginales.descripcion}</textarea>
        </div>
    `;
    
    // Inicializar CKEditor 5 en el textarea
    setTimeout(() => {
        const textareaElement = document.getElementById(`editor_${idPartida}`);
        if (textareaElement) {
            ClassicEditor
                .create(textareaElement, {
                    toolbar: {
                        items: [
                            'bold', 'italic', 'underline', 'strikethrough',
                            '|', 'numberedList', 'bulletedList', 'outdent', 'indent', 'blockQuote',
                            '|', 'alignment',
                            '|', 'heading'
                        ]
                    },
                    placeholder: 'Escriba la descripción aquí...'
                })
                .then(editor => {
                    // Guardar referencia al editor
                    textareaElement._ckeditor = editor;
                    console.log(`CKEditor 5 inicializado para el editor_${idPartida}`);
                })
                .catch(error => {
                    console.error(`Error al inicializar CKEditor para editor_${idPartida}:`, error);
                });
        } else {
            console.error(`No se encontró el elemento editor_${idPartida}`);
        }
    }, 100);
    
    // Reemplazar los datos numéricos
    const contenedorDatos = fila2.querySelector('.tabla-datos-partida');
    
    // Crear una nueva estructura para la edición
    const formHTML = `
        <div class="row p-2">
            <div class="col-md-3 mb-2">
                <div class="campo-edicion">
                    <label><strong>Unidad:</strong></label>
                    <select class="edit-unitario form-control form-control-sm">
                        <option value="Ud" ${datosOriginales.unitario === 'Ud' ? 'selected' : ''}>Ud</option>
                        <option value="M2" ${datosOriginales.unitario === 'M2' ? 'selected' : ''}>M2</option>
                        <option value="Ml" ${datosOriginales.unitario === 'Ml' ? 'selected' : ''}>Ml</option>
                        <option value="M3" ${datosOriginales.unitario === 'M3' ? 'selected' : ''}>M3</option>
                        <option value="PA" ${datosOriginales.unitario === 'PA' ? 'selected' : ''}>PA</option>
                    </select>
                </div>
            </div>
            <div class="col-md-3 mb-2">
                <div class="campo-edicion">
                    <label><strong>Cantidad:</strong></label>
                    <input type="number" class="edit-cantidad form-control form-control-sm" value="${parseFloat(datosOriginales.cantidad)}" step="0.01" min="0" onchange="calcularTotalEnEdicion()"> 
                </div>
            </div>
            <div class="col-md-3 mb-2">
                <div class="campo-edicion">
                    <label><strong>Precio:</strong></label>
                    <input type="number" class="edit-precio form-control form-control-sm" value="${parseFloat(datosOriginales.precio)}" step="0.01" min="0" onchange="calcularTotalEnEdicion()">
                </div>
            </div>
            <div class="col-md-3 mb-2">
                <div class="campo-edicion">
                    <label><strong>Margen (%):</strong></label>
                    <input type="number" class="edit-margen form-control form-control-sm" value="${parseFloat(datosOriginales.margen)}" step="0.01" min="0" onchange="calcularFinalEnEdicion()">
                </div>
            </div>
            <div class="col-md-12 mt-3">
                <div class="botones-edicion text-center">
                    <button type="button" class="btn btn-sm btn-primary" onclick="guardarEdicionPartida('${idPartida}')">Guardar</button>
                    <button type="button" class="btn btn-sm btn-danger" onclick="cancelarEdicionPartida()">Cancelar</button>
                </div>
            </div>
        </div>
    `;
    
    // Reemplazar el contenido del contenedor con el formulario de edición
    const divContenedor = document.createElement('div');
    divContenedor.className = 'formulario-edicion';
    divContenedor.innerHTML = formHTML;
    
    // Limpiar el contenedor y añadir el formulario
    contenedorDatos.innerHTML = '';
    contenedorDatos.appendChild(divContenedor);
    
    // Ocultar el botón de editar durante la edición
    const editarBtn = fila1.querySelector('.editar-partida-btn');
    if (editarBtn) editarBtn.style.display = 'none';
    
    // Enfocar el campo de descripción
    setTimeout(() => {
        const textarea = fila1.querySelector('.edit-descripcion');
        if (textarea) textarea.focus();
    }, 100);
}

// Función para calcular el total durante la edición
function calcularTotalEnEdicion() {
  if (!partidaEnEdicion) return;

  const fila2 = document.querySelector(`.partida-fila-2[data-partida-id="${partidaEnEdicion}"]`);
  if (!fila2) return;

  const cantidadInput = fila2.querySelector('.edit-cantidad');
  const precioInput = fila2.querySelector('.edit-precio');

  if (cantidadInput && precioInput) {
    const cantidad = parseFloat(cantidadInput.value) || 0;
    const precio = parseFloat(precioInput.value) || 0;
    const total = cantidad * precio;

    console.log(`Calculando total: ${cantidad} x ${precio} = ${total}`);

    // Crear un elemento para mostrar el total calculado si no existe
    let totalDisplay = fila2.querySelector('.calculated-total');
    if (!totalDisplay) {
        totalDisplay = document.createElement('div');
        totalDisplay.className = 'calculated-total alert alert-info p-2 mt-2 text-center';
        fila2.querySelector('.formulario-edicion').appendChild(totalDisplay);
    }

    totalDisplay.innerHTML = `<strong>Total calculado:</strong> ${total.toFixed(2).replace('.', ',')} €`;
  }
}

// Función para calcular el precio final durante la edición
function calcularFinalEnEdicion() {
    if (!partidaEnEdicion) return;
    
    const fila2 = document.querySelector(`.partida-fila-2[data-partida-id="${partidaEnEdicion}"]`);
    if (!fila2) return;
    
    const cantidadInput = fila2.querySelector('.edit-cantidad');
    const precioInput = fila2.querySelector('.edit-precio');
    const margenInput = fila2.querySelector('.edit-margen');
    
    if (cantidadInput && precioInput && margenInput) {
        const cantidad = parseFloat(cantidadInput.value) || 0;
        const precio = parseFloat(precioInput.value) || 0;
        const margen = parseFloat(margenInput.value) || 0;
        
        const total = cantidad * precio;
        const final = total * (1 + margen / 100);
        
        console.log(`Calculando final: ${total} x (1 + ${margen}/100) = ${final}`);
        
        // Actualizar o crear elemento para mostrar el precio final calculado
        let finalDisplay = fila2.querySelector('.calculated-final');
        if (!finalDisplay) {
            const formularioEdicion = fila2.querySelector('.formulario-edicion');
            finalDisplay = document.createElement('div');
            finalDisplay.className = 'calculated-final alert alert-success p-1 mt-2';
            formularioEdicion.appendChild(finalDisplay);
        }
        finalDisplay.innerHTML = `<strong>Total + Margen:</strong> ${final.toFixed(2).replace('.', ',')} €`;
    }
}

// Función para guardar los cambios de la edición
function guardarEdicionPartida(idPartida) {
    console.log('Guardando cambios de partida ID:', idPartida);
    
    const fila1 = document.querySelector(`.partida-fila-1[data-partida-id="${idPartida}"]`);
    const fila2 = document.querySelector(`.partida-fila-2[data-partida-id="${idPartida}"]`);
    
    if (!fila1 || !fila2) {
        console.error('No se encontraron las filas de la partida');
        return;
    }
    
    // Obtener los valores de los campos de edición
    const textareaElement = document.getElementById(`editor_${idPartida}`);
    let descripcion = '';
    
    if (textareaElement && textareaElement._ckeditor) {
        descripcion = textareaElement._ckeditor.getData();
    } else if (textareaElement) {
        descripcion = textareaElement.value;
    } else {
        const editDescripcion = fila1.querySelector('.edit-descripcion');
        if (editDescripcion) {
            descripcion = editDescripcion.value;
        }
    }
    const unitario = fila2.querySelector('.edit-unitario').value;
    const cantidad = parseFloat(fila2.querySelector('.edit-cantidad').value) || 0;
    const precio = parseFloat(fila2.querySelector('.edit-precio').value) || 0;
    const margen = parseFloat(fila2.querySelector('.edit-margen').value) || 40;
    
    // Preparar datos para enviar al servidor
    const datosActualizados = {
        descripcion: descripcion,
        unitario: unitario,
        cantidad: cantidad,
        precio: precio,
        margen: margen
    };
    
    console.log('Datos actualizados a enviar:', datosActualizados);
    
    // Obtener el token CSRF actualizado
    const token = csrfToken || document.querySelector('input[name="csrf_token"]')?.value || '';
    console.log('Usando CSRF token:', token);
    
    // Enviar datos al servidor usando fetch
    fetch(`/presupuestos/api/partida/editar/${idPartida}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': token
        },
        body: JSON.stringify(datosActualizados)
    })
    .then(response => {
        console.log('Respuesta del servidor status:', response.status);
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log('Respuesta del servidor:', data);
        
        if (data.success) {
            // Actualizar la vista con los datos actualizados
            const partida = data.partida;
            
            // Actualizar descripción (usando innerHTML para preservar el formato HTML)
            fila1.querySelector('.descripcion-celda').innerHTML = partida.descripcion;
            
            // Actualizar valores numéricos
            const contenedorDatos = fila2.querySelector('.tabla-datos-partida');
            contenedorDatos.innerHTML = `
                <div class="row g-1">
                    <div class="col-md-2 campo-dato-container">
                        <span class="campo-dato">
                            <strong>Unitario:</strong>
                            <span class="unitario-span">${partida.unitario}</span>
                        </span>
                    </div>
                    <div class="col-md-2 campo-dato-container">
                        <span class="campo-dato">
                            <strong>Cantidad:</strong>
                            <span class="cantidad-span">${partida.cantidad.toFixed(2).replace('.', ',')}</span>
                        </span>
                    </div>
                    <div class="col-md-2 campo-dato-container">
                        <span class="campo-dato">
                            <strong>Precio:</strong>
                            <span class="precio-span">${partida.precio.toFixed(2).replace('.', ',')}</span>
                        </span>
                    </div>
                    <div class="col-md-2 campo-dato-container">
                        <span class="campo-dato">
                            <strong>Margen:</strong>
                            <span class="margen-span">${partida.margen.toFixed(2).replace('.', ',')}%</span>
                        </span>
                    </div>
                    <div class="col-md-2 campo-dato-container">
                        <span class="campo-dato">
                            <strong>Total:</strong>
                            <span class="total-span">${partida.total.toFixed(2).replace('.', ',')} EUR</span>
                        </span>
                    </div>
                    <div class="col-md-2 campo-dato-container">
                        <span class="campo-dato total-campo">
                            <strong>Total+Margen:</strong>
                            <span class="final-span">${partida.final.toFixed(2).replace('.', ',')} EUR</span>
                        </span>
                    </div>
                </div>
            `;
            
            // Restaurar las clases y estilos
            fila1.classList.remove('partida-edicion');
            fila2.classList.remove('partida-edicion');
            
            // Mostrar nuevamente el botón de editar
            const editarBtn = fila1.querySelector('.editar-partida-btn');
            if (editarBtn) editarBtn.style.display = '';
            
            // Limpiar variable global
            partidaEnEdicion = null;
            datosOriginales = {};
            
            // Mostrar mensaje de éxito
            const mensajeExito = document.createElement('div');
            mensajeExito.className = 'alert alert-success position-fixed top-0 start-50 translate-middle-x mt-3';
            mensajeExito.style.zIndex = '1050';
            mensajeExito.innerHTML = '<strong>¡Éxito!</strong> Partida actualizada correctamente.';
            document.body.appendChild(mensajeExito);
            
            // Eliminar el mensaje después de 3 segundos
            setTimeout(() => {
                mensajeExito.remove();
            }, 3000);
        } else {
            alert('Error al guardar: ' + (data.error || 'Error desconocido'));
            cancelarEdicionPartida();
        }
    })
    .catch(error => {
        console.error('Error al enviar datos:', error);
        alert('Error al guardar cambios: ' + error.message);
        cancelarEdicionPartida();
    });
}

// Función para cancelar la edición y restaurar los valores originales
function cancelarEdicionPartida() {
    if (!partidaEnEdicion) return;
    
    console.log('Cancelando edición de partida');
    
    const fila1 = document.querySelector(`.partida-fila-1[data-partida-id="${partidaEnEdicion}"]`);
    const fila2 = document.querySelector(`.partida-fila-2[data-partida-id="${partidaEnEdicion}"]`);
    
    if (!fila1 || !fila2) {
        console.error('No se encontraron las filas de la partida');
        return;
    }
    
    // Destruir la instancia de CKEditor 5 si existe
    const textareaElement = document.getElementById(`editor_${partidaEnEdicion}`);
    if (textareaElement && textareaElement._ckeditor) {
        textareaElement._ckeditor.destroy()
            .then(() => {
                console.log(`CKEditor 5 para editor_${partidaEnEdicion} destruido`);
                textareaElement._ckeditor = null;
            })
            .catch(error => {
                console.error(`Error al destruir CKEditor para editor_${partidaEnEdicion}:`, error);
            });
    }
    
    // Restaurar el contenido original con el HTML completo
    fila1.querySelector('.descripcion-celda').innerHTML = datosOriginales.descripcion;
    
    // Restaurar datos numéricos
    const contenedorDatos = fila2.querySelector('.tabla-datos-partida');
    contenedorDatos.innerHTML = `
        <div class="row g-1">
            <div class="col-md-2 campo-dato-container">
                <span class="campo-dato">
                    <strong>Unitario:</strong>
                    <span class="unitario-span">${datosOriginales.unitario}</span>
                </span>
            </div>
            <div class="col-md-2 campo-dato-container">
                <span class="campo-dato">
                    <strong>Cantidad:</strong>
                    <span class="cantidad-span">${datosOriginales.cantidad}</span>
                </span>
            </div>
            <div class="col-md-2 campo-dato-container">
                <span class="campo-dato">
                    <strong>Precio:</strong>
                    <span class="precio-span">${datosOriginales.precio}</span>
                </span>
            </div>
            <div class="col-md-2 campo-dato-container">
                <span class="campo-dato">
                    <strong>Margen:</strong>
                    <span class="margen-span">${datosOriginales.margen}%</span>
                </span>
            </div>
            <div class="col-md-2 campo-dato-container">
                <span class="campo-dato">
                    <strong>Total:</strong>
                    <span class="total-span">${datosOriginales.total} EUR</span>
                </span>
            </div>
            <div class="col-md-2 campo-dato-container">
                <span class="campo-dato total-campo">
                    <strong>Total+Margen:</strong>
                    <span class="final-span">${datosOriginales.final} EUR</span>
                </span>
            </div>
        </div>
    `;
    
    // Restaurar las clases y estilos
    fila1.classList.remove('partida-edicion');
    fila2.classList.remove('partida-edicion');
    
    // Mostrar nuevamente el botón de editar
    const editarBtn = fila1.querySelector('.editar-partida-btn');
    if (editarBtn) editarBtn.style.display = '';
    
    // Limpiar variables globales
    partidaEnEdicion = null;
    datosOriginales = {};
}

// Funciones para el formulario inline de nueva partida
function calcularTotalNueva(capitulo_numero) {
    console.log('Calculando total para nueva partida en capítulo:', capitulo_numero);
    const form = document.querySelector(`.nuevo-partida-form[data-capitulo="${capitulo_numero}"]`);
    if (!form) {
        console.error(`No se encontró el formulario para el capítulo ${capitulo_numero}`);
        return;
    }
    
    const cantidadInput = form.querySelector('.nueva-cantidad');
    const precioInput = form.querySelector('.nueva-precio');
    
    if (!cantidadInput || !precioInput) {
        console.error('No se encontraron los campos de cantidad o precio');
        return;
    }
    
    const cantidad = parseFloat(cantidadInput.value) || 0;
    const precio = parseFloat(precioInput.value) || 0;
    const total = cantidad * precio;
    
    console.log(`Cálculo: ${cantidad} × ${precio} = ${total}`);
    
    // Actualizar el elemento que muestra el total
    let totalDisplay = form.querySelector('.nueva-total-calc');
    if (!totalDisplay) {
        totalDisplay = document.createElement('div');
        totalDisplay.className = 'nueva-total-calc alert alert-info p-2 mt-2 text-center';
        form.appendChild(totalDisplay);
    }
    
    totalDisplay.innerHTML = `<strong>Total calculado:</strong> ${total.toFixed(2).replace('.', ',')} €`;
    
    // Calcular también el final
    calcularFinalNueva(capitulo_numero);
}

function calcularFinalNueva(capitulo_numero) {
    console.log('Calculando precio final para nueva partida en capítulo:', capitulo_numero);
    const form = document.querySelector(`.nuevo-partida-form[data-capitulo="${capitulo_numero}"]`);
    if (!form) {
        console.error(`No se encontró el formulario para el capítulo ${capitulo_numero}`);
        return;
    }
    
    const cantidadInput = form.querySelector('.nueva-cantidad');
    const precioInput = form.querySelector('.nueva-precio');
    const margenInput = form.querySelector('.nueva-margen');
    
    if (!cantidadInput || !precioInput || !margenInput) {
        console.error('No se encontraron los campos necesarios');
        return;
    }
    
    const cantidad = parseFloat(cantidadInput.value) || 0;
    const precio = parseFloat(precioInput.value) || 0;
    const margen = parseFloat(margenInput.value) || 40;
    
    const total = cantidad * precio;
    const final = total * (1 + margen / 100);
    
    console.log(`Cálculo final: ${total} × (1 + ${margen}/100) = ${final}`);
    
    // Actualizar el elemento que muestra el precio final
    let finalDisplay = form.querySelector('.nueva-final-calc');
    if (!finalDisplay) {
        finalDisplay = document.createElement('div');
        finalDisplay.className = 'nueva-final-calc alert alert-success p-1 mt-2';
        form.appendChild(finalDisplay);
    }
    
    finalDisplay.innerHTML = `<strong>Total + Margen:</strong> ${final.toFixed(2).replace('.', ',')} €`;
}

// Funciones para cálculos en modales (mantenidas para compatibilidad)
function calcularTotal() {
    const cantidad = parseFloat(document.getElementById('cantidad').value) || 0;
    const precio = parseFloat(document.getElementById('precio').value) || 0;
    const total = cantidad * precio;
    
    // Actualizar campo de total
    const totalInput = document.getElementById('total');
    if (totalInput) totalInput.value = total.toFixed(2);
    
    calcularFinal();
}

function calcularFinal() {
    const total = parseFloat(document.getElementById('total').value) || 0;
    const margen = parseFloat(document.getElementById('margen').value) || 0;
    const final = total * (1 + margen / 100);
    
    // Actualizar campo de final
    const finalInput = document.getElementById('final');
    if (finalInput) finalInput.value = final.toFixed(2);
}

function calcularTotalEditar() {
    const cantidad = parseFloat(document.getElementById('editar_partida_cantidad').value) || 0;
    const precio = parseFloat(document.getElementById('editar_partida_precio').value) || 0;
    const total = cantidad * precio;
    
    // Actualizar campo de total
    const totalInput = document.getElementById('editar_partida_total');
    if (totalInput) totalInput.value = total.toFixed(2);
    
    calcularFinalEditar();
}

function calcularFinalEditar() {
    const total = parseFloat(document.getElementById('editar_partida_total').value) || 0;
    const margen = parseFloat(document.getElementById('editar_partida_margen').value) || 0;
    const final = total * (1 + margen / 100);
    
    // Actualizar campo de final
    const finalInput = document.getElementById('editar_partida_final');
    if (finalInput) finalInput.value = final.toFixed(2);
}

// Aplicación de márgenes
function aplicarMargen() {
    // Obtener el nuevo margen medio deseado
    const nuevoMargenMedio = parseFloat(document.getElementById('margen-medio').value);
    
    if (!nuevoMargenMedio || isNaN(nuevoMargenMedio)) {
        alert('Por favor, introduzca un valor válido para el margen.');
        return;
    }
    
    // Recopilar información de las partidas existentes directamente del DOM
    const partidas = [];
    document.querySelectorAll('.partida-fila-2').forEach(fila => {
        const partidaId = fila.getAttribute('data-partida-id');
        if (partidaId) {
            const margenSpan = fila.querySelector('.margen-span');
            const totalSpan = fila.querySelector('.total-span');
            
            if (margenSpan && totalSpan) {
                const margen = parseFloat(margenSpan.textContent.replace('%', '').replace(',', '.')) || 40;
                const total = parseFloat(totalSpan.textContent.replace('EUR', '').trim().replace(',', '.')) || 0;
                
                partidas.push({
                    id: partidaId,
                    margen: margen,
                    total: total
                });
            }
        }
    });
    
    // Calcular el margen medio actual (ponderado por el valor de cada partida)
    let totalMargenes = 0;
    let totalPesos = 0;
    
    for (const partida of partidas) {
        if (partida.total > 0) {
            totalMargenes += partida.margen * partida.total;
            totalPesos += partida.total;
        }
    }
    
    const margenMedioActual = totalPesos > 0 ? totalMargenes / totalPesos : 40;
    
    // Calcular el factor de escalado
    const factorEscalado = nuevoMargenMedio / margenMedioActual;
    
    console.log('Aplicando cambio proporcional de margen:');
    console.log('Margen medio actual:', margenMedioActual);
    console.log('Nuevo margen medio:', nuevoMargenMedio);
    console.log('Factor de escalado:', factorEscalado);
    
    if (!confirm(`¿Está seguro de actualizar el margen medio a ${nuevoMargenMedio.toFixed(2)}%? \nEsto cambiará proporcionalmente los márgenes de todas las partidas.`)) {
        return;
    }
    
    // Enviar mediante AJAX para que no se recargue la página
    fetch(`/presupuestos/aplicar-margen-todas/${presupuestoId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken || document.querySelector('input[name="csrf_token"]').value
        },
        body: JSON.stringify({
            margen: nuevoMargenMedio,
            aplicar_proporcionalmente: true,
            factor_escalado: factorEscalado
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Recargar la página para ver los cambios
            alert('Márgenes actualizados proporcionalmente');
            location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        alert('Error: ' + error);
    });
}

// Función para seleccionar un capítulo
function seleccionarCapitulo(numero) {
    const capituloSelect = document.getElementById('capitulo_numero');
    if (capituloSelect) {
        // Buscar la opción por valor
        for (let i = 0; i < capituloSelect.options.length; i++) {
            if (capituloSelect.options[i].value === numero) {
                capituloSelect.selectedIndex = i;
                break;
            }
        }
    }
}

// Función para editar un capítulo
function editarCapitulo(id, numero, descripcion) {
    const formEditarCapitulo = document.getElementById('formEditarCapitulo');
    const editarDescripcionInput = document.getElementById('editar_descripcion');
    
    if (formEditarCapitulo && editarDescripcionInput) {
        formEditarCapitulo.action = `/presupuestos/capitulo/editar/${id}`;
        editarDescripcionInput.value = descripcion;
        
        const modal = new bootstrap.Modal(document.getElementById('editarCapituloModal'));
        modal.show();
    }
}

// Función para preparar el envío del formulario de nueva partida
function prepararEnvioNuevaPartida(event, capitulo_numero) {
    console.log(`Preparando envío para nueva partida del capítulo ${capitulo_numero}`);
    
    // Encontrar el formulario correcto
    const form = document.getElementById(`form-nueva-partida-${capitulo_numero}`);
    if (!form) {
        console.error(`No se encontró el formulario para el capítulo ${capitulo_numero}`);
        alert('Error: No se encontró el formulario de la partida');
        return;
    }
    
    // Recopilar todos los datos del formulario
    const unitario = form.querySelector('.nueva-unitario').value;
    const cantidad = form.querySelector('.nueva-cantidad').value;
    const precio = form.querySelector('.nueva-precio').value;
    const margen = form.querySelector('.nueva-margen').value;
    const csrfToken = form.querySelector('input[name="csrf_token"]').value;
    
    // Manejar el contenido del editor CKEditor
    const textareaId = `descripcion_${capitulo_numero}`;
    const textareaElement = document.getElementById(textareaId);
    
    let descripcion = '';
    if (textareaElement && textareaElement._ckeditor) {
        try {
            descripcion = textareaElement._ckeditor.getData();
            console.log('Contenido del editor CKEditor obtenido');
        } catch (error) {
            console.error('Error al obtener datos del CKEditor:', error);
            // Intentar con el contenido directo del textarea como fallback
            descripcion = textareaElement.value || '<p>Sin descripción</p>';
            console.log('Fallback: Usando contenido directo del textarea');
        }
    } else if (textareaElement) {
        descripcion = textareaElement.value || '<p>Sin descripción</p>';
        console.log('Usando valor directo del textarea');
    } else {
        descripcion = '<p>Sin descripción</p>';
        console.log('No se encontró el textarea, usando valor por defecto');
    }
    
    // Crear formData para el envío
    const formData = new FormData();
    formData.append('csrf_token', csrfToken);
    formData.append('capitulo_numero', capitulo_numero);
    formData.append('descripcion', descripcion);
    formData.append('unitario', unitario);
    formData.append('cantidad', cantidad);
    formData.append('precio', precio);
    formData.append('margen', margen);
    
    console.log('Datos del formulario preparados para enviar');
    console.log('URL de destino:', form.action);
    
    // Mostrar loader o mensaje de espera
    const loadingMessage = document.createElement('div');
    loadingMessage.className = 'alert alert-info mt-2';
    loadingMessage.innerHTML = '<strong>Guardando partida...</strong> Por favor espere.';
    form.appendChild(loadingMessage);
    
    // Enviar mediante fetch
    fetch(form.action, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
    })
    .then(response => {
        console.log('Respuesta recibida:', response.status);
        if (!response.ok) {
            throw new Error(`Error en la respuesta del servidor: ${response.status} ${response.statusText}`);
        }
        // Mostrar mensaje de éxito
        loadingMessage.className = 'alert alert-success mt-2';
        loadingMessage.innerHTML = '<strong>¡Partida guardada correctamente!</strong> Recargando página...';
        
        // Recargar la página después de un breve retraso
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    })
    .catch(error => {
        console.error('Error al enviar los datos:', error);
        // Mostrar mensaje de error
        loadingMessage.className = 'alert alert-danger mt-2';
        loadingMessage.innerHTML = `<strong>Error al guardar la partida:</strong> ${error.message}`;
        
        // Añadir botón para reintentar
        const retryButton = document.createElement('button');
        retryButton.type = 'button';
        retryButton.className = 'btn btn-sm btn-warning mt-2';
        retryButton.innerHTML = 'Reintentar';
        retryButton.onclick = () => prepararEnvioNuevaPartida(event, capitulo_numero);
        loadingMessage.appendChild(retryButton);
    });
}

// Función para editar una partida en el modal
function editarPartida(id, capitulo_numero, numero, descripcion, unitario, cantidad, precio, margen) {
    const formEditarPartida = document.getElementById('formEditarPartida');
    
    if (formEditarPartida) {
        formEditarPartida.action = `/presupuestos/partida/editar/${id}`;
        
        // Actualizar campos del formulario
        const capituloSelect = document.getElementById('editar_partida_capitulo');
        if (capituloSelect) {
            // Seleccionar capítulo
            for (let i = 0; i < capituloSelect.options.length; i++) {
                if (capituloSelect.options[i].value === capitulo_numero) {
                    capituloSelect.selectedIndex = i;
                    break;
                }
            }
        }
        
        // Actualizar resto de campos
        document.getElementById('editar_partida_numero_display').value = numero || (capitulo_numero + '.?');
        document.getElementById('editar_partida_numero').value = numero;
        document.getElementById('editar_partida_descripcion').value = descripcion;
        document.getElementById('editar_partida_unitario').value = unitario;
        document.getElementById('editar_partida_cantidad').value = cantidad;
        document.getElementById('editar_partida_precio').value = precio;
        document.getElementById('editar_partida_margen').value = margen;
        
        // Calcular total y final
        calcularTotalEditar();
        
        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('editarPartidaModal'));
        modal.show();
    }
}
