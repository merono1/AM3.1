/**
 * Mejora para agregar proveedores directamente en la tabla sin modal
 */

// Modificar la tabla para agregar una fila editable
function agregarFilaEditable() {
  // Buscar todas las tablas de proveedores
  document.querySelectorAll('table[id^="tablaProveedores_"]').forEach(tabla => {
    // Obtener el ID de partida del ID de la tabla
    const partidaId = tabla.id.replace('tablaProveedores_', '');
    
    // Obtener el pie de tabla (donde está el botón "Agregar Proveedor")
    const tfoot = tabla.querySelector('tfoot');
    if (!tfoot) return;
    
    // Buscar los proveedores directamente desde los selectores existentes
    let opcionesProveedores = '';
    const selectoresExistentes = document.querySelectorAll('.proveedor-select');
    if (selectoresExistentes.length > 0) {
      const selector = selectoresExistentes[0];
      opcionesProveedores = Array.from(selector.options)
        .map(opt => `<option value="${opt.value}">${opt.textContent}</option>`)
        .join('');
    }
    
    // Obtener las opciones de unidades desde el selector unitario de la partida
    let opcionesUnidades = '';
    const partida = document.querySelector(`.partida[data-partida-id="${partidaId}"]`);
    if (partida) {
      const selectorUnitario = partida.querySelector('select[name*="[unitario]"]');
      if (selectorUnitario) {
        opcionesUnidades = Array.from(selectorUnitario.options)
          .map(opt => `<option value="${opt.value}">${opt.textContent}</option>`)
          .join('');
      } else {
        // Opciones estándar si no se encuentra el selector
        opcionesUnidades = `
          <option value="">Seleccione</option>
          <option value="ML">ML</option>
          <option value="M2">M2</option>
          <option value="M3">M3</option>
          <option value="PA">PA</option>
          <option value="UD">UD</option>
        `;
      }
    }
    
    // Reemplazar el contenido del tfoot con una tabla que incluye todos los campos
    tfoot.innerHTML = `
      <tr class="nueva-fila-proveedor" data-partida-id="${partidaId}">
        <td>
          <select class="form-select form-select-sm nuevo-proveedor-select">
            ${opcionesProveedores}
          </select>
        </td>
        <td>
          <select class="form-select form-select-sm nuevo-unitario-select">
            ${opcionesUnidades}
          </select>
        </td>
        <td>
          <input type="number" step="any" class="form-control form-control-sm nuevo-cantidad-input" value="1">
        </td>
        <td>
          <input type="number" step="any" class="form-control form-control-sm nuevo-precio-input" value="0">
        </td>
        <td>
          <input type="number" step="any" class="form-control form-control-sm nuevo-total-display" value="0" readonly>
        </td>
        <td>
          <input type="number" step="any" class="form-control form-control-sm nuevo-margen-real-display" value="0" readonly>
        </td>
        <td class="text-center">
          <div class="btn-group btn-group-sm">
            <button type="button" class="btn btn-success guardar-nuevo-proveedor-btn" title="Guardar proveedor">
              <i class="fas fa-save"></i>
            </button>
            <button type="button" class="btn btn-outline-primary nuevo-principal-check" title="Establecer como principal">
              <i class="fas fa-star"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
    
    // Actualizar tabla de proveedores con las nuevas columnas
    const thead = tabla.querySelector('thead');
    if (thead) {
      const headerRow = thead.querySelector('tr');
      if (headerRow) {
        headerRow.innerHTML = `
          <th>Proveedor</th>
          <th>Unitario</th>
          <th>Cantidad</th>
          <th>Precio (€)</th>
          <th>Total (€)</th>
          <th>Margen Real (%)</th>
          <th>Acciones</th>
        `;
      }
    }
    
    // Actualizar filas existentes de proveedores para incluir nuevos campos
    const tbody = tabla.querySelector('tbody');
    if (tbody) {
      const filas = tbody.querySelectorAll('tr');
      filas.forEach(fila => {
        const celdas = fila.querySelectorAll('td');
        if (celdas.length === 5) { // Si tiene 5 celdas, agregar las nuevas
          const nombreProveedor = celdas[0].innerHTML;
          const precioInput = celdas[1].querySelector('input');
          const precio = precioInput ? precioInput.value : '0';
          
          fila.innerHTML = `
            <td>${nombreProveedor}</td>
            <td>
              <select class="form-select form-select-sm unitario-proveedor-select">
                ${opcionesUnidades}
              </select>
            </td>
            <td>
              <input type="number" step="any" class="form-control form-control-sm cantidad-proveedor-input" 
                    value="1" data-original-value="1">
            </td>
            <td>
              <input type="number" step="any" class="form-control form-control-sm precio-proveedor-input" 
                    value="${precio}" data-original-value="${precio}">
            </td>
            <td>
              <input type="number" step="any" class="form-control form-control-sm total-proveedor-display" 
                    value="${precio}" readonly>
            </td>
            <td>
              <input type="number" step="any" class="form-control form-control-sm margen-real-proveedor-display" 
                    value="0" readonly>
            </td>
            <td class="text-center">
              <button type="button" class="btn btn-sm btn-outline-success guardar-proveedor-btn" title="Guardar cambios">
                <i class="fas fa-save"></i>
              </button>
              <button type="button" class="btn btn-sm btn-outline-primary establecer-principal-btn" title="Establecer como principal">
                <i class="fas fa-star"></i>
              </button>
              <button type="button" class="btn btn-sm btn-outline-danger eliminar-proveedor-btn" title="Eliminar proveedor">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          `;
          
          // Recalcular valores para esta fila
          recalcularFila(fila);
          
          // Re-asignar listeners para la fila actualizada
          setupProveedorRowListeners(fila);
        }
      });
    }
    
    // Configurar los eventos para la nueva fila
    const nuevaFila = tfoot.querySelector('.nueva-fila-proveedor');
    configurarNuevaFila(nuevaFila);
    
    // Actualizar el margen real para cada fila
    actualizarMargenesReales(partidaId);
  });
  
  // Si no hay opciones existentes en los selectores, intentar cargarlas de la API
  if (document.querySelector('.nuevo-proveedor-select') && 
      document.querySelector('.nuevo-proveedor-select').options.length <= 1) {
    cargarOpcionesProveedores();
  }
}

// Función para actualizar las opciones de proveedores
function cargarOpcionesProveedores() {
  // Obtener todos los proveedores directamente de los selectores existentes
  const proveedoresExistentes = document.querySelectorAll('.proveedor-select option');
  let opciones = '<option value="">Seleccione un proveedor</option>';
  
  // Si hay proveedores en los selectores existentes, usarlos
  if (proveedoresExistentes.length > 1) { // Más de 1 porque siempre hay una opción vacía
    proveedoresExistentes.forEach(option => {
      if (option.value) { // Ignorar la opción vacía
        opciones += `<option value="${option.value}">${option.textContent}</option>`;
      }
    });
    
    window.proveedoresOptions = opciones;
    
    // Actualizar todos los selectores nuevos
    document.querySelectorAll('.nuevo-proveedor-select').forEach(select => {
      select.innerHTML = opciones;
    });
  } else {
    // Intentar obtener los proveedores desde la API
    fetch('/api/proveedores/listar')
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Crear las opciones de proveedores
          window.proveedoresOptions = data.proveedores.map(prov => 
            `<option value="${prov.id}">${prov.nombre} (${prov.especialidad || 'Sin especialidad'})</option>`
          ).join('');
          
          opciones = `<option value="">Seleccione un proveedor</option>${window.proveedoresOptions}`;
          
          // Actualizar todos los selectores
          document.querySelectorAll('.nuevo-proveedor-select').forEach(select => {
            select.innerHTML = opciones;
          });
        } else {
          console.error('Error en la respuesta de la API de proveedores');
          // Plan B: Usar nombres genéricos
          cargarProveedoresGenericos();
        }
      })
      .catch(error => {
        console.error('Error al cargar proveedores:', error);
        // Plan B: Usar nombres genéricos
        cargarProveedoresGenericos();
      });
  }
}

// Función de respaldo para cargar proveedores genéricos
function cargarProveedoresGenericos() {
  // Buscar los proveedores directamente en la tabla
  const nombresProveedores = new Map();
  
  // Buscar en las filas existentes de las tablas
  document.querySelectorAll('table[id^="tablaProveedores_"] tbody tr').forEach(row => {
    const nombreCelda = row.querySelector('td:first-child');
    if (nombreCelda) {
      const nombre = nombreCelda.textContent.trim();
      const id = row.getAttribute('data-proveedor-partida-id');
      if (nombre && id) {
        nombresProveedores.set(id, nombre);
      }
    }
  });
  
  // Si encontramos proveedores, usarlos
  if (nombresProveedores.size > 0) {
    let opciones = '<option value="">Seleccione un proveedor</option>';
    nombresProveedores.forEach((nombre, id) => {
      opciones += `<option value="${id}">${nombre}</option>`;
    });
    
    window.proveedoresOptions = opciones;
    
    // Actualizar todos los selectores
    document.querySelectorAll('.nuevo-proveedor-select').forEach(select => {
      select.innerHTML = opciones;
    });
  } else {
    // Si todo falla, crear algunos proveedores genéricos
    const genericos = [
      {id: 'prov1', nombre: 'Proveedor 1'},
      {id: 'prov2', nombre: 'Proveedor 2'},
      {id: 'prov3', nombre: 'Proveedor 3'}
    ];
    
    let opciones = '<option value="">Seleccione un proveedor</option>';
    genericos.forEach(prov => {
      opciones += `<option value="${prov.id}">${prov.nombre}</option>`;
    });
    
    window.proveedoresOptions = opciones;
    
    // Actualizar todos los selectores
    document.querySelectorAll('.nuevo-proveedor-select').forEach(select => {
      select.innerHTML = opciones;
    });
  }
}

// Configurar eventos para la nueva fila
function configurarNuevaFila(fila) {
  const partidaId = fila.getAttribute('data-partida-id');
  const selectProveedor = fila.querySelector('.nuevo-proveedor-select');
  const selectUnitario = fila.querySelector('.nuevo-unitario-select');
  const inputCantidad = fila.querySelector('.nuevo-cantidad-input');
  const inputPrecio = fila.querySelector('.nuevo-precio-input');
  const displayTotal = fila.querySelector('.nuevo-total-display');
  const displayMargenReal = fila.querySelector('.nuevo-margen-real-display');
  const btnGuardar = fila.querySelector('.guardar-nuevo-proveedor-btn');
  const btnPrincipal = fila.querySelector('.nuevo-principal-check');
  
  // Cargar los proveedores directamente de los selectores existentes
  const existingSelect = document.querySelector('.proveedor-select');
  if (existingSelect) {
    const opciones = Array.from(existingSelect.options).map(opt => 
      `<option value="${opt.value}">${opt.textContent}</option>`
    ).join('');
    selectProveedor.innerHTML = opciones;
  }
  
  // Calcular total al cambiar cantidad o precio
  function calcularTotal() {
    const cantidad = parseFloat(inputCantidad.value) || 0;
    const precio = parseFloat(inputPrecio.value) || 0;
    const total = cantidad * precio;
    displayTotal.value = total.toFixed(2);
    
    // Actualizar el margen real
    actualizarMargenReal();
  }
  
  // Calcular margen real (comparando con el precio final de la partida)
  function actualizarMargenReal() {
    const partida = document.querySelector(`.partida[data-partida-id="${partidaId}"]`);
    if (partida) {
      const finalPartida = partida.querySelector('input[name*="[final]"]');
      const total = parseFloat(displayTotal.value) || 0;
      
      if (finalPartida && total > 0) {
        const finalValor = parseFloat(finalPartida.value) || 0;
        const margenReal = ((finalValor / total) - 1) * 100;
        displayMargenReal.value = margenReal.toFixed(2);
      } else {
        displayMargenReal.value = "0.00";
      }
    }
  }
  
  inputCantidad.addEventListener('input', calcularTotal);
  inputPrecio.addEventListener('input', calcularTotal);
  
  // Inicializar valores
  calcularTotal();
  
  // Guardar proveedor
  btnGuardar.addEventListener('click', function() {
    const proveedorId = selectProveedor.value;
    const unitario = selectUnitario.value;
    const cantidad = inputCantidad.value;
    const precio = inputPrecio.value;
    const total = displayTotal.value;
    const esPrincipal = btnPrincipal.classList.contains('active');
    
    if (!proveedorId) {
      alert('Por favor seleccione un proveedor');
      return;
    }
    
    // Preparar los datos para enviar
    const formData = new FormData();
    formData.append('id_partida', partidaId);
    formData.append('id_proveedor', proveedorId);
    formData.append('unitario', unitario);
    formData.append('cantidad', cantidad);
    formData.append('precio', precio);
    formData.append('total', total);
    formData.append('notas', '');  // Sin notas en la versión inline
    formData.append('es_principal', esPrincipal);
    
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
        // Añadir a la tabla
        const tablaId = `tablaProveedores_${partidaId}`;
        const tabla = document.getElementById(tablaId);
        
        if (tabla) {
          const tbody = tabla.querySelector('tbody');
          const newRow = document.createElement('tr');
          newRow.setAttribute('data-proveedor-partida-id', data.proveedor_partida.id);
          
          // Crear la fila con los datos del proveedor
          newRow.innerHTML = `
            <td>${data.proveedor_partida.nombre_proveedor}</td>
            <td>
              <select class="form-select form-select-sm unitario-proveedor-select">
                ${selectUnitario.innerHTML}
              </select>
            </td>
            <td>
              <input type="number" step="any" class="form-control form-control-sm cantidad-proveedor-input" 
                    value="${cantidad}" data-original-value="${cantidad}">
            </td>
            <td>
              <input type="number" step="any" class="form-control form-control-sm precio-proveedor-input" 
                    value="${precio}" data-original-value="${precio}">
            </td>
            <td>
              <input type="number" step="any" class="form-control form-control-sm total-proveedor-display" 
                    value="${total}" readonly>
            </td>
            <td>
              <input type="number" step="any" class="form-control form-control-sm margen-real-proveedor-display" 
                    value="${displayMargenReal.value}" readonly>
            </td>
            <td class="text-center">
              <button type="button" class="btn btn-sm btn-outline-success guardar-proveedor-btn" style="display:none;" title="Guardar cambios">
                <i class="fas fa-save"></i>
              </button>
              <button type="button" class="btn btn-sm btn-outline-primary establecer-principal-btn" title="Establecer como principal">
                <i class="fas fa-star"></i>
              </button>
              <button type="button" class="btn btn-sm btn-outline-danger eliminar-proveedor-btn" title="Eliminar proveedor">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          `;
          
          tbody.appendChild(newRow);
          
          // Seleccionar la unidad correcta
          const unitarioSelect = newRow.querySelector('.unitario-proveedor-select');
          if (unitarioSelect) {
            unitarioSelect.value = unitario;
          }
          
          // Configurar event listeners para la nueva fila
          setupProveedorRowListeners(newRow);
          
          // Si es principal, actualizar el selector en la partida
          if (esPrincipal) {
            const partida = document.querySelector(`.partida[data-partida-id="${partidaId}"]`);
            if (partida) {
              const proveedorSelect = partida.querySelector('.proveedor-select');
              const precioProveedorInput = partida.querySelector('.proveedor-precio');
              
              if (proveedorSelect && precioProveedorInput) {
                proveedorSelect.value = proveedorId;
                precioProveedorInput.value = precio;
                
                // Actualizar margen real
                actualizarMargenReal(precioProveedorInput);
              }
            }
          }
          
          // Limpiar la fila de entrada
          selectProveedor.value = '';
          inputCantidad.value = '1';
          inputPrecio.value = '0';
          displayTotal.value = '0';
          displayMargenReal.value = '0';
          btnPrincipal.classList.remove('active');
          btnPrincipal.classList.remove('btn-primary');
          btnPrincipal.classList.add('btn-outline-primary');
          
          // Actualizar contador de proveedores
          agregarContadorProveedores();
        }
      } else {
        alert('Error al asignar proveedor: ' + data.error);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Error de conexión al asignar proveedor');
    });
  });
  
  // Toggle de proveedor principal
  btnPrincipal.addEventListener('click', function() {
    this.classList.toggle('active');
    this.classList.toggle('btn-outline-primary');
    this.classList.toggle('btn-primary');
  });
}

// Elimina la necesidad del popup modal
function desactivarModalProveedor() {
  // Desactivar el evento click en los botones de agregar proveedor
  document.querySelectorAll('.agregar-proveedor-btn').forEach(btn => {
    btn.replaceWith(btn.cloneNode(true));
  });
  
  // Opcional: ocultar el modal completamente
  const modal = document.getElementById('agregarProveedorModal');
  if (modal) {
    modal.style.display = 'none';
    modal.classList.remove('fade');
    modal.setAttribute('aria-hidden', 'true');
  }
}

// Inicializar la funcionalidad
document.addEventListener('DOMContentLoaded', function() {
  // Desactivar el modal y usar la versión inline
  desactivarModalProveedor();
  agregarFilaEditable();
  
  // Estilo personalizado para la fila de nuevo proveedor
  const style = document.createElement('style');
  style.textContent = `
    .nueva-fila-proveedor {
      background-color: rgba(40, 167, 69, 0.05);
    }
    
    .nuevo-principal-check.active {
      background-color: #ffc107;
      color: #212529;
      border-color: #ffc107;
    }
    
    /* Estilo para tablas contraídas */
    .collapse:not(.show) + .agregarProveedorModal {
      display: none !important;
    }
    
    /* Estilos para hacer la tabla más compacta */
    .table-sm input.form-control-sm {
      padding: 0.1rem 0.3rem;
      height: calc(1.5em + 0.4rem);
    }
    
    /* Hacer más visible la fila de entrada */
    .nueva-fila-proveedor td {
      border-top: 2px dashed #ddd;
      padding-top: 8px;
    }
  `;
  document.head.appendChild(style);
});