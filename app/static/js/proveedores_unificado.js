/**
 * Sistema unificado para gestión de proveedores en hojas de trabajo
 * Combina la funcionalidad de proveedores_mejorado.js y proveedores_mejoras.js
 * en un único archivo optimizado.
 */

// Variable global para almacenar opciones de proveedores (con caché)
let proveedoresOpcionesGlobal = '';
let proveedoresCargados = false;

// Configuración global
const config = {
    expandirTodos: false,                 // Expandir todos los contenedores al cargar
    expandirConProveedores: true,         // Expandir solo contenedores con proveedores
    expandirSiError: true,                // Expandir si hay errores en el formulario
    mostrarBadgeSiempre: true,            // Mostrar el contador incluso si hay 0 proveedores
    badgeZeroClass: 'bg-secondary',       // Clase para el badge cuando hay 0 proveedores
    badgeClass: 'bg-danger',              // Clase para el badge cuando hay proveedores
    textoBoton: 'Proveedores',            // Texto base del botón
    usarLocalStorage: true,               // Usar localStorage para persistir estado
    usarCache: true                       // Usar caché para proveedores
};

// Inicialización principal - se ejecuta una vez al cargar el DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando sistema de proveedores unificado...');
    
    // Carga inicial de proveedores (optimizada con caché)
    cargarProveedoresGlobal();
    
    // Inicializar interfaz de usuario
    inicializarUI();
    
    // Persistir estados usando localStorage
    if (config.usarLocalStorage) {
        persistirEstadoExpansion();
    }
    
    // Añadir estilos CSS necesarios
    agregarEstilosCSS();
    
    // Preparar envío del formulario
    prepararEnvioFormulario();
});

// Función para cargar todos los proveedores disponibles (con caché)
function cargarProveedoresGlobal() {
    // Verificar si ya están cargados para evitar llamadas innecesarias
    if (proveedoresCargados && proveedoresOpcionesGlobal) {
        console.log('Usando proveedores en caché');
        actualizarSelectoresProveedores();
        return;
    }
    
    console.log('Cargando proveedores desde API...');
    fetch('/api/proveedores/listar')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.proveedores) {
                // Crear las opciones de proveedores
                proveedoresOpcionesGlobal = data.proveedores.map(prov => 
                    `<option value="${prov.id}">${prov.nombre} ${prov.especialidad ? '(' + prov.especialidad + ')' : ''}</option>`
                ).join('');
                
                // Marcar como cargados para caché
                proveedoresCargados = true;
                
                // Actualizar todos los selectores existentes
                actualizarSelectoresProveedores();
                
                // Inicializar contadores después de cargar proveedores
                actualizarContadoresProveedores();
            }
        })
        .catch(error => {
            console.error('Error al cargar proveedores:', error);
            // Intentar usar datos en localStorage como fallback si existen
            const cachedProveedores = localStorage.getItem('proveedoresCache');
            if (cachedProveedores) {
                proveedoresOpcionesGlobal = cachedProveedores;
                actualizarSelectoresProveedores();
            }
        });
}

// Función para actualizar todos los selectores de proveedores
function actualizarSelectoresProveedores() {
    // Guardar caché en localStorage para uso futuro
    if (config.usarCache && proveedoresOpcionesGlobal) {
        try {
            localStorage.setItem('proveedoresCache', proveedoresOpcionesGlobal);
        } catch (e) {
            console.warn('No se pudo guardar caché en localStorage:', e);
        }
    }

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

// Inicializar toda la interfaz de usuario
function inicializarUI() {
    // Configurar botones de proveedores
    configurarBotonesProveedores();
    
    // Inicializar campos de proveedores existentes
    inicializarCamposProveedores();
    
    // Expandir automáticamente algunos contenedores según configuración
    expandirAutomaticamente();
}

// Función para configurar los botones de proveedores
function configurarBotonesProveedores() {
    // Configurar botón principal de proveedores
    document.querySelectorAll('.btn-proveedores').forEach(btn => {
        // Limpiar eventos existentes
        const nuevoBtn = btn.cloneNode(true);
        if (btn.parentNode) {
            btn.parentNode.replaceChild(nuevoBtn, btn);
        }
        
        nuevoBtn.addEventListener('click', function(e) {
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
            
            // Guardar estado en localStorage si está habilitado
            if (config.usarLocalStorage) {
                try {
                    localStorage.setItem(`panelProveedores_${partidaId}`, 'abierto');
                } catch (e) {
                    console.warn('Error al guardar estado en localStorage:', e);
                }
            }
        } else {
            // Ocultar el panel
            container.style.display = 'none';
            button.classList.remove('btn-primary');
            button.classList.add('btn-info');
            
            // Guardar estado en localStorage
            if (config.usarLocalStorage) {
                try {
                    localStorage.setItem(`panelProveedores_${partidaId}`, 'cerrado');
                } catch (e) {
                    console.warn('Error al guardar estado en localStorage:', e);
                }
            }
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
    
    // Mostrar indicador de carga
    const addBtn = precioInput.closest('tr').querySelector('button');
    if (addBtn) {
        const originalText = addBtn.innerHTML;
        addBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Agregando...';
        addBtn.disabled = true;
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
            
            // Restaurar botón
            if (addBtn) {
                addBtn.innerHTML = '<i class="fas fa-plus"></i> Agregar';
                addBtn.disabled = false;
            }
            
            // Actualizar la lista de proveedores
            cargarProveedoresPartida(partidaId);
            
            // Si es principal, actualizar el selector principal
            if (esPrincipal) {
                actualizarProveedorPrincipal(partidaId, proveedorId, precio);
            }
            
            // Actualizar contador de proveedores
            actualizarContadoresProveedores();
        } else {
            // Restaurar botón
            if (addBtn) {
                addBtn.innerHTML = '<i class="fas fa-plus"></i> Agregar';
                addBtn.disabled = false;
            }
            alert('Error al agregar proveedor: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error al agregar proveedor:', error);
        // Restaurar botón
        if (addBtn) {
            addBtn.innerHTML = '<i class="fas fa-plus"></i> Agregar';
            addBtn.disabled = false;
        }
        alert('Error de conexión');
    });
}

// Función para cargar los proveedores de una partida específica
function cargarProveedoresPartida(partidaId) {
    const tbody = document.getElementById(`proveedores_tbody_${partidaId}`);
    
    if (!tbody) return;
    
    // Mensaje de carga
    tbody.innerHTML = '<tr><td colspan="5" class="text-center"><i class="fas fa-spinner fa-spin"></i> Cargando proveedores...</td></tr>';
    
    // Cargar proveedores asignados
    fetch(`/api/proveedores-partidas/por-partida/${partidaId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                tbody.innerHTML = '';
                
                if (!data.proveedores || data.proveedores.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" class="text-center">No hay proveedores asignados a esta partida.</td></tr>';
                    // Actualizar contador a cero
                    actualizarContadorPartida(partidaId, 0);
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
                    
                    tr.setAttribute('data-proveedor-partida-id', proveedor.id);
                    tr.innerHTML = `
                        <td>${proveedor.nombre_proveedor} ${proveedor.especialidad ? '(' + proveedor.especialidad + ')' : ''}</td>
                        <td>
                            <input type="number" step="any" class="form-control form-control-sm precio-proveedor-input" 
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
                
                // Actualizar contador con número real
                actualizarContadorPartida(partidaId, data.proveedores.length);
            } else {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Error al cargar proveedores.</td></tr>';
                actualizarContadorPartida(partidaId, 0);
            }
        })
        .catch(error => {
            console.error('Error al cargar proveedores:', error);
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Error de conexión al cargar proveedores.</td></tr>';
            actualizarContadorPartida(partidaId, 0);
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
            // El recuento se actualizará dentro de cargarProveedoresPartida
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
    if (!input) return;
    
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

// Función para calcular el margen real (versión para tabla de proveedores)
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

// Actualizar contador para una partida específica
function actualizarContadorPartida(partidaId, numProveedores) {
    const botonToggle = document.querySelector(`.btn-proveedores[data-partida-id="${partidaId}"]`);
    if (!botonToggle) return;
    
    // Eliminar contador existente
    const contadorExistente = botonToggle.querySelector('.contador-proveedores');
    if (contadorExistente) {
        contadorExistente.remove();
    }
    
    // Crear nuevo contador si hay proveedores o si se debe mostrar siempre
    if (numProveedores > 0 || config.mostrarBadgeSiempre) {
        const badgeClass = numProveedores > 0 ? config.badgeClass : config.badgeZeroClass;
        
        // Crear el contador
        const contador = document.createElement('span');
        contador.className = `contador-proveedores badge ${badgeClass} ms-1`;
        contador.innerText = numProveedores;
        
        // Insertar antes del icono o al final
        const caret = botonToggle.querySelector('i.fas');
        if (caret) {
            botonToggle.insertBefore(contador, caret);
        } else {
            botonToggle.appendChild(contador);
        }
    }
}

// Función para actualizar los contadores de proveedores en todos los botones
function actualizarContadoresProveedores() {
    const contenedores = document.querySelectorAll('[id^="proveedores_container_"]');
    
    // Para cada contenedor, contar los proveedores y actualizar el contador
    contenedores.forEach(container => {
        const partidaId = container.id.replace('proveedores_container_', '');
        const tabla = container.querySelector('table');
        if (!tabla) return;
        
        const filas = tabla.querySelectorAll('tbody tr');
        const numProveedores = filas.length;
        
        // No contar la fila de "No hay proveedores"
        const numProveedoresReal = filas[0]?.cells[0]?.colSpan === 5 ? 0 : numProveedores;
        
        actualizarContadorPartida(partidaId, numProveedoresReal);
    });
}

// Función para mantener el estado de expansión/contracción 
function persistirEstadoExpansion() {
    // Verificar si localStorage está disponible
    if (typeof localStorage === 'undefined') return;
    
    // Clave única basada en la URL actual para almacenar estados
    const storageKey = `hojaTrabajoExpansion_${window.location.pathname}`;
    
    // Al cargar la página, restaurar estados previos
    try {
        // Recorrer todos los contenedores y restaurar sus estados
        document.querySelectorAll('[id^="proveedores_container_"]').forEach(container => {
            const partidaId = container.id.replace('proveedores_container_', '');
            const estadoGuardado = localStorage.getItem(`panelProveedores_${partidaId}`);
            
            if (estadoGuardado === 'abierto') {
                // Mostrar contenedor
                container.style.display = 'block';
                
                // Actualizar botón
                const btn = document.querySelector(`.btn-proveedores[data-partida-id="${partidaId}"]`);
                if (btn) {
                    btn.classList.remove('btn-info');
                    btn.classList.add('btn-primary');
                }
                
                // Cargar proveedores
                cargarProveedoresPartida(partidaId);
            }
        });
    } catch (error) {
        console.error('Error al restaurar estados:', error);
    }
}

// Función para expandir automáticamente los proveedores con estados guardados
function expandirAutomaticamente() {
    // Recorrer todos los contenedores
    document.querySelectorAll('[id^="proveedores_container_"]').forEach(container => {
        const partidaId = container.id.replace('proveedores_container_', '');
        const btn = document.querySelector(`.btn-proveedores[data-partida-id="${partidaId}"]`);
        
        // Determinar si debe expandirse automáticamente
        let debeExpandirse = config.expandirTodos;
        
        // Si hay proveedores y la configuración lo permite
        if (config.expandirConProveedores) {
            // Verificar si hay proveedores (este es un heurístico, no consulta la API)
            const proveedorSelect = document.querySelector(`[name="proveedor_ids[${partidaId}]"]`);
            if (proveedorSelect && proveedorSelect.value) {
                debeExpandirse = true;
            }
        }
        
        // Si hay errores y la configuración lo permite
        if (config.expandirSiError && container.querySelector('.is-invalid')) {
            debeExpandirse = true;
        }
        
        // Expandir si cumple las condiciones y no está ya expandido
        if (debeExpandirse && container.style.display !== 'block') {
            container.style.display = 'block';
            if (btn) {
                btn.classList.remove('btn-info');
                btn.classList.add('btn-primary');
            }
            
            // Cargar proveedores
            cargarProveedoresPartida(partidaId);
            
            // Guardar estado
            if (config.usarLocalStorage) {
                try {
                    localStorage.setItem(`panelProveedores_${partidaId}`, 'abierto');
                } catch (e) {
                    console.warn('Error al guardar estado:', e);
                }
            }
        }
    });
}

// Función para agregar estilos CSS necesarios
function agregarEstilosCSS() {
    // Si ya existe, no agregar de nuevo
    if (document.getElementById('proveedores-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'proveedores-styles';
    style.textContent = `
        /* Estilos para el contador de proveedores */
        .contador-proveedores {
            font-size: 0.75rem;
            border-radius: 0.625rem;
            padding: 0.25rem 0.5rem;
            font-weight: bold;
        }
        
        /* Destacar sección de proveedores */
        .proveedores-inline-container {
            transition: background-color 0.3s ease;
        }
        
        .proveedores-inline-container.highlight {
            animation: highlight 1s ease-out;
        }
        
        @keyframes highlight {
            0% { background-color: rgba(255, 220, 200, 0.3); }
            100% { background-color: transparent; }
        }
        
        /* Mejoras de estilos para tablas de proveedores */
        [id^="proveedores_tbody_"] tr {
            transition: background-color 0.2s ease;
        }
        
        /* Estilos para mejorar compacidad */
        .table-sm td {
            padding: 0.3rem 0.5rem;
        }
        
        /* Arreglo para alineación vertical */
        .partida-detail-item {
            display: flex;
            align-items: center;
            margin-bottom: 0.25rem;
        }
        
        .partida-detail-label {
            min-width: 120px;
            font-weight: 500;
        }
    `;
    
    document.head.appendChild(style);
}

// Función para preparar el envío del formulario
function prepararEnvioFormulario() {
    const form = document.querySelector('form');
    if (!form) return;
    
    form.addEventListener('submit', function() {
        // Guardar estado de los proveedores
        document.querySelectorAll('[id^="proveedores_container_"]').forEach(container => {
            const partidaId = container.id.replace('proveedores_container_', '');
            const estaAbierto = container.style.display === 'block';
            
            if (config.usarLocalStorage) {
                try {
                    localStorage.setItem(`panelProveedores_${partidaId}`, estaAbierto ? 'abierto' : 'cerrado');
                } catch (e) {
                    console.warn('Error al guardar estado:', e);
                }
            }
        });
    });
}