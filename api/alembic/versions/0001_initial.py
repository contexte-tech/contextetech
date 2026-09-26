"""schéma initial

Revision ID: 0001
Revises:
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(30), nullable=False),
        sa.Column("password_hash", sa.String(200), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "resources",
        sa.Column("id", sa.String(120), primary_key=True),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("name", sa.String(60), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("author_handle", sa.String(30), nullable=False, server_default=""),
        sa.Column("description", sa.String(240), nullable=False, server_default=""),
        sa.Column("tags", postgresql.ARRAY(sa.String(40)), nullable=False, server_default="{}"),
        sa.Column("clang", sa.String(10), nullable=False, server_default=""),
        sa.Column("license", sa.String(40), nullable=False, server_default=""),
        sa.Column("sub", sa.String(20), nullable=False, server_default=""),
        sa.Column("data", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("row_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("blob_key", sa.Text(), nullable=True),
        sa.Column("uses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("likes_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_resources_kind", "resources", ["kind"])
    op.create_index("ix_resources_kind_likes", "resources", ["kind", "likes_count"])
    op.create_index("ix_resources_kind_updated", "resources", ["kind", "updated_at"])
    op.create_index("ix_resources_tags", "resources", ["tags"], postgresql_using="gin")

    op.create_table(
        "likes",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("resource_id", sa.String(120), sa.ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True),
    )


def downgrade():
    op.drop_table("likes")
    op.drop_table("resources")
    op.drop_table("users")
