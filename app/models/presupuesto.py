# app/models/presupuesto.py
from app import db
from datetime import datetime

class Presupuesto(db.Model):
    __tablename__ = 'presupuestos'
    
    id = db.Column(db.Integer, primary_key=True)
    id_proyecto = db.Column(db.Integer, db.ForeignKey('proyectos.id', ondelete='CASCADE'), nullable=False)
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
    estado_workflow = db.Column(db.String(50), default='En estudio')
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    proyecto = db.relationship('Proyecto', back_populates='presupuestos')
    capitulos = db.relationship('Capitulo', back_populates='presupuesto', cascade='all, delete-orphan')
    partidas = db.relationship('Partida', back_populates='presupuesto', cascade='all, delete-orphan')
    hojas_trabajo = db.relationship('HojaTrabajo', back_populates='presupuesto', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Presupuesto {self.id}: {self.referencia}>'
    
    @property
    def total(self):
        """Calcula el total del presupuesto sumando todas las partidas."""
        total_sum = 0
        for partida in self.partidas:
            if partida.final is not None:
                total_sum += partida.final
        return total_sum
    
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


class Capitulo(db.Model):
    __tablename__ = 'capitulos'
    
    id = db.Column(db.Integer, primary_key=True)
    id_presupuesto = db.Column(db.Integer, db.ForeignKey('presupuestos.id', ondelete='CASCADE'), nullable=False)
    numero = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.Text)
    
    presupuesto = db.relationship('Presupuesto', back_populates='capitulos')
    
    def __repr__(self):
        return f'<Capitulo {self.id}: {self.numero} - {self.descripcion}>'


class Partida(db.Model):
    __tablename__ = 'partidas'
    
    id = db.Column(db.Integer, primary_key=True)
    id_presupuesto = db.Column(db.Integer, db.ForeignKey('presupuestos.id', ondelete='CASCADE'), nullable=False)
    capitulo_numero = db.Column(db.String(20), nullable=False)
    numero = db.Column(db.String(20))
    descripcion = db.Column(db.Text)
    unitario = db.Column(db.String(20))
    cantidad = db.Column(db.Float)
    precio = db.Column(db.Float)
    total = db.Column(db.Float)
    margen = db.Column(db.Float)
    final = db.Column(db.Float)
    porcentaje_facturado = db.Column(db.Float, default=0)  # Porcentaje ya facturado (0-100)
    
    presupuesto = db.relationship('Presupuesto', back_populates='partidas')
    
    def __repr__(self):
        return f'<Partida {self.id}: {self.descripcion}>'
    
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