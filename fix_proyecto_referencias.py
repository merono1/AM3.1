#!/usr/bin/env python
# Script para verificar y actualizar las referencias de proyectos al nuevo formato
from app import create_app, db
from app.models.proyecto import Proyecto
from app.models.cliente import Cliente
from datetime import datetime
import argparse
import sys

app = create_app()

def get_tipo_abreviado(tipo_proyecto):
    """Extrae las letras del tipo de proyecto (primera y tercera)"""
    tipo_abreviado = ''
    if tipo_proyecto and len(tipo_proyecto) >= 3:
        tipo_abreviado = tipo_proyecto[0] + tipo_proyecto[2]
    elif tipo_proyecto and len(tipo_proyecto) >= 1:
        tipo_abreviado = tipo_proyecto[0] + 'X'  # Si el tipo es muy corto
    else:
        tipo_abreviado = 'XX'  # Valor por defecto
        
    return tipo_abreviado.upper()  # Convertir a mayúsculas

def generar_nueva_referencia(proyecto):
    """Genera una nueva referencia para el proyecto siguiendo el nuevo formato"""
    
    if not proyecto.id_cliente:
        return None, "El proyecto no tiene cliente asociado"
    
    # Formatear el número de cliente con tres dígitos
    cliente_formateado = f"{proyecto.id_cliente:03d}"
    
    # Obtener tipo de proyecto abreviado
    tipo_abreviado = get_tipo_abreviado(proyecto.tipo_proyecto)
    
    # Usar fecha de creación original o la actual si no está disponible
    if proyecto.fecha_creacion:
        fecha = proyecto.fecha_creacion
    else:
        fecha = datetime.now()
    
    fecha_formateada = fecha.strftime("%d%m%y")
    
    # Crear la nueva referencia en formato PR001RF-DDMMAA
    nueva_referencia = f"PR{cliente_formateado}{tipo_abreviado}-{fecha_formateada}"
    
    # Verificar si ya existe un proyecto con esta referencia
    proyecto_existente = Proyecto.query.filter_by(referencia=nueva_referencia).first()
    if proyecto_existente and proyecto_existente.id != proyecto.id:
        return None, f"Ya existe un proyecto con la referencia {nueva_referencia}"
    
    return nueva_referencia, None  # Retorna la referencia y None como error

def actualizar_referencias(dry_run=True, force=False):
    """Actualiza todas las referencias de proyectos al nuevo formato"""
    
    with app.app_context():
        proyectos = Proyecto.query.all()
        print(f"Encontrados {len(proyectos)} proyectos en la base de datos.")
        
        actualizados = 0
        errores = 0
        
        for proyecto in proyectos:
            # Verificar si ya tiene el formato correcto (empieza con PR)
            if proyecto.referencia and proyecto.referencia.startswith('PR') and not force:
                print(f"  Proyecto #{proyecto.id} ya tiene el formato correcto: {proyecto.referencia}")
                continue
                
            nueva_referencia, error = generar_nueva_referencia(proyecto)
            
            if error:
                print(f"  Error en proyecto #{proyecto.id} ({proyecto.referencia}): {error}")
                errores += 1
                continue
                
            print(f"  Proyecto #{proyecto.id}: {proyecto.referencia} -> {nueva_referencia}")
            
            if not dry_run:
                proyecto.referencia = nueva_referencia
                db.session.add(proyecto)
                actualizados += 1
        
        if not dry_run and actualizados > 0:
            db.session.commit()
            print(f"\nSe actualizaron {actualizados} referencias de proyectos.")
        else:
            db.session.rollback()
            print(f"\nSimulación completada. {actualizados} referencias se actualizarían.")
            
        if errores > 0:
            print(f"Se encontraron {errores} proyectos con errores que no se pudieron actualizar.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Actualizar referencias de proyectos al nuevo formato')
    parser.add_argument('--apply', action='store_true', help='Aplicar los cambios (sin este parámetro solo muestra lo que haría)')
    parser.add_argument('--force', action='store_true', help='Forzar actualización incluso si el formato parece correcto')
    
    args = parser.parse_args()
    
    print("Iniciando verificación de referencias de proyectos...\n")
    
    try:
        actualizar_referencias(dry_run=not args.apply, force=args.force)
        print("\nProceso completado.")
    except Exception as e:
        print(f"\nError durante la ejecución: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0)
