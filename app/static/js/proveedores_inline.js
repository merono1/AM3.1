/**
 * Código para gestionar proveedores inline en la página de hojas de trabajo
 */

// Cuando el documento está listo
document.addEventListener('DOMContentLoaded', function() {
    // Cargar proveedores automáticamente para todas las partidas
    document.querySelectorAll('.proveedores-inline-container').forEach(container => {
        const partidaId = container.id.replace('proveedores_container_', '');
        if (partidaId) {
            cargarProveedoresPartida(partidaId);
        }
    });
    
    // Calcular los márgenes reales iniciales
    document.querySelectorAll('.proveedor-precio').forEach(input => {
        actualizarMargenReal(input);
        input.addEventListener('input', function() {
            actualizarMargenReal(this);
        });
    });
});

// Función para cargar el contenedor de proveedores (modificada para siempre visible)
function toggleProveedoresContainer(partidaId) {
    const container = document.getElementById(`proveedores_container_${partidaId}`);
    
    if (container) {
        // Cargar los proveedores siempre
        cargarProveedoresPartida(partidaId);
    }
}

// Variable global para almacenar opciones de proveedores
let proveedoresOpcionesGlobal = '';

// Función para cargar todos los proveedores disponibles
function cargarProveedoresGlobal() {
    fetch('/api/proveedores/listar')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.proveedores) {
                // Crear las opciones de proveedores
                proveedoresOpcionesGlobal = data.proveedores.map(prov => 
                    `<option value="${prov.id}">${prov.nombre} ${prov.especialidad ? '(' + prov.especialidad + ')' : ''}</option>`
                ).join('');
                
                // Actualizar todos los selectores existentes
                document.querySelectorAll('[id^="nuevo_proveedor_"]').forEach(select => {
                    select.innerHTML = `<option value="">Seleccione proveedor</option>${proveedoresOpcionesGlobal}`;
                });
            }
        })
        .catch(error => console.error('Error al cargar proveedores:', error));
}

// Función para cargar los proveedores de una partida
function cargarProveedoresPartida(partidaId) {
    const tbody = document.getElementById(`proveedores_tbody_${partidaId}`);
    const selectNuevoProveedor = document.getElementById(`nuevo_proveedor_${partidaId}`);
    
    if (!tbody) return;
    
    // Cargar opciones de proveedores si es necesario
    if (proveedoresOpcionesGlobal === '') {
        cargarProveedoresGlobal();
    } else if (selectNuevoProveedor && selectNuevoProveedor.options.length <= 1) {
        selectNuevoProveedor.innerHTML = `<option value="">Seleccione proveedor</option>${proveedoresOpcionesGlobal}`;
    }
    
    // Mensaje de carga
    tbody.innerHTML = '<tr><td colspan="5" class="text-center">Cargando proveedores...</td></tr>';
    
    // Cargar proveedores asignados
    fetch(`/api/proveedores-partidas/por-partida/${partidaId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                tbody.innerHTML = '';
                
                if (!data.proveedores || data.proveedores.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" class="text-center">No hay proveedores asignados a esta partida.</td></tr>';
                    return;
                }
                
                // Mostrar cada proveedor
                data.proveedores.forEach(proveedor => {
                    const tr = document.createElement('tr');
                    if (proveedor.es_principal) {
                        tr.classList.add('table-warning');
                    }
                    
                    // Calcular el margen real
                    const partida = document.querySelector(`.partida[data-partida-id="${partidaId}"]`);
                    let margenReal = 0;
                    if (partida) {
                        const final = parseFloat(partida.querySelector('input[name*="[final]"]')?.value) || 0;
                        const precio = parseFloat(proveedor.precio) || 0;
                        if (precio > 0) {
                            margenReal = ((final / precio) - 1) * 100;
                        }
                    }
                    
                    tr.innerHTML = `
                        <td>${proveedor.nombre_proveedor} ${proveedor.especialidad ? '(' + proveedor.especialidad + ')' : ''}</td>
                        <td>
                            <input type="number" step="any" class="form-control form-control-sm" 
                                   value="${proveedor.precio || 0}" 
                                   data-original="${proveedor.precio || 0}"
                                   data-proveedor-id="${proveedor.id_proveedor}"
                                   onchange="guardarCambiosProveedor(this, ${partidaId}, ${proveedor.id})">
                        </td>
                        <td class="text-center">${margenReal.toFixed(2)}%</td>
                        <td class="text-center">
                            <input type="checkbox" class="form-check-input" 
                                   ${proveedor.es_principal ? 'checked' : ''} 
                                   onchange="establecerProveedorPrincipal(this, ${partidaId}, ${proveedor.id_proveedor})">
                        </td>
                        <td class="text-center">
                            <button type="button" class="btn btn-sm btn-outline-danger" 
                                    onclick="eliminarProveedor(${partidaId}, ${proveedor.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    `;
                    
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Error al cargar proveedores.</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error al cargar proveedores:', error);
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Error de conexión al cargar proveedores.</td></tr>';
        });
}

// Función para agregar un nuevo proveedor
function agregarProveedor(partidaId) {
    const proveedorSelect = document.getElementById(`nuevo_proveedor_${partidaId}`);
    const precioInput = document.getElementById(`nuevo_precio_${partidaId}`);
    const principalCheck = document.getElementById(`nuevo_principal_${partidaId}`);
    
    if (!proveedorSelect || !precioInput) return;
    
    const proveedorId = proveedorSelect.value;
    const precio = precioInput.value;
    const esPrincipal = principalCheck && principalCheck.checked;
    
    if (!proveedorId) {
        alert('Por favor seleccione un proveedor');
        return;
    }
    
    // Preparar datos
    const formData = new FormData();
    formData.append('id_partida', partidaId);
    formData.append('id_proveedor', proveedorId);
    formData.append('unitario', 'UD'); // Valor por defecto
    formData.append('cantidad', 1);
    formData.append('precio', precio || 0);
    formData.append('es_principal', esPrincipal ? 'true' : 'false');
    
    // Enviar a la API
    fetch('/api/proveedores-partidas/asignar', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Limpiar el formulario
            proveedorSelect.value = '';
            precioInput.value = '';
            if (principalCheck) principalCheck.checked = false;
            
            // Actualizar la lista de proveedores
            cargarProveedoresPartida(partidaId);
            
            // Si es principal, actualizar el selector principal
            if (esPrincipal) {
                actualizarProveedorPrincipal(partidaId, proveedorId, precio);
            }
        } else {
            alert('Error al agregar proveedor: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error al agregar proveedor:', error);
        alert('Error de conexión');
    });
}

// Función para guardar cambios de un proveedor existente
function guardarCambiosProveedor(input, partidaId, proveedorPartidaId) {
    const nuevoPrecio = input.value || 0;
    const originalPrecio = input.getAttribute('data-original');
    
    if (nuevoPrecio === originalPrecio) return;
    
    // Preparar datos
    const formData = new FormData();
    formData.append('precio', nuevoPrecio);
    
    // Enviar a la API
    fetch(`/api/proveedores-partidas/actualizar/${proveedorPartidaId}`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Actualizar el valor original
            input.setAttribute('data-original', nuevoPrecio);
            
            // Verificar si es el proveedor principal
            const row = input.closest('tr');
            const isPrincipal = row.querySelector('input[type="checkbox"]')?.checked;
            
            if (isPrincipal) {
                // Actualizar el input de precio en la partida
                const proveedorId = input.getAttribute('data-proveedor-id');
                actualizarProveedorPrincipal(partidaId, proveedorId, nuevoPrecio);
            }
            
            // Recalcular margen real
            const partida = document.querySelector(`.partida[data-partida-id="${partidaId}"]`);
            if (partida) {
                const final = parseFloat(partida.querySelector('input[name*="[final]"]')?.value) || 0;
                const precio = parseFloat(nuevoPrecio) || 0;
                let margenReal = 0;
                if (precio > 0) {
                    margenReal = ((final / precio) - 1) * 100;
                }
                
                // Actualizar el margen real en la tabla
                const margenRealCell = row.querySelector('td:nth-child(3)');
                if (margenRealCell) {
                    margenRealCell.textContent = margenReal.toFixed(2) + '%';
                }
            }
        } else {
            // Restaurar valor original en caso de error
            input.value = originalPrecio;
            alert('Error al guardar cambios: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error al guardar cambios:', error);
        input.value = originalPrecio;
        alert('Error de conexión');
    });
}

// Función para establecer un proveedor como principal
function establecerProveedorPrincipal(checkbox, partidaId, proveedorId) {
    // Si el checkbox está desmarcado, no hacer nada
    if (!checkbox.checked) {
        checkbox.checked = true;
        return;
    }
    
    // Preparar datos
    const formData = new FormData();
    formData.append('id_partida', partidaId);
    formData.append('id_proveedor', proveedorId);
    
    // Enviar a la API
    fetch('/api/proveedores-partidas/establecer-principal', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Desmarcar otros checkboxes
            const tbody = checkbox.closest('tbody');
            tbody.querySelectorAll('input[type="checkbox"]').forEach(cb => {
                if (cb !== checkbox) cb.checked = false;
            });
            
            // Actualizar estilos
            tbody.querySelectorAll('tr').forEach(row => {
                if (row.contains(checkbox)) {
                    row.classList.add('table-warning');
                } else {
                    row.classList.remove('table-warning');
                }
            });
            
            // Actualizar el precio del proveedor principal
            const row = checkbox.closest('tr');
            const precioInput = row.querySelector('input[type="number"]');
            if (precioInput) {
                actualizarProveedorPrincipal(partidaId, proveedorId, precioInput.value);
            }
        } else {
            checkbox.checked = false;
            alert('Error al establecer proveedor principal: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error al establecer proveedor principal:', error);
        checkbox.checked = false;
        alert('Error de conexión');
    });
}

// Función para eliminar un proveedor
function eliminarProveedor(partidaId, proveedorPartidaId) {
    if (!confirm('¿Está seguro de eliminar este proveedor?')) return;
    
    fetch(`/api/proveedores-partidas/eliminar/${proveedorPartidaId}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cargarProveedoresPartida(partidaId);
        } else {
            alert('Error al eliminar proveedor: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error al eliminar proveedor:', error);
        alert('Error de conexión');
    });
}

// Función para actualizar el proveedor principal en la partida
function actualizarProveedorPrincipal(partidaId, proveedorId, precio) {
    // Buscar los campos ocultos de proveedor principal en la partida
    const partida = document.querySelector(`.partida[data-partida-id="${partidaId}"]`);
    if (!partida) return;
    
    // Actualizar los campos ocultos
    const idProveedorInput = partida.querySelector('input[name*="[id_proveedor]"]');
    const precioProveedorInput = partida.querySelector('input[name*="[precio_proveedor]"]');
    
    if (idProveedorInput) {
        idProveedorInput.value = proveedorId;
    }
    
    if (precioProveedorInput) {
        precioProveedorInput.value = precio || 0;
    }
}

// Función para calcular y actualizar el margen real
function actualizarMargenReal(input) {
    const partida = input.closest('.partida');
    if (!partida) return;
    
    const finalInput = partida.querySelector('input[name*="[final]"]');
    const margenRealDisplay = partida.querySelector('.margen-real-display');
    
    if (!finalInput || !margenRealDisplay) return;
    
    const final = parseFloat(finalInput.value) || 0;
    const precioProveedor = parseFloat(input.value) || 0;
    
    let margenReal = 0;
    if (precioProveedor > 0) {
        margenReal = ((final / precioProveedor) - 1) * 100;
    }
    
    margenRealDisplay.value = margenReal.toFixed(2);
}