# 🗂️ Fichiers de la Pipeline CI/CD — Rôles et Usages

Ce document explique quel fichier est utilisé, à quelle étape du pipeline, et pour quoi faire.

---

## Vue d'ensemble

```
docker-political-solo/
├── .github/workflows/
│   ├── deploy.yml           ← Pipeline principale (Test + Build + Deploy)
│   └── fastapi-ci.yml       ← Pipeline secondaire (CI FastAPI seule)
│
├── Dockerfile.django        ← Recette de l'image Docker Django
├── Dockerfile.api           ← Recette de l'image Docker FastAPI
├── Dockerfile.ingest        ← Recette de l'image Docker Ingest (import données)
│
├── docker-compose.prod.yml  ← Définit tous les conteneurs pour la PRODUCTION
├── docker-compose.yml       ← Définit tous les conteneurs en LOCAL (dev)
│
├── scripts/
│   └── deploy.sh            ← Script exécuté sur le VPS pour redémarrer l'app
│
└── traefik/
    └── traefik.yml          ← Configuration du reverse proxy Traefik (HTTPS, routage)
```

---

## 📁 Détail de chaque fichier

---

### `.github/workflows/deploy.yml` — Le chef d'orchestre

**Quand ?** À chaque `git push` sur `develop` ou `main`.

**Ce qu'il fait :**

| Étape | Nom du Job | Description |
|---|---|---|
| 1 | `test-api` | Lance Pytest sur les tests FastAPI |
| 2 | `build-and-push` | Construit les images Docker et les pousse sur GHCR |
| 3 | `deploy-vps` | Envoie les fichiers de config sur le VPS via SCP puis exécute `deploy.sh` via SSH |

**Secrets utilisés :** `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, `DATABASE_URL`, `SECRET_KEY`, `POSTGRES_*`, `GITHUB_TOKEN`, `DOMAIN_NAME`, `TRAEFIK_DASHBOARD_CREDENTIALS`

---

### `.github/workflows/fastapi-ci.yml` — CI légère pour l'API

**Quand ?** À chaque push sur n'importe quelle branche modifiant le dossier `api/`.

**Ce qu'il fait :**
- Lint du code Python (`flake8`)
- Exécution des tests FastAPI (`pytest`)
- Build et push de l'image FastAPI sur GHCR

---

### `Dockerfile.django` — Construction de l'image Django

**Utilisé par :** `deploy.yml` → Job `build-and-push`

**Ce qu'il fait :** 
- Part d'une image Python de base
- Installe les dépendances (`pip install -r requirements.txt`)
- Copie le code source Django
- Lance `collectstatic` pour les fichiers CSS/JS
- Démarre Gunicorn (serveur web de production)

**Image produite :** `ghcr.io/john-do59/predilection-django:<tag>`

---

### `Dockerfile.api` — Construction de l'image FastAPI

**Utilisé par :** `deploy.yml` → Job `build-and-push`

**Ce qu'il fait :**
- Part d'une image Python de base
- Installe les dépendances FastAPI et ML
- Copie le code source de l'API
- Démarre Uvicorn (serveur ASGI pour FastAPI)

**Image produite :** `ghcr.io/john-do59/predilection-api:<tag>`

---

### `Dockerfile.ingest` — Construction de l'image d'ingestion

**Utilisé par :** `deploy.yml` → Job `build-and-push`

**Ce qu'il fait :**
- Contient les scripts d'import initial de données en base PostgreSQL
- Ce conteneur s'exécute **une seule fois** au démarrage puis s'arrête

**Image produite :** `ghcr.io/john-do59/predilection-ingest:<tag>`

---

### `docker-compose.prod.yml` — L'infrastructure de production

**Utilisé par :** `deploy.sh` sur le VPS via `docker compose -f docker-compose.prod.yml up -d`

**Ce qu'il définit :**

| Service | Image | Rôle |
|---|---|---|
| `traefik` | `traefik:v3` | Reverse proxy, HTTPS Let's Encrypt, routage |
| `db` | `postgres:17-alpine` | Base de données PostgreSQL |
| `ingest` | `predilection-ingest` | Import initial des données (run once) |
| `api` | `predilection-api` | API FastAPI + modèle ML |
| `django` | `predilection-django` | Application web Django |

**Particularité sécurité :** Pas de `env_file`. Les variables d'environnement (`${DATABASE_URL}`, `${SECRET_KEY}`…) sont lues depuis l'environnement système injecté par GitHub Actions.

---

### `docker-compose.yml` — L'environnement local (développement)

**Utilisé par :** Les développeurs sur leur machine (`docker compose up`)

**Différences avec la prod :**
- Utilise un fichier `.env` local (non commité)
- Ports exposés directement (sans Traefik)
- Volume de code source monté pour le rechargement à chaud

---

### `scripts/deploy.sh` — Le script de déploiement sur le VPS

**Utilisé par :** `deploy.yml` → Job `deploy-vps` → exécuté via SSH

**Ce qu'il fait pas à pas :**
1. `docker login ghcr.io` — Authentification GHCR avec le token GitHub
2. `docker compose pull` — Télécharge les nouvelles images
3. `docker compose up -d --remove-orphans` — Relance les conteneurs
4. `docker image prune -f` — Nettoie les vieilles images
5. `curl http://localhost/home` — Smoke Test (vérifie que le site répond)

---

### `traefik/traefik.yml` — Configuration Traefik

**Utilisé par :** Le conteneur `traefik` dans `docker-compose.prod.yml`
**Envoyé sur le VPS par :** `deploy.yml` → Job `deploy-vps` → `appleboy/scp-action`

**Ce qu'il configure :**

| Section | Description |
|---|---|
| `entryPoints.web` | Écoute le port 80 (HTTP) et redirige vers HTTPS |
| `entryPoints.websecure` | Écoute le port 443 (HTTPS) |
| `providers.docker` | Lit les labels des conteneurs Docker pour le routage automatique |
| `certificatesResolvers.letsencrypt` | Génère les certificats SSL via Let's Encrypt (challenge HTTP-01) |
| `api.dashboard` | Active le dashboard Traefik (protégé par BasicAuth) |

---

## 🔄 Ordre d'utilisation dans la pipeline complète

```
git push
   │
   ▼
deploy.yml
   │
   ├─ [test-api]
   │       └── pytest (tests FastAPI)
   │
   ├─ [build-and-push]
   │       ├── Dockerfile.django    → image predilection-django:vX.X
   │       ├── Dockerfile.api       → image predilection-api:vX.X
   │       └── Dockerfile.ingest    → image predilection-ingest:vX.X
   │
   └─ [deploy-vps]
           ├── SCP → docker-compose.prod.yml
           ├── SCP → traefik/traefik.yml
           ├── SCP → scripts/deploy.sh
           └── SSH → bash deploy.sh
                       └── docker compose up -d (utilise docker-compose.prod.yml)
```
