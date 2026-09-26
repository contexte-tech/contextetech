"""labs : statut accordé par l'administrateur pour publier des modèles

Revision ID: 0008
Revises: 0007
"""
import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("is_lab", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("lab_request", sa.String(500), nullable=False, server_default=""))
    op.add_column("users", sa.Column("lab_requested_at", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    for c in ("lab_requested_at", "lab_request", "is_lab"):
        op.drop_column("users", c)
