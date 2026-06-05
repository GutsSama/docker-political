# 🎯 Cheat Sheet DÉMO — Déploiement VPS CI/CD

> Garde ce fichier ouvert pendant ta présentation.
> Copie-colle les commandes dans l'ordre.

---

## 🖥️ PARTIE 1 — Connexion au VPS

```bash
# Se connecter au serveur VPS (depuis ton Mac)
ssh -p 1455 amaury@164.132.43.252
```

---

## 📦 PARTIE 2 — État de l'application sur le VPS

> Une fois connecté sur le VPS, te placer dans le dossier du projet :

```bash
cd ~/docker-political
```

```bash
# Voir tous les conteneurs actifs
docker compose -f docker-compose.prod.yml ps

# Voir les logs en temps réel (tous les conteneurs)
docker compose -f docker-compose.prod.yml logs -f

# Voir uniquement les logs de Traefik (reverse proxy / SSL)
docker compose -f docker-compose.prod.yml logs -f traefik

# Voir uniquement les logs de l'appli Django
docker compose -f docker-compose.prod.yml logs -f django

# Voir uniquement les logs de l'API FastAPI
docker compose -f docker-compose.prod.yml logs -f api
```

---

## 🔄 PARTIE 3 — Démontrer une release (déploiement d'une nouvelle version)

> Cette partie se fait DEPUIS TON MAC (pas le VPS)

### Étape 1 : Faire une modification de code visible

Exemple : modifier un texte sur la page d'accueil dans ton éditeur, puis :

```bash
# Depuis le dossier docker-political-solo sur ton Mac
git checkout develop
git add .
git commit -m "demo: modification visible pour la soutenance"
git push origin develop
```

### Étape 2 : Suivre le pipeline en direct

```bash
# Lister les pipelines GitHub Actions en cours
gh run list --limit 5

# Voir les logs d'un run en direct (remplacer l'ID)
gh run watch
```

> Ou ouvrir directement dans le navigateur : https://github.com/John-Do59/docker-political-solo/actions

### Étape 3 : Vérifier que le site est mis à jour

Ouvrir : **https://docker-political.duckdns.org/home**

---

## 🔐 PARTIE 4 — Prouver la sécurité (Zéro secret sur le disque)

> Une fois connecté sur le VPS

```bash
# Prouver qu'il n'y a aucun fichier .env avec des mots de passe
ls -la ~/docker-political/
# Attendu : PAS de fichier .env dans la liste

# Vérifier que les variables ne sont que dans la mémoire des conteneurs
docker inspect django-container | grep -A5 '"Env"'
```

---

## 🌐 PARTIE 5 — Vérifier le pare-feu et SSH

> Sur le VPS

```bash
# Voir les règles du pare-feu (seuls les ports 80, 443, 1455 sont autorisés)
sudo ufw status

# Voir les tentatives de connexion bloquées par Fail2ban
sudo fail2ban-client status sshd
```

---

## 🔒 PARTIE 6 — Vérifier le HTTPS

```bash
# Depuis ton Mac, vérifier le certificat SSL
curl -I https://docker-political.duckdns.org

# Attendu : HTTP/2 200 et header "server: traefik"
```

---

## 🐳 PARTIE 7 — Montrer les images versionnées dans la registry

> Depuis ton Mac

```bash
# Lister les images publiées sur GHCR (registry GitHub)
gh api /user/packages?package_type=container --jq '.[].name'
```

> Ou ouvrir directement : https://github.com/John-Do59?tab=packages

---

## 🔗 PARTIE 8 — URLs à avoir ouvertes pendant la démo

| Service | URL |
|---|---|
| Application Django | https://docker-political.duckdns.org/home |
| API FastAPI (Swagger) | https://api.docker-political.duckdns.org/docs |
| Dashboard Traefik | https://traefik.docker-political.duckdns.org/dashboard/ |
| GitHub Actions | https://github.com/John-Do59/docker-political-solo/actions |
| Registry GHCR | https://github.com/John-Do59?tab=packages |

---

## 🛠️ PARTIE 9 — En cas de problème (Urgence démo)

```bash
# Redémarrer tous les services manuellement (sur le VPS)
cd ~/docker-political
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d

# Redémarrer uniquement Traefik (si HTTPS cassé)
docker restart traefik-proxy

# Forcer un re-pull de toutes les images (si bug d'image)
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```
