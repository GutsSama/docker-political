# Architecture Docker (Production)

L'infrastructure applicative est entièrement conteneurisée et orchestrée via **Docker Compose** en utilisant le fichier `docker-compose.prod.yml`.

## Les Services

| Service | Rôle | Image Docker | Dépendances |
|---------|------|--------------|-------------|
| **traefik** | Reverse Proxy (point d'entrée unique). | `traefik:v3.3` (officielle) | - |
| **db** | Base de données relationnelle. | `postgres:17-alpine3.23` | - |
| **api** | Backend FastAPI (modèle ML et données). | `ghcr.io/.../predilection-api:<tag>` | `db` (healthy) |
| **django** | Frontend Web MVC. | `ghcr.io/.../predilection-django:<tag>` | `api` & `db` |
| **ingest** | Script d'ingestion de données initial. | `ghcr.io/.../predilection-ingest:<tag>`| `db` (healthy) |

> [!TIP]
> Le service `ingest` est conçu pour s'arrêter tout seul (exit 0) une fois son travail terminé. Il n'est pas redémarré en boucle (`restart: no`).

## Le Réseau Isolée (`predilection-net`)

Tous les conteneurs sont connectés à un réseau de type `bridge` nommé **`predilection-net`**.
**La règle d'or :** Aucun service applicatif (`api`, `django`, `db`) n'expose ses ports directement sur l'hôte VPS. Ils communiquent uniquement entre eux de manière sécurisée via les noms de services DNS internes gérés par Docker (ex: `http://api:8000`). Seul le service `traefik` écoute sur les ports `80` et `443` de l'hôte.

## Commandes Utiles

Les commandes suivantes doivent être exécutées dans le dossier contenant le `docker-compose.prod.yml`.

Vérifier l'état de tous les conteneurs :
```bash
docker compose -f docker-compose.prod.yml ps
```

Lire les logs en temps réel (ex: pour l'API) :
```bash
docker compose -f docker-compose.prod.yml logs -f api
```

Redémarrer manuellement l'infrastructure (zéro downtime si possible) :
```bash
docker compose -f docker-compose.prod.yml up -d
```

Nettoyer les anciennes images inutilisées :
```bash
docker image prune -f
```
