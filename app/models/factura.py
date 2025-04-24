# app/models/factura.py
from app import db
from datetime import datetime

class Factura(db.Model):
    __tablename__ = 'facturas'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), nullable=False, unique=True, index=True)
    id_proyecto = db.Column(db.Integer, db.ForeignKey('proyectos.id', ondelete='CASCADE'), nullable=False)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id', ondelete='CASCADE'), nullable=False)
    id_presupuesto = db.Column(db.Integer, db.ForeignKey('presupuestos.id'), nullable=True)
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_vencimiento = db.Column(db.DateTime)
    estado = db.Column(db.String(50), default='Pendiente')  # Pendiente, Pagada, Cancelada, Vencida
    concepto = db.Column(db.Text)
    base_imponible = db.Column(db.Float, default=0)
    iva_porcentaje = db.Column(db.Float, default=21.0)
    iva_importe = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    forma_pago = db.Column(db.String(100))
    datos_bancarios = db.Column(db.String(100))
    notas = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
# app/models/factura.py (continuación)
    # Relaciones
    proyecto = db.relationship('Proyecto')
    cliente = db.relationship('Cliente')
    presupuesto = db.relationship('Presupuesto', backref='facturas')
    lineas = db.relationship('LineaFactura', back_populates='factura', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Factura {self.id}: {self.numero}>'
    
    def calcular_totales(self):
        """Calcula los totales de la factura en base a sus líneas"""
        self.base_imponible = sum(linea.importe for linea in self.lineas)
        self.iva_importe = self.base_imponible * (self.iva_porcentaje / 100)
        self.total = self.base_imponible + self.iva_importe
        return self.total
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'id_proyecto': self.id_proyecto,
            'id_cliente': self.id_cliente,
            'fecha_emision': self.fecha_emision.isoformat() if self.fecha_emision else None,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'estado': self.estado,
            'concepto': self.concepto,
            'base_imponible': self.base_imponible,
            'iva_porcentaje': self.iva_porcentaje,
            'iva_importe': self.iva_importe,
            'total': self.total,
            'forma_pago': self.forma_pago,
            'datos_bancarios': self.datos_bancarios,
            'notas': self.notas,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None
        }


class LineaFactura(db.Model):
    __tablename__ = 'lineas_factura'
    
    id = db.Column(db.Integer, primary_key=True)
    id_factura = db.Column(db.Integer, db.ForeignKey('facturas.id', ondelete='CASCADE'), nullable=False)
    id_partida = db.Column(db.Integer, db.ForeignKey('partidas.id'), nullable=True)  # Relación con la partida de presupuesto
    porcentaje_facturado = db.Column(db.Float, default=100)  # Porcentaje que se está facturando en esta línea
    concepto = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    cantidad = db.Column(db.Float, default=1)
    precio_unitario = db.Column(db.Float, default=0)
    importe = db.Column(db.Float, default=0)
    
    # Relaciones
    factura = db.relationship('Factura', back_populates='lineas')
    partida = db.relationship('Partida', backref='lineas_factura')
    
    def __repr__(self):
        return f'<LineaFactura {self.id}: {self.concepto}>'
    
    def calcular_importe(self):
        """Calcula el importe total de la línea"""
        self.importe = self.cantidad * self.precio_unitario
        return self.importe