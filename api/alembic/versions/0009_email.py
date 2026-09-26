"""email : adresse e-mail des comptes (connexion, alertes, mot de passe oublié)

Revision ID: 0009
Revises: 0008
"""
import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("email", sa.String(254), nullable=False, server_default=""))
    # Une adresse ne sert qu'à un compte (sans tenir compte des majuscules) ; les comptes sans adresse sont permis
    op.create_index("ix_users_email_lower", "users", [sa.text("lower(email)")], unique=True, postgresql_where=sa.text("email <> ''"))


def downgrade():
    op.drop_index("ix_users_email_lower", table_name="users")
    op.drop_column("users", "email")
