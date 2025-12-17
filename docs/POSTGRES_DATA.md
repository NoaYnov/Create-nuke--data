# Migration des Données vers PostgreSQL

## 📋 Vue d'ensemble

Toutes les données collectées sont maintenant sauvegardées dans PostgreSQL. Ce document explique comment fonctionne le système et comment migrer les données existantes.

## 🗄️ Structure de la Base de Données

### Tables PostgreSQL

1. **`daily_stats`** - Statistiques globales quotidiennes
   - `date`, `platform`, `total_downloads`, `followers`, `versions_count`

2. **`version_stats`** - Statistiques par version
   - `date`, `platform`, `version_name`, `version_number`, `downloads`, `date_published`

3. **`modpack_stats`** - Statistiques des modpacks
   - `date`, `platform`, `modpack_name`, `modpack_slug`, `downloads`, `followers`

## 🔄 Flux de Données Actuel

### Collecte Automatique (via `collect_stats.py`)

Le script de collecte sauvegarde **TOUTES** les données dans PostgreSQL :

```
Modrinth API → PostgreSQL (daily_stats + version_stats)
CurseForge API → PostgreSQL (daily_stats + version_stats + modpack_stats)
```

### Fichiers CSV/JSON

Les fichiers CSV/JSON dans le dossier `data/` sont conservés pour :
- **Backup** - Copie de sauvegarde des données
- **Compatibilité** - Lecture par d'autres outils si nécessaire

## 📥 Import des Données Historiques

Pour importer les données existantes dans les fichiers CSV/JSON vers PostgreSQL :

### Via Docker

```bash
# Exécuter le script d'import dans le conteneur
docker-compose exec streamlit-app python scripts/import_to_postgres.py
```

### En local

```bash
# Depuis la racine du projet
python scripts/import_to_postgres.py
```

## ✅ Vérification des Données

### 1. Vérifier les données dans PostgreSQL

```bash
# Se connecter au conteneur PostgreSQL
docker-compose exec postgres psql -U createnuclear -d createnuclear_stats

# Commandes SQL utiles :
SELECT COUNT(*) FROM daily_stats;
SELECT COUNT(*) FROM version_stats;
SELECT COUNT(*) FROM modpack_stats;

# Voir les dernières entrées
SELECT * FROM daily_stats ORDER BY date DESC LIMIT 5;
SELECT * FROM modpack_stats ORDER BY date DESC LIMIT 10;
```

### 2. Vérifier via le script d'initialisation

```bash
docker-compose exec streamlit-app python scripts/init_db.py
```

## 🔧 Configuration

Les données vont automatiquement dans PostgreSQL grâce à :

1. **`DATABASE_URL`** dans `src/config.py` - URL de connexion
2. **`StatsDatabase`** dans `src/core/database.py` - Classe de gestion DB
3. **`collect_stats.py`** - Sauvegarde automatique lors de la collecte

## 📊 Utilisation dans Streamlit

Le dashboard Streamlit lit les données depuis PostgreSQL :

```python
# Les fonctions de cache chargent depuis PostgreSQL
@st.cache_data(ttl=CACHE_TTL)
def load_modrinth_stats():
    db = get_database()
    return db.get_daily_stats_history("modrinth")
```

## 🎯 Que Faire Maintenant ?

### Étape 1 : Importer les Données Existantes (optionnel)

Si vous avez des données dans `data/curseforge_modpacks.csv` ou `.json` :

```bash
docker-compose exec streamlit-app python scripts/import_to_postgres.py
```

### Étape 2 : Lancer la Collecte de Données

```bash
# Via le dashboard Streamlit
# Cliquez sur le bouton "🔄 Run Data Collection"

# Ou manuellement via Docker
docker-compose exec streamlit-app python src/collectors/collect_stats.py
```

### Étape 3 : Vérifier que Tout Fonctionne

```bash
# Vérifier la base de données
docker-compose exec streamlit-app python scripts/init_db.py
```

## 📝 Notes Importantes

- ✅ **Toutes les nouvelles données** vont automatiquement dans PostgreSQL
- ✅ **Les fichiers CSV/JSON** sont toujours créés comme backup
- ✅ **Le dashboard** lit depuis PostgreSQL (avec cache)
- ✅ **L'historique** est maintenu dans PostgreSQL pour les graphiques temporels

## 🚀 Performance

PostgreSQL offre :
- **Requêtes rapides** avec index optimisés
- **Historique complet** sans duplication
- **Agrégations** efficaces pour les graphiques
- **Concurrence** pour accès simultanés

## ⚠️ Backup

Pour sauvegarder la base de données :

```bash
# Créer un dump
docker-compose exec postgres pg_dump -U createnuclear createnuclear_stats > backup.sql

# Restaurer un dump
docker-compose exec -T postgres psql -U createnuclear createnuclear_stats < backup.sql
```

## 🔍 Debugging

Si les données ne s'affichent pas :

1. Vérifier la connexion DB :
   ```bash
   docker-compose logs streamlit-app | grep -i database
   ```

2. Vérifier le contenu :
   ```bash
   docker-compose exec streamlit-app python scripts/init_db.py
   ```

3. Vérifier les logs de collecte :
   ```bash
   docker-compose logs stats-collector
   ```
