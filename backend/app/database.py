"""Configuration de la base de données.

- En local : SQLite (fichier app.db, zéro serveur). Chemin surchargé par ULCERVISION_DB.
- En production : Postgres si DATABASE_URL est défini (ex. Supabase). Les corrections
  du médecin sont alors persistées dans une base managée, hors du disque éphémère.
"""
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Normalise le préfixe vers le driver psycopg v3.
    url = DATABASE_URL
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    # Supabase impose le SSL.
    if "sslmode=" not in url:
        url += ("&" if "?" in url else "?") + "sslmode=require"
    engine = create_engine(url, pool_pre_ping=True)
else:
    DB_PATH = Path(os.environ.get("ULCERVISION_DB", BASE_DIR / "app.db"))
    engine = create_engine(
        f"sqlite:///{DB_PATH}",
        connect_args={"check_same_thread": False},
    )

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """Dépendance FastAPI : ouvre une session par requête puis la ferme."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
