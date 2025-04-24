# app/models/proyecto.py
from app import db
from datetime import datetime

class Proyecto(db.Model):
    __tablename__ = 'proyectos'
    
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id', ondelete='CASCADE'), nullable=True)  # Cambiado a nullable=True
    tipo_proyecto = db.Column(db.String(50), nullable=True)
    tipo_via = db.Column(db.String(20), nullable=True)  # Añadido campo tipo_via
    calle = db.Column(db.String(100), nullable=True)  # Mantenido por compatibilidad
    nombre_via = db.Column(db.String(100), nullable=True)
    numero = db.Column(db.String(10), nullable=True)
    puerta = db.Column(db.String(10), nullable=True)
    codigo_postal = db.Column(db.String(10), nullable=True)
    poblacion = db.Column(db.String(100), nullable=True)
    nombre_proyecto = db.Column(db.String(200), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    referencia = db.Column(db.String(50), unique=True, nullable=True)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    estado = db.Column(db.String(50), default='Activo', nullable=True)
    
    # Relaciones
    cliente = db.relationship('Cliente', back_populates='proyectos')
    presupuestos = db.relationship('Presupuesto', back_populates='proyecto', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Proyecto {self.id}: {self.nombre_proyecto or self.referencia or "Sin nombre"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_cliente': self.id_cliente,
            'tipo_proyecto': self.tipo_proyecto,
            'tipo_via': self.tipo_via,
            'calle': self.calle,
            'nombre_via': self.nombre_via,
            'numero': self.numero,
            'puerta': self.puerta,
            'codigo_postal': self.codigo_postal,
            'poblacion': self.poblacion,
            'nombre_proyecto': self.nombre_proyecto,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'referencia': self.referencia,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None,
            'estado': self.estado
        }
    
    @property
    def direccion_completa(self):
        componentes = []
        if self.tipo_via:
            componentes.append(self.tipo_via)
        if self.calle:
            componentes.append(self.calle)
        elif self.nombre_via:
            componentes.append(self.nombre_via)
        if self.numero:
            componentes.append(self.numero)
        if self.puerta:
            componentes.append(self.puerta)
            
        direccion = ' '.join(componentes)
        
        if self.codigo_postal or self.poblacion:
            cp_poblacion = []
            if self.codigo_postal:
                cp_poblacion.append(self.codigo_postal)
            if self.poblacion:
                cp_poblacion.append(self.poblacion)
            direccion += f', {" ".join(cp_poblacion)}'
            
        return direccion