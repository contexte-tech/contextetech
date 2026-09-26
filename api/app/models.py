from datetime import datetime

from sqlalchemy import ARRAY, Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

KINDS = ("context", "prompt", "dataset", "lora", "tool", "model", "agent", "skill", "eval", "rag", "harness")
SUBS = {
    "context": ("fewshot", "system", "knowledge", "persona"),
    "dataset": ("chat", "instruction", "completion"),
    "lora": ("lora", "qlora"),
    "tool": ("mcp",),
    "model": ("finetune", "merge", "quantized", "base"),
    "agent": ("",),
    "skill": ("",),
    "eval": ("",),
    "rag": ("",),
    "harness": ("",),
    "prompt": ("",),
}
SUB_FIELD = {"context": "type", "dataset": "format", "lora": "method", "tool": "toolType", "model": "modelType"}


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    # Adresse e-mail : connexion, alertes de connexion, mot de passe oublié (jamais affichée publiquement)
    email: Mapped[str] = mapped_column(String(254), default="", server_default="")
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    # Profil public (facultatif)
    bio: Mapped[str] = mapped_column(String(500), default="")
    country: Mapped[str] = mapped_column(String(60), default="")
    city: Mapped[str] = mapped_column(String(80), default="")
    website: Mapped[str] = mapped_column(String(300), default="")
    # Profil désapprouvé par l'administrateur : page publique en 404, hors sitemap
    hidden: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    # Lab : statut accordé par l'administrateur, seul autorisé à publier des modèles
    is_lab: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    lab_request: Mapped[str] = mapped_column(String(500), default="", server_default="")
    lab_requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    kind: Mapped[str] = mapped_column(String(20), index=True)
    name: Mapped[str] = mapped_column(String(60))
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    author_handle: Mapped[str] = mapped_column(String(30), default="")
    description: Mapped[str] = mapped_column(String(240), default="")
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(40)), default=list)
    clang: Mapped[str] = mapped_column(String(10), default="")
    license: Mapped[str] = mapped_column(String(40), default="")
    source_url: Mapped[str] = mapped_column(String(500), default="")
    # Désapprouvée par l'administrateur : conservée mais invisible (404, hors listes et sitemap)
    hidden: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    sub: Mapped[str] = mapped_column(String(20), default="")
    data: Mapped[dict] = mapped_column(JSONB, default=dict)
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    blob_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    uses: Mapped[int] = mapped_column(Integer, default=0)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_resources_kind_likes", "kind", "likes_count"),
        Index("ix_resources_kind_updated", "kind", "updated_at"),
        Index("ix_resources_tags", "tags", postgresql_using="gin"),
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resource_id: Mapped[str] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_comments_resource_created", "resource_id", "created_at"),)


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_type: Mapped[str] = mapped_column(String(10))          # resource | user
    target_id: Mapped[str] = mapped_column(String(120), index=True)
    reporter_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reason: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Like(Base):
    __tablename__ = "likes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    resource_id: Mapped[str] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)
