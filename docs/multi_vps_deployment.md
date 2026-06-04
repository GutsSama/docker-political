# Stratégie de Déploiement en Équipe (Multi-VPS)

Ce document explique comment le projet gère le déploiement continu (CI/CD) pour une équipe de développeurs disposant chacun de son propre VPS, tout en travaillant sur un seul et unique dépôt GitHub.

## Le Problème Initial
Dans une configuration CI/CD classique, un tag Git (ex: `v1.0.0`) déclenche un déploiement vers un serveur cible unique défini par les secrets du dépôt (`VPS_HOST`, `VPS_USER`, etc.).
Pour une équipe de 3 développeurs avec 3 VPS différents, cette approche est **dangereuse** : un tag poussé par le développeur A pourrait écraser le serveur du développeur B.

## Notre Solution : Les GitHub Environments
Pour résoudre ce problème, nous utilisons les **GitHub Environments**. Cela permet d'isoler les secrets (`VPS_HOST`, `VPS_SSH_KEY`, etc.) par environnement cible, et d'utiliser un seul pipeline `deploy.yml`.

### Les 3 Environnements
Dans les paramètres du dépôt GitHub (`Settings` > `Environments`), 3 environnements distincts doivent être créés :
1. **`dev`** : Environnement de développement.
2. **`staging`** : Environnement de pré-production/test.
3. **`prod`** : Environnement de production finale.

Pour chacun d'entre eux, les secrets suivants doivent être configurés :
- `VPS_HOST`
- `VPS_USER`
- `VPS_SSH_KEY`
- `DOMAIN_NAME`

*(Chaque développeur peut ainsi s'attribuer un environnement et y renseigner les informations de **son** propre VPS).*

### Routage Automatique
Le pipeline CI/CD (`.github/workflows/deploy.yml`) route dynamiquement le déploiement vers le bon environnement (et donc le bon VPS) en fonction de l'action Git effectuée :

- Push sur la branche **`develop`** ➔ Déploie sur le VPS de l'environnement **`dev`**
- Push sur la branche **`main`** ➔ Déploie sur le VPS de l'environnement **`staging`**
- Poussée d'un Tag **`v*.*.*`** ➔ Déploie sur le VPS de l'environnement **`prod`**

## Conventions de Nommage Docker
Les images Docker poussées sur le GitHub Container Registry (GHCR) sont taguées intelligemment par le pipeline :
- Si c'est un Tag Git (`v1.0.0`), l'image est taguée `v1.0.0`.
- Si c'est une branche (`develop`), l'image est taguée avec le nom de la branche et le SHA court du commit (ex: `develop-a1b2c3d`).

Cela permet de toujours identifier exactement quelle version du code tourne sur quel environnement.
