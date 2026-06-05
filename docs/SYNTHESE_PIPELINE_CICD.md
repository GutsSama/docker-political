# Synthèse de la Pipeline CI/CD Complète

Ce document résume le fonctionnement de la livraison continue (Continuous Integration / Continuous Deployment) mise en place pour le projet `docker-political`.

---

## 🚀 1. Déclencheur (Le Trigger)

Le pipeline complet est orchestré par GitHub Actions (via le fichier `.github/workflows/deploy.yml`).
Il se déclenche de manière 100% automatisée lors d'un événement précis :
- Un `git push` sur la branche **`develop`** ou **`main`**.
- La création d'un tag de version (ex: `v1.0.0`).

---

## 🔄 2. Les 3 Étapes du Pipeline (Jobs)

Le pipeline est divisé en 3 travaux (Jobs) séquentiels. Si une étape échoue, la suivante est bloquée.

### Étape 1 : Tests (`test-api`)
- **Environnement** : Serveur éphémère Ubuntu fourni par GitHub.
- **Action** : Installe Python, les dépendances, et exécute les tests unitaires (Pytest) sur le code de l'API FastAPI.
- **Objectif** : Interdire le déploiement d'un code défectueux qui casserait la production.

### Étape 2 : Construction et Publication (`build-and-push`)
- **Prérequis** : Ne se lance que si les tests (`test-api`) ont réussi.
- **Action** : 
  1. Utilise les `Dockerfile` de l'API, de Django et du script d'ingestion.
  2. Construit les nouvelles images Docker applicatives.
  3. Publie (Push) ces images sur le registre privé **GitHub Container Registry (GHCR)** sous le compte `ghcr.io/john-do59/`.
- **Objectif** : Packager le code sous forme de conteneurs standardisés et les stocker dans le cloud de manière versionnée.

### Étape 3 : Déploiement sur le VPS (`deploy-vps`)
- **Prérequis** : Ne se lance que si le build (`build-and-push`) a réussi.
- **Action** : 
  1. **Transfert de fichiers (SCP)** : Copie uniquement les fichiers de configuration nécessaires (`docker-compose.prod.yml`, `scripts/deploy.sh`, `traefik.yml`) depuis GitHub vers le VPS. *Le code source Python n'est pas envoyé.*
  2. **Exécution SSH** : Se connecte au VPS et lance le script de déploiement (`deploy.sh`).
- **Objectif** : Mettre à jour le serveur sans intervention humaine.

---

## 🔐 3. L'Injection de Secrets en Mémoire (Sécurité)

La particularité de cette pipeline est sa **haute sécurité**.

- **Le problème classique** : Stocker un fichier `.env` sur le serveur. Si le serveur est piraté, tous les mots de passe sont compromis.
- **Notre solution DevOps** : 
  - Les mots de passe (DB, Clé Django, Tokens) sont stockés uniquement dans les **GitHub Secrets**.
  - Lors de l'Étape 3, GitHub Actions se connecte au VPS et lance la commande SSH en passant les secrets en tant que *variables d'environnement système* éphémères.
  - Le `docker-compose.prod.yml` intercepte ces variables dans la RAM pour démarrer les bases de données et les applications.
  - **Bilan** : Aucun mot de passe n'est écrit sur le disque dur du VPS.

---

## 🖥️ 4. Que fait concrètement le script `deploy.sh` sur le VPS ?

Ce script exécuté par le pipeline accomplit le travail final :
1. **Docker Login** : Il s'authentifie temporairement auprès de GitHub (GHCR) pour avoir le droit de télécharger nos images privées.
2. **Docker Pull** : Il télécharge les toutes dernières images Docker (fraîchement créées à l'Étape 2).
3. **Docker Compose Up** : Il relance les conteneurs en tâche de fond (`-d`) avec l'instruction `--remove-orphans`. Seuls les conteneurs dont l'image a changé sont redémarrés.
4. **Nettoyage** : Il supprime les vieilles images obsolètes pour éviter de saturer le disque du VPS (`docker image prune`).

---

## 🌍 5. Le Rôle de Traefik (Le Reverse Proxy)

Une fois l'application déployée, Traefik prend le relais pour exposer l'application sur Internet :
- **Routage** : Il écoute les ports 80 et 443. Si la requête demande `docker-political.duckdns.org`, il l'envoie à Django. Si elle demande `api.docker-political.duckdns.org`, il l'envoie à FastAPI.
- **HTTPS Automatique** : Il communique directement avec Let's Encrypt pour obtenir le certificat SSL vert, sans aucune intervention de notre part.

## 📈 Schéma Résumé

```text
💻 git push 
   │
   ▼
🐙 GitHub Actions
   ├── 🧪 1. Pytest (Vérifie le code)
   ├── 🐳 2. Build Docker (Construit les images)
   └── 📤 3. Push vers GHCR (Stocke les images)
   │
   ▼
🌐 Connexion SSH vers le VPS OVH
   ├── 📄 SCP (Copie du docker-compose.prod.yml)
   └── ⚡ Exécution avec variables injectées (Secrets en RAM)
       │
       ▼
🐳 Docker sur le VPS
   └── `docker compose pull && docker compose up -d`
       │
       ▼
🚀 L'application est en ligne (Traefik gère le HTTPS)
```
