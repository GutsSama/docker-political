# Document d'Implémentation Technique : Observabilité & DevSecOps

Ce document est le journal d'implémentation technique des outils ajoutés au projet `docker-political-solo`. Il sera mis à jour à chaque nouvelle fonctionnalité intégrée.

## Phase 1 : DevSecOps

### 1. Gitleaks (Détection de secrets)
**Branche :** `feature/gitleaks`
**Implémentation :**
- Création d'un workflow GitHub Actions dédié : `.github/workflows/gitleaks.yml`.
- Se déclenche sur les `push` et `pull_request` vers `develop` et `main`.
- Utilise l'action officielle `gitleaks/gitleaks-action@v2`.
- `fetch-depth: 0` permet de scanner l'ensemble de l'historique Git pour détecter toute compromission passée.
**Statut :** ✅ Implémenté.

*(À venir : CodeQL, Trivy)*

## Phase 2 : Observabilité (Monitoring Infrastructure)

*(À venir : Node Exporter, Prometheus, Grafana, cAdvisor)*

## Phase 3 : Supervision (Disponibilité)

*(À venir : Uptime Kuma)*

## Phase 4 : Centralisation des Logs (Optionnel)

*(À venir : Loki, Promtail)*
