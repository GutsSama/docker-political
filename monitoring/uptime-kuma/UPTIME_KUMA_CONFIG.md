# Configuration Uptime Kuma — Checks & Alertes

Ce fichier documente la configuration manuelle à effectuer dans Uptime Kuma
(interface web : `https://kuma.<DOMAIN_NAME>`) pour les checks définis dans le plan.

> ⚠️ Uptime Kuma ne supporte pas encore le provisionnement par fichier.
> La configuration se fait via l'interface web ou via l'API REST (décrite ci-dessous).

---

## Checks à configurer

### 1. Frontend Django

| Paramètre     | Valeur                                       |
|---------------|----------------------------------------------|
| Type          | HTTP(s)                                      |
| URL           | `https://<DOMAIN_NAME>/home/`                |
| Nom           | `Frontend Django`                            |
| Intervalle    | 60s                                          |
| Timeout       | 10s                                          |
| Code HTTP OK  | 200, 301, 302                                |
| Notification  | Discord + Email                              |

---

### 2. Backend API FastAPI

| Paramètre     | Valeur                              |
|---------------|-------------------------------------|
| Type          | HTTP(s)                             |
| URL           | `https://api.<DOMAIN_NAME>/health`  |
| Nom           | `API FastAPI`                       |
| Intervalle    | 60s                                 |
| Timeout       | 10s                                 |
| Code HTTP OK  | 200                                 |
| Notification  | Discord + Email                     |

---

### 3. Traefik

| Paramètre     | Valeur                                          |
|---------------|-------------------------------------------------|
| Type          | HTTP(s)                                         |
| URL           | `https://traefik.<DOMAIN_NAME>/api/rawdata`     |
| Nom           | `Traefik Dashboard`                             |
| Intervalle    | 60s                                             |
| Timeout       | 10s                                             |
| Code HTTP OK  | 200                                             |
| Auth          | Basic Auth (même credentials que Traefik)       |
| Notification  | Discord                                         |

---

### 4. Grafana

| Paramètre     | Valeur                                          |
|---------------|-------------------------------------------------|
| Type          | HTTP(s)                                         |
| URL           | `https://grafana.<DOMAIN_NAME>/api/health`      |
| Nom           | `Grafana`                                       |
| Intervalle    | 60s                                             |
| Timeout       | 10s                                             |
| Code HTTP OK  | 200                                             |
| Notification  | Discord                                         |

---

### 5. PostgreSQL (optionnel — TCP)

| Paramètre     | Valeur                       |
|---------------|------------------------------|
| Type          | TCP Port                     |
| Host          | `db` (container name)        |
| Port          | `5432`                       |
| Nom           | `PostgreSQL DB`              |
| Intervalle    | 60s                          |
| Notification  | Discord + Email              |

---

## Configuration des notifications

### Canal Discord

1. Dans Uptime Kuma → **Settings** → **Notifications** → **Add**
2. Type : **Discord**
3. Webhook URL : `$DISCORD_WEBHOOK_URL` (depuis les secrets GitHub/VPS)
4. Cocher : **Notify on recover**

### Canal Email SMTP

1. Type : **Email (SMTP)**
2. SMTP Host : `smtp.gmail.com`
3. Port : `587`
4. TLS : STARTTLS
5. Username / Password : variables d'environnement

---

## Configuration via API REST Uptime Kuma (automatisation)

Uptime Kuma expose une API Socket.IO. Exemple avec `uptime-kuma-api` (Python) :

```bash
pip install uptime-kuma-api
```

```python
from uptime_kuma_api import UptimeKumaApi

api = UptimeKumaApi("https://kuma.yourdomain.com")
api.login("admin", "YOUR_PASSWORD")

api.add_monitor(
    type="http",
    name="Frontend Django",
    url="https://yourdomain.com/home/",
    interval=60,
)

api.disconnect()
```

---

## Résultat attendu

- ✅ 5 checks actifs (Frontend, API, Traefik, Grafana, DB)
- ✅ Notification Discord en < 1 minute après incident
- ✅ Notification Email pour les incidents critiques (API, DB)
- ✅ Page de statut publique activée
