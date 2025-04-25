/**
 * Mejoras para la gestión de proveedores en hojas de trabajo
 * 
 * Este script agrega:
 * 1. Indicador visual del número de proveedores por partida
 * 2. Opción para mantener contenedores de proveedores expandidos
 * 3. Persistencia de datos entre actualizaciones
 */

// Función para añadir indicador de número de proveedores a todos los botones
function agregarContadorProveedores() {
  // Procesar cada partida
  document.querySelectorAll('[id^="proveedoresAdicionales_"]').forEach(container => {
    // Obtener el ID de partida del contenedor
    const partidaId = container.id.replace('proveedoresAdicionales_', '');
    
    // Encontrar el botón que controla este contenedor
    const botonToggle = document.querySelector(`button[data-bs-target="#proveedoresAdicionales_${partidaId}"]`);
    if (!botonToggle) return;
    
    // Contar el número de filas de proveedores (excluyendo la fila de 'Agregar Proveedor')
    const tabla = container.querySelector('table');
    if (!tabla) return;
    
    const numProveedores = tabla.querySelectorAll('tbody tr').length;
    
    // Actualizar el botón para incluir el contador
    if (numProveedores > 0) {
      // Eliminar cualquier contador existente
      const contadorExistente = botonToggle.querySelector('.contador-proveedores');
      if (contadorExistente) {
        contadorExistente.remove();
      }
      
      // Crear el contador
      const contador = document.createElement('span');
      contador.className = 'contador-proveedores badge bg-danger ms-1';
      contador.innerText = numProveedores;
      
      // Insertar antes del icono de caret
      const caret = botonToggle.querySelector('i.fas.fa-caret-down');
      if (caret) {
        botonToggle.insertBefore(contador, caret);
      } else {
        botonToggle.appendChild(contador);
      }
      
      // Actualizar el texto del botón para hacerlo más claro
      botonToggle.innerHTML = botonToggle.innerHTML.replace('Proveedores Adicionales', `Proveedores (${numProveedores})`);
    }
  });
}

// Función para mantener el estado de expansión/contracción 
function persistirEstadoExpansion() {
  // Verificar si localStorage está disponible
  if (typeof localStorage === 'undefined') return;
  
  // Clave única basada en la URL actual para almacenar estados
  const storageKey = `hojaTrabajoExpansion_${window.location.pathname}`;
  
  // Al cargar la página, restaurar estados previos
  window.addEventListener('DOMContentLoaded', () => {
    try {
      const estadosGuardados = JSON.parse(localStorage.getItem(storageKey)) || {};
      
      // Aplicar estados guardados
      Object.keys(estadosGuardados).forEach(id => {
        const expandido = estadosGuardados[id];
        const collapse = document.getElementById(id);
        
        if (collapse) {
          if (expandido) {
            // Expandir el contenedor
            new bootstrap.Collapse(collapse, { toggle: true });
          }
        }
      });
    } catch (error) {
      console.error('Error al restaurar estados:', error);
    }
  });
  
  // Escuchar eventos de expansión/contracción
  document.querySelectorAll('[id^="proveedoresAdicionales_"]').forEach(container => {
    container.addEventListener('shown.bs.collapse', function() {
      // Guardar estado expandido
      try {
        const estadosGuardados = JSON.parse(localStorage.getItem(storageKey)) || {};
        estadosGuardados[this.id] = true;
        localStorage.setItem(storageKey, JSON.stringify(estadosGuardados));
      } catch (error) {
        console.error('Error al guardar estado:', error);
      }
    });
    
    container.addEventListener('hidden.bs.collapse', function() {
      // Guardar estado contraído
      try {
        const estadosGuardados = JSON.parse(localStorage.getItem(storageKey)) || {};
        estadosGuardados[this.id] = false;
        localStorage.setItem(storageKey, JSON.stringify(estadosGuardados));
      } catch (error) {
        console.error('Error al guardar estado:', error);
      }
    });
  });
}

// Función para evitar pérdida de datos al establecer un proveedor como principal
function preservarDatosProveedor() {
  // Capturar todos los botones de establecer como principal
  document.querySelectorAll('.establecer-principal-btn').forEach(btn => {
    // Reemplazar el evento existente
    const oldClickHandler = btn.onclick;
    btn.onclick = null;
    
    btn.addEventListener('click', async function(e) {
      // Evitar navegación por defecto
      e.preventDefault();
      
      try {
        // Obtener datos del proveedor
        const row = this.closest('tr');
        const proveedorPartidaId = row.getAttribute('data-proveedor-partida-id');
        const partida = this.closest('.partida');
        const partidaId = partida.getAttribute('data-partida-id');
        
        // Obtener el precio actual del proveedor para enviarlo después
        const precioInput = row.querySelector('.precio-proveedor-input');
        const precioProveedor = precioInput ? precioInput.value : 0;
        
        // Obtener información del proveedor para establecerlo como principal
        const response = await fetch(`/api/proveedores-partidas/por-partida/${partidaId}`);
        const data = await response.json();
        
        if (data.success) {
          // Buscar el proveedor correspondiente
          const proveedor = data.proveedores.find(p => p.id.toString() === proveedorPartidaId);
          
          if (proveedor) {
            // Preparar los datos para enviar
            const formData = new FormData();
            formData.append('id_partida', partidaId);
            formData.append('id_proveedor', proveedor.id_proveedor);
            
            // Actualizar interface antes de enviar la solicitud
            const proveedorPrincipalSelect = partida.querySelector('.proveedor-select');
            const precioPrincipalInput = partida.querySelector('.proveedor-precio');
            
            if (proveedorPrincipalSelect && precioPrincipalInput) {
              // Guardar valores actuales para restaurar en caso de error
              const prevProveedor = proveedorPrincipalSelect.value;
              const prevPrecio = precioPrincipalInput.value;
              
              // Actualizar la interfaz inmediatamente
              proveedorPrincipalSelect.value = proveedor.id_proveedor;
              precioPrincipalInput.value = precioProveedor;
              
              // Actualizar el margen real
              const finalPartidaInput = partida.querySelector('input[name*="[final]"]');
              const margenRealInput = partida.querySelector('.margen-real-display');
              
              if (finalPartidaInput && margenRealInput && precioProveedor > 0) {
                const final = parseFloat(finalPartidaInput.value) || 0;
                const margenReal = ((final / parseFloat(precioProveedor)) - 1) * 100;
                margenRealInput.value = margenReal.toFixed(2);
              }
              
              // Enviar al servidor
              const serverResponse = await fetch('/api/proveedores-partidas/establecer-principal', {
                method: 'POST',
                body: formData,
                headers: {
                  'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                }
              });
              
              const result = await serverResponse.json();
              
              if (!result.success) {
                // Restaurar valores previos en caso de error
                proveedorPrincipalSelect.value = prevProveedor;
                precioPrincipalInput.value = prevPrecio;
                
                alert('Error al establecer proveedor como principal: ' + result.error);
              } else {
                // Éxito
                alert('Proveedor establecido como principal correctamente');
                
                // Actualizar el contador de proveedores para reflejar cambios
                agregarContadorProveedores();
              }
            }
          }
        }
      } catch (error) {
        console.error('Error al establecer proveedor principal:', error);
        alert('Error de conexión al establecer proveedor principal');
      }
    });
  });
}

// Función para expandir automáticamente los proveedores con estados guardados
function expandirAutomaticamente() {
  // Opciones de configuración (personalizable)
  const config = {
    expandirTodos: false,                 // Expandir todos los contenedores al cargar
    expandirConProveedores: true,         // Expandir solo contenedores con proveedores
    expandirSiError: true,                // Expandir si hay errores en el formulario
    mostrarBadgeSiempre: true,            // Mostrar el contador incluso si hay 0 proveedores
    badgeZeroClass: 'bg-secondary',       // Clase para el badge cuando hay 0 proveedores
    badgeClass: 'bg-danger',              // Clase para el badge cuando hay proveedores
    textoBoton: 'Proveedores',            // Texto base del botón
    mantenerExpandidoFormulario: true     // Mantener expandido cuando se envía el formulario
  };
  
  // Expandir contenedores según configuración
  document.querySelectorAll('[id^="proveedoresAdicionales_"]').forEach(container => {
    const numProveedores = container.querySelectorAll('tbody tr').length;
    
    // Determinar si debe expandirse
    let debeExpandirse = config.expandirTodos;
    
    if (config.expandirConProveedores && numProveedores > 0) {
      debeExpandirse = true;
    }
    
    if (config.expandirSiError && container.querySelector('.is-invalid')) {
      debeExpandirse = true;
    }
    
    // Expandir si cumple las condiciones
    if (debeExpandirse) {
      new bootstrap.Collapse(container, { toggle: true });
    }
    
    // Actualizar el botón toggle
    const botonToggle = document.querySelector(`button[data-bs-target="#${container.id}"]`);
    if (botonToggle) {
      // Crear o actualizar el badge
      if (config.mostrarBadgeSiempre || numProveedores > 0) {
        const badgeClass = numProveedores > 0 ? config.badgeClass : config.badgeZeroClass;
        
        // Verificar si ya tiene un badge
        let badge = botonToggle.querySelector('.contador-proveedores');
        if (!badge) {
          badge = document.createElement('span');
          badge.className = `contador-proveedores badge ${badgeClass} ms-1`;
          
          // Posicionar el badge
          const caret = botonToggle.querySelector('i.fas.fa-caret-down');
          if (caret) {
            botonToggle.insertBefore(badge, caret);
          } else {
            botonToggle.appendChild(badge);
          }
        } else {
          badge.className = `contador-proveedores badge ${badgeClass} ms-1`;
        }
        
        badge.innerText = numProveedores;
        
        // Actualizar el texto del botón
        const textNode = document.createTextNode(` ${config.textoBoton} `);
        
        // Eliminar texto actual
        while (botonToggle.childNodes.length) {
          if (botonToggle.childNodes[0].nodeType === 3) { // Es un nodo de texto
            botonToggle.removeChild(botonToggle.childNodes[0]);
          } else if (botonToggle.childNodes[0].nodeType === 1 && 
                    !botonToggle.childNodes[0].classList.contains('contador-proveedores') && 
                    !botonToggle.childNodes[0].classList.contains('fas')) {
            botonToggle.removeChild(botonToggle.childNodes[0]);
          } else {
            break;
          }
        }
        
        // Insertar al inicio
        botonToggle.insertBefore(textNode, botonToggle.firstChild);
      }
    }
  });
}

// Función principal
function mejorarGestionProveedores() {
  // Agregar contadores a todos los botones
  agregarContadorProveedores();
  
  // Configurar persistencia de estado
  persistirEstadoExpansion();
  
  // Evitar pérdida de datos
  preservarDatosProveedor();
  
  // Expandir automáticamente algunos contenedores
  expandirAutomaticamente();
  
  // Al enviar el formulario, guardar estados actuales
  document.querySelector('form').addEventListener('submit', function() {
    // Guardar el estado de los contenedores
    document.querySelectorAll('[id^="proveedoresAdicionales_"]').forEach(container => {
      localStorage.setItem(`estado_${container.id}`, container.classList.contains('show'));
    });
  });
}

// Inicializar cuando el documento esté listo
document.addEventListener('DOMContentLoaded', mejorarGestionProveedores);

// Agregar estilos necesarios
document.addEventListener('DOMContentLoaded', function() {
  // Crear elemento de estilo
  const style = document.createElement('style');
  style.textContent = `
    /* Estilos para el contador de proveedores */
    .contador-proveedores {
      font-size: 0.75rem;
      border-radius: 0.625rem;
      padding: 0.25rem 0.5rem;
      font-weight: bold;
    }
    
    /* Destacar sección de proveedores */
    .collapse.show .card-body {
      animation: highlight 1s ease-out;
    }
    
    @keyframes highlight {
      0% { background-color: rgba(255, 220, 200, 0.3); }
      100% { background-color: transparent; }
    }
    
    /* Mejoras de estilos para tablas de proveedores */
    #tablaProveedores_* {
      margin-bottom: 0;
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
  
  // Añadir al documento
  document.head.appendChild(style);
});