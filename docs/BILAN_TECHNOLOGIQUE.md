# Bilan Technologique : Alerting & Résilience

Ce document synthétise les technologies mises en place pour assurer la résilience, la surveillance et la fiabilité du projet **Prédi'lection**.

L'objectif de cette implémentation était de passer d'un simple déploiement à une **infrastructure robuste de niveau production**, capable de se surveiller elle-même, de prévenir les équipes en cas d'anomalie, de sauvegarder ses données et de résister à la charge.

---

## 1. Monitoring & Alerting (Observabilité)

### 📊 Prometheus & Middleware FastAPI
- **Rôle :** Collecter et stocker les métriques temporelles de l'application.
- **Implémentation :** Nous avons développé un middleware sur mesure (`metrics.py`) dans FastAPI. Ce middleware intercepte chaque requête API et expose des métriques de type *compteur* (nombre de requêtes, erreurs HTTP) et *histogramme* (temps de latence).
- **Avantage :** Permet d'avoir une vue précise sur la santé métier (Business Metrics) : requêtes par seconde, latence (p95, p99), taux d'erreurs (4xx, 5xx).

### 📈 Grafana & Unified Alerting
- **Rôle :** Visualisation des données et gestion des règles d'alertes.
- **Implémentation :** Configuration **as-code** via le provisioning (dossier `provisioning/alerting/`).
- **Fonctionnement :** Grafana interroge Prometheus en permanence. Si une règle est enfreinte (ex: *Utilisation CPU > 85%* ou *Latence API > 2s*), Grafana déclenche une alerte qui est envoyée sur un canal de communication (ex: Discord) via les *Contact Points*.

---

## 2. Haute Disponibilité (Uptime)

### 🟢 Uptime Kuma
- **Rôle :** Surveillance externe active (Blackbox monitoring).
- **Implémentation :** Un service indépendant qui effectue des requêtes (ping / HTTP) régulières (toutes les 60 secondes) vers les points critiques :
  - `https://api.domain.com/health` (FastAPI)
  - `https://app.domain.com/home` (Django)
- **Avantage :** En cas de chute complète de l'infrastructure Docker, Prometheus ne pourrait potentiellement pas envoyer d'alertes. Uptime Kuma agit comme un superviseur externe ultime. Un script Python automatisé (`setup_uptime_kuma.py`) configure ces moniteurs via API pour éviter une configuration manuelle.

---

## 3. Sécurité des Données (Résilience)

### 💾 Scripts Bash & GitHub Actions (Sauvegardes PostgreSQL)
- **Rôle :** Prévenir la perte de données en cas de crash critique de la base de données.
- **Implémentation :**
  - Scripts Bash sécurisés (`backup.sh`, `restore.sh`, `verify_backup.sh`) effectuant des dumps SQL compressés (`pg_dump`).
  - **Automatisation CI/CD :** Un workflow GitHub Actions (`backup.yml`) déclenché via un *CRON* régulier. Il se connecte en SSH au VPS, lance la sauvegarde, et s'assure qu'elle n'est pas corrompue.
  - **Rotation :** Suppression automatique des sauvegardes de plus de 7 jours pour préserver l'espace disque.

---

## 4. Tests de Performance & Saturation

### 🔥 k6 (Load Testing)
- **Rôle :** Valider la capacité du serveur à absorber un fort trafic (tests de charge) et trouver le point de rupture (tests de stress).
- **Implémentation :** Scripts en JavaScript exécutés par le moteur k6 (écrit en Go, conçu pour les hautes performances).
  - `smoke.js` : Test rapide pour la CI/CD (1 utilisateur).
  - `load.js` : Test de charge standard simulant 100 utilisateurs simultanés sur une longue période.
  - `stress.js` : Test poussant le serveur à bout (500 VUs) pour identifier ce qui lâche en premier (Base de données ? RAM ? CPU ?).
- **Impact :** Garantir que lors d'un pic de fréquentation (ex: période électorale), l'infrastructure ne s'écroulera pas.

---

## 5. Déploiement Fiable & Runbooks

### 🚀 GitHub Actions & Mécanismes de "Retry"
- **Rôle :** S'assurer que le pipeline de déploiement ne génère pas de faux-positifs et tolère les ralentissements du serveur.
- **Implémentation :** Le fichier `deploy.yml` intègre désormais des boucles de réessai (*Retry loops*) lors des Smoke Tests post-déploiement. L'application dispose de 2 minutes pour démarrer correctement et obtenir ses certificats Let's Encrypt (Traefik) avant que la CI/CD ne signale une erreur.

### 📚 Documentation Opérationnelle (RUNBOOK)
- **Rôle :** Démocratiser la gestion du serveur et réduire le temps de réponse humain en cas d'incident (MTTR - *Mean Time To Recovery*).
- **Documents :**
  - `RUNBOOK.md` : Guide d'intervention d'urgence (redémarrages, rollbacks).
  - `DEPLOYMENT.md` : Architecture du déploiement et gestion des variables sécurisées (`secrets` & `vars`).

---

## Résumé du Flux de Résilience

1. **Prévention** : Tests k6 pour dimensionner le serveur + Pipeline CI de qualité.
2. **Surveillance** : Uptime Kuma (externe) et Prometheus (interne).
3. **Alerte** : Grafana contacte l'équipe via Discord/Email.
4. **Action** : L'équipe utilise le `RUNBOOK.md` pour intervenir.
5. **Récupération** : Les données sont restaurées grâce à `restore.sh` issu des backups automatisés.
