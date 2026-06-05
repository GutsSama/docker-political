# Document d'Implémentation Technique : Observabilité & DevSecOps

Ce document explique les choix techniques et l'implémentation des outils ajoutés au projet `docker-political-solo`. Il sert de référence pour comprendre *comment* et *pourquoi* chaque technologie a été configurée.

---

## Sprint 1 : DevSecOps (Sécurité du Pipeline)

L'objectif de ce sprint est de s'assurer qu'aucune faille ou secret n'est déployé en production. Les vérifications s'exécutent automatiquement via GitHub Actions.

### 1. Gitleaks (Détection de secrets)
**Branche :** `feature/gitleaks`
**Technologie :** Gitleaks est un outil d'analyse statique (SAST) spécialisé dans la détection de secrets (clés API, mots de passe, tokens) codés en dur.
**Implémentation :**
- Création du workflow `.github/workflows/gitleaks.yml`.
- Le paramètre `fetch-depth: 0` permet de vérifier **tout l'historique** Git. Si un développeur commite un mot de passe et l'efface au commit suivant, Gitleaks le trouvera quand même et bloquera la Pull Request.

### 2. CodeQL (Analyse statique de sécurité)
**Branche :** `feature/codeql-security`
**Technologie :** Le moteur d'analyse de code de GitHub.
**Implémentation :**
- Création du workflow `.github/workflows/codeql.yml`.
- Scanne les langages `python` (Django, FastAPI) et `javascript` (Frontend).
- Il analyse le code source à la recherche de vulnérabilités logiques (injections SQL, XSS, etc.) et remonte les alertes directement dans l'onglet "Security" du dépôt GitHub.

### 3. Trivy (Scan d'images Docker)
**Branche :** `feature/trivy-image-scan`
**Technologie :** Un scanner de vulnérabilités pour les conteneurs développé par Aqua Security.
**Implémentation :**
- Ajouté directement dans `.github/workflows/deploy.yml`.
- **Stratégie intelligente :** Au lieu de construire l'image et de la pousser aveuglément sur le registre (GHCR), GitHub Actions la construit **localement** (`load: true`), Trivy la scanne, et si aucune faille `CRITICAL` n'est détectée au niveau de l'OS ou des bibliothèques (`exit-code: 1`), l'image est alors poussée (`docker push`).

---

## Sprint 2 : Observabilité (Monitoring Infrastructure)

La mise en place d'une stack de monitoring pour surveiller la santé du VPS et des conteneurs. Pour ne pas interférer avec l'application, ces outils tournent dans leur propre fichier de configuration : `docker-compose.monitoring.yml`.

Toutes les images utilisées sont des versions **Alpine** ou minimalistes pour économiser la RAM du VPS (8 Go).

### 1. Node Exporter
**Branche :** `feature/node-exporter`
**Technologie :** Un agent (démon) qui collecte les métriques matérielles et de l'OS du serveur (CPU, RAM, E/S disques, Réseau).
**Implémentation :** Il est monté avec des accès en lecture seule (`:ro`) au système de fichiers hôte (`/proc`, `/sys`) pour récolter les informations du VPS physique.

### 2. cAdvisor (Container Advisor)
**Branche :** `feature/cadvisor-monitoring`
**Technologie :** Un outil de Google qui collecte les métriques spécifiques à l'utilisation des ressources **des conteneurs Docker** en cours d'exécution.
**Implémentation :** Il écoute directement le démon Docker (`/var/lib/docker`) pour analyser combien de RAM et de CPU consomment spécifiquement Django, FastAPI, Postgres, etc.

### 3. Prometheus
**Branche :** `feature/prometheus-monitoring`
**Technologie :** La base de données temporelle au cœur de la stack. C'est lui qui va aspirer (scrapper) les métriques.
**Implémentation :**
- Configuration dans `monitoring/prometheus/prometheus.yml`.
- Il est configuré pour interroger `node-exporter` et `cadvisor` toutes les 15 secondes.
- Les données sont stockées dans un volume persistant (`prometheus_data`).

### 4. Grafana
**Branche :** `feature/grafana-dashboard`
**Technologie :** L'interface de visualisation (tableaux de bord) qui se connecte à Prometheus pour afficher des graphiques.
**Implémentation :**
- Connecté au réseau `predilection-net`.
- Exposé sur Internet via Traefik sur le sous-domaine `grafana.DOMAIN_NAME`.
- **Sécurité :** L'accès est protégé par la réutilisation du middleware `auth@file` (BasicAuth) défini précédemment pour le dashboard Traefik.

---

## Sprint 3 : Supervision (Disponibilité)

### 1. Uptime Kuma
**Branche :** `feature/uptime-kuma`
**Technologie :** Un outil de monitoring de type "Ping" très visuel, agissant comme une alternative auto-hébergée à UptimeRobot.
**Implémentation :**
- Ajouté dans `docker-compose.monitoring.yml`.
- Exposé publiquement via Traefik sur le sous-domaine `kuma.DOMAIN_NAME` (ex: `kuma.docker-political.duckdns.org`).
- Contrairement à Grafana, Uptime Kuma intègre nativement son propre système d'authentification robuste avec création de compte admin lors du premier lancement, le BasicAuth de Traefik n'est donc pas imposé dessus.
- **Rôle :** Il va appeler périodiquement nos API et notre Frontend (HTTP 200) et nous alertera (visuellement, ou via Discord/Telegram plus tard) si le serveur tombe en panne.

---

## Sprint 4 : Centralisation des Logs

*(À venir : Loki et Promtail)*
