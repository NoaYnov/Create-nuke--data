# 📚 Documentation - Index

Bienvenue dans la documentation du projet **Create Nuclear Statistics Dashboard** !

---

## 🚀 Démarrage

### Pour les Nouveaux Utilisateurs

1. **[Guide de Démarrage Rapide](QUICKSTART.md)** ⭐
   - Installation en 5 minutes
   - Configuration minimale
   - Premiers pas

2. **[Guide de Déploiement](DEPLOYMENT.md)**
   - Installation complète
   - Configuration détaillée
   - Production et développement

---

## 📖 Guides Principaux

### [📘 Architecture](ARCHITECTURE.md)
Comprendre la structure du projet

- Structure des fichiers et dossiers
- Architecture technique (couches, services)
- Flux de données
- Schéma de base de données
- Bonnes pratiques
- Roadmap

**À lire si**: Vous voulez comprendre comment le projet fonctionne

---

### [🐘 Base de Données PostgreSQL](DATABASE.md)
Guide complet de la base de données

- Installation (locale et Docker)
- Configuration
- Initialisation automatique
- Maintenance et optimisation
- Sauvegarde et restauration
- Troubleshooting détaillé
- Déploiement en production

**À lire si**: Vous gérez la base de données ou rencontrez des problèmes

---

### [📋 Référence Rapide](REFERENCE.md)
Commandes et astuces au quotidien

- Commandes Docker essentielles
- Commandes PostgreSQL
- Scripts de maintenance
- Dépannage rapide
- Astuces et alias
- Support d'urgence

**À lire si**: Vous cherchez une commande spécifique

---

### [🚀 Déploiement](DEPLOYMENT.md)
Guide de déploiement complet

- Prérequis et vérification
- Installation rapide
- Configuration avancée
- Production vs Développement
- Maintenance
- Monitoring

**À lire si**: Vous déployez le projet pour la première fois

---

## 🔧 Ressources Techniques

### Scripts Utilitaires

Tous les scripts sont dans le dossier `scripts/`:

| Script | Description | Usage |
|--------|-------------|-------|
| `check_env.py` | Vérification environnement | `python scripts/check_env.py` |
| `init_db.py` | Initialisation base de données | `python scripts/init_db.py` |
| `backup.py` | Sauvegarde automatique | `python scripts/backup.py` |
| `restore.py` | Restauration interactive | `python scripts/restore.py` |
| `migrate.py` | Migrations de schéma | `python scripts/migrate.py status` |

### Configuration

| Fichier | Description |
|---------|-------------|
| `.env.example` | Template de configuration |
| `docker-compose.yml` | Configuration Docker standard |
| `docker-compose.prod.yml` | Configuration production |
| `config.py` | Configuration application Python |

### Scripts PostgreSQL

Dans `docker/postgres/init/`:

| Script | Description |
|--------|-------------|
| `01-init-database.sql` | Extensions et configuration |
| `02-create-tables.sql` | Création des tables |

---

## 📊 Diagrammes et Schémas

### Architecture Globale

```
┌─────────────────────────────────────────┐
│    Interface Utilisateur (Streamlit)    │
│         Ports 8501 / 8502               │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Couche Métier (Core)            │
│  - Collecteurs (Modrinth, CurseForge)   │
│  - Gestionnaires de modpacks            │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│    Couche d'Accès aux Données           │
│  - Database Manager (PostgreSQL)        │
│  - API Clients                          │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         PostgreSQL Database             │
│              Port 5432                  │
└─────────────────────────────────────────┘
```

### Services Docker

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  streamlit   │  │  streamlit   │  │    stats     │
│     app      │  │   onepage    │  │  collector   │
│   :8501      │  │   :8502      │  │              │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┴─────────────────┘
                         │
                         ↓
                  ┌──────────────┐
                  │  PostgreSQL  │
                  │    :5432     │
                  └──────────────┘
```

---

## 🎯 Cas d'Usage

### Je veux...

#### ...installer le projet rapidement
→ **[Guide de Démarrage Rapide](QUICKSTART.md)**

#### ...déployer en production
→ **[Guide de Déploiement](DEPLOYMENT.md)** + **[Base de Données](DATABASE.md)**

#### ...comprendre l'architecture
→ **[Architecture](ARCHITECTURE.md)**

#### ...résoudre un problème
→ **[Référence Rapide](REFERENCE.md)** (section Troubleshooting)

#### ...sauvegarder mes données
→ **[Base de Données](DATABASE.md)** (section Sauvegarde)

#### ...modifier le schéma de la base
→ **[Base de Données](DATABASE.md)** + utiliser `scripts/migrate.py`

#### ...optimiser les performances
→ **[Base de Données](DATABASE.md)** (section Optimisation)

#### ...contribuer au projet
→ **[Architecture](ARCHITECTURE.md)** + **README.md**

---

## 🔍 Index par Sujet

### Docker
- [Démarrage Rapide - Docker](QUICKSTART.md#3-démarrer-les-services)
- [Déploiement - Configuration Docker](DEPLOYMENT.md#démarrage)
- [Référence - Commandes Docker](REFERENCE.md#commandes-essentielles)

### PostgreSQL
- [Base de Données - Guide Complet](DATABASE.md)
- [Architecture - Schéma DB](ARCHITECTURE.md#schéma-de-base-de-données)
- [Référence - SQL Utiles](REFERENCE.md#base-de-données)

### Configuration
- [Démarrage Rapide - Configuration](QUICKSTART.md#2-configuration)
- [Déploiement - Variables d'Environnement](DEPLOYMENT.md#configuration)
- [Base de Données - Configuration](DATABASE.md#configuration)

### Maintenance
- [Base de Données - Maintenance](DATABASE.md#maintenance)
- [Référence - Nettoyage](REFERENCE.md#maintenance)
- [Déploiement - Mise à Jour](DEPLOYMENT.md#mise-à-jour)

### Troubleshooting
- [Base de Données - Troubleshooting](DATABASE.md#troubleshooting)
- [Référence - Dépannage](REFERENCE.md#dépannage)
- [Déploiement - Dépannage](DEPLOYMENT.md#dépannage)

---

## 📝 Changelog

Voir **[CHANGELOG.md](../CHANGELOG.md)** pour l'historique complet des modifications.

---

## 🆘 Besoin d'Aide ?

### Ordre de Consultation

1. **Vérifier les logs**: `docker-compose logs`
2. **Consulter la [Référence Rapide](REFERENCE.md)**
3. **Lire le guide approprié** (voir ci-dessus)
4. **Exécuter**: `python scripts/check_env.py`
5. **Créer une issue** sur GitHub avec les détails

### Ressources Externes

- [Documentation Docker](https://docs.docker.com/)
- [Documentation PostgreSQL](https://www.postgresql.org/docs/15/)
- [Documentation Streamlit](https://docs.streamlit.io/)
- [Documentation psycopg2](https://www.psycopg.org/docs/)

---

## 📄 Fichiers de Documentation

```
docs/
├── README.md              # Ce fichier (index)
├── QUICKSTART.md          # Démarrage rapide (5 min)
├── DEPLOYMENT.md          # Guide de déploiement
├── DATABASE.md            # Guide PostgreSQL complet
├── ARCHITECTURE.md        # Architecture du projet
└── REFERENCE.md           # Référence rapide
```

---

## 🎓 Parcours d'Apprentissage

### Niveau Débutant
1. [Guide de Démarrage Rapide](QUICKSTART.md)
2. [Guide de Déploiement](DEPLOYMENT.md) (sections de base)
3. [Référence Rapide](REFERENCE.md) (commandes essentielles)

### Niveau Intermédiaire
1. [Architecture](ARCHITECTURE.md)
2. [Base de Données](DATABASE.md) (installation et maintenance)
3. [Déploiement](DEPLOYMENT.md) (configuration avancée)

### Niveau Avancé
1. [Architecture](ARCHITECTURE.md) (flux de données, optimisations)
2. [Base de Données](DATABASE.md) (optimisation, production)
3. Scripts Python (`scripts/`)
4. Code source (`*.py`)

---

## 🔄 Mises à Jour

Cette documentation est maintenue activement. Dernière mise à jour: **2025-11-27**

Pour contribuer à la documentation:
1. Fork le projet
2. Modifier les fichiers Markdown
3. Soumettre une Pull Request

---

**Navigation**:
- [← Retour au README principal](../README.md)
- [Démarrage Rapide →](QUICKSTART.md)
- [Architecture →](ARCHITECTURE.md)
