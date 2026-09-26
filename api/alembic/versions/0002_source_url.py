"""url source des ressources

Revision ID: 0002
Revises: 0001
"""
import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("resources", sa.Column("source_url", sa.String(500), nullable=False, server_default=""))


def downgrade():
    op.drop_column("resources", "source_url")
