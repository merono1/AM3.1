# migrations/add_proveedor_columns.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Añadir columnas a la tabla partidas_hojas
    op.add_column('partidas_hojas', sa.Column('id_proveedor_principal', sa.Integer(), nullable=True))
    op.add_column('partidas_hojas', sa.Column('precio_proveedor', sa.Float(), nullable=True))
    op.create_foreign_key('fk_partida_proveedor', 'partidas_hojas', 'proveedores', ['id_proveedor_principal'], ['id'])
    
    # Crear la tabla de asociación de proveedores con partidas
    op.create_table('proveedores_partidas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_partida', sa.Integer(), nullable=False),
        sa.Column('id_proveedor', sa.Integer(), nullable=False),
        sa.Column('precio', sa.Float(), nullable=True),
        sa.Column('fecha_asignacion', sa.DateTime(), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('estado', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['id_partida'], ['partidas_hojas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['id_proveedor'], ['proveedores.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_proveedores_partidas_id_partida', 'proveedores_partidas', ['id_partida'])
    op.create_index('ix_proveedores_partidas_id_proveedor', 'proveedores_partidas', ['id_proveedor'])

def downgrade():
    # Eliminar columnas y restricciones de clave foránea
    op.drop_constraint('fk_partida_proveedor', 'partidas_hojas', type_='foreignkey')
    op.drop_column('partidas_hojas', 'precio_proveedor')
    op.drop_column('partidas_hojas', 'id_proveedor_principal')
    
    # Eliminar la tabla de asociación
    op.drop_index('ix_proveedores_partidas_id_proveedor', 'proveedores_partidas')
    op.drop_index('ix_proveedores_partidas_id_partida', 'proveedores_partidas')
    op.drop_table('proveedores_partidas')