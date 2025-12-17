# 📊 Create Nuclear Statistics Dashboard

> Dashboard professionnel pour suivre les statistiques du mod **Create Nuclear** sur Modrinth et CurseForge avec base de données PostgreSQL et collecte automatique.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

---

## ✨ Fonctionnalités

### 📈 Statistiques en Temps Réel
- **Modrinth**: Téléchargements totaux, followers, statistiques par version
- **CurseForge**: Stats API + 600+ modpacks utilisant Create Nuclear
- **Historique**: Graphiques d'évolution avec PostgreSQL

### 🎯 Collecte Automatique
- Collecteur de données planifié (toutes les 6h par défaut)
- Scraping intelligent des modpacks CurseForge
- Enrichissement via API CurseForge
- Sauvegarde automatique en base de données

### 🎨 Interface Moderne
- Dashboard interactif avec Streamlit
- Graphiques dynamiques avec Plotly
- Vue détaillée et vue simplifiée (one-page)
- Export de données

### 🏗️ Architecture Professionnelle
- Code modulaire et maintenable
- Base de données PostgreSQL avec migrations
- Déploiement Docker complet
- Tests et CI/CD ready

---

## 🚀 Démarrage Rapide

### Prérequis

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Git**

### Installation (5 minutes)

```bash
# 1. Cloner le projet
git clone <votre-repo>
cd Create-nuke--data

# 2. Configuration
cp .env.example .env
# Éditer .env avec vos valeurs (POSTGRES_PASSWORD et CURSEFORGE_API_KEY)

# 3. Démarrer
docker-compose up -d

# 4. Vérifier
docker-compose ps
```

### Accès

- **Dashboard principal**: http://localhost:8501
- **Vue simplifiée**: http://localhost:8502
- **PostgreSQL**: localhost:5432

📖 **[Guide de démarrage détaillé](docs/QUICKSTART.md)**

---

## 📁 Structure du Projet

---

## 🎯 Fonctionnalités Détaillées

### 📊 Collecte de Données

#### Modrinth
- ✅ Statistiques globales (downloads, followers)
- ✅ Stats par version avec dates de publication
- ✅ Versions Minecraft supportées

#### CurseForge
- ✅ Statistiques via API officielle
- ✅ Stats par fichier/version
- ✅ Scraping des modpacks (600+)
- ✅ Enrichissement automatique

#### Base de Données
- ✅ PostgreSQL 15 avec Alpine Linux
- ✅ 3 tables principales (daily_stats, version_stats, modpack_stats)
- ✅ Index optimisés pour les performances
- ✅ Contraintes d'intégrité
- ✅ Triggers pour updated_at automatique

### 🎨 Dashboard

#### Vue Principale (`streamlit_app.py`)
- Statistiques globales avec KPIs
- Graphiques d'évolution temporelle
- Comparaison Modrinth vs CurseForge
- Liste détaillée des versions
- Top modpacks utilisant Create Nuclear
- Export de données (CSV, JSON)

#### Vue Simplifiée (`app_onepage.py`)
- Vue condensée sur une page
- Métriques essentielles
- Graphiques compacts
- Idéal pour affichage permanent

---

## 🐳 Services Docker

### `postgres`
- Image: `postgres:15-alpine`
- Port: 5432
- Volume: `pgdata` (persistant)
- Healthcheck: `pg_isready`
- Configuration optimisée pour les performances

### `streamlit-app`
- Application principale Streamlit
- Port: 8501
- Dépend de: postgres (healthy)
- Auto-restart

### `streamlit-onepage`
- Vue simplifiée
- Port: 8502
- Dépend de: postgres (healthy)
- Auto-restart

### `stats-collector`
- Collecteur de statistiques
- Exécution planifiée (6h par défaut)
- Dépend de: postgres (healthy)
- Auto-restart

---

## ⚙️ Configuration

### Variables d'Environnement

| Variable | Description | Défaut | Requis |
|----------|-------------|--------|--------|
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | - | ✅ |
| `POSTGRES_USER` | Utilisateur PostgreSQL | `createnuclear` | ❌ |
| `POSTGRES_DB` | Nom de la base | `createnuclear_stats` | ❌ |
| `CURSEFORGE_API_KEY` | Clé API CurseForge | - | ✅ |
| `DATABASE_URL` | URL de connexion | Auto-généré | ❌ |
| `COLLECTION_INTERVAL` | Intervalle collecte (sec) | `21600` (6h) | ❌ |

### Obtenir une Clé API CurseForge

1. Créer un compte sur [CurseForge Console](https://console.curseforge.com/)
2. Créer une nouvelle API Key
3. Copier la clé dans `.env`

---

## 🔧 Commandes Utiles

### Gestion Docker

```bash
# Démarrer tous les services
docker-compose up -d

# Arrêter
docker-compose down

# Redémarrer un service
docker-compose restart streamlit-app

# Voir les logs
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f postgres
docker-compose logs -f stats-collector

# Reconstruire après modification
docker-compose up -d --build
```

### Base de Données

```bash
# Accéder à PostgreSQL
docker-compose exec postgres psql -U createnuclear -d createnuclear_stats

# Initialiser/Vérifier
python scripts/init_db.py

# Sauvegarder
python scripts/backup.py

# Restaurer
cat backup.sql | docker-compose exec -T postgres psql -U createnuclear createnuclear_stats
```

### Collecte Manuelle

```bash
# Collecter immédiatement
docker-compose exec stats-collector python collect_stats.py

# Voir le statut
docker-compose logs stats-collector
```

---

## 📊 Schéma de Base de Données

### Table: `daily_stats`
Statistiques quotidiennes globales par plateforme

| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL | Clé primaire |
| date | DATE | Date de collecte |
| platform | VARCHAR(20) | modrinth / curseforge |
| total_downloads | INTEGER | Total téléchargements |
| followers | INTEGER | Nombre de followers |
| versions_count | INTEGER | Nombre de versions |

### Table: `version_stats`
Statistiques par version du mod

| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL | Clé primaire |
| date | DATE | Date de collecte |
| platform | VARCHAR(20) | modrinth / curseforge |
| version_name | VARCHAR(255) | Nom de la version |
| downloads | INTEGER | Téléchargements |
| date_published | TIMESTAMP | Date de publication |

### Table: `modpack_stats`
Statistiques des modpacks utilisant Create Nuclear

| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL | Clé primaire |
| date | DATE | Date de collecte |
| platform | VARCHAR(20) | curseforge |
| modpack_name | VARCHAR(255) | Nom du modpack |
| modpack_slug | VARCHAR(255) | Slug unique |
| downloads | INTEGER | Téléchargements |
| followers | INTEGER | Followers |

---

## 🛠️ Maintenance

### Sauvegardes Automatiques

Le script `scripts/backup.py` crée des sauvegardes compressées et garde les 7 dernières.

```bash
# Sauvegarde manuelle
python scripts/backup.py

# Planifier avec cron (Linux/Mac)
0 2 * * * cd /chemin/vers/projet && python scripts/backup.py
```

### Nettoyage des Données

```sql
-- Supprimer les données de plus de 90 jours
DELETE FROM daily_stats WHERE date < CURRENT_DATE - INTERVAL '90 days';
DELETE FROM version_stats WHERE date < CURRENT_DATE - INTERVAL '90 days';
DELETE FROM modpack_stats WHERE date < CURRENT_DATE - INTERVAL '90 days';

-- Récupérer l'espace
VACUUM FULL;
```

---

## 📚 Documentation

- **[Guide de Démarrage Rapide](docs/QUICKSTART.md)** - Installation en 5 minutes
- **[Guide PostgreSQL](docs/DATABASE.md)** - Déploiement et maintenance de la base de données
- **[Architecture](docs/ARCHITECTURE.md)** - Architecture détaillée du projet

---

## 🐛 Troubleshooting

### PostgreSQL ne démarre pas

```bash
docker-compose logs postgres
docker-compose down -v
docker-compose up -d
```

### Erreur de connexion

```bash
docker-compose exec postgres pg_isready -U createnuclear
docker-compose exec streamlit-app env | grep DATABASE
```

### Collecteur ne fonctionne pas

```bash
docker-compose logs stats-collector
docker-compose restart stats-collector
```

📖 **[Guide de troubleshooting complet](docs/DATABASE.md#troubleshooting)**

---

## 🚀 Roadmap

### Court Terme
- [ ] Tests unitaires complets
- [ ] CI/CD avec GitHub Actions
- [ ] Monitoring avec Prometheus/Grafana
- [ ] Alertes email sur erreurs

### Moyen Terme
- [ ] API REST pour accès externe
- [ ] Authentification utilisateurs
- [ ] Export automatique S3
- [ ] Rapports PDF automatiques

### Long Terme
- [ ] Machine Learning pour prédictions
- [ ] Dashboard temps réel WebSockets
- [ ] Multi-tenancy
- [ ] Clustering PostgreSQL

---

## 📄 License

MIT License - Voir [LICENSE](LICENSE) pour plus de détails

---

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Ouvrir une issue pour signaler un bug
- Proposer une nouvelle fonctionnalité
- Soumettre une pull request

---

## 📧 Support

Pour toute question ou problème :
1. Consulter la [documentation](docs/)
2. Vérifier les [issues existantes](../../issues)
3. Créer une nouvelle issue avec les détails

---

**Fait avec ❤️ pour la communauté Create Nuclear**
