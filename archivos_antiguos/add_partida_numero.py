"""
Script para agregar el campo numero a la tabla partidas y actualizar las partidas existentes
siguiendo el formato de numeración automática (capítulo.secuencia)
"""
import os
import sys
from sqlalchemy import create_engine, Column, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from app import db
from app.models.presupuesto import Presupuesto, Capitulo, Partida

def add_numero_column():
    """Añade la columna numero a la tabla partidas si no existe"""
    try:
        # Verificar si la columna ya existe
        inspector = db.inspect(db.engine)
        columns = [column['name'] for column in inspector.get_columns('partidas')]
        
        if 'numero' not in columns:
            print("Agregando columna 'numero' a la tabla partidas...")
            # Agregar la columna a la tabla existente
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE partidas ADD COLUMN numero VARCHAR(20)"))
            print("Columna agregada exitosamente.")
        else:
            print("La columna 'numero' ya existe en la tabla partidas.")
        
        return True
    except Exception as e:
        print(f"Error al agregar columna: {str(e)}")
        return False

def update_partidas_numeros():
    """Actualiza los números de partidas existentes con el formato capítulo.secuencia"""
    try:
        # Obtener todos los presupuestos
        presupuestos = Presupuesto.query.all()
        
        for presupuesto in presupuestos:
            print(f"Procesando presupuesto: {presupuesto.referencia}")
            
            # Organizar partidas por capítulo
            capitulos_nums = set([p.capitulo_numero for p in presupuesto.partidas])
            
            for cap_num in capitulos_nums:
                # Ordenar partidas por ID para asignar números secuenciales
                partidas = Partida.query.filter_by(
                    id_presupuesto=presupuesto.id, 
                    capitulo_numero=cap_num
                ).order_by(Partida.id).all()
                
                # Asignar números en formato x.y
                for i, partida in enumerate(partidas, 1):
                    partida.numero = f"{cap_num}.{i}"
                    print(f"  Asignando número {partida.numero} a partida {partida.id}")
        
        # Guardar cambios
        db.session.commit()
        print("Actualización de números de partidas completada.")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar números de partidas: {str(e)}")
        return False

if __name__ == "__main__":
    print("Iniciando actualización de la estructura de la base de datos...")
    
    # Agregar columna si no existe
    if add_numero_column():
        # Actualizar números de partidas existentes
        update_partidas_numeros()
    
    print("Proceso completado.")
