# Brief Métier : Déployer une application IA conteneurisée sur un VPS sécurisé

## Description rapide
Une entreprise souhaite mettre à disposition une application Data/IA déjà développée, testée et dockerisée, afin de la démontrer et de faciliter ses futures mises à jour. Votre équipe doit reprendre ce projet existant et le déployer sur un VPS OVH neuf.
Vous devrez préparer et sécuriser le serveur à un niveau minimal, exécuter l’application avec Docker Compose, configure un reverse proxy Traefik avec protection des accès sensibles, publier des images versionnées dans une registry et automatiser la livraison d’une release avec GitHub Actions ou GitLab CI/CD.
L’objectif est de comprendre la démarche DevOps/MLOps nécessaire pour livrer une application IA de manière sécurisée, reproductible et traçable.

## Contexte
### Contexte professionnel
Vous êtes développeur·se en intelligence artificielle au sein d’une équipe chargée d’industrialiser une application Data/IA. L’application a déjà été réalisée lors d’un précédent projet : elle fonctionne en local, dispose de tests automatisés et peut être lancée avec Docker.
Votre responsable technique souhaite désormais disposer d’un environnement distant permettant de présenter l’application et de déployer ses nouvelles versions avec une méthode fiable. Un VPS OVH vierge est mis à disposition de votre groupe.

### Votre mission
À partir du projet existant, vous devez réaliser sa première mise en production pédagogique sur le VPS. Vous devrez :
1. Analyser l’application existante, ses services Docker, ses variables d’environnement et ses tests.
2. Prendre en main le VPS et préparer un environnement de déploiement exploitable.
3. Mettre en place les mesures de sécurité minimales demandées.
4. Déployer l’application avec Docker Compose.
5. Configurer Traefik comme reverse proxy afin de router les requêtes vers l’application.
6. Protéger les accès sensibles par authentification.
7. Publier les images Docker de l’application dans une registry.
8. Mettre en place une pipeline CI/CD permettant de tester, construire, publier puis déployer une release.
9. Vérifier le bon fonctionnement de la version déployée et diagnostiquer les éventuels incidents.
10. Documenter et présenter votre démarche.

## Contraintes obligatoires
### Sécurisation minimale du VPS
Vous devez mettre en place et documenter :
* La mise à jour initiale du système ;
* Un utilisateur dédié au déploiement, sans utilisation quotidienne directe de root ;
* Une connexion SSH par clé ;
* La désactivation de l’authentification SSH par mot de passe une fois l’accès par clé vérifié ;
* La modification du port SSH ( manipulation pédagogique de configuration sur le port `1455`) ;
* Un pare-feu n’autorisant que les ports strictement nécessaires (`80`, `443`, `1455`) ;
* Une protection contre les tentatives répétées de connexion, par exemple Fail2ban ;
* L’absence de secret dans le dépôt Git.

*Note : changer le port SSH ne constitue pas, à lui seul, une sécurisation du serveur. La sécurité repose principalement sur les clés SSH, la limitation des accès, le pare-feu et la protection des secrets.*

### Déploiement conteneurisé
Votre application doit être déployée avec Docker et Docker Compose. Vous devez reprendre l’existant et l’adapter uniquement pour le déploiement : variables d’environnement, images, réseau, volumes éventuels et configuration de production pédagogique.

### Reverse proxy
Vous devez mettre en place Traefik afin de donner accès à l’application sans exposer inutilement les conteneurs applicatifs. Tout dashboard ou accès d’administration exposé doit être protégé par authentification. Si un nom de domaine est fourni, l’accès HTTPS via certificat TLS devra être configuré.

### Livraison continue
La livraison doit s’appuyer sur GitHub Actions ou GitLab CI/CD et sur une registry d’images Docker. La pipeline devra au minimum :
* Lancer les tests automatisés existants ;
* Construire une image Docker versionnée ;
* Publier l’image dans la registry ;
* Permettre le déploiement de la release sur le VPS.

Vous devrez démontrer le déploiement d’une nouvelle version identifiable de l’application.

## Limites du projet
Vous ne devez pas développer de nouvelle fonctionnalité métier majeure. Le travail porte sur l’industrialisation, le déploiement, la sécurisation minimale, l’automatisation et la documentation.
Ce VPS est un environnement pédagogique. Il ne constitue pas une infrastructure de production complète : la haute disponibilité, la sauvegarde avancée, le dimensionnement, la supervision complète et les politiques de sécurité d’entreprise sont hors périmètre.

## Déroulement conseillé
* **J1 — VPS et sécurisation minimale** : Analyse locale, première connexion, mises à jour, utilisateur dédié, accès clé SSH, configuration port `1455`, pare-feu (UFW), Fail2ban et installation propre de Docker & Docker Compose.
* **J2 — Déploiement Docker et reverse proxy** : Docker Compose en local/distant, routage Traefik, BasicAuth et HTTPS (TLS).
* **J3 — Registry, CI/CD et release** : Pipelines (GitHub Actions), tests automatisés, builds d'images, push registry, pull sur VPS et déploiement continu.
* **J4 — Finalisation et restitution** : README final, schéma d'architecture complet, journal d'incidents, restitution et démo.
