# DEPLOYMENT — Guide de déploiement

> Procédures de déploiement de l'infrastructure Prédi'lection sur VPS.

---

## Architecture de déploiement

```text
GitHub Actions (CI/CD)
        │
        ├── Tests FastAPI (pytest)
        ├── Build images Docker (GHCR)
        ├── Scan sécurité (Trivy)
        └── Deploy SSH → VPS OVH
                │
                ├── docker-compose.prod.yml  (app)
                └── docker-compose.monitoring.yml  (observabilité)
```

---

## Environnements

| Branche | Environnement GitHub | Description |
|---------|---------------------|-------------|
| `develop` | `dev` | Développement continu |
| `main` | `staging` | Préproduction (push direct) |
| `v*.*.*` (tag) | `prod` | Production (release officielle) |

---

## Déployer manuellement sur le VPS

### Prérequis

```bash
# Sur le VPS : connexion SSH
ssh -p 1455 user@vps-ip

cd ~/docker-political
```

### Déploiement complet

```bash
# Tirer les dernières images depuis GHCR
docker compose -f docker-compose.prod.yml pull

# Relancer les services avec les nouvelles images
RELEASE_TAG=latest docker compose -f docker-compose.prod.yml up -d --remove-orphans

# Vérifier l'état
docker compose -f docker-compose.prod.yml ps
```

### Déploiement via script

```bash
bash scripts/deploy.sh <RELEASE_TAG>
# Exemple :
bash scripts/deploy.sh develop-abc1234
```

---

## Ajouter un nouveau secret GitHub

1. Aller sur : `https://github.com/John-Do59/docker-political-solo/settings/secrets/actions`
2. Cliquer **New repository secret**
3. Nommer le secret en MAJUSCULES (ex: `GRAFANA_DISCORD_WEBHOOK_URL`)
4. Référencer dans `deploy.yml` :

```yaml
envs: ...,GRAFANA_DISCORD_WEBHOOK_URL
env:
  GRAFANA_DISCORD_WEBHOOK_URL: ${{ secrets.GRAFANA_DISCORD_WEBHOOK_URL }}
```

---

## Secrets GitHub requis

| Secret | Description |
|--------|-------------|
| `VPS_HOST` | IP du VPS |
| `VPS_USER` | Utilisateur SSH |
| `VPS_SSH_KEY` | Clé SSH privée |
| `POSTGRES_USER` | Utilisateur PostgreSQL |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL |
| `POSTGRES_DB` | Nom de la base de données |
| `SECRET_KEY` | Django SECRET_KEY |
| `DOMAIN_NAME` | Domaine principal |
| `TRAEFIK_DASHBOARD_CREDENTIALS` | BasicAuth Traefik |
| `GRAFANA_DISCORD_WEBHOOK_URL` | Webhook Discord alerting |
| `GRAFANA_ALERT_EMAIL` | Email pour alertes Grafana |
| `GF_SMTP_USER` | Compte SMTP Grafana |
| `GF_SMTP_PASSWORD` | Mot de passe SMTP Grafana |

---

## Variables d'environnement sur le VPS

Créer `/home/user/docker-political/.env` (non versionné) :

```env
RELEASE_TAG=latest
POSTGRES_USER=predilection
POSTGRES_PASSWORD=XXXX
POSTGRES_DB=predilection
SECRET_KEY=XXXX
DOMAIN_NAME=yourdomain.com
TRAEFIK_DASHBOARD_CREDENTIALS=admin:$hashed_password
GRAFANA_DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
GRAFANA_ALERT_EMAIL=alerts@yourdomain.com
```

---

## Vérification post-déploiement

```bash
# Smoke test manuel
curl -sk https://api.${DOMAIN_NAME}/health
curl -sk -o /dev/null -w "HTTP %{http_code}\n" https://${DOMAIN_NAME}/home/

# k6 smoke test automatisé
BASE_URL=https://api.${DOMAIN_NAME} k6 run k6/smoke.js
```
