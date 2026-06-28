# syntax=docker/dockerfile:1
# Backend ULCERVISION — API + images uniquement.
# Le frontend Angular est hébergé séparément sur Vercel.

FROM python:3.12-slim
WORKDIR /app/backend

# Dépendances Python
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Code backend + images servies sous /storage (backend/storage/images)
COPY backend/ /app/backend/
# CSV d'import pour le seed initial
COPY Données/annotations.csv /app/Données/annotations.csv

EXPOSE 8080
RUN chmod +x /app/backend/entrypoint.sh
CMD ["/app/backend/entrypoint.sh"]
