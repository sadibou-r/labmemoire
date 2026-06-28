#!/bin/sh
# Démarrage du conteneur :
#  - seed idempotent (--if-empty) : importe les 279 annotations UNIQUEMENT si la base
#    est vide. Aux redéploiements, la base Postgres garde les corrections du médecin.
#  - --db-only : les images sont déjà dans l'image (backend/storage/images).
set -e

echo ">> Initialisation de la base (importe seulement si vide)..."
python seed.py --db-only --if-empty

echo ">> Démarrage du serveur sur le port ${PORT:-8080}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}"
