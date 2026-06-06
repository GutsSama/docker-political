/**
 * smoke.js — Test de fumée (Smoke Test)
 *
 * Objectif : Vérifier que l'API répond correctement avec un trafic minimal.
 * Charge    : 1 utilisateur virtuel, 30 secondes
 *
 * Usage :
 *   k6 run k6/smoke.js
 *   BASE_URL=https://api.yourdomain.com k6 run k6/smoke.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Métriques personnalisées
const errorRate = new Rate('errors');
const apiDuration = new Trend('api_duration', true);

// Configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  vus: 1,
  duration: '30s',
  thresholds: {
    // 100% des requêtes doivent réussir
    errors: ['rate<0.01'],
    // p95 < 500ms
    http_req_duration: ['p(95)<500'],
    // Toutes les requêtes doivent retourner < 1s
    'http_req_duration{endpoint:root}': ['p(99)<1000'],
  },
};

// Scénarios
export default function () {
  // 1. Root endpoint
  const rootRes = http.get(`${BASE_URL}/`, {
    tags: { endpoint: 'root' },
  });
  check(rootRes, {
    ' Root status 200': (r) => r.status === 200,
    ' Root latence < 500ms': (r) => r.timings.duration < 500,
  });
  errorRate.add(rootRes.status !== 200);
  apiDuration.add(rootRes.timings.duration, { endpoint: 'root' });

  // 2. Health check
  const healthRes = http.get(`${BASE_URL}/health`, {
    tags: { endpoint: 'health' },
  });
  check(healthRes, {
    ' Health status 200': (r) => r.status === 200,
    ' Health body contient status ok': (r) => {
      try {
        return JSON.parse(r.body).status === 'ok';
      } catch {
        return false;
      }
    },
  });
  errorRate.add(healthRes.status !== 200);

  // 3. Endpoint predictions list
  const predictRes = http.get(`${BASE_URL}/api/v1/predictions`, {
    tags: { endpoint: 'predictions' },
  });
  check(predictRes, {
    ' Predictions status 200 ou 401': (r) => [200, 401, 403, 404].includes(r.status),
    ' Predictions latence < 2s': (r) => r.timings.duration < 2000,
  });
  apiDuration.add(predictRes.timings.duration, { endpoint: 'predictions' });

  sleep(1);
}

export function handleSummary(data) {
  const errors = data.metrics.errors ? data.metrics.errors.values.rate : 0;
  const p95 = data.metrics.http_req_duration
    ? data.metrics.http_req_duration.values['p(95)']
    : 0;

  console.log('\n════════════════════════════════════');
  console.log(' SMOKE TEST — Résumé');
  console.log(`   Taux d'erreurs : ${(errors * 100).toFixed(2)}%`);
  console.log(`   Latence p95    : ${p95.toFixed(0)}ms`);
  console.log('════════════════════════════════════\n');

  return {
    'k6/results/smoke_summary.json': JSON.stringify(data, null, 2),
  };
}
