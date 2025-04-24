/**
 * Archivo para manejar el modal de nueva partida
 */

// Variable global para almacenar la instancia del editor CK
let modalCKEditor = null;

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando módulo de modal para nueva partida...');
    
    // Inicializar CKEditor para el modal de nueva partida
    const modalDescripcion = document.getElementById('modal_descripcion');
    if (modalDescripcion && !modalDescripcion._ckeditor) {
        ClassicEditor
            .create(modalDescripcion, {
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
                modalCKEditor = editor; // Guardar en variable global
                modalDescripcion._ckeditor = editor;
                console.log('CKEditor 5 inicializado para el modal de nueva partida');
            })
            .catch(error => {
                console.error('Error al inicializar CKEditor para el modal:', error);
            });
    }
    
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
    
    // Manejar el clic en el botón de guardar partida
    const btnGuardarPartida = document.getElementById('btnGuardarPartida');
    if (btnGuardarPartida) {
        btnGuardarPartida.addEventListener('click', function() {
            console.log('Botón Guardar Partida clickeado');
            guardarNuevaPartida();
        });
    }
    
    // Manejar envío del formulario modal
    const formNuevaPartida = document.getElementById('formNuevaPartida');
    if (formNuevaPartida) {
        formNuevaPartida.addEventListener('submit', function(event) {
            event.preventDefault(); // Detener el envío normal del formulario
            guardarNuevaPartida();
        });
    }
});

// Función principal para guardar la partida
function guardarNuevaPartida() {
    console.log('Iniciando guardarNuevaPartida');
    const formNuevaPartida = document.getElementById('formNuevaPartida');
    if (!formNuevaPartida) {
        console.error('No se encontró el formulario formNuevaPartida');
        return;
    }
    
    // Obtener el contenido del editor CKEditor
    const modalDescripcion = document.getElementById('modal_descripcion');
    let descripcion = '';
    const hiddenDescripcion = document.getElementById('hidden_descripcion');
    
    if (modalCKEditor) {
        try {
            descripcion = modalCKEditor.getData();
            console.log('Contenido obtenido del editor CK:', descripcion);
            
            // Actualizar también el campo oculto
            if (hiddenDescripcion) {
                hiddenDescripcion.value = descripcion;
                console.log('Campo hidden actualizado con descripción de longitud:', descripcion.length);
            }
        } catch (error) {
            console.error('Error al obtener datos del CKEditor:', error);
            descripcion = '<p>Error al obtener descripción</p>';
        }
    } else if (modalDescripcion) {
        descripcion = modalDescripcion.value || '<p>Sin descripción</p>';
        console.log('Editor no disponible, usando valor directo del textarea');
    } else {
        descripcion = '<p>Sin descripción</p>';
        console.log('No se encontró el textarea, usando valor por defecto');
    }
    
    // Solo usar el campo oculto si está presente
    if (hiddenDescripcion) {
        console.log('Usando campo hidden para la descripción');
        // El campo hidden ya tiene el valor actualizado
    } else {
        console.log('Campo hidden no encontrado, enviando descripción directamente');
    }
    
    // Recopilar el resto de datos del formulario
    const formData = new FormData();
    formData.append('csrf_token', document.querySelector('input[name="csrf_token"]').value);
    formData.append('capitulo_numero', document.getElementById('nueva_partida_capitulo_numero').value);
    
    // Añadir el ID de la partida anterior si existe (para intercalar)
    const partidaAnteriorInput = document.getElementById('partida_anterior_id');
    if (partidaAnteriorInput) {
        formData.append('partida_anterior_id', partidaAnteriorInput.value);
        console.log('Añadiendo partida_anterior_id:', partidaAnteriorInput.value);
    }
    
    // Estrategia para enviar la descripción
    if (hiddenDescripcion) {
        // Si tenemos el campo oculto, la descripción ya está en él
        // Asegurarnos de que también se añada al FormData
        formData.append('descripcion', descripcion);
    } else {
        // Si no hay campo oculto, añadir directamente al FormData
        formData.append('descripcion', descripcion);
    }
    
    formData.append('unitario', document.getElementById('modal_unitario').value);
    formData.append('cantidad', document.getElementById('modal_cantidad').value);
    formData.append('precio', document.getElementById('modal_precio').value);
    formData.append('margen', document.getElementById('modal_margen').value);
    
    // Mostrar indicador de carga
    const modalBody = formNuevaPartida.querySelector('.modal-body');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'alert alert-info mt-3';
    loadingDiv.innerHTML = '<strong>Guardando partida...</strong> Por favor espere.';
    modalBody.appendChild(loadingDiv);
    
    // Deshabilitar botones mientras se procesa
    const submitBtn = document.getElementById('btnGuardarPartida');
    const cancelBtn = formNuevaPartida.querySelector('button[data-bs-dismiss="modal"]');
    if (submitBtn) submitBtn.disabled = true;
    if (cancelBtn) cancelBtn.disabled = true;
    
    console.log('Enviando datos del formulario modal a:', formNuevaPartida.action);
    
    // Enviar mediante fetch
    fetch(formNuevaPartida.action, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
    })
    .then(response => {
        console.log('Respuesta del servidor recibida:', response.status);
        if (!response.ok) {
            throw new Error(`Error en la respuesta del servidor: ${response.status}`);
        }
        console.log('Partida guardada exitosamente');
        // Mostrar mensaje de éxito antes de recargar
        loadingDiv.className = 'alert alert-success mt-3';
        loadingDiv.innerHTML = '<strong>¡Partida guardada correctamente!</strong> Recargando página...';
        
        // Recargar la página después de un breve retraso
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    })
    .catch(error => {
        console.error('Error al guardar partida:', error);
        loadingDiv.className = 'alert alert-danger mt-3';
        loadingDiv.innerHTML = `<strong>Error al guardar:</strong> ${error.message}`;
        if (submitBtn) submitBtn.disabled = false;
        if (cancelBtn) cancelBtn.disabled = false;
    });
}

// Variable para almacenar el ID de la partida después de la cual insertar (para inserción intercalada)
let partidaDespuesDeLaCual = null;

// Función para preparar el modal de nueva partida
function prepararModalNuevaPartida(capitulo_numero) {
    console.log('Preparando modal para nueva partida del capítulo:', capitulo_numero);
    
    // Resetear la variable de inserción intercalada
    partidaDespuesDeLaCual = null;
    
    // Cambiar el título del modal a "Nueva Partida"
    const modalTitle = document.getElementById('nuevaPartidaModalLabel');
    if (modalTitle) {
        modalTitle.textContent = 'Nueva Partida';
    }
    
    // Establecer el capítulo seleccionado
    document.getElementById('nueva_partida_capitulo_numero').value = capitulo_numero;
    
    // Inicializar o limpiar el editor
    if (modalCKEditor) {
        try {
            modalCKEditor.setData('');
            console.log('Editor CK limpiado correctamente');
        } catch (error) {
            console.error('Error al limpiar el editor CK:', error);
        }
    } else {
        console.warn('Editor CK no disponible al preparar modal');
        // Intentar recuperar la instancia si está disponible en el elemento
        const modalDescripcion = document.getElementById('modal_descripcion');
        if (modalDescripcion && modalDescripcion._ckeditor) {
            modalCKEditor = modalDescripcion._ckeditor;
            modalCKEditor.setData('');
            console.log('Editor CK recuperado y limpiado correctamente');
        }
    }
    
    // Restablecer valores por defecto
    document.getElementById('modal_unitario').value = 'Ud';
    document.getElementById('modal_cantidad').value = '1';
    document.getElementById('modal_precio').value = '0';
    document.getElementById('modal_margen').value = '40';
    
    // Eliminar el campo hidden de partida_anterior si existe
    const partidaAnteriorHidden = document.getElementById('partida_anterior_id');
    if (partidaAnteriorHidden) {
        partidaAnteriorHidden.remove();
    }
    
    // Calcular valores iniciales
    calcularTotalModal();
    calcularFinalModal();
}

// Función para preparar el modal de nueva partida intercalada
function prepararModalNuevaPartidaIntercalada(capitulo_numero, partida_id) {
    console.log('Preparando modal para nueva partida intercalada después de:', partida_id);
    
    // Establecer la partida después de la cual insertar
    partidaDespuesDeLaCual = partida_id;
    
    // Cambiar el título del modal a "Nueva Partida Intercalada"
    const modalTitle = document.getElementById('nuevaPartidaModalLabel');
    if (modalTitle) {
        modalTitle.textContent = 'Nueva Partida Intercalada';
    }
    
    // Primero hacer la preparación normal
    prepararModalNuevaPartida(capitulo_numero);
    
    // Añadir un campo oculto con el ID de la partida después de la cual insertar
    const form = document.getElementById('formNuevaPartida');
    if (form) {
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'partida_anterior_id';
        hiddenInput.id = 'partida_anterior_id';
        hiddenInput.value = partida_id;
        form.appendChild(hiddenInput);
    }
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
        finalCalc.innerHTML = `<strong>Total + Margen:</strong> ${final.toFixed(2).replace('.', ',')} €`;
    }
}