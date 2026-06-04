# Diagnostic Technique et Résolutions — Projet Docker Political

Ce document résume le diagnostic technique de l'application, les problèmes identifiés en termes de sécurité, de dette technique et de duplication, ainsi que les étapes de résolution implémentées.

---

## 1. Diagnostic des Problèmes Identifiés

### 🔐 Sécurité & Stabilité
1. **Problème de Typage FastAPI (Bug / Sécurité) :** Dans `api/app/endpoints/communes_endpoints.py`, l'endpoint `/commune` retournait directement un entier (`status.HTTP_400_BAD_REQUEST`) en cas de paramètres manquants au lieu de lever une exception, provoquant un plantage Pydantic (erreur 500) à la place d'une réponse propre.
2. **Absence de CORS dans FastAPI (Sécurité) :** Bien qu'une liste d'origines de confiance soit présente, le middleware `CORSMiddleware` n'était pas configuré sur l'instance FastAPI, bloquant ou ouvrant à tort les requêtes cross-origin.
3. **Clé Secrète de Secours Infiltrée (Sécurité) :** Django disposait d'une clé secrète de secours codée en dur (`django-insecure-default-key-for-build`) utilisable silencieusement si la variable d'environnement venait à manquer en production.

### 🏗️ Dette Technique & Bugs fonctionnels
1. **Mode `light` Cassé dans `CommuneService` :** Dans `api/app/services/communes.py`, la requête optimisée en mode léger (`light=True`) de `get_by_department` était intégralement écrasée quelques lignes plus bas par une sélection générique (`select(Communes)`), consommant inutilement du réseau et de la mémoire.
2. **Duplication de route dans l'API :** Dans `api/app/routers/api.py`, le routeur `prediction_router` était importé et inclus deux fois.

### 👥 Duplications de code
1. **Assignation redondante dans `predict.py` :** L'instruction `city_name = result[0].city if result else "Commune inconnue"` était répétée consécutivement aux lignes 38 et 42.
2. **Double déclaration dans `settings.py` :** La variable `STATIC_ROOT` était définie à deux reprises à la fin de la configuration Django.

---

## 2. Étapes de Résolution

Toutes les résolutions ont été appliquées pour assainir durablement l'architecture :

### 🎯 Phase 1 : Sécurité
* **Exceptions explicites :** Ajout de la levée d'exceptions FastAPI propre dans les endpoints.
* **CORS activé :** Enregistrement de `CORSMiddleware` avec les origines de confiance définies.
* **Clé secrète renforcée :** Conditionnement de la clé par défaut uniquement lorsque `DEBUG = True`, sinon levée d'erreur.

### 🎯 Phase 2 : Structure & Performance
* **Nettoyage des routeurs :** Retrait des inclusions doublées de `prediction_router`.
* **Correction du mode léger (`light`) :** Restauration de la sélection de colonnes restreinte dans `get_by_department`.
* **Retrait des duplications :** Nettoyage des affectations en double de `city_name` et de `STATIC_ROOT`.

### 🎯 Phase 3 : Tests
* **Tests unitaires et de fumée :** Intégration de tests robustes validant les scénarios de réussite et d'échec de l'API.
