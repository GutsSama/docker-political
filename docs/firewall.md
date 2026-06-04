# Configuration du Pare-Feu (UFW)

Le projet utilise **UFW** (Uncomplicated Firewall) pour sécuriser le VPS en production.

## Politique Globale
Pour garantir une sécurité maximale (approche "Zero Trust" par défaut) :
- **Trafic entrant (Incoming)** : Refusé par défaut (`deny`)
- **Trafic sortant (Outgoing)** : Autorisé par défaut (`allow`)

## Ports Ouverts

Seuls les 3 ports strictement nécessaires au fonctionnement de l'application et à son administration sont ouverts vers l'extérieur :

| Port | Protocole | Service | Rôle |
|------|-----------|---------|------|
| **1455** | TCP | SSH | Port personnalisé pour l'accès administrateur et le déploiement CI/CD. |
| **80** | TCP | HTTP | Point d'entrée Traefik. Sert uniquement à rediriger vers HTTPS et à résoudre les défis ACME (Let's Encrypt). |
| **443** | TCP | HTTPS | Trafic sécurisé vers l'application (API FastAPI, Web Django, Dashboard Traefik). |

> [!WARNING]
> Les ports de l'application (ex: `8000` pour FastAPI, `8001` pour Django, `5432` pour PostgreSQL) ne sont **JAMAIS** exposés à travers UFW. Ils ne sont accessibles qu'en interne via le réseau Docker partagé avec Traefik.

## Commandes Utiles

Vérifier le statut du pare-feu et les règles actives :
```bash
sudo ufw status verbose
```

Ajouter une règle (exemple pour ouvrir le port 1455) :
```bash
sudo ufw allow 1455/tcp
```

Supprimer une règle existante :
```bash
# Lister les règles avec un numéro
sudo ufw status numbered
# Supprimer la règle numéro X
sudo ufw delete X
```
