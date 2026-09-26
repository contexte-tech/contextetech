"""modération : ressources masquées

Revision ID: 0005
Revises: 0004
"""
import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("resources", sa.Column("hidden", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_index("ix_resources_hidden", "resources", ["hidden"])


def downgrade():
    op.drop_index("ix_resources_hidden", "resources")
    op.drop_column("resources", "hidden")
