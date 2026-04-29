# --- Étape 1 : Builder (Optionnel mais recommandé pour les grosses dépendances) ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Empêcher Python de générer des fichiers .pyc et forcer l'affichage des logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installation des dépendances système nécessaires (ex: libpq pour postgres)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# --- Étape 2 : Image Finale ---
FROM python:3.12-slim

WORKDIR /app

# On récupère uniquement les libs installées proprement
COPY --from=builder /install /usr/local

# Sécurité : Créer un utilisateur non-privilégié
RUN addgroup --system appgroup && adduser --system appuser --ingroup appgroup

# Copie sélective pour éviter de polluer l'image (ignore .git, __pycache__, etc.)
# Assure-toi d'avoir un fichier .dockerignore
COPY --chown=appuser:appgroup . .

# Passer sur l'utilisateur sécurisé
USER appuser

# Exposer le port pour la documentation/Docker
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]