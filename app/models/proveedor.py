# app/models/proveedor.py
from app import db
from datetime import datetime

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.Integer, primary_key=True)
    referencia = db.Column(db.String(50), unique=True, index=True)
    tipo = db.Column(db.String(50))
    nombre = db.Column(db.String(100), nullable=False)
    razon_social = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    codigo_postal = db.Column(db.String(10))
    localidad = db.Column(db.String(100))
    provincia = db.Column(db.String(100))
    pais = db.Column(db.String(100))
    telefono1 = db.Column(db.String(20))
    telefono2 = db.Column(db.String(20))
    telefono3 = db.Column(db.String(20))
    telefono4 = db.Column(db.String(20))
    email1 = db.Column(db.String(100))
    email2 = db.Column(db.String(100))
    contacto = db.Column(db.String(100))
    contacto_telefono1 = db.Column(db.String(20))
    contacto_telefono2 = db.Column(db.String(20))
    contacto_email = db.Column(db.String(100))
    fecha_alta = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    facturas = db.Column(db.Integer, default=0)
    especialidad = db.Column(db.String(100), default='Ninguna')
    notas = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Proveedor {self.id}: {self.nombre}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'referencia': self.referencia,
            'tipo': self.tipo,
            'nombre': self.nombre,
            'razon_social': self.razon_social,
            'direccion': self.direccion,
            'codigo_postal': self.codigo_postal,
            'localidad': self.localidad,
            'provincia': self.provincia,
            'pais': self.pais,
            'telefono1': self.telefono1,
            'telefono2': self.telefono2,
            'telefono3': self.telefono3,
            'telefono4': self.telefono4,
            'email1': self.email1,
            'email2': self.email2,
            'contacto': self.contacto,
            'contacto_telefono1': self.contacto_telefono1,
            'contacto_telefono2': self.contacto_telefono2,
            'contacto_email': self.contacto_email,
            'fecha_alta': self.fecha_alta.isoformat() if self.fecha_alta else None,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None,
            'facturas': self.facturas,
            'especialidad': self.especialidad,
            'notas': self.notas
        }