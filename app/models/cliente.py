# app/models/cliente.py
from app import db
from datetime import datetime

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo_via = db.Column(db.String(20))
    nombre_via = db.Column(db.String(100))
    numero_via = db.Column(db.String(10))
    puerta = db.Column(db.String(10))
    codigo_postal = db.Column(db.String(10))
    poblacion = db.Column(db.String(100))
    cif_nif = db.Column(db.String(20), index=True)
    telefono1 = db.Column(db.String(20))
    telefono2 = db.Column(db.String(20))
    telefono3 = db.Column(db.String(20))
    telefono4 = db.Column(db.String(20))
    mail1 = db.Column(db.String(100))
    mail2 = db.Column(db.String(100))
    tipo_cliente = db.Column(db.String(50))
    categoria_cliente = db.Column(db.String(50))
    notas = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    proyectos = db.relationship('Proyecto', back_populates='cliente', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Cliente {self.id}: {self.nombre}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo_via': self.tipo_via,
            'nombre_via': self.nombre_via,
            'numero_via': self.numero_via,
            'puerta': self.puerta,
            'codigo_postal': self.codigo_postal,
            'poblacion': self.poblacion,
            'cif_nif': self.cif_nif,
            'telefono1': self.telefono1,
            'telefono2': self.telefono2,
            'telefono3': self.telefono3,
            'telefono4': self.telefono4,
            'mail1': self.mail1,
            'mail2': self.mail2,
            'tipo_cliente': self.tipo_cliente,
            'categoria_cliente': self.categoria_cliente,
            'notas': self.notas,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None
        }
    
    @property
    def direccion_completa(self):
        componentes = []
        if self.tipo_via:
            componentes.append(self.tipo_via)
        if self.nombre_via:
            componentes.append(self.nombre_via)
        if self.numero_via:
            componentes.append(self.numero_via)
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