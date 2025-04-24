/**
 * partidas_contraibles.js - Sistema de partidas contraíbles para AM3.1
 */

// Función principal de inicialización
function inicializarPartidasContraibles() {
  // Convertir las partidas existentes al formato contraíble
  convertirPartidasExistentes();
  
  // Inicializar eventos para contraer/expandir
  inicializarEventos();
}

// Función para convertir partidas existentes al formato contraíble
function convertirPartidasExistentes() {
  // Para cada capítulo en la página
  document.querySelectorAll('.card-header').forEach(headerCapitulo => {
    const cardBody = headerCapitulo.nextElementSibling;
    if (!cardBody || !cardBody.classList.contains('card-body')) return;
    
    // Obtener el contenedor de la tabla
    const tableContainer = cardBody.querySelector('.table-responsive');
    if (!tableContainer) return;
    
    // Obtener todas las filas de partidas (agrupadas de 3 en 3)
    const tbody = tableContainer.querySelector('tbody');
    if (!tbody) return;
    
    // Obtener todas las filas
    const filas = Array.from(tbody.querySelectorAll('tr'));
    
    // Necesitamos procesar las filas en grupos de 3:
    // 1. partida-descripcion
    // 2. partida-datos
    // 3. separador-partida
    const nuevasFilas = [];
    
    // Procesar filas de 3 en 3 (descripción, datos, separador)
    for (let i = 0; i < filas.length; i += 3) {
      // Si no quedan suficientes filas o estamos en una fila de subtotal, sal
      if (i + 1 >= filas.length || filas[i].classList.contains('table-light')) {
        // Agregar filas restantes como están (podría ser el subtotal)
        for (let j = i; j < filas.length; j++) {
          nuevasFilas.push(filas[j]);
        }
        break;
      }
      
      // Fila de descripción
      const filaDescripcion = filas[i];
      // Fila de datos
      const filaDatos = filas[i + 1];
      // Fila de separador
      const filaSeparador = filas[i + 2];
      
      // Identificar elementos
      const numero = filaDescripcion.querySelector('td:first-child').textContent.trim();
      const descripcion = filaDescripcion.querySelector('td:nth-child(2)').textContent.trim();
      const botones = filaDescripcion.querySelector('td:last-child').innerHTML;
      
      // Obtener datos numéricos
      const datosContainer = filaDatos.querySelector('.tabla-datos-partida');
      if (!datosContainer) continue;
      
      // Datos numéricos que necesitamos para la visualización
      let unitario = "", cantidad = "", precio = "", total = "", margen = "", totalConMargen = "";
      
      const datosCols = datosContainer.querySelectorAll('.datos-col');
      if (datosCols.length >= 5) {
        unitario = datosCols[0].querySelector('.datos-valor').textContent.trim();
        cantidad = datosCols[1].querySelector('.datos-valor').textContent.trim();
        precio = datosCols[2].querySelector('.datos-valor').textContent.trim();
        total = datosCols[3].querySelector('.datos-valor').textContent.trim();
        totalConMargen = datosCols[4].querySelector('.datos-valor').textContent.trim();
      }
      
      // Extraer ID de partida del botón editar
      let partidaId = "";
      const btnEditar = filaDescripcion.querySelector('button[onclick*="editarPartida"]');
      if (btnEditar) {
        const onclickAttr = btnEditar.getAttribute('onclick');
        // Extraer el primer parámetro que debería ser el ID
        const match = onclickAttr.match(/editarPartida\s*\(\s*['"]([^'"]+)['"]/);
        if (match && match[1]) {
          partidaId = match[1];
        }
      }
      
      // Crear nueva fila contraíble
      const nuevaFila = document.createElement('tr');
      nuevaFila.className = 'partida-contraible';
      nuevaFila.dataset.partidaId = partidaId;
      
      // Crear celda de contenido para la partida contraíble
      nuevaFila.innerHTML = `
        <td colspan="3" class="p-0">
          <div class="partida-container">
            <div class="partida-header">
              <div class="partida-header-left">
                <div class="partida-numero">${numero}</div>
                <div class="partida-descripcion">${descripcion}</div>
              </div>
              <div class="partida-header-right">
                <div class="partida-total">${totalConMargen}</div>
                <div class="partida-acciones">${botones}</div>
                <div class="toggle-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18 15-6-6-6 6"/></svg>
                </div>
              </div>
            </div>
            <div class="partida-content">
              <div class="partida-details">
                <div class="partida-detail-item">
                  <span class="partida-detail-label">Unitario:</span>
                  <span class="partida-detail-value">${unitario}</span>
                </div>
                <div class="partida-detail-item">
                  <span class="partida-detail-label">Cantidad:</span>
                  <span class="partida-detail-value">${cantidad}</span>
                </div>
                <div class="partida-detail-item">
                  <span class="partida-detail-label">Precio:</span>
                  <span class="partida-detail-value">${precio}</span>
                </div>
                <div class="partida-detail-item">
                  <span class="partida-detail-label">Total:</span>
                  <span class="partida-detail-value">${total}</span>
                </div>
                <div class="partida-detail-item">
                  <span class="partida-detail-label">Total + Margen:</span>
                  <span class="partida-detail-value">${totalConMargen}</span>
                </div>
              </div>
            </div>
          </div>
        </td>
      `;
      
      nuevasFilas.push(nuevaFila);
    }
    
    // Reemplazar el contenido del tbody con las nuevas filas contraíbles
    tbody.innerHTML = '';
    nuevasFilas.forEach(fila => {
      tbody.appendChild(fila);
    });
  });
}

// Función para inicializar eventos
function inicializarEventos() {
  // Evento para contraer/expandir al hacer clic en el encabezado
  document.addEventListener('click', function(event) {
    const header = event.target.closest('.partida-header');
    if (!header) return;
    
    // Si el clic fue en un botón de acción, no expandir/contraer
    if (event.target.closest('.partida-acciones')) return;
    
    const container = header.closest('.partida-container');
    if (!container) return;
    
    // Toggle de la clase expandida
    container.classList.toggle('expanded');
  });
  
  // Asegurar que al editar una partida se expanda
  document.addEventListener('click', function(event) {
    const editButton = event.target.closest('button[onclick*="editarPartida"]');
    if (!editButton) return;
    
    const partidaContainer = editButton.closest('.partida-container');
    if (partidaContainer) {
      partidaContainer.classList.add('expanded');
    }
  });
}

// Adaptar función existente de editar partida para trabajar con partidas contraíbles
const originalEditarPartida = window.editarPartida;
if (originalEditarPartida) {
  window.editarPartida = function() {
    // Llamar a la función original
    originalEditarPartida.apply(this, arguments);
    
    // Expandir la partida correspondiente si existe
    const id = arguments[0];
    const partidaContainer = document.querySelector(`.partida-container[data-partida-id="${id}"]`);
    if (partidaContainer) {
      partidaContainer.classList.add('expanded');
    }
  };
}

// Inicializar cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', inicializarPartidasContraibles);
