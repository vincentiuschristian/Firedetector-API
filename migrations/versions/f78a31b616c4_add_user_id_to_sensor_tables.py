"""Add user_id to sensor tables

Revision ID: f78a31b616c4
Revises: 7e7210e28c27
Create Date: 2025-05-13 12:38:14.975453

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = 'f78a31b616c4'
down_revision = '7e7210e28c27'
branch_labels = None
depends_on = None


def upgrade():
    # Tambahkan kolom dengan nullable=True terlebih dahulu
    with op.batch_alter_table('kamar', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
    
    with op.batch_alter_table('ruang_tamu', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))

    # Gunakan SQLAlchemy text() untuk menjalankan query SELECT
    conn = op.get_bind()
    default_user = conn.execute(text('SELECT id FROM "user" LIMIT 1')).fetchone()
    if default_user:
        user_id = default_user[0]
        conn.execute(text(f"UPDATE kamar SET user_id = :user_id WHERE user_id IS NULL"), {"user_id": user_id})
        conn.execute(text(f"UPDATE ruang_tamu SET user_id = :user_id WHERE user_id IS NULL"), {"user_id": user_id})

    # Ubah menjadi NOT NULL
    with op.batch_alter_table('kamar', schema=None) as batch_op:
        batch_op.alter_column('user_id', nullable=False)
    
    with op.batch_alter_table('ruang_tamu', schema=None) as batch_op:
        batch_op.alter_column('user_id', nullable=False)

    # Tambahkan foreign key constraint
    op.create_foreign_key(None, 'kamar', 'user', ['user_id'], ['id'])
    op.create_foreign_key(None, 'ruang_tamu', 'user', ['user_id'], ['id'])
    
def downgrade():
    # Hapus foreign key dan kolom
    with op.batch_alter_table('ruang_tamu', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('user_id')
    
    with op.batch_alter_table('kamar', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('user_id')