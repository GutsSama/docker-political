# RUNBOOK — Opérations courantes

> Référence d'exploitation pour l'infrastructure Prédi'lection.
> Ce document couvre les procédures de maintenance, de dépannage et de récupération.

---

## Services et leurs rôles

| Service | Rôle | Port interne | URL publique |
|---------|------|-------------|--------------|
| `django` | Frontend Django | 8000 | `https://app.domain.com` |
| `api` | API FastAPI | 8000 | `https://api.domain.com` |
| `db` | PostgreSQL | 5432 | — (interne) |
| `traefik` | Reverse proxy + TLS | 80/443 | `https://traefik.domain.com` |
| `grafana` | Dashboards monitoring | 3000 | `https://grafana.domain.com` |
| `prometheus` | Collecte métriques | 9090 | — (interne) |
| `loki` | Agrégation logs | 3100 | — (interne) |
| `uptime-kuma` | Supervision uptime | 3001 | `https://kuma.domain.com` |

---

## Commandes de base

### Voir l'état des services

```bash
cd ~/docker-political
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.monitoring.yml ps
```

### Redémarrer un service spécifique

```bash
# Redémarrer l'API FastAPI
docker compose -f docker-compose.prod.yml restart api

# Redémarrer Django
docker compose -f docker-compose.prod.yml restart django

# Redémarrer Grafana
docker compose -f docker-compose.monitoring.yml restart grafana
```

### Voir les logs en temps réel

```bash
# Tous les services prod
docker compose -f docker-compose.prod.yml logs -f

# Un service spécifique (ex: api)
docker compose -f docker-compose.prod.yml logs -f api

# Dernières 100 lignes
docker compose -f docker-compose.prod.yml logs --tail=100 api django
```

### Inspecter un container

```bash
docker inspect predilection-api
docker stats predilection-api predilection-django predilection-db
```

---

## Redémarrage complet de l'infrastructure

```bash
cd ~/docker-political

# Arrêt
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.monitoring.yml down

# Redémarrage
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.monitoring.yml up -d

# Vérification
docker compose -f docker-compose.prod.yml ps
```

---

## Rollback vers une version précédente

```bash
# Identifier la version précédente (GHCR)
# Remplacer <version> par le tag voulu (ex: develop-abc1234)
RELEASE_TAG=<version>

docker compose -f docker-compose.prod.yml pull
RELEASE_TAG=${RELEASE_TAG} docker compose -f docker-compose.prod.yml up -d

# Vérifier que l'application répond
curl -sk https://api.${DOMAIN_NAME}/health
```

---

## Vérifications de santé post-redémarrage

```bash
# API FastAPI
curl -sk https://api.${DOMAIN_NAME}/health

# Django frontend
curl -sk -o /dev/null -w "%{http_code}" https://${DOMAIN_NAME}/home/

# Prometheus (métriques)
curl -sk http://localhost:9090/-/healthy

# Grafana
curl -sk https://grafana.${DOMAIN_NAME}/api/health
```

---

## Rotation des certificats TLS (Traefik Let's Encrypt)

```bash
# Forcer le renouvellement (extrême recours — Traefik gère auto)
docker compose -f docker-compose.prod.yml restart traefik
```

---

## Nettoyage Docker

```bash
# Images inutilisées
docker image prune -f

# Volumes orphelins (attention : ne pas supprimer les volumes de données)
docker volume ls -f dangling=true

# Logs container trop volumineux
truncate -s 0 /var/lib/docker/containers/<container-id>/<container-id>-json.log
```
