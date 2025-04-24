"""
Script simple para probar la generación del PDF mínimo mejorado
"""

import os
import tempfile

# Simular objetos mínimos necesarios
class PresupuestoSimulado:
    def __init__(self):
        self.referencia = "2025-0001-P02"
        self.fecha = None
        self.tipo_via = "Avenida"
        self.nombre_via = "nolase"
        self.numero_via = "52"
        self.titulo = "poner airecito"

class ClienteSimulado:
    def __init__(self):
        self.nombre = "Juan Vicente"

class ProyectoSimulado:
    def __init__(self):
        self.nombre_proyecto = "Proyecto de prueba"
        self.referencia = "2025-0001"

class CapituloSimulado:
    def __init__(self, numero, descripcion):
        self.numero = numero
        self.descripcion = descripcion

class PartidaSimulada:
    def __init__(self, cap_num, numero, descripcion, unitario="ud", cantidad=1, precio=100, margen=40):
        self.capitulo_numero = cap_num
        self.numero = f"{cap_num}.{numero}"
        self.descripcion = descripcion
        self.unitario = unitario
        self.cantidad = cantidad
        self.precio = precio
        self.total = cantidad * precio
        self.margen = margen
        self.final = self.total * (1 + margen/100)

# Crear datos de prueba
def crear_datos_prueba():
    presupuesto = PresupuestoSimulado()
    cliente = ClienteSimulado()
    proyecto = ProyectoSimulado()
    
    # Crear capítulos
    capitulos = [
        CapituloSimulado("1", "Trabajos preliminares")
    ]
    
    # Crear partidas
    partidas = [
        PartidaSimulada("1", "1", "Partida extensa de trabajos previos en la demolición de un baño", cantidad=2, precio=3809.295)
    ]
    
    # Organizar partidas por capítulo
    partidas_por_capitulo = {}
    for partida in partidas:
        if partida.capitulo_numero not in partidas_por_capitulo:
            partidas_por_capitulo[partida.capitulo_numero] = []
        partidas_por_capitulo[partida.capitulo_numero].append(partida)
    
    return presupuesto, cliente, proyecto, capitulos, partidas_por_capitulo

# Función simplificada para generar PDF mínimo
def generar_pdf_minimo(presupuesto, cliente, capitulos, partidas_por_capitulo):
    # Crear un archivo temporal para el PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.close()
    
    # Calcular el total del presupuesto
    total_presupuesto = sum((p.final or 0) for partidas in partidas_por_capitulo.values() for p in partidas)
    
    # Evaluar variables primero (importante para evitar errores de formato)
    ref = presupuesto.referencia
    cli = cliente.nombre
    dir_tipo = presupuesto.tipo_via or ''
    dir_nombre = presupuesto.nombre_via or ''
    dir_numero = presupuesto.numero_via or ''
    titulo = presupuesto.titulo or ''
    total_format = "{:.2f}".format(total_presupuesto)
    
    # Contenido del PDF mínimo
    pdf_content = f'''%PDF-1.7
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica-Bold>>>>/ProcSet[/PDF/Text]>>/Contents 4 0 R>>endobj
4 0 obj<</Length 2000>>stream
BT /F1 14 Tf 50 750 Td (PRESUPUESTO) Tj ET
BT /F1 12 Tf 50 730 Td (AM CONSTRUCCION) Tj ET
BT /F1 10 Tf 50 700 Td (Referencia: {ref}) Tj ET
BT /F1 10 Tf 50 680 Td (Cliente: {cli}) Tj ET
BT /F1 10 Tf 50 640 Td (Direccion: {dir_tipo} {dir_nombre} {dir_numero}) Tj ET
BT /F1 10 Tf 50 620 Td (Titulo: {titulo}) Tj ET
BT /F1 11 Tf 50 590 Td (RESUMEN DE CAPITULOS) Tj ET
'''
    
    # Agregar resumen de capítulos
    y_pos = 570
    for capitulo in capitulos:
        partidas = partidas_por_capitulo.get(capitulo.numero, [])
        subtotal_capitulo = sum((p.final or 0) for p in partidas)
        
        cap_num = capitulo.numero
        cap_desc = capitulo.descripcion
        cap_subtotal = "{:.2f}".format(subtotal_capitulo)
        
        pdf_content += f'BT /F1 10 Tf 70 {y_pos} Td (Cap. {cap_num}: {cap_desc}) Tj ET\n'
        y_pos -= 20
        pdf_content += f'BT /F1 10 Tf 350 {y_pos+20} Td ({cap_subtotal} EUR) Tj ET\n'
        
        # Mostrar partidas
        for i, partida in enumerate(partidas[:3]):
            if hasattr(partida, 'numero') and '.' in str(partida.numero):
                num_partida = partida.numero.split('.')[-1]
            else:
                num_partida = "X"
                
            desc = (partida.descripcion or '')[:40]
            part_num = f"{cap_num}.{num_partida}"
            
            pdf_content += f'BT /F1 9 Tf 90 {y_pos} Td ({part_num} {desc}) Tj ET\n'
            y_pos -= 15
    
    # Agregar el total del presupuesto
    pdf_content += f'''
BT /F1 11 Tf 70 {y_pos-30} Td (TOTAL PRESUPUESTO:) Tj ET
BT /F1 11 Tf 350 {y_pos-30} Td ({total_format} EUR) Tj ET
BT /F1 10 Tf 350 {y_pos-50} Td ((IVA no incluido)) Tj ET
BT /F1 8 Tf 100 100 Td (C/ Juan de Garay 88 bajo. 46017 Valencia. CIF: B98833773) Tj ET
BT /F1 8 Tf 100 80 Td (Email: mariano.direccion@gmail.com   Tel: 633327187) Tj ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000010 00000 n
0000000053 00000 n
0000000102 00000 n
0000000245 00000 n
trailer<</Size 5/Root 1 0 R>>
startxref
2297
%%EOF
'''
    
    # Codificar a bytes y escribir el archivo
    minimal_pdf = pdf_content.encode('utf-8')
    with open(temp_file.name, 'wb') as f:
        f.write(minimal_pdf)
    
    return temp_file.name

# Ejecutar prueba
if __name__ == "__main__":
    presupuesto, cliente, proyecto, capitulos, partidas_por_capitulo = crear_datos_prueba()
    
    print(f"Generando PDF mínimo para el presupuesto: {presupuesto.referencia}")
    
    # Generar PDF con el método mejorado (usando FPDF)
    try:
        from fpdf import FPDF
        
        # Crear PDF mejorado con diseño profesional
        pdf = FPDF()
        pdf.add_page()
        
        # Configurar colores corporativos
        color_verde_oscuro = (0, 100, 0)  # Verde oscuro
        color_verde_claro = (200, 230, 201)  # Verde claro
        color_gris_oscuro = (80, 80, 80)  # Gris oscuro para texto
        color_gris_medio = (150, 150, 150)  # Gris medio para líneas
        color_gris_claro = (240, 240, 240)  # Gris claro para fondos alternos
        
        # Márgenes y configuración
        pdf.set_margins(10, 10, 10)
        pdf.set_auto_page_break(True, 25)  # Espacio para footer
        
        # ----------------------------------------
        # CABECERA CON DISEÑO MEJORADO
        # ----------------------------------------
        # Rectángulo superior con color de fondo
        pdf.set_fill_color(*color_verde_claro)
        pdf.rect(0, 0, 210, 25, 'F')  # Franja superior con color
        
        # Título del documento
        pdf.set_font("Arial", 'B', 18)
        pdf.set_text_color(*color_verde_oscuro)
        pdf.cell(0, 10, txt="PRESUPUESTO", ln=1, align='C')
        pdf.ln(2)
        
        # Logo y nombre empresa (mejorado)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(*color_verde_oscuro)
        pdf.cell(0, 10, txt="AM CONSTRUCCIÓN", ln=1, align='C')
        pdf.set_text_color(0, 0, 0)  # Volver a negro
        
        pdf.ln(5)  # Espacio después de la cabecera
        
        # ----------------------------------------
        # DATOS DE CLIENTE Y PRESUPUESTO
        # ----------------------------------------
        # Cuadro para datos del cliente
        pdf.set_fill_color(*color_gris_claro)
        pdf.rect(10, 35, 190, 30, 'F')
        pdf.set_draw_color(*color_gris_medio)
        pdf.rect(10, 35, 190, 30, 'D')  # Borde
        
        # Columna 1: Cliente y Referencia
        pdf.set_xy(15, 38)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(*color_gris_oscuro)
        pdf.cell(25, 6, txt="Cliente:", ln=0)
        pdf.set_font("Arial", '', 10)
        pdf.cell(70, 6, txt=f"{cliente.nombre or ''}", ln=1)
        
        pdf.set_xy(15, 46)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(25, 6, txt="N° Ref.:", ln=0)
        pdf.set_font("Arial", '', 10)
        pdf.cell(70, 6, txt=f"{presupuesto.referencia}", ln=1)
        
        # Columna 2: Dirección y Fecha
        pdf.set_xy(110, 38)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(25, 6, txt="Dirección:", ln=0)
        pdf.set_font("Arial", '', 10)
        dir_completa = f"{presupuesto.tipo_via or ''} {presupuesto.nombre_via or ''} {presupuesto.numero_via or ''}"
        pdf.cell(65, 6, txt=dir_completa.strip(), ln=1)
        
        pdf.set_xy(110, 46)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(25, 6, txt="Fecha:", ln=0)
        pdf.set_font("Arial", '', 10)
        fecha_str = presupuesto.fecha.strftime('%d/%m/%Y') if presupuesto.fecha else '-'
        pdf.cell(65, 6, txt=fecha_str, ln=1)
        
        pdf.ln(10)  # Espacio después de datos cliente
        
        # ----------------------------------------
        # TÍTULO DEL PRESUPUESTO
        # ----------------------------------------
        if presupuesto.titulo:
            pdf.set_fill_color(*color_verde_claro)  # Fondo verde claro
            pdf.set_draw_color(*color_verde_oscuro)  # Borde verde oscuro
            pdf.rect(10, 70, 190, 12, 'FD')  # Rectángulo con fondo y borde
            
            pdf.set_xy(10, 71)
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(*color_verde_oscuro)
            pdf.cell(190, 10, txt=f"{presupuesto.titulo}", ln=1, align='C')
            pdf.ln(5)
        else:
            pdf.ln(3)
        
        # ----------------------------------------
        # CAPÍTULOS Y PARTIDAS
        # ----------------------------------------
        pdf.set_text_color(0, 0, 0)  # Texto negro para el contenido
        
        for capitulo in capitulos:
            # Encabezado de capítulo con diseño destacado
            pdf.set_fill_color(*color_verde_oscuro)
            pdf.set_text_color(255, 255, 255)  # Texto blanco
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(190, 8, txt=f"CAPÍTULO {capitulo.numero}: {capitulo.descripcion}", ln=1, align='L', fill=True)
            pdf.set_text_color(0, 0, 0)  # Volver a negro
            
            partidas = partidas_por_capitulo.get(capitulo.numero, [])
            
            # Cabecera de tabla de partidas con diseño mejorado
            pdf.set_fill_color(*color_gris_claro)  # Gris claro
            pdf.set_font("Arial", 'B', 9)
            pdf.cell(15, 7, txt="Núm.", border=1, ln=0, fill=True, align='C')
            pdf.cell(15, 7, txt="UD", border=1, ln=0, fill=True, align='C')
            pdf.cell(90, 7, txt="Descripción", border=1, ln=0, fill=True, align='C')
            pdf.cell(20, 7, txt="Cantidad", border=1, ln=0, fill=True, align='C')
            pdf.cell(25, 7, txt="Precio €", border=1, ln=0, fill=True, align='C')
            pdf.cell(25, 7, txt="Total €", border=1, ln=1, fill=True, align='C')
            
            # Filas de partidas con formato alternado
            pdf.set_font("Arial", '', 8)
            subtotal_capitulo = 0
            fill = False
            
            for partida in partidas:
                # Obtener número de partida
                num_partida = partida.numero.split('.')[-1] if '.' in str(partida.numero) else ''
                partida_num = f"{capitulo.numero}.{num_partida}"
                
                # Procesar descripción para texto largo
                desc = partida.descripcion or ''
                desc = desc.replace('<p>', '').replace('</p>', '').replace('<br>', ' ')
                
                # Truncar si es muy largo
                if len(desc) > 60:
                    desc = desc[:57] + "..."
                
                # Color de fondo alternado para las filas
                fill_color = color_gris_claro if fill else (255, 255, 255)
                pdf.set_fill_color(*fill_color)
                
                # Impresiones con formato alternado
                pdf.cell(15, 7, txt=partida_num, border=1, ln=0, fill=fill, align='C')
                pdf.cell(15, 7, txt=partida.unitario or '', border=1, ln=0, fill=fill, align='C')
                pdf.cell(90, 7, txt=desc, border=1, ln=0, fill=fill)
                pdf.cell(20, 7, txt='{:.2f}'.format(partida.cantidad or 0), border=1, ln=0, align='R', fill=fill)
                pdf.cell(25, 7, txt='{:.2f}'.format(partida.precio or 0), border=1, ln=0, align='R', fill=fill)
                
                # Total con formato destacado
                if partida.final:
                    pdf.set_font("Arial", 'B', 8)
                    pdf.cell(25, 7, txt='{:.2f}'.format(partida.final), border=1, ln=1, align='R', fill=fill)
                    pdf.set_font("Arial", '', 8)  # Restaurar fuente normal
                else:
                    pdf.cell(25, 7, txt='0.00', border=1, ln=1, align='R', fill=fill)
                
                subtotal_capitulo += (partida.final or 0)
                fill = not fill  # Alternar colores de fondo
            
            # Subtotal del capítulo con diseño destacado
            pdf.set_fill_color(*color_verde_claro)
            pdf.set_draw_color(*color_verde_oscuro)
            pdf.set_font("Arial", 'B', 10)
            pdf.set_text_color(*color_verde_oscuro)
            pdf.cell(140, 8, txt="Subtotal Capítulo", border=1, ln=0, align='R', fill=True)
            pdf.cell(50, 8, txt='{:.2f} €'.format(subtotal_capitulo), border=1, ln=1, align='R', fill=True)
            
            pdf.set_text_color(0, 0, 0)  # Restaurar color negro
            pdf.ln(5)  # Espacio entre capítulos
        
        # ----------------------------------------
        # RESUMEN DE CAPÍTULOS
        # ----------------------------------------
        pdf.set_fill_color(*color_verde_oscuro)
        pdf.set_text_color(255, 255, 255)  # Texto blanco
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(190, 8, txt="RESUMEN POR CAPÍTULOS", ln=1, align='C', fill=True)
        pdf.set_text_color(0, 0, 0)  # Restaurar color negro
        
        # Tabla de resumen
        pdf.set_fill_color(*color_gris_claro)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(140, 7, txt="Capítulo", border=1, ln=0, fill=True)
        pdf.cell(50, 7, txt="Importe €", border=1, ln=1, fill=True, align='R')
        
        # Filas del resumen
        total_presupuesto = 0
        pdf.set_font("Arial", '', 9)
        fill = False
        
        for capitulo in capitulos:
            fill_color = color_gris_claro if fill else (255, 255, 255)
            pdf.set_fill_color(*fill_color)
            
            partidas = partidas_por_capitulo.get(capitulo.numero, [])
            subtotal_capitulo = sum((p.final or 0) for p in partidas)
            total_presupuesto += subtotal_capitulo
            
            pdf.cell(140, 7, txt=f"Capítulo {capitulo.numero}: {capitulo.descripcion}", border=1, ln=0, fill=fill)
            pdf.cell(50, 7, txt='{:.2f}'.format(subtotal_capitulo), border=1, ln=1, align='R', fill=fill)
            fill = not fill
        
        # Total del presupuesto con diseño destacado
        pdf.set_fill_color(*color_verde_oscuro)
        pdf.set_text_color(255, 255, 255)  # Texto blanco
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(140, 8, txt="TOTAL PRESUPUESTO (IVA no incluido)", border=1, ln=0, align='R', fill=True)
        pdf.cell(50, 8, txt='{:.2f} €'.format(total_presupuesto), border=1, ln=1, align='R', fill=True)
        
        # ----------------------------------------
        # FOOTER CON INFORMACIÓN DE CONTACTO
        # ----------------------------------------
        # Línea divisoria
        pdf.set_draw_color(*color_verde_oscuro)
        pdf.line(10, 270, 200, 270)
        
        # Información de contacto
        pdf.set_y(272)
        pdf.set_text_color(*color_gris_oscuro)
        pdf.set_font("Arial", '', 8)
        pdf.cell(190, 5, txt="C/ Juan de Garay 88 bajo. 46017 Valencia. CIF: B98833773", ln=1, align='C')
        pdf.cell(190, 5, txt="Email: mariano.direccion@gmail.com   Tel: 633327187", ln=1, align='C')
        
        # Numeración de página
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(190, 5, txt=f"Página 1/1", ln=1, align='R')
        
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.close()
        
        # Guardar el PDF
        pdf.output(temp_file.name)
        pdf_file = temp_file.name
        print(f"PDF generado correctamente con FPDF: {pdf_file}")
        
    except Exception as e:
        print(f"Error al generar PDF con FPDF: {e}")
        print("Fallback a método básico")
        # Si falla FPDF, usar el método básico como fallback
        pdf_file = generar_pdf_minimo(presupuesto, cliente, capitulos, partidas_por_capitulo)
    
    # Guardar una copia en una ubicación conocida
    output_dir = os.path.join("app", "static", "pdfs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"presupuesto_test_minimo.pdf")
    
    # Copiar el archivo temporal
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
