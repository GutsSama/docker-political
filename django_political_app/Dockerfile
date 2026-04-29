FROM python:3.12-slim

WORKDIR /app

# Empêcher les fichiers .pyc et forcer les logs en temps réel
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installation des dépendances système (libpq-dev est nécessaire pour psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# On installe gunicorn explicitement s'il n'est pas dans ton requirements
RUN pip install --no-cache-dir gunicorn

# Copie du projet
COPY . .

# Création de l'utilisateur pour la sécurité
RUN addgroup --system appgroup && adduser --system appuser --ingroup appgroup
# Donner les droits sur le dossier app pour le collectstatic
RUN chown -R appuser:appgroup /app

RUN mkdir -p /app/staticfiles && chown -R appuser:appgroup /app/staticfiles

USER appuser

# Génération des fichiers statiques
RUN python manage.py collectstatic --noinput

# Utilisation de Gunicorn au lieu de runserver
# On lie le port 8001 comme dans ton docker-compose
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "django_political_app.wsgi:application"]