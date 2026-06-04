# Sécurisation SSH avec Fail2Ban

Pour protéger l'accès administrateur au VPS, nous utilisons **Fail2Ban**. Son rôle est de bannir automatiquement (au niveau du pare-feu) les adresses IP effectuant des tentatives de connexion SSH infructueuses répétées.

## Configuration "Journal-based" (Bonne pratique)

Sur les systèmes modernes (Ubuntu récents), nous n'utilisons plus la surveillance d'un port spécifique ou des logs textuels bruts (ex: `/var/log/auth.log`).
La configuration s'appuie directement sur le **journal systemd** pour surveiller le service SSH (`_SYSTEMD_UNIT=ssh.service`).

**Avantages :**
- Indépendant du numéro de port SSH utilisé (ici 1455).
- Plus rapide et moins sujet aux manipulations de logs.
- Supporte nativement les logs centralisés (systemd-journald).

## Paramètres de la "Jail" (Prison) `sshd`

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| **maxretry** | 5 | Nombre d'échecs avant bannissement. |
| **findtime** | 600s (10m) | Fenêtre de temps durant laquelle les échecs sont comptabilisés. |
| **bantime** | 3600s (1h) | Durée pendant laquelle l'adresse IP de l'attaquant est bloquée. |

## Commandes Utiles

Vérifier l'état global de Fail2Ban :
```bash
sudo fail2ban-client status
```

Voir les statistiques détaillées et les IP bannies pour SSH :
```bash
sudo fail2ban-client status sshd
```

Débannir une IP manuellement (si vous vous êtes bloqué vous-même) :
```bash
sudo fail2ban-client set sshd unbanip 192.168.1.50
```
