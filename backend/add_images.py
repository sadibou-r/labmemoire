"""Insère les nouvelles images (mapping_nouvelles_images.csv) dans la base comme
images NON annotées (is_annotated=False) -> elles apparaissent dans undefined-batch.

Idempotent : une image dont le `path` existe déjà est ignorée. Ne touche à AUCUNE
annotation ni correction existante.

Usage (prod) :
    cd backend
    export DATABASE_URL='postgresql://...supabase...'
    python add_images.py
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import Image  # noqa: E402

BACKEND_DIR = Path(__file__).resolve().parent
MAPPING_CSV = BACKEND_DIR.parent / "Données" / "mapping_nouvelles_images.csv"


def main():
    with open(MAPPING_CSV, newline="", encoding="utf-8") as f:
        paths = [row["path"].strip() for row in csv.DictReader(f)]

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    existing = {p for (p,) in db.query(Image.path).all()}
    added = 0
    skipped = 0
    for path in paths:
        if path in existing:
            skipped += 1
            continue
        db.add(Image(path=path, is_annotated=False))
        existing.add(path)
        added += 1
    db.commit()

    total = db.query(Image).count()
    undefined = db.query(Image).filter(Image.is_annotated == False).count()  # noqa: E712
    db.close()
    print(f"Ajoutées : {added} | déjà présentes (ignorées) : {skipped}")
    print(f"Total images en base : {total} | non annotées (undefined-batch) : {undefined}")


if __name__ == "__main__":
    main()
