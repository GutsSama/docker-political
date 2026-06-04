# Plan d'implémentation CI/CD propre (sans .env sur VPS)

## Objectif

| Contrainte | Statut |
|---|---|
| Zéro repo git sur VPS | ✅ Accompli |
| Zéro `.env` sur VPS | 🔧 En cours |
| Secrets via GitHub Actions | 🔧 En cours |
| Docker Compose propre (sans `env_file`) | 🔧 En cours |
| HTTPS DuckDNS + Traefik | 🔧 En cours |

---

## Architecture cible

```
GitHub Secrets
      ↓
GitHub Actions (runtime sécurisé et éphémère)
      ↓  (SCP)
VPS : docker-compose.prod.yml + scripts/deploy.sh uniquement
      ↓
docker compose up -d (variables injectées via --env / environment)
      ↓
Conteneurs actifs (secrets uniquement en mémoire)
```

---

## 1. Fichiers modifiés

### `docker-compose.prod.yml`
- ❌ Supprimer `env_file: - .env` dans les services `api` et `django`
- ✅ Remplacer par des variables `environment:` explicites lues depuis les variables d'environnement du shell (injectées par GitHub Actions)

### `.github/workflows/deploy.yml`
- ❌ Supprimer la génération du `.env` temporaire et le SCP du `.env`
- ✅ Envoyer uniquement `docker-compose.prod.yml` et `scripts/deploy.sh` via SCP
- ✅ Injecter les secrets directement via `appleboy/ssh-action` en tant que variables d'environnement de la commande SSH
- ✅ Le script `deploy.sh` reçoit les variables et les passe à `docker compose` via `--env-file /dev/stdin` ou `export`

### `scripts/deploy.sh`
- ❌ Supprimer toute référence à `.env` ou `scp`
- ✅ Recevoir les variables via l'environnement du shell (injecté par GitHub Actions SSH)

---

## 2. GitHub Secrets à configurer

Dans **Settings → Secrets and variables → Actions → New repository secret** :

| Secret | Valeur |
|---|---|
| `VPS_HOST` | `164.132.43.252` |
| `VPS_USER` | `amaury` |
| `VPS_SSH_KEY` | Contenu de `~/.ssh/id_ed25519_vps` |
| `DOMAIN_NAME` | `docker-political.duckdns.org` |
| `POSTGRES_USER` | à définir |
| `POSTGRES_PASSWORD` | à définir (fort) |
| `POSTGRES_DB` | `predilection` |
| `DATABASE_URL` | `postgresql://user:pass@db:5432/predilection` |
| `SECRET_KEY` | clé Django (générer avec `python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
| `DEBUG` | `false` |
| `TRAEFIK_DASHBOARD_CREDENTIALS` | hash htpasswd |

---

## 3. Commandes VPS

```bash
# (A) Vérifier Docker
docker --version
docker compose version

# (B) Supprimer l'ancien .env
rm -f ~/docker-political/.env

# (C) Sécuriser le répertoire
chmod -R 700 ~/docker-political
```

---

## 4. DNS / HTTPS (DuckDNS + Traefik)

Le domaine `docker-political.duckdns.org` pointe déjà vers `164.132.43.252`. ✅

```
DuckDNS (DNS)
   ↓ docker-political.duckdns.org → 164.132.43.252
Traefik (reverse proxy)
   ↓ Host(`docker-political.duckdns.org`) sur port 443
Let's Encrypt (certresolver=letsencrypt)
   ↓ certificat HTTPS automatique
Application accessible en HTTPS ✅
```

**Vérification DNS :**
```bash
nslookup docker-political.duckdns.org
# Attendu : 164.132.43.252
```

---

## 5. Checklist finale

- [ ] `env_file` supprimé de `docker-compose.prod.yml`
- [ ] Variables `environment:` explicites dans `api` et `django`
- [ ] `deploy.yml` SSH-only (pas de `.env` transféré)
- [ ] Secrets GitHub configurés (voir tableau section 2)
- [ ] VPS sans `.env` (`rm -f ~/docker-political/.env`)
- [ ] `traefik/acme.json` présent avec `chmod 600`
- [ ] DuckDNS pointe vers l'IP VPS ✅
- [ ] Merge des 4 PR vers `develop` pour déclencher le pipeline

---

## 6. Résultat attendu

```
https://docker-political.duckdns.org   → Application Django ✅
https://api.docker-political.duckdns.org → API FastAPI ✅
https://traefik.docker-political.duckdns.org → Dashboard Traefik ✅
```

- ✅ HTTPS valide (Let's Encrypt)
- ✅ Zéro secret stocké durablement sur le VPS
- ✅ CI/CD entièrement automatisé via GitHub Actions
- ✅ Architecture "niveau junior DevOps" défendable en soutenance
