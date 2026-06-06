/**
 * load.js — Test de charge (Load Test)
 *
 * Objectif : Simuler un trafic normal soutenu et valider les performances.
 * Charge    : montée progressive jusqu'à 100 VUs, maintenu 5 min, puis descente.
 *
 * Usage :
 *   k6 run k6/load.js
 *   BASE_URL=https://api.yourdomain.com k6 run k6/load.js
 *   k6 run --out json=k6/results/load_output.json k6/load.js
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

// Métriques personnalisées
const errorRate = new Rate('errors');
const successCounter = new Counter('successful_requests');
const apiTrend = new Trend('api_response_time', true);

// Configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  stages: [
    { duration: '1m', target: 20 },   // Rampe : 0 → 20 VUs en 1 min
    { duration: '2m', target: 100 },  // Montée : 20 → 100 VUs en 2 min
    { duration: '5m', target: 100 },  // Plateau : 100 VUs pendant 5 min
    { duration: '1m', target: 20 },   // Descente : 100 → 20 VUs en 1 min
    { duration: '30s', target: 0 },   // Arrêt progressif
  ],
  thresholds: {
    // Taux d'erreurs < 1%
    errors: ['rate<0.01'],
    // 95% des requêtes < 1 seconde
    http_req_duration: ['p(95)<1000'],
    // 99% des requêtes < 2 secondes
    'http_req_duration{p(99)}': ['p(99)<2000'],
    // Moins de 1% de failed checks
    checks: ['rate>0.99'],
  },
};

// Headers communs
const HEADERS = {
  'Content-Type': 'application/json',
  Accept: 'application/json',
};

// Scénarios
export default function () {
  group('Health & Disponibilité', () => {
    const res = http.get(`${BASE_URL}/health`, {
      headers: HEADERS,
      tags: { endpoint: 'health' },
    });
    const ok = check(res, {
      ' Health 200': (r) => r.status === 200,
      ' Health latence < 200ms': (r) => r.timings.duration < 200,
    });
    errorRate.add(!ok);
    if (ok) successCounter.add(1);
    apiTrend.add(res.timings.duration, { endpoint: 'health' });
  });

  sleep(0.3);

  group('API Predictions', () => {
    const res = http.get(`${BASE_URL}/api/v1/predictions`, {
      headers: HEADERS,
      tags: { endpoint: 'predictions' },
    });
    const ok = check(res, {
      ' Predictions réponse valide': (r) => [200, 401, 403, 404].includes(r.status),
      ' Predictions latence < 1s': (r) => r.timings.duration < 1000,
    });
    errorRate.add(!ok);
    if (ok) successCounter.add(1);
    apiTrend.add(res.timings.duration, { endpoint: 'predictions' });
  });

  sleep(0.5);

  group('API Root', () => {
    const res = http.get(`${BASE_URL}/`, {
      headers: HEADERS,
      tags: { endpoint: 'root' },
    });
    const ok = check(res, {
      ' Root 200': (r) => r.status === 200,
    });
    errorRate.add(!ok);
    apiTrend.add(res.timings.duration, { endpoint: 'root' });
  });

  // Pause réaliste entre les actions utilisateur
  sleep(Math.random() * 2 + 0.5); // 0.5s à 2.5s
}

export function handleSummary(data) {
  const metrics = data.metrics;
  const p95 = metrics.http_req_duration?.values['p(95)'] ?? 0;
  const p99 = metrics.http_req_duration?.values['p(99)'] ?? 0;
  const errRate = metrics.errors?.values.rate ?? 0;
  const reqCount = metrics.http_reqs?.values.count ?? 0;
  const rps = metrics.http_reqs?.values.rate ?? 0;

  console.log('\n════════════════════════════════════');
  console.log(' LOAD TEST — Résumé');
  console.log(`   Requêtes totales  : ${reqCount}`);
  console.log(`   Req/sec (avg)     : ${rps.toFixed(1)}`);
  console.log(`   Taux d'erreurs    : ${(errRate * 100).toFixed(2)}%`);
  console.log(`   Latence p95       : ${p95.toFixed(0)}ms`);
  console.log(`   Latence p99       : ${p99.toFixed(0)}ms`);
  console.log('════════════════════════════════════\n');

  return {
    'k6/results/load_summary.json': JSON.stringify(data, null, 2),
  };
}
