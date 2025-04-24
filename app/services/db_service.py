"""
Servicio para operaciones de base de datos.
Este módulo provee funciones genéricas para realizar operaciones CRUD en la base de datos.
"""

from app import db
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_all(model, order_by=None):
    """
    Obtiene todos los registros de un modelo específico.
    
    Args:
        model: El modelo de SQLAlchemy
        order_by: Campo opcional para ordenar los resultados
        
    Returns:
        Lista de instancias del modelo
    """
    try:
        if order_by:
            return model.query.order_by(order_by).all()
        return model.query.all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de {model.__name__}: {str(e)}")
        return []

def get_by_id(model, id):
    """
    Obtiene un registro por su ID.
    
    Args:
        model: El modelo de SQLAlchemy
        id: El ID del registro a buscar
        
    Returns:
        Instancia del modelo o None si no se encuentra
    """
    try:
        return model.query.get(id)
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener {model.__name__} con ID {id}: {str(e)}")
        return None

def create(model, data):
    """
    Crea un nuevo registro en la base de datos.
    
    Args:
        model: El modelo de SQLAlchemy
        data: Diccionario con los datos a insertar
        
    Returns:
        La instancia creada si se realizó correctamente, None en caso contrario
    """
    try:
        instance = model(**data)
        db.session.add(instance)
        db.session.commit()
        return instance
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error al crear {model.__name__}: {str(e)}")
        raise e

def update(model, id, data):
    """
    Actualiza un registro existente.
    
    Args:
        model: El modelo de SQLAlchemy
        id: ID del registro a actualizar
        data: Diccionario con los datos a actualizar
        
    Returns:
        La instancia actualizada si se realizó correctamente, None en caso contrario
    """
    try:
        instance = get_by_id(model, id)
        if not instance:
            return None
            
        for key, value in data.items():
            setattr(instance, key, value)
            
        db.session.commit()
        return instance
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error al actualizar {model.__name__} con ID {id}: {str(e)}")
        raise e

def delete(model, id):
    """
    Elimina un registro de la base de datos.
    
    Args:
        model: El modelo de SQLAlchemy
        id: ID del registro a eliminar
        
    Returns:
        True si se eliminó correctamente, False en caso contrario
    """
    try:
        instance = get_by_id(model, id)
        if not instance:
            return False
            
        db.session.delete(instance)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error al eliminar {model.__name__} con ID {id}: {str(e)}")
        raise e

def get_filtered(model, **filters):
    """
    Obtiene registros filtrados por los criterios proporcionados.
    
    Args:
        model: El modelo de SQLAlchemy
        **filters: Filtros a aplicar (campo=valor)
        
    Returns:
        Lista de instancias del modelo que cumplen los filtros
    """
    try:
        query = model.query
        for attr, value in filters.items():
            if hasattr(model, attr):
                query = query.filter(getattr(model, attr) == value)
        return query.all()
    except SQLAlchemyError as e:
        logger.error(f"Error al filtrar {model.__name__}: {str(e)}")
        return []

def get_paginated(model, page=1, per_page=10, order_by=None):
    """
    Obtiene registros paginados.
    
    Args:
        model: El modelo de SQLAlchemy
        page: Número de página (empezando por 1)
        per_page: Número de registros por página
        order_by: Campo opcional para ordenar los resultados
        
    Returns:
        Objeto de paginación de SQLAlchemy
    """
    try:
        if order_by:
            return model.query.order_by(order_by).paginate(page=page, per_page=per_page, error_out=False)
        return model.query.paginate(page=page, per_page=per_page, error_out=False)
    except SQLAlchemyError as e:
        logger.error(f"Error al paginar {model.__name__}: {str(e)}")
        return None