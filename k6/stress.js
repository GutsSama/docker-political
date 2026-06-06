/**
 * stress.js — Test de stress (Stress Test)
 *
 * Objectif : Identifier les limites du système par montée progressive jusqu'à 500 VUs.
 *            Observer le point de saturation CPU, latence et erreurs.
 *
 * Usage :
 *   k6 run k6/stress.js
 *   BASE_URL=https://api.yourdomain.com k6 run k6/stress.js
 *   k6 run --out json=k6/results/stress_output.json k6/stress.js
 *
 * ⚠️  NE PAS exécuter contre la production sans accord.
 *     Utiliser sur staging ou environnement de test dédié.
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// ─── Métriques personnalisées ──────────────────────────────────────────────
const errorRate = new Rate('errors');
const apiTrend = new Trend('api_response_time', true);
const saturatedRequests = new Counter('saturated_requests'); // req > 5s

// ─── Configuration ────────────────────────────────────────────────────────
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  stages: [
    // Phase 1 — Charge normale (baseline)
    { duration: '2m', target: 50 },

    // Phase 2 — Stress léger
    { duration: '3m', target: 100 },

    // Phase 3 — Stress modéré
    { duration: '3m', target: 200 },

    // Phase 4 — Stress élevé
    { duration: '3m', target: 300 },

    // Phase 5 — Stress maximum (point de rupture attendu)
    { duration: '3m', target: 500 },

    // Phase 6 — Récupération (vérification auto-heal)
    { duration: '2m', target: 100 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    // Accepter jusqu'à 10% d'erreurs en stress max
    errors: ['rate<0.10'],
    // p95 doit rester < 5s même en saturation
    http_req_duration: ['p(95)<5000'],
    // Pas de thresholds bloquants — on veut observer le comportement
  },
};

export default function () {
  // Endpoint principal — focus sur latence sous charge extrême
  const res = http.get(`${BASE_URL}/health`, {
    timeout: '10s',
    tags: {
      endpoint: 'health',
      vu_count: String(__VU),
    },
  });

  const ok = check(res, {
    '✅ Réponse reçue': (r) => r.status !== 0,
    '✅ Status 200': (r) => r.status === 200,
    '⚠️  Latence < 2s': (r) => r.timings.duration < 2000,
    '🔴 Saturation (> 5s)': (r) => r.timings.duration < 5000,
  });

  errorRate.add(res.status !== 200 && res.status !== 0);
  apiTrend.add(res.timings.duration);

  // Comptabiliser les requêtes saturées (latence > 5s)
  if (res.timings.duration >= 5000) {
    saturatedRequests.add(1);
  }

  // Pause minimale pour simuler des utilisateurs réels
  sleep(Math.random() * 1 + 0.2); // 0.2s à 1.2s
}

export function handleSummary(data) {
  const metrics = data.metrics;
  const p50 = metrics.http_req_duration?.values['p(50)'] ?? 0;
  const p90 = metrics.http_req_duration?.values['p(90)'] ?? 0;
  const p95 = metrics.http_req_duration?.values['p(95)'] ?? 0;
  const p99 = metrics.http_req_duration?.values['p(99)'] ?? 0;
  const maxDur = metrics.http_req_duration?.values.max ?? 0;
  const errRate = metrics.errors?.values.rate ?? 0;
  const reqCount = metrics.http_reqs?.values.count ?? 0;
  const rps = metrics.http_reqs?.values.rate ?? 0;
  const saturated = metrics.saturated_requests?.values.count ?? 0;

  console.log('\n════════════════════════════════════════════');
  console.log('💥 STRESS TEST — Rapport de saturation');
  console.log('────────────────────────────────────────────');
  console.log(`   Requêtes totales   : ${reqCount}`);
  console.log(`   Req/sec (peak)     : ${rps.toFixed(1)}`);
  console.log(`   Taux d'erreurs     : ${(errRate * 100).toFixed(2)}%`);
  console.log('────────────────────────────────────────────');
  console.log(`   Latence p50        : ${p50.toFixed(0)}ms`);
  console.log(`   Latence p90        : ${p90.toFixed(0)}ms`);
  console.log(`   Latence p95        : ${p95.toFixed(0)}ms`);
  console.log(`   Latence p99        : ${p99.toFixed(0)}ms`);
  console.log(`   Latence max        : ${maxDur.toFixed(0)}ms`);
  console.log('────────────────────────────────────────────');
  console.log(`   Requêtes saturées (>5s) : ${saturated}`);
  console.log('════════════════════════════════════════════\n');

  // Analyse automatique du point de saturation
  if (errRate > 0.05) {
    console.log('⚠️  ALERTE : Taux d\'erreurs > 5% — Le système a atteint sa limite.');
  }
  if (p95 > 3000) {
    console.log('⚠️  ALERTE : p95 > 3s — Dégradation significative des performances.');
  }
  if (errRate < 0.01 && p95 < 1000) {
    console.log('✅ Système stable même sous stress maximum (500 VUs).');
  }

  return {
    'k6/results/stress_summary.json': JSON.stringify(data, null, 2),
  };
}
