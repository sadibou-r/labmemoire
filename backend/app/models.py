"""Modèles SQLAlchemy : User, Image, Annotation."""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    # Jeton d'API courant (Bearer). Un seul jeton actif par utilisateur suffit ici.
    token: Mapped[str | None] = mapped_column(String, nullable=True, index=True)

    annotations = relationship("Annotation", back_populates="user")


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Chemin relatif servi par /storage/, ex: "images/Pied001.jpg"
    path: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    is_annotated: Mapped[bool] = mapped_column(Boolean, default=False)

    annotations = relationship("Annotation", back_populates="image")


class Annotation(Base):
    __tablename__ = "annotations"
    # Une seule annotation par couple (image, médecin) : ré-annoter met à jour.
    __table_args__ = (UniqueConstraint("image_id", "user_id", name="uq_image_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    grade: Mapped[str] = mapped_column(String, nullable=False)
    stade: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    image = relationship("Image", back_populates="annotations")
    user = relationship("User", back_populates="annotations")
