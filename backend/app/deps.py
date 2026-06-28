"""Authentification par jeton Bearer (lecture de l'en-tête Authorization)."""
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db
from .models import User


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Jeton manquant")
    token = authorization.split(" ", 1)[1].strip()
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Jeton invalide")
    return user
