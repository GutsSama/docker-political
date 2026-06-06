# Tests de charge k6 — Prédi'lection API

## Présentation

Ce dossier contient les scénarios de tests de charge [k6](https://k6.io) pour valider
les performances de l'API FastAPI sous différents niveaux de trafic.

---

## Scénarios disponibles

| Fichier | Type | VUs max | Durée | Objectif |
|---------|------|---------|-------|----------|
| `smoke.js` | Smoke Test | 1 | 30s | Vérifier que l'API fonctionne |
| `load.js` | Load Test | 100 | ~10min | Valider les performances en charge normale |
| `stress.js` | Stress Test | 500 | ~17min | Identifier le point de saturation |

---

## Prérequis

### Installation k6 (macOS)

```bash
brew install k6
```

### Installation k6 (Linux / VPS)

```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
    --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] \
    https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update && sudo apt-get install k6
```

---

## Utilisation

### Variable d'environnement

```bash
export BASE_URL=https://api.yourdomain.com
```

> Par défaut : `http://localhost:8000`

---

### Smoke Test (vérification rapide)

```bash
k6 run k6/smoke.js
```

**Thresholds :**
- Taux d'erreurs < 1%
- p95 latence < 500ms

---

### Load Test (charge normale)

```bash
# Lancer le test
k6 run k6/load.js

# Avec sortie JSON pour analyse
k6 run --out json=k6/results/load_output.json k6/load.js
```

**Profil de charge :**
```
VUs
100 ┤              ████████████████
 20 ┤        █████                  ████
  0 ┤  ──────                            ──────
    0   1m   3m                  8m   9m  9m30s
```

**Thresholds :**
- Taux d'erreurs < 1%
- p95 < 1s, p99 < 2s
- Checks > 99%

---

### Stress Test (limite du système)

> ⚠️ **Ne pas lancer en production.** Utiliser sur staging uniquement.

```bash
k6 run k6/stress.js
```

**Profil de charge :**
```
VUs
500 ┤                          ████████
300 ┤                   ███████
200 ┤             ███████
100 ┤       ███████                      █████
 50 ┤ ██████                                   ──────
  0 ┤                                                 ──
    0  2m   5m   8m   11m  14m  17m             18m  19m
```

**Thresholds :**
- Taux d'erreurs < 10% (stress mode — tolérant)
- p95 < 5s

---

## Résultats

Les rapports JSON sont sauvegardés dans `k6/results/` (ignoré par git).

```
k6/results/
├── smoke_summary.json
├── load_summary.json
└── stress_summary.json
```

### Interpréter les résultats

| Métrique | Bon | Acceptable | Critique |
|----------|-----|------------|---------|
| p95 latence | < 500ms | < 1s | > 2s |
| Taux d'erreurs | < 0.1% | < 1% | > 5% |
| Req/sec | > 100 | > 50 | < 10 |

---

## Intégration CI/CD

Pour exécuter le smoke test après chaque déploiement, ajouter dans `deploy.yml` :

```yaml
- name: Smoke test k6
  run: |
    k6 run --env BASE_URL=https://${{ secrets.DOMAIN_NAME }} k6/smoke.js
```

---

## Métriques Grafana

Après un test de charge, observer dans Grafana :
- **CPU usage** — doit rester < 80%
- **RAM usage** — doit rester < 85%
- **http_requests_total** — montée en charge visible
- **http_request_duration_seconds** — dégradation progressive sous stress
