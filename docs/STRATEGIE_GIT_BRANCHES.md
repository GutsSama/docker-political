# Stratégie Git – Branches à créer

## Branche de référence

```text
main
```

Contient uniquement les versions stables déployées en production.

---

## Branche d'intégration

```text
develop
```

Toutes les nouvelles fonctionnalités sont fusionnées dans cette branche avant d'être intégrées à `main`.

---

# Branches Feature

## Phase 1 – DevSecOps

### Gitleaks

```text
feature/gitleaks
```

### CodeQL

```text
feature/codeql-security
```

### Trivy

```text
feature/trivy-image-scan
```

---

## Phase 2 – Observabilité

### Node Exporter

```text
feature/node-exporter
```

### Prometheus

```text
feature/prometheus-monitoring
```

### Grafana

```text
feature/grafana-dashboard
```

### cAdvisor

```text
feature/cadvisor-monitoring
```

---

## Phase 3 – Supervision

### Uptime Kuma

```text
feature/uptime-kuma
```

---

## Phase 4 – Logs centralisés (optionnel)

### Loki

```text
feature/loki-logging
```

### Promtail

```text
feature/promtail-logging
```

---

# Ordre recommandé

1. feature/gitleaks
2. feature/codeql-security
3. feature/trivy-image-scan
4. feature/node-exporter
5. feature/prometheus-monitoring
6. feature/grafana-dashboard
7. feature/cadvisor-monitoring
8. feature/uptime-kuma
9. feature/loki-logging
10. feature/promtail-logging

---

# Workflow Git recommandé

```text
feature/*
      │
      ▼
develop
      │
Pull Request
      │
      ▼
main
      │
      ▼
Production VPS
```

---

# Nombre total de branches

## Version minimale

```text
feature/gitleaks
feature/codeql-security
feature/trivy-image-scan
feature/node-exporter
feature/prometheus-monitoring
feature/grafana-dashboard
feature/cadvisor-monitoring
feature/uptime-kuma
```

Total : **8 branches**

---

## Version complète

```text
feature/gitleaks
feature/codeql-security
feature/trivy-image-scan
feature/node-exporter
feature/prometheus-monitoring
feature/grafana-dashboard
feature/cadvisor-monitoring
feature/uptime-kuma
feature/loki-logging
feature/promtail-logging
```

Total : **10 branches**
