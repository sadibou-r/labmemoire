# ULCERVISION — Backend (FastAPI + SQLite)

Backend léger reconstruit pour le frontend Angular d'annotation des plaies.
Aucun serveur de base de données : tout tient dans un fichier `app.db` (SQLite)
et les images sont servies en statique depuis `storage/`.

## Démarrage rapide

```bash
cd backend
pip install -r requirements.txt    # fastapi, uvicorn, sqlalchemy

python seed.py                     # importe Données/annotations.csv + copie les images
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- API : http://localhost:8000/api
- Docs interactives : http://localhost:8000/docs
- Images : http://localhost:8000/storage/images/Pied001.jpg

Le frontend (`src/app/constants.ts`) pointe déjà vers `http://localhost:8000`.
Côté Angular : `npm install` puis `npm start` (http://localhost:4200).

## Comptes (mot de passe : `ulcervision2025`)

| Email | Rôle |
|---|---|
| `medecin@ulcervision.com` | Médecin — **possède les 279 annotations importées**, peut les corriger |
| `specialiste@ulcervision.com` | Spécialiste |
| `etudiant@ulcervision.com` | Annotateur (voit toutes les images à annoter) |
| `validateur@ulcervision.com` | id=4, déclenche `undefined-batch` |

## Endpoints (contrat repris du frontend existant)

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/login` | `{email, password}` → `{token, user}` |
| POST | `/api/logout` | invalide le jeton |
| GET | `/api/images/next-batch` | lot d'images non annotées par l'utilisateur |
| GET | `/api/images/undefined-batch` | images sans aucune annotation |
| POST | `/api/batch-annotations` | `{annotations:[{image_id, grade, stade}]}` |
| GET | `/api/annotations/annotated-by-me` | annotations de l'utilisateur |
| PUT | `/api/annotations/{id}` | **correction** `{grade, stade}` |

## Notes sur les données

- `annotations.csv` = export aplati : 279 lignes (1 ligne = 1 image + son grade/stade).
- Seules **156 images** sur 279 existaient encore dans `Données/Images/` ; les autres
  annotations sont conservées en base (la vignette renvoie juste 404).
- Pour réimporter de zéro : relancer `python seed.py` (recrée la base proprement).

## Déploiement

Un seul process. Pour déployer (VPS, conteneur, etc.) :

```bash
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --host 0.0.0.0 --port 8000
# en production, derrière nginx ou avec --workers / gunicorn
```
