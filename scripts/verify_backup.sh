#!/usr/bin/env bash
# =============================================================================
# verify_backup.sh — Vérification d'intégrité des backups PostgreSQL
# =============================================================================
# Usage : bash scripts/verify_backup.sh [fichier.sql.gz]
#   Sans argument → vérifie le backup le plus récent
# =============================================================================

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/predilection}"
LOG_FILE="${BACKUP_DIR}/backup.log"
MIN_SIZE_BYTES=1000   # taille minimale acceptable (1 Ko)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
}

# ─── Sélection du fichier ─────────────────────────────────────────────────────
if [[ -n "${1:-}" ]]; then
    BACKUP_FILE="${1}"
else
    # Dernier backup
    BACKUP_FILE="$(find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f | sort | tail -1)"
fi

if [[ -z "${BACKUP_FILE}" || ! -f "${BACKUP_FILE}" ]]; then
    log "Aucun fichier backup trouvé dans ${BACKUP_DIR}"
    exit 1
fi

log "Vérification : ${BACKUP_FILE}"

# ─── Test 1 : taille minimale ─────────────────────────────────────────────────
FILE_SIZE=$(stat -c%s "${BACKUP_FILE}" 2>/dev/null || stat -f%z "${BACKUP_FILE}")
if [[ "${FILE_SIZE}" -lt "${MIN_SIZE_BYTES}" ]]; then
    log "ERREUR : Fichier trop petit (${FILE_SIZE} bytes < ${MIN_SIZE_BYTES} bytes minimum)"
    exit 1
fi
log "Taille OK : $(du -sh "${BACKUP_FILE}" | cut -f1)"

# ─── Test 2 : intégrité gzip ──────────────────────────────────────────────────
if gzip -t "${BACKUP_FILE}" 2>/dev/null; then
    log " Intégrité gzip OK"
else
    log "ERREUR : Le fichier gzip est corrompu."
    exit 1
fi

# ─── Test 3 : contenu SQL (header PostgreSQL) ────────────────────────────────
HEADER=$(gunzip -c "${BACKUP_FILE}" 2>/dev/null | head -5)
if echo "${HEADER}" | grep -qi "postgresql"; then
    log " OK :Header SQL PostgreSQL détecté"
else
    log "AVERTISSEMENT : Header PostgreSQL non détecté (fichier potentiellement vide ou corrompu)"
fi

# ─── Résumé ───────────────────────────────────────────────────────────────────
log "Vérification terminée — backup valide : ${BACKUP_FILE}"
