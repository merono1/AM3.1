# app/services/export_service.py
import csv
import io
import tempfile
import zipfile
import json
import xlsxwriter
from datetime import datetime

def exportar_a_csv(data, headers=None):
    """
    Exporta datos a un archivo CSV.
    
    Args:
        data: Lista de diccionarios o lista de listas con los datos a exportar
        headers: Lista con las cabeceras (si data es lista de listas)
        
    Returns:
        Ruta al archivo CSV generado
    """
    output = io.StringIO()
    
    if headers and isinstance(data[0], list):
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(headers)
        writer.writerows(data)
    elif isinstance(data[0], dict):
        headers = headers or data[0].keys()
        writer = csv.DictWriter(output, fieldnames=headers, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        writer.writerows(data)
    
    # Guardar en archivo temporal
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w')
    temp_file.write(output.getvalue())
    temp_file.close()
    
    return temp_file.name

def exportar_a_excel(data, sheet_name='Datos', headers=None):
    """
    Exporta datos a un archivo Excel.
    
    Args:
        data: Lista de diccionarios o lista de listas con los datos a exportar
        sheet_name: Nombre de la hoja de cálculo
        headers: Lista con las cabeceras (opcional)
        
    Returns:
        Ruta al archivo Excel generado
    """
    # Crear archivo temporal
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    temp_file.close()
    
    # Crear workbook
    workbook = xlsxwriter.Workbook(temp_file.name)
    worksheet = workbook.add_worksheet(sheet_name)
    
    # Definir formatos
    header_format = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#D3D3D3'
    })
    
    cell_format = workbook.add_format({
        'border': 1
    })
    
    # Escribir datos
    if isinstance(data[0], dict):
        headers = headers or list(data[0].keys())
        
        # Escribir cabeceras
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Escribir datos
        for row, item in enumerate(data, start=1):
            for col, key in enumerate(headers):
                worksheet.write(row, col, item.get(key, ''), cell_format)
    else:
        # Escribir cabeceras si existen
        if headers:
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
        
        # Determinar fila de inicio
        start_row = 1 if headers else 0
        
        # Escribir datos
        for row, item in enumerate(data, start=start_row):
            for col, value in enumerate(item):
                worksheet.write(row, col, value, cell_format)
    
    # Ajustar anchos de columna
    for col_num, _ in enumerate(headers if headers else data[0]):
        worksheet.set_column(col_num, col_num, 15)
    
    workbook.close()
    
    return temp_file.name

def exportar_a_json(data):
    """
    Exporta datos a un archivo JSON.
    
    Args:
        data: Datos a exportar en formato compatible con JSON
        
    Returns:
        Ruta al archivo JSON generado
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w')
    json.dump(data, temp_file, indent=2, default=str)
    temp_file.close()
    
    return temp_file.name

def exportar_multiples_archivos(data_dict, formato='csv'):
    """
    Exporta múltiples conjuntos de datos a un archivo ZIP.
    
    Args:
        data_dict: Diccionario con {nombre_archivo: datos}
        formato: Formato de los archivos ('csv', 'excel', 'json')
        
    Returns:
        Ruta al archivo ZIP generado
    """
    # Crear archivo ZIP temporal
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_zip.close()
    
    with zipfile.ZipFile(temp_zip.name, 'w') as zipf:
        for filename, data in data_dict.items():
            if formato == 'csv':
                temp_file = exportar_a_csv(data)
                zipf.write(temp_file, f"{filename}.csv")
            elif formato == 'excel':
                temp_file = exportar_a_excel(data, sheet_name=filename)
                zipf.write(temp_file, f"{filename}.xlsx")
            elif formato == 'json':
                temp_file = exportar_a_json(data)
                zipf.write(temp_file, f"{filename}.json")
    
    return temp_zip.name