# 📋 Cheat Sheet VPS — docker-political

Toutes les commandes utiles au quotidien pour administrer le VPS et l'application.

---

## 🔌 Connexion VPS

# Cheat Sheet : Commandes VPS, Docker et Traefik

Ce fichier regroupe toutes les commandes utiles pour administrer, débugger et maintenir votre serveur VPS et l'application `docker-political-solo`.

## 1. Connexion au VPS
Pour se connecter au serveur en SSH :
```bash
ssh -p 1455 amaury@164.132.43.252
```

---

## 📊 Vérifier que le serveur fonctionne

```bash
uptime          # Durée de fonctionnement du serveur
free -h         # Mémoire RAM disponible
df -h           # Espace disque
top             # Processus en cours (basique)
htop            # Processus en cours (amélioré)
```

---

## 🐳 Vérifier Docker

```bash
# Version Docker
docker --version

# Version Compose
docker compose version

# Conteneurs en cours d'exécution
docker ps

# Tous les conteneurs (y compris arrêtés)
docker ps -a

# Images téléchargées
docker images

# Volumes persistants
docker volume ls

# Réseaux Docker
docker network ls
```

---

## 📜 Logs des conteneurs

```bash
# Traefik (reverse proxy / SSL)
docker logs traefik-proxy --tail=100

# FastAPI
docker logs fastapi-container --tail=100

# Django
docker logs django-container --tail=100

# PostgreSQL
docker logs prediclection-db-container --tail=100

# Suivre les logs en temps réel (Ctrl+C pour quitter)
docker logs -f django-container
docker logs -f traefik-proxy
```

---

## 🔀 Vérifier Traefik

```bash
# Voir les erreurs SSL / Let's Encrypt
docker logs traefik-proxy | grep ACME

# Voir les erreurs réseau
docker logs traefik-proxy | grep network

# Tester HTTP
curl -I http://docker-political.duckdns.org

# Tester HTTPS
curl -I https://docker-political.duckdns.org

# Tester l'API FastAPI
curl https://api.docker-political.duckdns.org
```

---

## 🔒 Vérifier Let's Encrypt

```bash
# Voir le volume letsencrypt
docker volume ls | grep letsencrypt

# ⚠️  Supprimer acme.json corrompu (UNIQUEMENT si le HTTPS est cassé)
docker run --rm -v docker-political_letsencrypt_data:/letsencrypt alpine rm -f /letsencrypt/acme.json

# Redémarrer Traefik pour regénérer le certificat
docker restart traefik-proxy
```

---

## 🛡️ Vérifier le Pare-feu

```bash
# Statut général
sudo ufw status

# Avec numéros de règles
sudo ufw status numbered

# Voir les ports en écoute
sudo ss -tulpn
```

---

## 🌐 Vérifier le DNS

```bash
# Depuis ton Mac (vérifier que le domaine pointe bien vers le VPS)
nslookup docker-political.duckdns.org
# ou
dig docker-political.duckdns.org
```

> ✅ Résultat attendu : `164.132.43.252`

---

## 🗄️ Vérifier PostgreSQL

```bash
# Entrer dans le conteneur PostgreSQL
docker exec -it prediclection-db-container sh

# Se connecter à PostgreSQL
psql -U postgres

# Lister les bases de données
\l

# Lister les tables
\dt

# Quitter
\q
```

---

## 🐍 Vérifier Django

```bash
# Lancer les migrations
docker exec -it django-container python manage.py migrate

# Créer les fichiers de migration
docker exec -it django-container python manage.py makemigrations

# Ouvrir le shell Django interactif
docker exec -it django-container python manage.py shell

# Créer un superutilisateur (admin)
docker exec -it django-container python manage.py createsuperuser
```

---

## ⚡ Vérifier FastAPI

```bash
# Entrer dans le conteneur FastAPI
docker exec -it fastapi-container sh

# Tester l'API localement depuis l'intérieur du conteneur
curl http://localhost:8000

# Tester depuis l'extérieur
curl https://api.docker-political.duckdns.org/docs
```

---

## 🔄 Redéployer manuellement (sans CI/CD)

```bash
# Se placer dans le dossier du projet
cd ~/docker-political

# Télécharger les nouvelles images depuis GHCR
docker compose -f docker-compose.prod.yml pull

# Redémarrer les conteneurs
docker compose -f docker-compose.prod.yml up -d

# Nettoyer les vieilles images
docker image prune -af
```

---

## ⚡ Diagnostic Rapide (5 commandes prioritaires)

En cas de problème, lancer dans cet ordre :

```bash
# 1. État des conteneurs
docker ps

# 2. Logs Traefik (problèmes de routage / SSL)
docker logs traefik-proxy --tail=50

# 3. Logs Django (erreurs Python)
docker logs django-container --tail=50

# 4. Logs FastAPI (erreurs API)
docker logs fastapi-container --tail=50

# 5. Pare-feu
sudo ufw status
```

---

## 🧠 Rappel : Les 2 Problèmes Historiques Résolus

> Ces deux commandes permettent de vérifier que les bugs originaux n'ont pas réapparu.

```bash
# 1. Vérifier que Let's Encrypt n'affiche plus "example.com"
docker logs traefik-proxy --tail=100 | grep ACME

# 2. Vérifier le nom exact du réseau Docker (doit être "predilection-net")
docker network ls | grep predilection
```

| Problème | Cause | Solution appliquée |
|---|---|---|
| HTTPS cassé | Email `example.com` banni par Let's Encrypt | Remplacé par `admin@docker-political.duckdns.org` |
| Traefik 404 | Réseau Docker préfixé (`docker-political_predilection-net`) | Forcé `name: predilection-net` dans `docker-compose.prod.yml` |
## 2. Commandes Docker Essentielles
Une fois connecté sur le VPS, placez-vous dans le dossier du projet :
```bash
cd ~/docker-political
```

### Voir l'état des conteneurs
```bash
docker compose ps
# ou plus détaillé :
docker ps -a
```

### Redémarrer les services (manuellement)
*Normalement, GitHub Actions le fait pour vous, mais c'est utile pour forcer un redémarrage.*
```bash
docker compose down
docker compose up -d
```

### Lire les logs en direct
```bash
# Tous les conteneurs :
docker compose logs -f

# Uniquement Traefik (très utile pour débugger le HTTPS) :
docker compose logs -f traefik-proxy

# Uniquement Django (pour voir les erreurs Python) :
docker compose logs -f django
```

### Nettoyer le serveur (Libérer de l'espace)
Docker a tendance à accumuler les vieilles images. Pour nettoyer :
```bash
# Supprime les images non utilisées :
docker image prune -a -f

# Grand nettoyage (images, conteneurs arrêtés, volumes non utilisés) :
docker system prune -a --volumes
```

## 3. Gestion du SSL / HTTPS (Traefik & Let's Encrypt)

Si le HTTPS tombe en panne ou affiche "Non sécurisé", c'est généralement que Traefik a enregistré une erreur dans son fichier `acme.json` et refuse de réessayer.

### Comment forcer la regénération du certificat SSL :
1. **Supprimer le fichier corrompu stocké dans le volume Docker :**
```bash
docker run --rm -v docker-political_letsencrypt_data:/letsencrypt alpine rm -f /letsencrypt/acme.json
```
2. **Redémarrer Traefik pour qu'il refasse la demande :**
```bash
docker restart traefik-proxy
```
3. **Vérifier que Traefik a bien obtenu le certificat :**
```bash
docker logs traefik-proxy --tail=50
# Vous cherchez le message : "Successfully obtained certificate"
```

## 4. Vérifications de Santé (Health Checks)

### Vérifier que le serveur web répond localement
```bash
curl -I http://localhost
```

### Vérifier les ports ouverts sur le pare-feu
```bash
sudo ufw status
# Assurez-vous que les ports 80 (HTTP), 443 (HTTPS) et 1455 (SSH) sont en ALLOW
```

## 5. Commandes GitHub Actions (Bonus)
Si vous devez relancer le pipeline manuellement sans faire de `git push`, vous pouvez utiliser le CLI GitHub (`gh`) depuis votre Mac :
```bash
# Lister les derniers déploiements
gh run list

# Relancer le dernier déploiement échoué
gh run rerun <ID_DU_RUN>
```
