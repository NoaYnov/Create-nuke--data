# Architecture du Projet Create Nuclear Stats

## 📁 Structure du Projet

```
Create-nuke--data/
├── .devcontainer/          # Configuration VS Code Dev Container
├── .streamlit/             # Configuration Streamlit
├── assets/                 # Images et ressources statiques
├── data/                   # Données CSV/JSON (gitignored)
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md     # Ce fichier
│   ├── DEPLOYMENT.md       # Guide de déploiement
│   └── DATABASE.md         # Documentation base de données
├── docker/                 # Configurations Docker
│   ├── postgres/           # Configuration PostgreSQL
│   │   ├── init/           # Scripts d'initialisation
│   │   └── Dockerfile      # Image PostgreSQL personnalisée
│   └── app/                # Configuration application
│       └── Dockerfile      # Image application
├── src/                    # Code source principal
│   ├── core/               # Logique métier
│   │   ├── __init__.py
│   │   ├── database.py     # Gestion base de données
│   │   ├── api_clients.py  # Clients API
│   │   ├── scraper.py      # Web scraping
│   │   └── modpack_manager.py
│   ├── collectors/         # Collecteurs de données
│   │   ├── __init__.py
│   │   ├── base.py         # Classe de base
│   │   ├── modrinth.py     # Collecteur Modrinth
│   │   ├── curseforge.py   # Collecteur CurseForge
│   │   └── scheduler.py    # Planification
│   ├── ui/                 # Interfaces utilisateur
│   │   ├── __init__.py
│   │   ├── components/     # Composants réutilisables
│   │   ├── pages/          # Pages Streamlit
│   │   └── utils.py        # Utilitaires UI
│   ├── config/             # Configuration
│   │   ├── __init__.py
│   │   ├── settings.py     # Paramètres globaux
│   │   └── constants.py    # Constantes
│   └── utils/              # Utilitaires généraux
│       ├── __init__.py
│       ├── logger.py       # Logging
│       └── helpers.py      # Fonctions helpers
├── scripts/                # Scripts utilitaires
│   ├── init_db.py          # Initialisation DB
│   ├── migrate.py          # Migrations
│   └── backup.py           # Sauvegarde
├── tests/                  # Tests unitaires
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_collectors.py
│   └── test_api_clients.py
├── .env.example            # Exemple de configuration
├── .gitignore
├── docker-compose.yml      # Orchestration Docker
├── docker-compose.prod.yml # Production
├── requirements.txt        # Dépendances Python
├── setup.py                # Installation package
└── README.md
```

## 🏗️ Architecture Technique

### Couches de l'Application

```
┌─────────────────────────────────────────┐
│         Interface Utilisateur           │
│    (Streamlit Apps - Port 8501/8502)    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Couche Métier (Core)            │
│  - Collecteurs de données               │
│  - Gestionnaires de modpacks            │
│  - Logique de traitement                │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Couche d'Accès aux Données         │
│  - Database Manager (PostgreSQL)        │
│  - API Clients (Modrinth, CurseForge)   │
│  - Web Scraper                          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Sources de Données              │
│  - PostgreSQL (Port 5432)               │
│  - API Modrinth                         │
│  - API CurseForge                       │
│  - Web Scraping CurseForge              │
└─────────────────────────────────────────┘
```

### Services Docker

1. **postgres** - Base de données PostgreSQL 15
   - Port: 5432
   - Volume persistant: `pgdata`
   - Healthcheck actif
   - Scripts d'initialisation automatiques

2. **streamlit-app** - Application principale
   - Port: 8501
   - Dépend de: postgres
   - Auto-restart

3. **streamlit-onepage** - Vue simplifiée
   - Port: 8502
   - Dépend de: postgres
   - Auto-restart

4. **stats-collector** - Collecteur de statistiques
   - Pas de port exposé
   - Dépend de: postgres
   - Exécution planifiée

## 🔄 Flux de Données

### Collecte de Statistiques

```
┌──────────────┐
│  Scheduler   │ (Toutes les 6h)
└──────┬───────┘
       │
       ↓
┌──────────────────────────────────────┐
│     Stats Collector Daemon           │
├──────────────────────────────────────┤
│  1. Modrinth Collector               │
│     - Récupère stats globales        │
│     - Récupère stats par version     │
│  2. CurseForge Collector             │
│     - Récupère stats API             │
│     - Récupère stats par fichier     │
│  3. Modpack Collector                │
│     - Scrape nouveaux modpacks       │
│     - Enrichit via API               │
└──────┬───────────────────────────────┘
       │
       ↓
┌──────────────────────────────────────┐
│         PostgreSQL Database          │
├──────────────────────────────────────┤
│  Tables:                             │
│  - daily_stats                       │
│  - version_stats                     │
│  - modpack_stats                     │
└──────┬───────────────────────────────┘
       │
       ↓
┌──────────────────────────────────────┐
│      Streamlit Applications          │
│  - Visualisation temps réel          │
│  - Graphiques interactifs            │
│  - Export de données                 │
└──────────────────────────────────────┘
```

## 🗄️ Schéma de Base de Données

### Table: daily_stats
Stocke les statistiques quotidiennes globales par plateforme.

| Colonne          | Type      | Description                    |
|------------------|-----------|--------------------------------|
| id               | SERIAL    | Clé primaire                   |
| date             | DATE      | Date de collecte               |
| platform         | VARCHAR   | modrinth / curseforge          |
| total_downloads  | INTEGER   | Total téléchargements          |
| followers        | INTEGER   | Nombre de followers            |
| versions_count   | INTEGER   | Nombre de versions             |
| created_at       | TIMESTAMP | Date de création               |

**Index**: `idx_daily_stats_date` sur (date DESC)
**Contrainte**: UNIQUE(date, platform)

### Table: version_stats
Stocke les statistiques par version du mod.

| Colonne          | Type      | Description                    |
|------------------|-----------|--------------------------------|
| id               | SERIAL    | Clé primaire                   |
| date             | DATE      | Date de collecte               |
| platform         | VARCHAR   | modrinth / curseforge          |
| version_name     | VARCHAR   | Nom de la version              |
| version_number   | VARCHAR   | Numéro de version              |
| downloads        | INTEGER   | Téléchargements                |
| date_published   | TIMESTAMP | Date de publication            |
| created_at       | TIMESTAMP | Date de création               |

**Index**: `idx_version_stats_date` sur (date DESC, platform)
**Contrainte**: UNIQUE(date, platform, version_name)

### Table: modpack_stats
Stocke les statistiques des modpacks utilisant le mod.

| Colonne          | Type      | Description                    |
|------------------|-----------|--------------------------------|
| id               | SERIAL    | Clé primaire                   |
| date             | DATE      | Date de collecte               |
| platform         | VARCHAR   | curseforge                     |
| modpack_name     | VARCHAR   | Nom du modpack                 |
| modpack_slug     | VARCHAR   | Slug unique                    |
| downloads        | INTEGER   | Téléchargements                |
| followers        | INTEGER   | Nombre de followers            |
| created_at       | TIMESTAMP | Date de création               |

**Index**: `idx_modpack_stats_date` sur (date DESC, platform)
**Contrainte**: UNIQUE(date, platform, modpack_slug)

## 🔐 Sécurité

### Variables d'Environnement

Les informations sensibles sont stockées dans `.env` (non versionné):

```env
POSTGRES_PASSWORD=mot_de_passe_securise
CURSEFORGE_API_KEY=votre_cle_api
DATABASE_URL=postgresql://user:pass@host:port/db
```

### Bonnes Pratiques

- ✅ Mots de passe forts pour PostgreSQL
- ✅ API keys stockées en variables d'environnement
- ✅ Connexions base de données avec SSL en production
- ✅ Volumes Docker persistants pour les données
- ✅ Healthchecks pour tous les services
- ✅ Restart automatique des conteneurs

## 📊 Monitoring et Logs

### Logs Docker

```bash
# Voir les logs d'un service
docker-compose logs -f postgres
docker-compose logs -f streamlit-app
docker-compose logs -f stats-collector

# Voir tous les logs
docker-compose logs -f
```

### Healthchecks

Tous les services ont des healthchecks configurés:
- PostgreSQL: `pg_isready`
- Applications: vérification HTTP

## 🚀 Performance

### Optimisations Base de Données

- Index sur les colonnes fréquemment requêtées
- Contraintes UNIQUE pour éviter les doublons
- Requêtes optimisées avec DISTINCT ON
- Connection pooling

### Optimisations Application

- Cache Streamlit pour les requêtes fréquentes
- Batch processing pour les API calls
- Rate limiting pour éviter les bans
- Délais configurables entre requêtes

## 🔄 Évolutions Futures

### Court Terme
- [ ] Tests unitaires complets
- [ ] CI/CD avec GitHub Actions
- [ ] Monitoring avec Prometheus/Grafana
- [ ] Alertes email sur erreurs

### Moyen Terme
- [ ] API REST pour accès externe
- [ ] Authentification utilisateurs
- [ ] Export automatique vers S3
- [ ] Rapports PDF automatiques

### Long Terme
- [ ] Machine Learning pour prédictions
- [ ] Dashboard temps réel avec WebSockets
- [ ] Multi-tenancy
- [ ] Clustering PostgreSQL
