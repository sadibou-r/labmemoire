"""Réimporte les données exportées (Données/annotations.csv + Données/Images/)
dans la base SQLite, et copie les images dans backend/storage/images/.

Usage :
    cd backend
    python seed.py

Idempotent : on peut le relancer, il repart d'une base propre.
"""
import csv
import os
import shutil
import sys
from pathlib import Path

# Permet d'importer le package app/ quel que soit le dossier courant.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import Annotation, Image, User  # noqa: E402
from app.security import hash_password  # noqa: E402

BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = BACKEND_DIR.parent / "Données"
CSV_PATH = DATA_DIR / "annotations.csv"
# Sources d'images, fouillées récursivement par ordre de priorité.
# Datasets/dataset/ contient les 279 Pied*.jpg complets ; Données/Images sert de repli.
IMAGE_SOURCES = [
    BACKEND_DIR.parent.parent / "Datasets" / "dataset",
    DATA_DIR / "Images",
]
DST_IMAGES = BACKEND_DIR / "storage" / "images"

# Mot de passe commun aux comptes de démonstration.
DEFAULT_PASSWORD = "ulcervision2025"
USERS = [
    {"id": 1, "name": "Dr Médecin", "email": "medecin@ulcervision.com"},
    {"id": 2, "name": "Dr Spécialiste", "email": "specialiste@ulcervision.com"},
    {"id": 3, "name": "Étudiant Annotateur", "email": "etudiant@ulcervision.com"},
    {"id": 4, "name": "Validateur", "email": "validateur@ulcervision.com"},
]
# Toutes les annotations importées appartiennent à ce médecin (il pourra les corriger).
OWNER_ID = 1


def copy_images() -> set[str]:
    """Copie les images depuis les sources (récursif) et retourne les noms présents.

    La première source qui fournit un nom de fichier l'emporte (priorité à
    Datasets/dataset/). Les noms sont aplatis dans storage/images/.
    """
    DST_IMAGES.mkdir(parents=True, exist_ok=True)
    present: set[str] = set()
    for source in IMAGE_SOURCES:
        if not source.exists():
            print(f"⚠️  Source ignorée (introuvable) : {source}")
            continue
        for root, _, files in os.walk(source):
            for fname in files:
                if fname in present:
                    continue
                shutil.copy2(os.path.join(root, fname), DST_IMAGES / fname)
                present.add(fname)
    print(f"📁 {len(present)} fichiers image copiés vers {DST_IMAGES}")
    return present


def main():
    # Mode --db-only : les images sont déjà en place (ex. baked dans l'image Docker),
    # on ne fait que (re)peupler la base. Utilisé au premier démarrage en production.
    db_only = "--db-only" in sys.argv
    if db_only:
        present_files = set(os.listdir(DST_IMAGES)) if DST_IMAGES.exists() else set()
        print(f"📁 mode --db-only : {len(present_files)} images déjà présentes (pas de copie)")
    else:
        present_files = copy_images()

    # Mode --if-empty (PRODUCTION) : ne JAMAIS détruire les données existantes
    # (corrections du médecin). On crée les tables si besoin et on n'importe que
    # si la base est vide. Sinon (local) : reset complet.
    if_empty = "--if-empty" in sys.argv
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if if_empty and db.query(Annotation).count() > 0:
        n = db.query(Annotation).count()
        db.close()
        print(f"✅ Base déjà peuplée ({n} annotations) — import ignoré, données conservées.")
        return

    if not if_empty:
        # Reset complet (usage local / réinitialisation explicite).
        db.close()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()

    # Utilisateurs.
    for u in USERS:
        db.add(User(
            id=u["id"], name=u["name"], email=u["email"],
            password_hash=hash_password(DEFAULT_PASSWORD),
        ))
    db.commit()

    # Images + annotations depuis le CSV.
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    image_by_path: dict[str, Image] = {}
    missing = 0
    for row in rows:
        path = row["path"].strip()            # ex: images/Pied001.jpg
        grade = str(row["grade"]).strip()
        stade = str(row["stade"]).strip()
        fname = os.path.basename(path)
        has_file = fname in present_files
        if not has_file:
            missing += 1

        image = image_by_path.get(path)
        if image is None:
            image = Image(path=path, is_annotated=True)
            db.add(image)
            db.flush()  # pour obtenir image.id
            image_by_path[path] = image

        db.add(Annotation(
            image_id=image.id, user_id=OWNER_ID, grade=grade, stade=stade,
        ))
    db.commit()

    n_images = db.query(Image).count()
    n_annotations = db.query(Annotation).count()
    db.close()

    print(f"✅ Import terminé : {n_images} images, {n_annotations} annotations")
    print(f"   ({missing} lignes sans fichier image présent — annotation conservée, vignette vide)")
    print("\nComptes de connexion (mot de passe : "
          f"{DEFAULT_PASSWORD}) :")
    for u in USERS:
        print(f"   - {u['email']}")
    print("\n👉 Connecte-toi avec medecin@ulcervision.com pour voir/corriger les annotations.")


if __name__ == "__main__":
    main()
