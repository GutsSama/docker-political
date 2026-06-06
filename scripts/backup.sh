#!/usr/bin/env bash
# =============================================================================
# backup.sh — Sauvegarde automatique PostgreSQL
# =============================================================================
# Usage : bash scripts/backup.sh
# Variables d'env requises :
#   POSTGRES_USER     — utilisateur PostgreSQL
#   POSTGRES_DB       — nom de la base de données
#   POSTGRES_PASSWORD — mot de passe PostgreSQL
#   BACKUP_DIR        — dossier de destination (défaut: /var/backups/predilection)
#   BACKUP_RETENTION  — nombre de jours de rétention (défaut: 7)
# =============================================================================

set -euo pipefail

# ─── Configuration ────────────────────────────────────────────────────────────
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-predilection}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"
POSTGRES_HOST="${POSTGRES_HOST:-db}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/predilection}"
BACKUP_RETENTION="${BACKUP_RETENTION:-7}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="${BACKUP_DIR}/backup_${POSTGRES_DB}_${TIMESTAMP}.sql.gz"
LOG_FILE="${BACKUP_DIR}/backup.log"

# ─── Création du dossier de backup ────────────────────────────────────────────
mkdir -p "${BACKUP_DIR}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
}

log "════════════════════════════════════════"
log "Démarrage du backup : ${POSTGRES_DB}"
log "Destination         : ${BACKUP_FILE}"

# ─── Export du mot de passe (évite le prompt interactif) ─────────────────────
export PGPASSWORD="${POSTGRES_PASSWORD}"

# ─── Dump + compression ───────────────────────────────────────────────────────
log "Exécution de pg_dump..."
if pg_dump \
    --host="${POSTGRES_HOST}" \
    --port="${POSTGRES_PORT}" \
    --username="${POSTGRES_USER}" \
    --dbname="${POSTGRES_DB}" \
    --format=plain \
    --no-owner \
    --no-acl \
    | gzip -9 > "${BACKUP_FILE}"; then
    log " Backup créé avec succès."
else
    log " ERREUR : pg_dump a échoué."
    exit 1
fi

# ─── Vérification taille minimale (fichier non vide) ──────────────────────────
BACKUP_SIZE=$(stat -c%s "${BACKUP_FILE}" 2>/dev/null || stat -f%z "${BACKUP_FILE}")
if [[ "${BACKUP_SIZE}" -lt 100 ]]; then
    log "ERREUR : Le fichier backup semble vide (${BACKUP_SIZE} bytes)."
    rm -f "${BACKUP_FILE}"
    exit 1
fi
log "Taille du backup : $(du -sh "${BACKUP_FILE}" | cut -f1)"

# ─── Rotation : suppression des backups > BACKUP_RETENTION jours ──────────────
log "Rotation : suppression des backups de plus de ${BACKUP_RETENTION} jours..."
find "${BACKUP_DIR}" -name "backup_*.sql.gz" -mtime "+${BACKUP_RETENTION}" -delete
REMAINING=$(find "${BACKUP_DIR}" -name "backup_*.sql.gz" | wc -l)
log "Backups restants : ${REMAINING}"

log "Backup terminé : ${BACKUP_FILE}"
log "════════════════════════════════════════"
unset PGPASSWORD
