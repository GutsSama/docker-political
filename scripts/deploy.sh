#!/bin/bash
# deploy.sh — Script de déploiement idempotent sur le VPS
# Usage : ./scripts/deploy.sh <IMAGE_TAG>
# Exemple : ./scripts/deploy.sh v1.2.3
#
# Secrets requis (injectés par GitHub Actions via SSH envs, jamais stockés sur disque) :
#   DATABASE_URL, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
#   SECRET_KEY, DEBUG, DOMAIN_NAME, TRAEFIK_DASHBOARD_CREDENTIALS

set -euo pipefail

IMAGE_TAG="${1:-latest}"
DEPLOY_DIR="/home/amaury/docker-political"
COMPOSE_FILE="docker-compose.prod.yml"

echo "▶ [deploy.sh] Déploiement de la version : ${IMAGE_TAG}"
echo "  Répertoire de déploiement : ${DEPLOY_DIR}"

# 1. Se placer dans le dossier du projet
cd "${DEPLOY_DIR}"

# 2. Exporter le tag de l'image pour que docker compose le prenne en compte
#    Les autres variables (DATABASE_URL, SECRET_KEY, etc.) sont déjà présentes
#    dans l'environnement du shell SSH, injectées par GitHub Actions.
export RELEASE_TAG="${IMAGE_TAG}"

# 3. Connexion au registre GHCR pour pouvoir pull les images privées
echo "🔐 Connexion à GHCR..."
echo "${GITHUB_TOKEN:-}" | docker login ghcr.io -u john-do59 --password-stdin 2>/dev/null || true

# 4. Récupérer les nouvelles images depuis GHCR
echo "📦 Pull des images depuis GHCR..."
docker compose -f "${COMPOSE_FILE}" pull

# 5. Redémarrer les services (recréation uniquement si l'image a changé)
echo "🔄 Redémarrage des services..."
docker compose -f "${COMPOSE_FILE}" up -d --remove-orphans

# 6. Supprimer les images inutilisées pour libérer de l'espace
docker image prune -f

echo "✅ Déploiement terminé avec succès."

# 7. Vérification rapide : health check HTTP sur l'app Django
echo "🩺 Vérification santé de l'application..."
sleep 5
HTTP_CODE=$(curl -s -H "Host: ${DOMAIN_NAME}" -o /dev/null -w "%{http_code}" http://localhost/home || echo "000")
if [ "${HTTP_CODE}" = "200" ] || [ "${HTTP_CODE}" = "302" ]; then
    echo "✅ Application accessible (HTTP ${HTTP_CODE})."
else
    echo "⚠️  Attention : l'application renvoie HTTP ${HTTP_CODE}. Vérifiez les logs :"
    echo "   docker compose -f ${COMPOSE_FILE} logs --tail=50"
fi
