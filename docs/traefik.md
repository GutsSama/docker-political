# Traefik : Reverse Proxy & SSL

Dans notre environnement de production, [Traefik](https://traefik.io/) est le chef d'orchestre de notre trafic réseau. Il s'agit d'un "Edge Router" moderne qui écoute toutes les requêtes entrantes sur le VPS (ports 80 et 443) et les redirige vers le bon conteneur Docker.

## Fonctions Principales

1. **Découverte Automatique (Docker Provider) :** 
   Traefik surveille le socket Docker (`/var/run/docker.sock`). Lorsqu'un nouveau conteneur est lancé avec les bons labels (ex: `traefik.enable=true`), Traefik crée automatiquement la route réseau correspondante sans nécessiter de redémarrage.

2. **Terminaison TLS (HTTPS / Let's Encrypt) :**
   Il gère automatiquement la génération et le renouvellement des certificats SSL gratuits via l'autorité ACME (Let's Encrypt). Le trafic HTTP sur le port 80 est systématiquement redirigé vers HTTPS sur le port 443.

## Configuration des Routes (Labels)

Dans `docker-compose.prod.yml`, nous définissons les règles de routage sous forme de *labels* attachés aux conteneurs cibles :

### Application Web (Django)
```yaml
- "traefik.http.routers.django.rule=Host(`${DOMAIN_NAME}`)"
```
➜ Si la requête HTTP demande le nom de domaine principal (ex: `monsite.fr`), elle est envoyée à Django.

### Fichiers Statiques (Django)
```yaml
- "traefik.http.routers.static.rule=Host(`${DOMAIN_NAME}`) && PathPrefix(`/static/`)"
```
➜ Si l'URL contient `/static/`, la requête est également routée vers le serveur Django (qui utilise WhiteNoise).

### API Backend (FastAPI)
```yaml
- "traefik.http.routers.api.rule=Host(`api.${DOMAIN_NAME}`)"
```
➜ Le trafic sur le sous-domaine `api.monsite.fr` est envoyé au conteneur FastAPI.

## Dashboard Sécurisé

Traefik expose une interface web d'administration permettant de visualiser l'état de toutes les routes.
- **Accès :** `https://traefik.votre-domaine.fr/dashboard/` (Ne pas oublier le slash final).
- **Sécurité :** L'accès est protégé par un middleware `BasicAuth`.

Pour modifier le mot de passe du dashboard, vous devez générer un nouveau hash (utilitaire `htpasswd`) et mettre à jour la variable `TRAEFIK_DASHBOARD_CREDENTIALS` dans votre fichier `.env` ou dans les secrets de CI/CD.
