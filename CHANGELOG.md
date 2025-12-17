# 📝 Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

---

## [2.0.0] - 2025-11-27

### 🎉 Refactorisation Majeure

Cette version représente une refactorisation complète de l'architecture du projet avec un focus sur la production-readiness et la maintenabilité.

### ✨ Ajouté

#### Infrastructure
- **Docker Compose amélioré** avec healthchecks pour tous les services
- **PostgreSQL 15** avec Alpine Linux pour une image légère
- **Scripts d'initialisation automatique** pour PostgreSQL
- **Configuration production** séparée (`docker-compose.prod.yml`)
- **Réseau Docker dédié** pour l'isolation des services
- **Limites de ressources** configurables pour chaque service

#### Base de Données
- **Scripts d'initialisation SQL** dans `docker/postgres/init/`:
  - `01-init-database.sql`: Extensions et configuration
  - `02-create-tables.sql`: Création des tables avec contraintes
- **Triggers automatiques** pour `updated_at`
- **Index optimisés** pour les performances
- **Contraintes d'intégrité** (CHECK, UNIQUE)
- **Commentaires SQL** pour la documentation
- **Système de migration** avec versioning

#### Scripts Utilitaires
- **`scripts/init_db.py`**: Initialisation et vérification de la base
- **`scripts/backup.py`**: Sauvegarde automatique avec compression
- **`scripts/restore.py`**: Restauration interactive
- **`scripts/migrate.py`**: Système de migration de schéma
- **`scripts/check_env.py`**: Vérification de l'environnement

#### Documentation
- **`docs/ARCHITECTURE.md`**: Architecture détaillée du projet
- **`docs/DATABASE.md`**: Guide complet PostgreSQL (déploiement, maintenance)
- **`docs/QUICKSTART.md`**: Guide de démarrage en 5 minutes
- **`docs/REFERENCE.md`**: Référence rapide des commandes
- **README.md amélioré** avec badges et structure professionnelle
- **`.env.example`**: Template de configuration complet

#### Configuration
- **Variables d'environnement** centralisées
- **Configuration PostgreSQL** optimisée pour production
- **Logging configuré** avec rotation
- **Healthchecks** pour tous les services

### 🔄 Modifié

#### Docker
- **Dockerfile multi-stage** pour optimiser la taille
- **Utilisateur non-root** pour la sécurité
- **Healthcheck Streamlit** intégré
- **Volumes nommés** pour meilleure gestion

#### Base de Données
- **Colonne `updated_at`** ajoutée à toutes les tables
- **Contraintes CHECK** pour validation des données
- **Index supplémentaires** pour les requêtes fréquentes
- **Timezone UTC** forcée

#### Configuration
- **`.gitignore` amélioré** avec exception pour scripts SQL
- **Port PostgreSQL** non exposé en production
- **Restart policy** configuré pour tous les services

### 🛠️ Améliorations

#### Performance
- **Configuration PostgreSQL** optimisée (shared_buffers, work_mem, etc.)
- **Connection pooling** préparé
- **Index sur colonnes fréquemment requêtées**
- **VACUUM et ANALYZE** automatiques

#### Sécurité
- **Mots de passe** via variables d'environnement
- **Utilisateur non-root** dans les conteneurs
- **Volumes read-only** pour les scripts d'init
- **Isolation réseau** entre services

#### Maintenabilité
- **Code modulaire** et bien documenté
- **Scripts Python** avec gestion d'erreurs
- **Logging structuré** avec niveaux
- **Documentation complète** en français

### 📚 Documentation

#### Guides Créés
1. **QUICKSTART.md**: Installation en 5 minutes
2. **DATABASE.md**: 
   - Installation locale et Docker
   - Configuration détaillée
   - Maintenance et optimisation
   - Sauvegarde/restauration
   - Troubleshooting complet
3. **ARCHITECTURE.md**:
   - Structure du projet
   - Flux de données
   - Schéma de base de données
   - Bonnes pratiques
4. **REFERENCE.md**:
   - Commandes essentielles
   - SQL utiles
   - Astuces et alias
   - Support d'urgence

### 🔧 Outils

#### Scripts de Maintenance
- **Sauvegarde automatique** avec compression gzip
- **Rotation des sauvegardes** (garde les 7 dernières)
- **Restauration interactive** avec sélection
- **Vérification d'environnement** complète
- **Migrations de schéma** avec rollback

### 🐛 Corrections

- **Gestion des transactions** améliorée avec rollback
- **Encodage UTF-8** forcé pour PostgreSQL
- **Timezone UTC** pour cohérence
- **Gestion d'erreurs** robuste dans tous les scripts

### 🔐 Sécurité

- **Secrets** non versionnés (.env dans .gitignore)
- **Validation des entrées** avec contraintes SQL
- **Permissions PostgreSQL** restreintes
- **Healthchecks** pour détecter les problèmes

---

## [1.0.0] - 2025-11-XX

### Initial Release

#### Fonctionnalités
- Dashboard Streamlit pour statistiques Create Nuclear
- Collecte de données Modrinth et CurseForge
- Base de données PostgreSQL
- Docker Compose basique
- Scraping de modpacks CurseForge

---

## Types de Changements

- **✨ Ajouté** : Nouvelles fonctionnalités
- **🔄 Modifié** : Changements dans les fonctionnalités existantes
- **🗑️ Déprécié** : Fonctionnalités bientôt supprimées
- **🔥 Supprimé** : Fonctionnalités supprimées
- **🐛 Corrigé** : Corrections de bugs
- **🔐 Sécurité** : Corrections de vulnérabilités
- **🛠️ Améliorations** : Améliorations de performance ou qualité

---

## Roadmap

### Version 2.1.0 (Court terme)
- [ ] Tests unitaires complets
- [ ] CI/CD avec GitHub Actions
- [ ] Monitoring avec Prometheus
- [ ] Alertes email sur erreurs
- [ ] Documentation API

### Version 2.2.0 (Moyen terme)
- [ ] API REST publique
- [ ] Authentification utilisateurs
- [ ] Export automatique S3
- [ ] Rapports PDF
- [ ] Dashboard admin

### Version 3.0.0 (Long terme)
- [ ] Machine Learning pour prédictions
- [ ] WebSockets temps réel
- [ ] Multi-tenancy
- [ ] Clustering PostgreSQL
- [ ] Kubernetes deployment

---

**Légende des versions**:
- **MAJOR**: Changements incompatibles avec l'API
- **MINOR**: Nouvelles fonctionnalités rétrocompatibles
- **PATCH**: Corrections de bugs rétrocompatibles
