"""
Script para corregir el problema con el cálculo del margen medio en presupuestos.
El problema es que el margen medio no se actualiza correctamente al cambiar los márgenes
de las partidas individuales y al aplicar el margen a todas las partidas.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys

# Función para modificar el archivo presupuesto_routes.py
def corregir_aplicar_margen_todas():
    ruta_archivo = os.path.join('app', 'routes', 'presupuesto_routes.py')
    
    # Leer el contenido actual
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar la función aplicar_margen_todas
    inicio_funcion = contenido.find("@presupuestos_bp.route('/aplicar-margen-todas/")
    if inicio_funcion == -1:
        print("No se encontró la función aplicar_margen_todas en el archivo.")
        return False
    
    # Buscar el bloque donde se actualizan las partidas
    bloque_actualizar = contenido.find("# Aplicar el margen a todas las partidas", inicio_funcion)
    if bloque_actualizar == -1:
        print("No se encontró el bloque para actualizar partidas.")
        return False
    
    fin_bloque = contenido.find("# Guardar los cambios", bloque_actualizar)
    if fin_bloque == -1:
        print("No se encontró el final del bloque para actualizar partidas.")
        return False
    
    # Código original a reemplazar
    codigo_original = contenido[bloque_actualizar:fin_bloque]
    
    # Nuevo código corregido
    codigo_nuevo = """        # Aplicar el margen a todas las partidas
        partidas = Partida.query.filter_by(id_presupuesto=id).all()
        for partida in partidas:
            partida.margen = nuevo_margen
            if partida.total is not None:
                partida.final = partida.total * (1 + nuevo_margen / 100)
            else:
                # Si el total es None, calcular basado en cantidad y precio
                cantidad = partida.cantidad or 0
                precio = partida.precio or 0
                partida.total = cantidad * precio
                partida.final = partida.total * (1 + nuevo_margen / 100)
        
"""
    
    # Reemplazar el código
    contenido_nuevo = contenido.replace(codigo_original, codigo_nuevo)
    
    # Guardar el archivo modificado
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.write(contenido_nuevo)
    
    print(f"✅ Función aplicar_margen_todas corregida en {ruta_archivo}")
    return True

# Función para corregir el cálculo del margen medio en el template
def corregir_template_margen_medio():
    ruta_archivo = os.path.join('app', 'templates', 'presupuestos', 'editar_pres.html')
    
    # Leer el contenido actual
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar la función calcularMargenMedio en el JavaScript
    inicio_funcion = contenido.find("function calcularMargenMedio() {")
    if inicio_funcion == -1:
        print("No se encontró la función calcularMargenMedio en el template.")
        return False
    
    fin_funcion = contenido.find("}", inicio_funcion)
    fin_funcion = contenido.find("}", fin_funcion + 1)  # Buscar el final del bloque completo
    if fin_funcion == -1:
        print("No se encontró el final de la función calcularMargenMedio.")
        return False
    
    # Código original a reemplazar
    codigo_original = contenido[inicio_funcion:fin_funcion+1]
    
    # Nuevo código corregido para calcular el margen medio correctamente
    codigo_nuevo = """function calcularMargenMedio() {
        if (partidas.length === 0) {
            document.getElementById('margen_medio').value = '40.00';
            document.getElementById('margen_medio_valor').textContent = '40.00 %';
            return 40;
        }
        
        let totalMargenes = 0;
        let totalPesos = 0;
        
        // Calculamos un margen medio ponderado por el valor final de cada partida
        for (const partida of partidas) {
            if (partida.margen !== null && !isNaN(partida.margen) && 
                partida.final !== null && !isNaN(partida.final) && partida.final > 0) {
                totalMargenes += parseFloat(partida.margen) * parseFloat(partida.final);
                totalPesos += parseFloat(partida.final);
            }
            else if (partida.margen !== null && !isNaN(partida.margen) && 
                     partida.total !== null && !isNaN(partida.total) && partida.total > 0) {
                const final = parseFloat(partida.total) * (1 + parseFloat(partida.margen) / 100);
                totalMargenes += parseFloat(partida.margen) * final;
                totalPesos += final;
            }
        }
        
        // Calcular el margen medio ponderado
        let margenMedio = 40; // Valor por defecto
        if (totalPesos > 0) {
            margenMedio = totalMargenes / totalPesos;
        }
        
        console.log('Total margenes ponderados:', totalMargenes);
        console.log('Total pesos:', totalPesos);
        console.log('Margen medio calculado:', margenMedio);
        
        // Actualizar el campo de entrada con el valor del margen medio
        document.getElementById('margen_medio').value = margenMedio.toFixed(2);
        
        // Actualizar el valor en la tabla de resumen si existe
        const margenMedioValor = document.getElementById('margen_medio_valor');
        if (margenMedioValor) {
            margenMedioValor.textContent = margenMedio.toFixed(2) + ' %';
        }
        
        return margenMedio;
    }"""
    
    # Reemplazar el código
    contenido_nuevo = contenido.replace(codigo_original, codigo_nuevo)
    
    # Guardar el archivo modificado
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.write(contenido_nuevo)
    
    print(f"✅ Función calcularMargenMedio corregida en {ruta_archivo}")
    return True

# Función principal
def main():
    print("Iniciando corrección del cálculo de margen medio en presupuestos...")
    
    # Corregir la función aplicar_margen_todas
    if not corregir_aplicar_margen_todas():
        print("❌ No se pudo corregir la función aplicar_margen_todas.")
        return False
    
    # Corregir el cálculo del margen medio en el template
    if not corregir_template_margen_medio():
        print("❌ No se pudo corregir el cálculo del margen medio en el template.")
        return False
    
    print("✅ Correcciones completadas con éxito.")
    print("Para que los cambios surtan efecto, reinicia la aplicación.")
    return True

if __name__ == "__main__":
    main()
