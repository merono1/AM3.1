"""
Script para generar un PDF de presupuesto de prueba

Este script genera un PDF de prueba utilizando la función generar_pdf_presupuesto.
Además, muestra información detallada sobre el presupuesto que se está utilizando.
"""

import os
import sys
from flask import Flask
from app import create_app, db
from app.models.presupuesto import Presupuesto, Capitulo, Partida
from app.models.proyecto import Proyecto
from app.models.cliente import Cliente
from app.services.pdf_service import generar_pdf_presupuesto

# Crear una aplicación Flask para el contexto
app = create_app()

with app.app_context():
    # Buscar un presupuesto existente
    presupuesto = Presupuesto.query.first()
    
    if not presupuesto:
        print("No hay presupuestos en la base de datos.")
        sys.exit(1)
    
    print(f"Generando PDF para el presupuesto: {presupuesto.referencia}")
    
    # Obtener los datos relacionados
    proyecto = Proyecto.query.get(presupuesto.id_proyecto)
    cliente = Cliente.query.get(proyecto.id_cliente)
    
    # Obtener capítulos y partidas
    capitulos = Capitulo.query.filter_by(id_presupuesto=presupuesto.id).order_by(Capitulo.numero).all()
    partidas = Partida.query.filter_by(id_presupuesto=presupuesto.id).all()
    
    # Organizar partidas por capítulo
    partidas_por_capitulo = {}
    for partida in partidas:
        if partida.capitulo_numero not in partidas_por_capitulo:
            partidas_por_capitulo[partida.capitulo_numero] = []
        partidas_por_capitulo[partida.capitulo_numero].append(partida)
    
    # Verificar que hay datos para procesar
    if not capitulos:
        print("⚠️ Advertencia: No hay capítulos para este presupuesto.")
        
    if not partidas:
        print("⚠️ Advertencia: No hay partidas para este presupuesto.")
    
    # Mostrar información de lo que vamos a procesar
    print(f"\nDatos que se utilizarán en el PDF:")
    print(f"- Presupuesto ID: {presupuesto.id}, Referencia: {presupuesto.referencia}")
    print(f"- Proyecto ID: {proyecto.id}, Referencia: {proyecto.referencia}")
    print(f"- Cliente ID: {cliente.id}, Nombre: {cliente.nombre}")
    print(f"- Número de capítulos: {len(capitulos)}")
    num_partidas = sum(len(partidas) for partidas in partidas_por_capitulo.values())
    print(f"- Número total de partidas: {num_partidas}")
    
    # Generar PDF
    print("\nGenerando PDF...")
    pdf_file = generar_pdf_presupuesto(presupuesto, proyecto, cliente, capitulos, partidas_por_capitulo)
    
    # Guardar una copia en una ubicación conocida
    output_dir = os.path.join("app", "static", "pdfs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"presupuesto_{presupuesto.referencia}.pdf")
    
    # Verificar que el archivo temporal existe
    if not os.path.exists(pdf_file):
        print(f"⚠️ Advertencia: El archivo temporal {pdf_file} no existe.")
        sys.exit(1)
    
    # Copiar el archivo temporal generado
    import shutil
    shutil.copy2(pdf_file, output_path)
    
    if os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"\n✅ PDF generado correctamente:")
        print(f"   - Ruta: {output_path}")
        print(f"   - Tamaño: {size} bytes")
        print(f"   - Archivo temporal: {pdf_file}")
        print("\nAhora puedes abrir el archivo para verificar que se muestran correctamente los datos.")
    else:
        print(f"\n❌ Error: No se pudo generar el PDF en {output_path}")
        print(f"   - Archivo temporal: {pdf_file}")
        print("\nVerifica los logs para más información.")
