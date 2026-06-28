"""Backend ULCERVISION — API d'annotation/correction des plaies (FastAPI + SQLite).

Reconstruit pour être 100% compatible avec le frontend Angular existant :
préfixe /api, jetons Bearer, fichiers statiques servis sous /storage.
"""
import math
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .deps import get_current_user
from .models import Annotation, Image, Token, User
from .schemas import (
    AnnotationOut,
    AnnotationUpdateIn,
    BatchAnnotationsIn,
    BatchAnnotationsOut,
    BatchImagesOut,
    LoginIn,
    LoginOut,
    UndefinedImagesOut,
)
from .security import generate_token, verify_password

# Nombre d'images proposées par page d'annotation.
BATCH_SIZE = 9

# Crée les tables si elles n'existent pas encore.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ULCERVISION API")

# CORS ouvert : le frontend Angular tourne sur un autre port (4200) en dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fichiers statiques : /storage/images/PiedXXX.jpg -> backend/storage/images/...
STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/storage", StaticFiles(directory=STORAGE_DIR), name="storage")

# Frontend Angular compilé (présent uniquement en production / image Docker).
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend_dist"


@app.get("/api")
def api_root():
    return {"service": "ULCERVISION API", "docs": "/docs"}


# ---------------------------------------------------------------------------
# Authentification
# ---------------------------------------------------------------------------
@app.post("/api/login", response_model=LoginOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants invalides")
    # Un nouveau jeton par connexion : les sessions existantes restent valides.
    token = Token(value=generate_token(), user_id=user.id)
    db.add(token)
    db.commit()
    return {"token": token.value, "user": user}


@app.post("/api/logout")
def logout(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    # Supprime uniquement le jeton de cette session.
    if authorization and authorization.lower().startswith("bearer "):
        value = authorization.split(" ", 1)[1].strip()
        db.query(Token).filter(Token.value == value).delete()
        db.commit()
    return {"message": "Déconnecté"}


# ---------------------------------------------------------------------------
# Images à annoter
# ---------------------------------------------------------------------------
@app.get("/api/images/next-batch", response_model=BatchImagesOut)
def next_batch(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lot d'images pas encore annotées par l'utilisateur courant."""
    annotated_ids = [
        a.image_id for a in db.query(Annotation.image_id).filter(Annotation.user_id == user.id)
    ]
    query = db.query(Image)
    if annotated_ids:
        query = query.filter(~Image.id.in_(annotated_ids))
    images = query.order_by(Image.id).limit(BATCH_SIZE).all()

    total_images = db.query(Image).count()
    done = len(annotated_ids)
    total_batches = max(1, math.ceil(total_images / BATCH_SIZE))
    current_batch = min(total_batches, done // BATCH_SIZE + 1)
    return {"current_batch": current_batch, "total_batches": total_batches, "images": images}


@app.get("/api/images/undefined-batch", response_model=UndefinedImagesOut)
def undefined_batch(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Images sans aucune annotation (utilisé par le compte validateur)."""
    images = db.query(Image).filter(Image.is_annotated == False).order_by(Image.id).all()  # noqa: E712
    return {"images": images}


# ---------------------------------------------------------------------------
# Annotations
# ---------------------------------------------------------------------------
@app.post("/api/batch-annotations", response_model=BatchAnnotationsOut)
def batch_annotations(
    payload: BatchAnnotationsIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crée (ou met à jour) un lot d'annotations pour l'utilisateur courant."""
    saved: list[Annotation] = []
    for item in payload.annotations:
        image = db.get(Image, item.image_id)
        if not image:
            continue
        annotation = (
            db.query(Annotation)
            .filter(Annotation.image_id == item.image_id, Annotation.user_id == user.id)
            .first()
        )
        if annotation:
            annotation.grade = item.grade
            annotation.stade = item.stade
        else:
            annotation = Annotation(
                image_id=item.image_id,
                user_id=user.id,
                grade=item.grade,
                stade=item.stade,
            )
            db.add(annotation)
        image.is_annotated = True
        saved.append(annotation)
    db.commit()
    for a in saved:
        db.refresh(a)
    return {"annotations": saved}


@app.get("/api/annotations/annotated-by-me", response_model=list[AnnotationOut])
def annotated_by_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Annotation)
        .filter(Annotation.user_id == user.id)
        .order_by(Annotation.id.desc())
        .all()
    )


@app.put("/api/annotations/{annotation_id}", response_model=AnnotationOut)
def update_annotation(
    annotation_id: int,
    payload: AnnotationUpdateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Correction d'une annotation (grade et/ou stade)."""
    annotation = db.get(Annotation, annotation_id)
    if not annotation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Annotation introuvable")
    annotation.grade = payload.grade
    annotation.stade = payload.stade
    db.commit()
    db.refresh(annotation)
    return annotation


# ---------------------------------------------------------------------------
# Frontend Angular (servi par le même process — déclaré en DERNIER pour ne pas
# masquer /api, /storage ni /docs).
# ---------------------------------------------------------------------------
if FRONTEND_DIR.exists():

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        candidate = FRONTEND_DIR / full_path
        # Fichier statique réel (js, css, images, favicon...) -> on le sert.
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        # Sinon, route gérée côté Angular -> on renvoie index.html.
        return FileResponse(FRONTEND_DIR / "index.html")

