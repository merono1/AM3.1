/**
 * Sistema mejorado para gestión de proveedores en hojas de trabajo
 */

// Variable global para almacenar opciones de proveedores
let proveedoresOpcionesGlobal = '';

document.addEventListener('DOMContentLoaded', function() {
    // Cargar proveedores disponibles
    cargarProveedoresGlobal();
    
    // Configurar botones de proveedores
    configurarBotonesProveedores();
    
    // Inicializar campos de proveedores existentes
    inicializarCamposProveedores();
});

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
                actualizarSelectoresProveedores();
            }
        })
        .catch(error => console.error('Error al cargar proveedores:', error));
}

// Función para actualizar todos los selectores de proveedores
function actualizarSelectoresProveedores() {
    // Actualizar selectores principales
    document.querySelectorAll('.proveedor-select').forEach(select => {
        const valorActual = select.value;
        select.innerHTML = `<option value="">Seleccione proveedor</option>${proveedoresOpcionesGlobal}`;
        if (valorActual) {
            select.value = valorActual;
        }
        select.disabled = false;
    });
    
    // Actualizar selectores para nuevos proveedores
    document.querySelectorAll('[id^="nuevo_proveedor_"]').forEach(select => {
        select.innerHTML = `<option value="">Seleccione proveedor</option>${proveedoresOpcionesGlobal}`;
    });
}

// Función para configurar los botones de proveedores
function configurarBotonesProveedores() {
    // Configurar botón principal de proveedores
    document.querySelectorAll('.btn-proveedores').forEach(btn => {
        btn.removeEventListener('click', window.location);
        btn.setAttribute('onclick', '');
        
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const partidaId = this.getAttribute('data-partida-id');
            if (partidaId) {
                togglePanelProveedores(partidaId);
            }
        });
    });
    
    // Configurar botón secundario de proveedores
    document.querySelectorAll('.btn-proveedores-adicionales').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const partidaId = this.getAttribute('data-partida-id');
            if (partidaId) {
                togglePanelProveedores(partidaId);
            }
        });
    });
}

// Función para mostrar/ocultar el panel de proveedores
function togglePanelProveedores(partidaId) {
    // Verificar si es un ID temporal (negativo)
    if (parseInt(partidaId) < 0) {
        alert('Debe guardar la hoja de trabajo primero para poder gestionar proveedores.');
        return;
    }
    
    const container = document.getElementById(`proveedores_container_${partidaId}`);
    const button = document.querySelector(`.btn-proveedores[data-partida-id="${partidaId}"]`);
    
    if (container && button) {
        if (container.style.display === 'none' || !container.style.display) {
            // Mostrar el panel
            container.style.display = 'block';
            button.classList.remove('btn-info');
            button.classList.add('btn-primary');
            
            // Cargar los proveedores
            cargarProveedoresPartida(partidaId);
        } else {
            // Ocultar el panel
            container.style.display = 'none';
            button.classList.remove('btn-primary');
            button.classList.add('btn-info');
        }
    }
}

// Función para inicializar los campos de proveedores
function inicializarCamposProveedores() {
    // Configurar cálculo de margen real
    document.querySelectorAll('.proveedor-precio').forEach(input => {
        actualizarMargenReal(input);
        input.addEventListener('input', function() {
            actualizarMargenReal(this);
        });
        input.disabled = false;
    });
}

// Función para cargar los proveedores de una partida específica
function cargarProveedoresPartida(partidaId) {
    const tbody = document.getElementById(`proveedores_tbody_${partidaId}`);
    
    if (!tbody) return;
    
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
                    let margenReal = calcularMargenReal(partidaId, proveedor.precio);
                    
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

// Función para calcular el margen real
function calcularMargenReal(partidaId, precioProveedor) {
    let margenReal = 0;
    const partida = document.querySelector(`.partida[data-partida-id="${partidaId}"]`);
    
    if (partida) {
        // Buscar todos los campos posibles que pueden contener el valor final
        const finalInput = partida.querySelector('input[name*="[final]"]') || 
                          partida.querySelector('input[id*="final_"]');
        
        const final = parseFloat(finalInput?.value) || 0;
        const precio = parseFloat(precioProveedor) || 0;
        
        if (precio > 0) {
            margenReal = ((final / precio) - 1) * 100;
        }
    }
    
    return margenReal;
}

// Función para agregar un nuevo proveedor
function agregarProveedor(partidaId) {
    const proveedorSelect = document.getElementById(`nuevo_proveedor_${partidaId}`);
    const precioInput = document.getElementById(`nuevo_precio_${partidaId}`);
    const principalCheck = document.getElementById(`nuevo_principal_${partidaId}`);
    
    if (!proveedorSelect || !precioInput) return;
    
    // Verificar si es un ID temporal (negativo)
    if (parseInt(partidaId) < 0) {
        alert('Debe guardar la hoja de trabajo primero para poder asignar proveedores a esta partida.');
        return;
    }
    
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
    
    // Obtener unitario y cantidad específicos de esta partida
    const partida = document.querySelector(`.partida[data-partida-id="${partidaId}"]`);
    let unitario = 'UD';
    let cantidad = 1;
    
    if (partida) {
        const unitarioSelect = partida.querySelector('select[name*="[unitario]"]');
        const cantidadInput = partida.querySelector('input[name*="[cantidad]"]');
        
        if (unitarioSelect) unitario = unitarioSelect.value;
        if (cantidadInput) cantidad = cantidadInput.value || 1;
    }
    
    formData.append('unitario', unitario);
    formData.append('cantidad', cantidad);
    formData.append('precio', precio || 0);
    formData.append('margen_proveedor', 0); // Valor por defecto
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
            const margenReal = calcularMargenReal(partidaId, nuevoPrecio);
            
            // Actualizar el margen real en la tabla
            const margenRealCell = row.querySelector('td:nth-child(3)');
            if (margenRealCell) {
                margenRealCell.textContent = margenReal.toFixed(2) + '%';
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
    const partida = document.querySelector(`.partida[data-partida-id="${partidaId}"]`);
    if (!partida) return;
    
    // Actualizar el selector de proveedor principal
    const proveedorSelect = partida.querySelector('.proveedor-select');
    if (proveedorSelect) {
        proveedorSelect.value = proveedorId;
        proveedorSelect.setAttribute('data-proveedor-id', proveedorId);
    }
    
    // Actualizar el precio del proveedor
    const precioInput = partida.querySelector('.proveedor-precio');
    if (precioInput) {
        precioInput.value = precio || 0;
        actualizarMargenReal(precioInput);
    }
}

// Función para calcular y actualizar el margen real
function actualizarMargenReal(input) {
    const partida = input.closest('.partida');
    if (!partida) return;
    
    // Buscar campos de manera más flexible
    const finalInput = partida.querySelector('input[name*="[final]"]') ||
                      partida.querySelector('input[id*="final_"]');
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
