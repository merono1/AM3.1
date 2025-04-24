/**
 * partidas_contraibles.js - Sistema de partidas contraíbles adaptado para la vista de editar_partidas_simple.html
 */

// Función principal de inicialización
function inicializarPartidasContraibles() {
  console.log("Inicializando sistema de partidas contraíbles...");
  
  // Convertir las partidas existentes al formato contraíble
  convertirPartidasExistentes();
  
  // Inicializar eventos para contraer/expandir
  inicializarEventos();
}

// Función para convertir partidas existentes al formato contraíble
function convertirPartidasExistentes() {
  console.log("Convirtiendo partidas existentes...");
  
  // Para cada capítulo en la página
  document.querySelectorAll('.card-header').forEach(headerCapitulo => {
    const cardBody = headerCapitulo.nextElementSibling;
    if (!cardBody || !cardBody.classList.contains('card-body')) return;
    
    // Obtener todos los contenedores de partidas
    const partidas = cardBody.querySelectorAll('.partida-container');
    console.log(`Encontradas ${partidas.length} partidas en capítulo`);
    
    partidas.forEach(partida => {
      // Obtener referencias a los elementos existentes
      const row1 = partida.querySelector('.partida-row-1');
      const row2 = partida.querySelector('.partida-row-2');
      
      if (!row1 || !row2) return;
      
      // Extraer datos importantes de la partida
      const numero = row1.querySelector('.partida-numero')?.textContent.trim() || '';
      const descripcion = row1.querySelector('.partida-descripcion')?.textContent.trim() || '';
      const accionesBotones = row1.querySelector('.partida-acciones')?.innerHTML || '';
      
      // Extraer los valores de la partida
      const datosDivs = row2.querySelectorAll('.partida-dato');
      let unitario = '', cantidad = '', precio = '', total = '', margen = '', final = '';
      
      datosDivs.forEach(datoDiv => {
        const label = datoDiv.querySelector('.partida-dato-label')?.textContent.trim() || '';
        const valor = datoDiv.querySelector('div:last-child')?.textContent.trim() || '';
        
        if (label.includes('Unidad')) unitario = valor;
        else if (label.includes('Cantidad')) cantidad = valor;
        else if (label.includes('Precio')) precio = valor;
        else if (label.includes('Total') && !label.includes('Final')) total = valor;
        else if (label.includes('Margen')) margen = valor;
        else if (label.includes('Final')) final = valor;
      });
      
      // Extraer ID de partida del botón editar para mantener la funcionalidad
      let partidaId = "";
      const btnEditar = row1.querySelector('button[onclick*="editarPartida"]');
      if (btnEditar) {
        const onclickAttr = btnEditar.getAttribute('onclick');
        const match = onclickAttr.match(/editarPartida\s*\(\s*['"]([^'"]+)['"]/);
        if (match && match[1]) {
          partidaId = match[1];
        }
      }
      
      // Crear el nuevo HTML para la partida contraíble
      partida.innerHTML = `
        <div class="partida-header">
          <div class="partida-header-left">
            <div class="partida-numero">${numero}</div>
            <div class="partida-descripcion">${descripcion}</div>
          </div>
          <div class="partida-header-right">
            <div class="partida-total">${final}</div>
            <div class="partida-acciones">${accionesBotones}</div>
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
              <span class="partida-detail-label">Margen %:</span>
              <span class="partida-detail-value">${margen}</span>
            </div>
            <div class="partida-detail-item">
              <span class="partida-detail-label">Total + Margen:</span>
              <span class="partida-detail-value">${final}</span>
            </div>
          </div>
        </div>
      `;
      
      // Asignar ID para referencia
      partida.dataset.partidaId = partidaId;
    });
  });
  
  console.log("Conversión de partidas completada");
}

// Función para inicializar eventos
function inicializarEventos() {
  console.log("Inicializando eventos de partidas contraíbles...");
  
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
    
    // Contraer otras partidas al expandir esta
    if (container.classList.contains('expanded')) {
      const otrasPartidas = document.querySelectorAll('.partida-container.expanded');
      otrasPartidas.forEach(otra => {
        if (otra !== container) {
          otra.classList.remove('expanded');
        }
      });
    }
  });
  
  // Asegurar que al editar una partida se expanda
  document.addEventListener('click', function(event) {
    const editButton = event.target.closest('button[onclick*="editarPartida"]');
    if (!editButton) return;
    
    const partidaContainer = editButton.closest('.partida-container');
    if (partidaContainer) {
      // Expandir esta partida
      partidaContainer.classList.add('expanded');
      
      // Contraer otras partidas
      const otrasPartidas = document.querySelectorAll('.partida-container.expanded');
      otrasPartidas.forEach(otra => {
        if (otra !== partidaContainer) {
          otra.classList.remove('expanded');
        }
      });
    }
  });
  
  console.log("Eventos de partidas contraíbles inicializados");
}

// Adaptar función existente de editar partida para trabajar con partidas contraíbles
const originalEditarPartida = window.editarPartida;
if (originalEditarPartida) {
  console.log("Adaptando función editarPartida existente...");
  
  window.editarPartida = function() {
    // Llamar a la función original
    originalEditarPartida.apply(this, arguments);
    
    // Expandir la partida correspondiente si existe
    const id = arguments[0];
    const partidaContainer = document.querySelector(`.partida-container[data-partida-id="${id}"]`);
    if (partidaContainer) {
      // Expandir esta partida
      partidaContainer.classList.add('expanded');
      
      // Contraer otras partidas
      const otrasPartidas = document.querySelectorAll('.partida-container.expanded');
      otrasPartidas.forEach(otra => {
        if (otra !== partidaContainer) {
          otra.classList.remove('expanded');
        }
      });
    }
  };
  
  console.log("Función editarPartida adaptada correctamente");
}

// Inicializar cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', inicializarPartidasContraibles);

console.log("Script de partidas contraíbles cargado correctamente");
