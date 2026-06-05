# Plan d'Implémentation Observabilité & DevSecOps

## Contexte

Le projet dispose déjà :

* d'un dépôt GitHub
* d'une pipeline CI/CD GitHub Actions
* d'une application conteneurisée avec Docker
* d'un déploiement automatique sur VPS OVH
* d'un reverse proxy Traefik
* d'un environnement de production fonctionnel

L'objectif est maintenant de renforcer :

1. La sécurité du pipeline (DevSecOps)
2. L'observabilité de l'infrastructure
3. La supervision de la disponibilité
4. La collecte et l'analyse des métriques

---

# Phase 1 — Renforcement DevSecOps

## Branche : feature/gitleaks

### Objectif

Détecter les secrets exposés dans le dépôt Git.

### Tâches

* Ajouter Gitleaks dans GitHub Actions
* Bloquer la pipeline en cas de fuite de secret
* Vérifier les faux positifs

### Résultat attendu

* Détection automatique des clés API
* Détection des tokens GitHub
* Détection des mots de passe accidentellement versionnés

---

## Branche : feature/codeql-security

### Objectif

Mettre en place une analyse statique de sécurité du code.

### Tâches

* Activer GitHub CodeQL
* Configurer l'analyse Python
* Vérifier les alertes GitHub Security

### Résultat attendu

* Détection de vulnérabilités potentielles
* Rapports de sécurité directement dans GitHub

---

## Branche : feature/trivy-scan

### Objectif

Scanner les images Docker avant leur publication.

### Tâches

* Ajouter Trivy à la pipeline
* Scanner les images générées
* Bloquer les vulnérabilités critiques

### Résultat attendu

Pipeline :

Tests
→ Trivy
→ Build Docker
→ Push Registry
→ Deploy VPS

---

# Phase 2 — Monitoring Infrastructure

## Branche : feature/node-exporter

### Objectif

Collecter les métriques système du VPS.

### Tâches

* Ajouter Node Exporter au docker-compose.monitoring.yml
* Exposer les métriques à Prometheus

### Métriques collectées

* CPU
* RAM
* Disque
* Réseau
* Charge système

### Résultat attendu

Le VPS devient observable par Prometheus.

---

## Branche : feature/prometheus-monitoring

### Objectif

Centraliser les métriques de supervision.

### Tâches

* Déployer Prometheus
* Configurer les targets
* Ajouter Node Exporter

### Résultat attendu

Prometheus collecte les métriques du VPS.

---

## Branche : feature/grafana-dashboard

### Objectif

Visualiser les métriques via des dashboards.

### Tâches

* Déployer Grafana
* Connecter Prometheus
* Importer les dashboards recommandés

### Dashboards

#### VPS Monitoring

* CPU
* RAM
* Disque
* Réseau

#### Infrastructure Monitoring

* Disponibilité
* Consommation globale

### Résultat attendu

Visualisation en temps réel de l'état du serveur.

---

## Branche : feature/cadvisor

### Objectif

Superviser les conteneurs Docker.

### Tâches

* Déployer cAdvisor
* Connecter Prometheus

### Métriques collectées

* CPU des conteneurs
* RAM des conteneurs
* I/O disque
* Réseau

### Résultat attendu

Monitoring détaillé des conteneurs.

---

# Phase 3 — Supervision

## Branche : feature/uptime-kuma

### Objectif

Surveiller la disponibilité des services.

### Tâches

* Déployer Uptime Kuma
* Configurer les endpoints

### Services surveillés

* Frontend
* Backend API
* Grafana
* Traefik

### Alertes

* Email
* Discord
* Telegram (optionnel)

### Résultat attendu

Notification automatique en cas d'indisponibilité.

---

# Phase 4 — Centralisation des Logs (Optionnelle)

## Branche : feature/loki

### Objectif

Stocker les logs applicatifs.

### Tâches

* Déployer Loki
* Configurer le stockage

### Résultat attendu

Centralisation des logs.

---

## Branche : feature/promtail

### Objectif

Collecter les logs Docker.

### Tâches

* Déployer Promtail
* Connecter Loki

### Résultat attendu

Visualisation des logs dans Grafana.

---

# Architecture Finale

GitHub
│
├── Tests Automatisés
├── Gitleaks
├── CodeQL
├── Trivy
└── GitHub Actions
│
▼
VPS OVH
│
├── Traefik
├── Application
├── Prometheus
├── Grafana
├── Node Exporter
├── cAdvisor
├── Uptime Kuma
├── Loki (optionnel)
└── Promtail (optionnel)

---

# Structure Docker Recommandée

## docker-compose.yml

Services métier :

* Application
* Base de données
* Traefik

## docker-compose.monitoring.yml

Services d'observabilité :

* Prometheus
* Grafana
* Node Exporter
* cAdvisor
* Uptime Kuma
* Loki (optionnel)
* Promtail (optionnel)

---

# Priorité d'Implémentation

## Priorité Haute

1. Gitleaks
2. CodeQL
3. Trivy

## Priorité Moyenne

4. Node Exporter
5. Prometheus
6. Grafana
7. cAdvisor

## Priorité Basse

8. Uptime Kuma
9. Loki
10. Promtail

---

# Résultat Final

Le projet disposera :

* d'une CI/CD automatisée
* d'un contrôle de sécurité du code
* d'un contrôle de sécurité des images Docker
* d'une détection de secrets
* d'un monitoring système
* d'un monitoring Docker
* d'une supervision de disponibilité
* d'une observabilité complète
* d'une architecture DevSecOps moderne
