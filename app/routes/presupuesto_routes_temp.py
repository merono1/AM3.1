"""
Versión temporal de las rutas de presupuestos para resolver el problema de la columna numero
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.presupuesto import Presupuesto, Capitulo, Partida
from app.models.proyecto import Proyecto
from app.models.cliente import Cliente
from app.services.db_service import get_by_id
from app import db
from datetime import datetime
import re

# Importamos la función alternativa para crear partida
from app.routes.partida_routes_temp import crear_partida_temp

# Copia de la ruta de nueva partida pero modificada para evitar el campo numero
def nueva_partida_temp(id_presupuesto):
    # Llamamos a la función alternativa
    exito = crear_partida_temp(id_presupuesto)
    return redirect(url_for('presupuestos.editar_presupuesto', id=id_presupuesto))
