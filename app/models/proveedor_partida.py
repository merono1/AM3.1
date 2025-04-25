# app/models/proveedor_partida.py
from app import db
from datetime import datetime

class ProveedorPartida(db.Model):
    __tablename__ = 'proveedores_partidas'
    
    id = db.Column(db.Integer, primary_key=True)
    id_partida = db.Column(db.Integer, db.ForeignKey('partidas_hojas.id', ondelete='CASCADE'), nullable=False)
    id_proveedor = db.Column(db.Integer, db.ForeignKey('proveedores.id', ondelete='CASCADE'), nullable=False)
    unitario = db.Column(db.String(10))  # ML, M2, M3, PA, UD, etc.
    cantidad = db.Column(db.Float, default=1)
    precio = db.Column(db.Float)
    margen_proveedor = db.Column(db.Float)
    final_proveedor = db.Column(db.Float)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)
    notas = db.Column(db.Text)
    estado = db.Column(db.String(50), default='Pendiente') # Pendiente, Aceptado, Rechazado, Completado
    
    # Relaciones
    partida = db.relationship('PartidaHoja', backref=db.backref('proveedores_asignados', cascade='all, delete-orphan'))
    proveedor = db.relationship('Proveedor', backref=db.backref('partidas_asignadas', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ProveedorPartida {self.id}: Partida {self.id_partida} - Proveedor {self.id_proveedor}>'        
        
    def calcular_final_proveedor(self):
        """Calcula el precio final del proveedor aplicando el margen"""
        cantidad = self.cantidad or 1
        if self.precio is not None and self.margen_proveedor is not None:
            # Primero calculamos el total (precio * cantidad)
            total = self.precio * cantidad
            # Luego aplicamos el margen
            self.final_proveedor = total * (1 + self.margen_proveedor / 100)
        else:
            self.final_proveedor = (self.precio or 0) * cantidad
        return self.final_proveedor