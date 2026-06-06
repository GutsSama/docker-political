#!/usr/bin/env python3
"""
Script d'automatisation Uptime Kuma via API.
Crée les 5 monitors définis dans le plan alerting.

Usage :
    KUMA_URL=https://kuma.yourdomain.com \
    KUMA_USER=admin \
    KUMA_PASSWORD=yourpassword \
    python3 scripts/setup_uptime_kuma.py
"""

import os
import sys

try:
    from uptime_kuma_api import UptimeKumaApi, MonitorType
except ImportError:
    print("❌ Installer le package : pip install uptime-kuma-api")
    sys.exit(1)

KUMA_URL = os.environ.get("KUMA_URL", "")
KUMA_USER = os.environ.get("KUMA_USER", "admin")
KUMA_PASSWORD = os.environ.get("KUMA_PASSWORD", "")
DOMAIN = os.environ.get("DOMAIN_NAME", "yourdomain.com")

if not KUMA_URL or not KUMA_PASSWORD:
    print("❌ Variables KUMA_URL et KUMA_PASSWORD requises.")
    sys.exit(1)

MONITORS = [
    {
        "type": MonitorType.HTTP,
        "name": "Frontend Django",
        "url": f"https://{DOMAIN}/home/",
        "interval": 60,
        "retryInterval": 60,
        "maxretries": 3,
        "accepted_statuscodes": ["200-299", "301", "302"],
    },
    {
        "type": MonitorType.HTTP,
        "name": "API FastAPI",
        "url": f"https://api.{DOMAIN}/health",
        "interval": 60,
        "retryInterval": 60,
        "maxretries": 3,
        "accepted_statuscodes": ["200-299"],
    },
    {
        "type": MonitorType.HTTP,
        "name": "Traefik Dashboard",
        "url": f"https://traefik.{DOMAIN}/api/rawdata",
        "interval": 60,
        "retryInterval": 60,
        "maxretries": 3,
        "accepted_statuscodes": ["200-299"],
    },
    {
        "type": MonitorType.HTTP,
        "name": "Grafana",
        "url": f"https://grafana.{DOMAIN}/api/health",
        "interval": 60,
        "retryInterval": 60,
        "maxretries": 3,
        "accepted_statuscodes": ["200-299"],
    },
    {
        "type": MonitorType.TCP,
        "name": "PostgreSQL DB",
        "hostname": "db",
        "port": 5432,
        "interval": 60,
        "retryInterval": 60,
        "maxretries": 3,
    },
]


def main() -> None:
    print(f"🔗 Connexion à Uptime Kuma : {KUMA_URL}")
    api = UptimeKumaApi(KUMA_URL)

    try:
        api.login(KUMA_USER, KUMA_PASSWORD)
        print("✅ Connecté")

        for monitor in MONITORS:
            name = monitor["name"]
            try:
                result = api.add_monitor(**monitor)
                print(f"✅ Monitor créé : {name} (id={result.get('monitorID')})")
            except Exception as exc:
                print(f"⚠️  Erreur pour '{name}': {exc}")

    finally:
        api.disconnect()
        print("🔌 Déconnecté")


if __name__ == "__main__":
    main()
