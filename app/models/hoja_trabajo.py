# app/models/hoja_trabajo.py
from app import db
from datetime import datetime
from app.models.proveedor import Proveedor

class HojaTrabajo(db.Model):
    __tablename__ = 'hojas_trabajo'
    
    id = db.Column(db.Integer, primary_key=True)
    id_presupuesto = db.Column(db.Integer, db.ForeignKey('presupuestos.id', ondelete='CASCADE'), nullable=False)
    referencia = db.Column(db.String(50), nullable=False, index=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tipo_via = db.Column(db.String(20))
    nombre_via = db.Column(db.String(100))
    numero_via = db.Column(db.String(10))
    puerta = db.Column(db.String(10))
    codigo_postal = db.Column(db.String(10))
    poblacion = db.Column(db.String(100))
    titulo = db.Column(db.String(200))
    notas = db.Column(db.Text)
    tecnico_encargado = db.Column(db.String(100))
    aprobacion = db.Column(db.String(100))
    fecha_aprobacion = db.Column(db.DateTime)
    estado = db.Column(db.String(50), default='Borrador')
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    presupuesto = db.relationship('Presupuesto', back_populates='hojas_trabajo')
    capitulos = db.relationship('CapituloHoja', back_populates='hoja_trabajo', cascade='all, delete-orphan')
    partidas = db.relationship('PartidaHoja', back_populates='hoja_trabajo', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<HojaTrabajo {self.id}: {self.referencia}>'
    
    @property
    def total(self):
        """Calcula el total de la hoja de trabajo sumando todas las partidas."""
        return sum(partida.final or 0 for partida in self.partidas)
    
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


class CapituloHoja(db.Model):
    __tablename__ = 'capitulos_hojas'
    
    id = db.Column(db.Integer, primary_key=True)
    id_hoja = db.Column(db.Integer, db.ForeignKey('hojas_trabajo.id', ondelete='CASCADE'), nullable=False)
    numero = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.Text)
    
    hoja_trabajo = db.relationship('HojaTrabajo', back_populates='capitulos')
    
    def __repr__(self):
        return f'<CapituloHoja {self.id}: {self.numero} - {self.descripcion}>'


class PartidaHoja(db.Model):
    __tablename__ = 'partidas_hojas'
    
    id = db.Column(db.Integer, primary_key=True)
    id_hoja = db.Column(db.Integer, db.ForeignKey('hojas_trabajo.id', ondelete='CASCADE'), nullable=False)
    capitulo_numero = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.Text)
    unitario = db.Column(db.String(20))
    cantidad = db.Column(db.Float)
    precio = db.Column(db.Float)
    total = db.Column(db.Float)
    margen = db.Column(db.Float)
    final = db.Column(db.Float)
    id_proveedor_principal = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=True)
    precio_proveedor = db.Column(db.Float, nullable=True)
    
    hoja_trabajo = db.relationship('HojaTrabajo', back_populates='partidas')
    proveedor_principal = db.relationship('Proveedor', foreign_keys=[id_proveedor_principal], backref=db.backref('partidas_principales', lazy='dynamic'))
    
    def __repr__(self):
        return f'<PartidaHoja {self.id}: {self.descripcion}>'
    
    def calcular_total(self):
        """Calcula el total (cantidad * precio)"""
        if self.cantidad is not None and self.precio is not None:
            self.total = self.cantidad * self.precio
        else:
            self.total = 0
        return self.total
    
    def calcular_final(self):
        """Calcula el precio final aplicando el margen"""
        if self.total is not None and self.margen is not None:
            self.final = self.total * (1 + self.margen / 100)
        else:
            self.final = self.total or 0
        return self.final