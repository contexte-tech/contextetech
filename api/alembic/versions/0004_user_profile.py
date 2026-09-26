"""profil public des membres

Revision ID: 0004
Revises: 0003
"""
import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

COLS = (("bio", 500), ("country", 60), ("city", 80), ("website", 300))


def upgrade():
    for name, size in COLS:
        op.add_column("users", sa.Column(name, sa.String(size), nullable=False, server_default=""))


def downgrade():
    for name, _ in COLS:
        op.drop_column("users", name)
