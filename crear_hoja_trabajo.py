#!/usr/bin/env python
"""
Script para crear una hoja de trabajo directamente en la base de datos.
Evita los problemas con SQLAlchemy insertando directamente en SQLite.
"""

import os
import sys
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

def main():
    """Función principal para crear una hoja de trabajo."""
    parser = argparse.ArgumentParser(description='Crear una hoja de trabajo a partir de un presupuesto')
    parser.add_argument('id_presupuesto', type=int, help='ID del presupuesto base')
    args = parser.parse_args()
    
    print(f"\n===== CREANDO HOJA DE TRABAJO PARA PRESUPUESTO #{args.id_presupuesto} =====\n")
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener la ruta de la base de datos desde .env
    db_path = os.environ.get('DB_PATH', 'instance/app.db')
    
    # Convertir a ruta absoluta si es relativa
    if not os.path.isabs(db_path):
        base_dir = Path(__file__).resolve().parent
        db_path = str(base_dir / db_path)
    
    print(f"Ruta de la base de datos: {db_path}")
    
    # Verificar si existe
    if not os.path.exists(db_path):
        print("Error: La base de datos no existe.")
        return 1
    
    # Conectar a la base de datos
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar si el presupuesto existe
        cursor.execute("SELECT * FROM presupuestos WHERE id = ?", (args.id_presupuesto,))
        presupuesto = cursor.fetchone()
        
        if not presupuesto:
            print(f"Error: No se encontró el presupuesto con ID {args.id_presupuesto}")
            return 1
        
        # Generar referencia
        referencia = f"{presupuesto['referencia']}HT"
        
        # Verificar si ya existe una hoja con esa referencia
        cursor.execute("SELECT COUNT(*) as count FROM hojas_trabajo WHERE referencia = ?", (referencia,))
        if cursor.fetchone()['count'] > 0:
            print(f"Error: Ya existe una hoja de trabajo con la referencia {referencia}")
            return 1
        
        # Crear la hoja de trabajo
        fecha_actual = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO hojas_trabajo (
                id_presupuesto, referencia, fecha, tipo_via, nombre_via, numero_via, 
                puerta, codigo_postal, poblacion, titulo, notas, tecnico_encargado, 
                estado, fecha_modificacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            presupuesto['id'],
            referencia,
            fecha_actual,
            presupuesto['tipo_via'],
            presupuesto['nombre_via'],
            presupuesto['numero_via'],
            presupuesto['puerta'],
            presupuesto['codigo_postal'],
            presupuesto['poblacion'],
            f"Hoja de trabajo para {presupuesto['titulo'] or referencia}",
            "",
            presupuesto['tecnico_encargado'] or "Sin asignar",
            "Borrador",
            fecha_actual
        ))
        
        # Obtener el ID de la hoja creada
        id_hoja = cursor.lastrowid
        print(f"Hoja de trabajo creada con ID: {id_hoja}, Referencia: {referencia}")
        
        # Obtener capítulos del presupuesto
        cursor.execute("SELECT * FROM capitulos WHERE id_presupuesto = ?", (args.id_presupuesto,))
        capitulos = cursor.fetchall()
        
        print(f"Copiando {len(capitulos)} capítulos...")
        
        # Insertar capítulos
        for capitulo in capitulos:
            cursor.execute("""
                INSERT INTO capitulos_hojas (id_hoja, numero, descripcion)
                VALUES (?, ?, ?)
            """, (
                id_hoja,
                capitulo['numero'],
                capitulo['descripcion']
            ))
        
        # Obtener partidas del presupuesto
        cursor.execute("SELECT * FROM partidas WHERE id_presupuesto = ?", (args.id_presupuesto,))
        partidas = cursor.fetchall()
        
        print(f"Copiando {len(partidas)} partidas...")
        
        # Insertar partidas
        for partida in partidas:
            cursor.execute("""
                INSERT INTO partidas_hojas (
                    id_hoja, capitulo_numero, descripcion, unitario, 
                    cantidad, precio, total, margen, final
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_hoja,
                partida['capitulo_numero'],
                partida['descripcion'],
                partida['unitario'],
                partida['cantidad'],
                partida['precio'],
                partida['total'],
                partida['margen'],
                partida['final']
            ))
        
        # Confirmar cambios
        conn.commit()
        
        print("\n¡Hoja de trabajo creada exitosamente!")
        print(f"Puede acceder a ella en: http://localhost:5000/hojas_trabajo/editar/{id_hoja}")
        return 0
        
    except sqlite3.Error as e:
        print(f"Error de base de datos: {e}")
        return 1
    except Exception as e:
        print(f"Error general: {e}")
        return 1
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    sys.exit(main())
