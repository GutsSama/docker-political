#!/usr/bin/env bash
# =============================================================================
# restore.sh — Restauration d'un backup PostgreSQL
# =============================================================================
# Usage : bash scripts/restore.sh <fichier_backup.sql.gz>
# Variables d'env requises :
#   POSTGRES_USER     — utilisateur PostgreSQL
#   POSTGRES_DB       — nom de la base de données
#   POSTGRES_PASSWORD — mot de passe PostgreSQL
#   POSTGRES_HOST     — host PostgreSQL (défaut: db)
# =============================================================================

set -euo pipefail

POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-predilection}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"
POSTGRES_HOST="${POSTGRES_HOST:-db}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

BACKUP_FILE="${1:-}"

# ─── Vérifications ────────────────────────────────────────────────────────────
if [[ -z "${BACKUP_FILE}" ]]; then
    echo "Usage : $0 <fichier_backup.sql.gz>"
    echo "Exemple : $0 /var/backups/predilection/backup_predilection_20240601_020000.sql.gz"
    exit 1
fi

if [[ ! -f "${BACKUP_FILE}" ]]; then
    echo " Fichier introuvable : ${BACKUP_FILE}"
    exit 1
fi

echo "════════════════════════════════════════"
echo " RESTAURATION DE LA BASE : ${POSTGRES_DB}"
echo "Fichier source : ${BACKUP_FILE}"
echo "Host           : ${POSTGRES_HOST}:${POSTGRES_PORT}"
echo "════════════════════════════════════════"
echo ""
read -rp " ATTENTION : cette opération écrase la base existante. Continuer ? (oui/non) : " CONFIRM

if [[ "${CONFIRM}" != "oui" ]]; then
    echo "Restauration annulée."
    exit 0
fi

export PGPASSWORD="${POSTGRES_PASSWORD}"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Début de la restauration..."

# ─── Décompression et restauration ───────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Décompression et import en cours..."
gunzip -c "${BACKUP_FILE}" | psql \
    --host="${POSTGRES_HOST}" \
    --port="${POSTGRES_PORT}" \
    --username="${POSTGRES_USER}" \
    --dbname="${POSTGRES_DB}" \
    --set ON_ERROR_STOP=1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Restauration terminée avec succès."
echo "════════════════════════════════════════"

unset PGPASSWORD
