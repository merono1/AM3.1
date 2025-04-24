/**
 * partidas_contraibles_editar_pres.js - Sistema de partidas contraíbles para editar_pres.html
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
    if (!headerCapitulo.textContent.includes('.')) return; // Solo capítulos numerados
    
    const cardBody = headerCapitulo.nextElementSibling;
    if (!cardBody || !cardBody.classList.contains('card-body')) return;
    
    // Obtener la tabla de partidas
    const table = cardBody.querySelector('table');
    if (!table) return;
    
    const tbody = table.querySelector('tbody');
    if (!tbody) return;
    
    // Procesar las filas en pares (fila1: descripción, fila2: datos)
    const filas = Array.from(tbody.querySelectorAll('tr'));
    const nuevasFilas = [];
    
    // Filtrar solo las filas de partidas (no incluir el subtotal u otras filas)
    let i = 0;
    while (i < filas.length) {
      // Verificar si es una fila de partida (debe tener las clases partida-fila-1 y partida-fila-2)
      if (i + 1 < filas.length && 
          filas[i].classList.contains('partida-fila-1') && 
          filas[i+1].classList.contains('partida-fila-2')) {
        
        const fila1 = filas[i];
        const fila2 = filas[i+1];
        
        // Extraer los datos necesarios
        const partidaId = fila1.dataset.partidaId;
        const numero = fila1.querySelector('td:first-child').textContent.trim();
        const descripcion = fila1.querySelector('.descripcion-celda').innerHTML;
        const accionesBotones = fila1.querySelector('td:last-child').innerHTML;
        
        // Extraer los datos numéricos
        const datosContainer = fila2.querySelector('.tabla-datos-partida');
        if (!datosContainer) {
          i += 2;
          continue;
        }
        
        // Extraer valores de los campos de datos
        const unitarioSpan = datosContainer.querySelector('.unitario-span');
        const cantidadSpan = datosContainer.querySelector('.cantidad-span');
        const precioSpan = datosContainer.querySelector('.precio-span');
        const margenSpan = datosContainer.querySelector('.margen-span');
        const totalSpan = datosContainer.querySelector('.total-span');
        const finalSpan = datosContainer.querySelector('.final-span');
        
        const unitario = unitarioSpan ? unitarioSpan.textContent.trim() : '';
        const cantidad = cantidadSpan ? cantidadSpan.textContent.trim() : '';
        const precio = precioSpan ? precioSpan.textContent.trim() : '';
        const margen = margenSpan ? margenSpan.textContent.trim() : '';
        const total = totalSpan ? totalSpan.textContent.trim() : '';
        const final = finalSpan ? finalSpan.textContent.trim() : '';
        
        // Crear la nueva fila contraíble
        const nuevaFila = document.createElement('tr');
        nuevaFila.className = 'partida-contraible';
        nuevaFila.dataset.partidaId = partidaId;
        
        nuevaFila.innerHTML = `
          <td colspan="3" class="p-0">
            <div class="partida-container" data-partida-id="${partidaId}">
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
            </div>
          </td>
        `;
        
        nuevasFilas.push(nuevaFila);
        i += 2; // Saltamos las dos filas procesadas
      } else {
        // Si no es una fila de partida, la mantenemos igual
        nuevasFilas.push(filas[i]);
        i++;
      }
    }
    
    // Limpiar tbody y agregar las nuevas filas
    tbody.innerHTML = '';
    nuevasFilas.forEach(fila => {
      tbody.appendChild(fila);
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
    
    // Contraer otras partidas cuando esta se expande
    if (container.classList.contains('expanded')) {
      document.querySelectorAll('.partida-container.expanded').forEach(otra => {
        if (otra !== container) {
          otra.classList.remove('expanded');
        }
      });
    }
  });
  
  // Asegurar que al editar una partida se expanda
  document.addEventListener('click', function(event) {
    // Verificar si se hizo clic en un botón de edición
    const editButton = event.target.closest('.editar-partida-btn');
    if (!editButton) return;
    
    // Extraer el ID de la partida del botón o del contenedor
    let partidaId = '';
    if (editButton.hasAttribute('onclick')) {
      const onclickAttr = editButton.getAttribute('onclick');
      const match = onclickAttr.match(/iniciarEdicionPartida\s*\(\s*['"]([^'"]+)['"]/);
      if (match && match[1]) {
        partidaId = match[1];
      }
    }
    
    // Si encontramos ID, expandir la partida
    if (partidaId) {
      const container = document.querySelector(`.partida-container[data-partida-id="${partidaId}"]`);
      if (container) {
        container.classList.add('expanded');
        
        // Contraer otras partidas
        document.querySelectorAll('.partida-container.expanded').forEach(otra => {
          if (otra !== container) {
            otra.classList.remove('expanded');
          }
        });
      }
    }
  });
  
  console.log("Eventos de partidas contraíbles inicializados");
}

// Adaptar funciones existentes para trabajar con partidas contraíbles
if (window.iniciarEdicionPartida) {
  console.log("Adaptando función iniciarEdicionPartida existente...");
  
  const originalIniciarEdicionPartida = window.iniciarEdicionPartida;
  window.iniciarEdicionPartida = function(id) {
    // Llamar a la función original
    originalIniciarEdicionPartida(id);
    
    // Expandir la partida correspondiente
    const container = document.querySelector(`.partida-container[data-partida-id="${id}"]`);
    if (container) {
      container.classList.add('expanded');
      
      // Contraer otras partidas
      document.querySelectorAll('.partida-container.expanded').forEach(otra => {
        if (otra !== container) {
          otra.classList.remove('expanded');
        }
      });
    }
  };
}

// Añadir estilos CSS específicos para las partidas contraíbles
function añadirEstilosCSS() {
  const estilos = `
    /* Contenedor de partida contraíble */
    .partida-container {
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      margin-bottom: 8px;
      overflow: hidden;
      transition: all 0.3s ease;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    /* Encabezado de partida */
    .partida-header {
      display: flex;
      justify-content: space-between;
      padding: 12px 15px;
      background-color: #f9fafb;
      cursor: pointer;
      align-items: center;
      user-select: none;
    }
    
    .partida-header:hover {
      background-color: #f3f4f6;
    }
    
    /* Lado izquierdo del encabezado */
    .partida-header-left {
      display: flex;
      align-items: center;
      gap: 15px;
      flex: 1;
    }
    
    .partida-numero {
      font-weight: 600;
      min-width: 50px;
      color: #4f46e5;
    }
    
    .partida-descripcion {
      font-weight: 500;
      color: #111827;
      flex: 1;
    }
    
    /* Lado derecho del encabezado */
    .partida-header-right {
      display: flex;
      align-items: center;
      gap: 15px;
    }
    
    .partida-total {
      font-weight: 600;
      text-align: right;
      min-width: 120px;
      color: #111827;
    }
    
    .toggle-icon {
      transition: transform 0.3s ease;
      color: #6b7280;
    }
    
    /* Contenido de la partida (contraído/expandido) */
    .partida-content {
      max-height: 0;
      overflow: hidden;
      transition: max-height 0.3s ease, padding 0.3s ease;
      padding: 0 15px;
      background-color: #ffffff;
    }
    
    .partida-container.expanded {
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .partida-container.expanded .partida-content {
      max-height: 1000px;
      padding: 15px;
    }
    
    .partida-container.expanded .toggle-icon {
      transform: rotate(180deg);
    }
    
    .partida-container.expanded .partida-header {
      background-color: #eef2ff;
      border-bottom: 1px solid #e5e7eb;
    }
    
    /* Detalles de la partida */
    .partida-details {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
      margin-top: 5px;
    }
    
    .partida-detail-item {
      display: flex;
      flex-direction: column;
      margin-bottom: 10px;
    }
    
    .partida-detail-label {
      font-size: 0.85rem;
      color: #6b7280;
      margin-bottom: 3px;
    }
    
    .partida-detail-value {
      font-weight: 500;
      color: #111827;
    }
    
    /* Ajustes para tener en cuenta el tema Bootstrap existente */
    tr.partida-contraible {
      background-color: transparent !important;
    }
    
    tr.partida-contraible td {
      padding: 0 !important;
      border-top: none !important;
    }
    
    /* Animación al expandir */
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-5px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    .partida-container.expanded .partida-content {
      animation: fadeIn 0.3s ease-in-out;
    }
  `;
  
  const style = document.createElement('style');
  style.textContent = estilos;
  document.head.appendChild(style);
}

// Inicializar cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
  añadirEstilosCSS();
  inicializarPartidasContraibles();
});

console.log("Script de partidas contraíbles cargado correctamente");
