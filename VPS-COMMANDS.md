# Cheat Sheet : Commandes VPS, Docker et Traefik

Ce fichier regroupe toutes les commandes utiles pour administrer, débugger et maintenir votre serveur VPS et l'application `docker-political-solo`.

## 1. Connexion au VPS
Pour se connecter au serveur en SSH :
```bash
ssh -p 1455 amaury@164.132.43.252
```

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
