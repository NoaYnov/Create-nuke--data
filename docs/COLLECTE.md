# 📊 Système de Collecte de Données

## Vue d'ensemble

Le système collecte automatiquement les statistiques du mod **Create Nuclear** depuis deux plateformes :
- 🟢 **Modrinth** (API publique)
- 🔥 **CurseForge** (API avec clé requise)

Les données sont historisées dans **PostgreSQL** pour suivre l'évolution dans le temps.

---

## 🗄️ Structure de la Base de Données

### Table `daily_stats`
Statistiques globales quotidiennes par plateforme.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | SERIAL | Identifiant unique auto-incrémenté |
| `date` | DATE | Date de la collecte (format : YYYY-MM-DD) |
| `platform` | VARCHAR(20) | Plateforme : `"modrinth"` ou `"curseforge"` |
| `total_downloads` | INTEGER | Nombre total de téléchargements |
| `followers` | INTEGER | Followers (Modrinth) ou Likes (CurseForge) |
| `versions_count` | INTEGER | Nombre de versions/fichiers disponibles |
| `created_at` | TIMESTAMP | Horodatage de l'insertion (automatique) |

**Contrainte unique** : `UNIQUE(date, platform)` - Une seule entrée par jour et par plateforme.

**Index** : `idx_daily_stats_date` sur `date DESC` pour accès rapide.

---

### Table `version_stats`
Statistiques détaillées par version/fichier.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | SERIAL | Identifiant unique |
| `date` | DATE | Date de la collecte |
| `platform` | VARCHAR(20) | Plateforme source |
| `version_name` | VARCHAR(255) | Nom de la version (ex: "1.0.3") |
| `version_number` | VARCHAR(255) | Numéro ou nom de fichier |
| `downloads` | INTEGER | Téléchargements de cette version |
| `date_published` | TIMESTAMP | Date de publication de la version |
| `created_at` | TIMESTAMP | Horodatage de l'insertion |

**Contrainte unique** : `UNIQUE(date, platform, version_name)` - Une entrée par version, par jour, par plateforme.

**Index** : `idx_version_stats_date` sur `(date DESC, platform)`.

---

### Table `modpack_stats`
Statistiques des modpacks contenant Create Nuclear.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | SERIAL | Identifiant unique |
| `date` | DATE | Date de la collecte |
| `platform` | VARCHAR(20) | Plateforme source |
| `modpack_name` | VARCHAR(255) | Nom du modpack |
| `modpack_slug` | VARCHAR(255) | Identifiant unique du modpack |
| `downloads` | INTEGER | Téléchargements du modpack |
| `followers` | INTEGER | Followers du modpack |
| `created_at` | TIMESTAMP | Horodatage de l'insertion |

**Contrainte unique** : `UNIQUE(date, platform, modpack_slug)`.

**Index** : `idx_modpack_stats_date` sur `(date DESC, platform)`.

---

## 🔄 Fréquence de Collecte

### Mode Docker (Production)
- **Daemon automatique** : `collect_daemon.py`
- **Première collecte** : 30 secondes après le démarrage (attente de PostgreSQL)
- **Fréquence** : **Toutes les 24 heures** (86400 secondes)
- **Redémarrage** : Automatique en cas d'erreur
- **Logs** : Visible via `docker logs createnuclear-collector`

### Mode Manuel
```bash
# Exécution unique
python collect_stats.py

# Planification avec cron (Linux/Mac)
0 2 * * * /usr/bin/python3 /path/to/collect_stats.py

# Planification avec Task Scheduler (Windows)
# Créer une tâche quotidienne à 2h00
```

---

## 📡 Sources de Données

### Modrinth API
- **Endpoint projet** : `https://api.modrinth.com/v2/project/createnuclear`
- **Endpoint versions** : `https://api.modrinth.com/v2/project/createnuclear/version`
- **Authentification** : Aucune (API publique)
- **Rate limit** : 300 requêtes/5 minutes
- **Données collectées** :
  - Total téléchargements
  - Nombre de followers
  - Liste complète des versions avec stats individuelles
  - Versions Minecraft supportées
  - Dates de publication

### CurseForge API
- **Endpoint mod** : `https://api.curseforge.com/v1/mods/989797`
- **Endpoint fichiers** : `https://api.curseforge.com/v1/mods/989797/files`
- **Authentification** : Clé API requise (`x-api-key` header)
- **Rate limit** : Variable selon le tier
- **Données collectées** :
  - Total téléchargements
  - Likes (thumbsUpCount)
  - Liste des fichiers avec stats
  - Versions Minecraft supportées
  - Dates de publication

---

## 🕐 Horodatage et Fuseaux Horaires

### Dates de collecte
- **Format stocké** : `DATE` (YYYY-MM-DD)
- **Timezone** : UTC (Coordinated Universal Time)
- **Génération** : `datetime.now(timezone.utc).date()`
- **Une seule collecte par jour** : Contrainte UNIQUE empêche les doublons

### Dates de publication (versions)
- **Format stocké** : `TIMESTAMP`
- **Parsing** : Utilisation de `dateutil.parser` pour compatibilité multi-formats
- **Sources** :
  - Modrinth : ISO 8601 standard (ex: `2024-05-08T10:51:16Z`)
  - CurseForge : ISO 8601 avec microsecondes tronquées (ex: `2024-05-08T10:51:16.18+00:00`)

### Horodatage de création
- **Colonne** : `created_at`
- **Valeur par défaut** : `CURRENT_TIMESTAMP` (PostgreSQL)
- **Usage** : Traçabilité, détection de modifications

---

## 🔐 Configuration Requise

### Variables d'environnement

```bash
# Obligatoire pour PostgreSQL
DATABASE_URL=postgresql://user:password@host:5432/database

# Optionnel pour CurseForge
CURSEFORGE_API_KEY=your_api_key_here
```

### Fichier .env (Docker)
```env
POSTGRES_PASSWORD=your_secure_password
CURSEFORGE_API_KEY=your_curseforge_key
DATABASE_URL=postgresql://createnuclear:your_secure_password@postgres:5432/createnuclear_stats
```

---

## 🚀 Démarrage

### Docker Compose (Recommandé)
```bash
# Démarrer tous les services (app, collector, postgres)
docker-compose up -d

# Vérifier les logs du collecteur
docker logs -f createnuclear-collector

# Arrêter tous les services
docker-compose down
```

### Exécution manuelle
```bash
# Installer les dépendances
pip install -r requirements.txt

# Configuration PostgreSQL
export DATABASE_URL="postgresql://user:pass@localhost:5432/createnuclear_stats"
export CURSEFORGE_API_KEY="your_key"

# Lancer la collecte
python collect_stats.py
```

---

## 📈 Exemple de Collecte

```
=== Create Nuclear Stats Collection ===
Started at: 2025-11-26 14:30:00.123456

✓ Connected to database
[2025-11-26 14:30:01] Collecting Modrinth stats...
✓ Modrinth: 45723 downloads, 127 versions

[2025-11-26 14:30:02] Collecting CurseForge stats...
✓ CurseForge: 38456 downloads, 89 files

=== Summary ===
Modrinth: ✓
CurseForge: ✓
Completed at: 2025-11-26 14:30:03.789012
```

---

## 🔍 Requêtes SQL Utiles

### Voir les dernières collectes
```sql
SELECT date, platform, total_downloads, followers 
FROM daily_stats 
ORDER BY date DESC, platform 
LIMIT 10;
```

### Croissance sur 30 jours
```sql
SELECT 
    platform,
    MAX(total_downloads) - MIN(total_downloads) as growth
FROM daily_stats
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY platform;
```

### Top 10 versions (Modrinth)
```sql
SELECT DISTINCT ON (version_name)
    version_name, downloads
FROM version_stats
WHERE platform = 'modrinth'
ORDER BY version_name, date DESC
LIMIT 10;
```

---

## ⚠️ Gestion des Erreurs

### Collecte échouée
- **Comportement** : Le daemon continue et réessaie après 24h
- **Logs** : `✗ Error collecting [platform] stats: [error message]`
- **Impact** : Pas de donnée pour ce jour, pas d'interruption du service

### Base de données inaccessible
- **Erreur** : `Fatal error: could not connect to server`
- **Solution** : Vérifier que PostgreSQL est démarré et accessible
- **Docker** : Attente automatique de 30 secondes au démarrage

### API Key manquante (CurseForge)
- **Comportement** : Skip CurseForge, continue avec Modrinth
- **Log** : `⚠ CURSEFORGE_API_KEY not set, skipping CurseForge stats`
- **Solution** : Définir la variable d'environnement

---

## 📊 Visualisation des Données

Les données collectées sont visualisées dans le dashboard Streamlit :
- **Onglet "Base de données"** : Accès direct aux tables
- **Graphiques historiques** : Évolution temporelle
- **Export CSV** : Téléchargement des données brutes
- **Filtres** : Jour/Semaine/Mois/Année

---

## 🔧 Maintenance

### Nettoyage des anciennes données
```sql
-- Supprimer les données de plus de 2 ans
DELETE FROM daily_stats WHERE date < CURRENT_DATE - INTERVAL '2 years';
DELETE FROM version_stats WHERE date < CURRENT_DATE - INTERVAL '2 years';
DELETE FROM modpack_stats WHERE date < CURRENT_DATE - INTERVAL '2 years';
```

### Backup
```bash
# Dump de la base
docker exec createnuclear-postgres pg_dump -U createnuclear createnuclear_stats > backup.sql

# Restauration
docker exec -i createnuclear-postgres psql -U createnuclear createnuclear_stats < backup.sql
```

---

## 📚 Documentation Complémentaire

- [DATABASE.md](DATABASE.md) - Configuration PostgreSQL détaillée
- [DEPLOYMENT.md](DEPLOYMENT.md) - Options d'hébergement
- [QUICKSTART.md](QUICKSTART.md) - Guide de démarrage rapide
- [README.md](README.md) - Vue d'ensemble du projet
