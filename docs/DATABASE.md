# Guide de Déploiement PostgreSQL

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Installation Locale](#installation-locale)
3. [Déploiement Docker](#déploiement-docker)
4. [Configuration](#configuration)
5. [Initialisation](#initialisation)
6. [Maintenance](#maintenance)
7. [Sauvegarde et Restauration](#sauvegarde-et-restauration)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 Prérequis

### Logiciels Requis

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Python** >= 3.10 (pour scripts locaux)
- **Git** (pour cloner le projet)

### Vérification

```bash
# Vérifier Docker
docker --version
docker-compose --version

# Vérifier Python
python --version
```

---

## 💻 Installation Locale

### Option 1: PostgreSQL Natif (Windows)

#### 1. Télécharger PostgreSQL

Téléchargez PostgreSQL 15 depuis [postgresql.org](https://www.postgresql.org/download/windows/)

#### 2. Installation

```powershell
# Installer avec les paramètres par défaut
# Port: 5432
# Utilisateur: postgres
# Définir un mot de passe fort
```

#### 3. Créer la Base de Données

```powershell
# Ouvrir psql
psql -U postgres

# Dans psql:
CREATE DATABASE createnuclear_stats;
CREATE USER createnuclear WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE createnuclear_stats TO createnuclear;
\q
```

#### 4. Configuration

Créer un fichier `.env` à la racine du projet:

```env
DATABASE_URL=postgresql://createnuclear:votre_mot_de_passe@localhost:5432/createnuclear_stats
POSTGRES_PASSWORD=votre_mot_de_passe
CURSEFORGE_API_KEY=votre_cle_api
```

#### 5. Initialiser les Tables

```bash
# Installer les dépendances
pip install -r requirements.txt

# Exécuter le script d'initialisation
python scripts/init_db.py
```

---

## 🐳 Déploiement Docker (Recommandé)

### Avantages

- ✅ Isolation complète
- ✅ Reproductibilité
- ✅ Facile à déployer
- ✅ Pas de conflit avec d'autres services
- ✅ Sauvegarde simplifiée

### Étape 1: Cloner le Projet

```bash
git clone <votre-repo>
cd Create-nuke--data
```

### Étape 2: Configuration

Copier le fichier d'exemple et le modifier:

```bash
# Copier le template
cp .env.example .env

# Éditer avec vos valeurs
notepad .env
```

Contenu du `.env`:

```env
# PostgreSQL
POSTGRES_PASSWORD=VotreMotDePasseSecurise123!
POSTGRES_USER=createnuclear
POSTGRES_DB=createnuclear_stats

# CurseForge API
CURSEFORGE_API_KEY=votre_cle_api_curseforge

# Database URL (utilisé par l'application)
DATABASE_URL=postgresql://createnuclear:VotreMotDePasseSecurise123!@postgres:5432/createnuclear_stats
```

### Étape 3: Lancer les Services

```bash
# Construire et démarrer tous les services
docker-compose up -d

# Vérifier que tout fonctionne
docker-compose ps
```

Vous devriez voir:

```
NAME                        STATUS              PORTS
createnuclear-postgres      Up (healthy)        0.0.0.0:5432->5432/tcp
createnuclear-app           Up                  0.0.0.0:8501->8501/tcp
createnuclear-onepage       Up                  0.0.0.0:8502->8502/tcp
createnuclear-collector     Up
```

### Étape 4: Accéder aux Applications

- **Application principale**: http://localhost:8501
- **Vue simplifiée**: http://localhost:8502
- **PostgreSQL**: localhost:5432

---

## ⚙️ Configuration

### Structure du docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: createnuclear-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-createnuclear_stats}
      POSTGRES_USER: ${POSTGRES_USER:-createnuclear}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./docker/postgres/init:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-createnuclear}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - createnuclear-network

volumes:
  pgdata:
    driver: local

networks:
  createnuclear-network:
    driver: bridge
```

### Variables d'Environnement

| Variable              | Description                          | Défaut                    | Requis |
|-----------------------|--------------------------------------|---------------------------|--------|
| POSTGRES_DB           | Nom de la base de données            | createnuclear_stats       | Non    |
| POSTGRES_USER         | Utilisateur PostgreSQL               | createnuclear             | Non    |
| POSTGRES_PASSWORD     | Mot de passe PostgreSQL              | -                         | **Oui**|
| CURSEFORGE_API_KEY    | Clé API CurseForge                   | -                         | **Oui**|
| DATABASE_URL          | URL complète de connexion            | Auto-généré               | Non    |

---

## 🚀 Initialisation

### Scripts d'Initialisation Automatiques

Les scripts dans `docker/postgres/init/` sont exécutés automatiquement au premier démarrage:

#### 01-init-database.sql

```sql
-- Création des extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Configuration
ALTER DATABASE createnuclear_stats SET timezone TO 'UTC';
```

#### 02-create-tables.sql

```sql
-- Table des statistiques quotidiennes
CREATE TABLE IF NOT EXISTS daily_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    platform VARCHAR(20) NOT NULL,
    total_downloads INTEGER NOT NULL,
    followers INTEGER,
    versions_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, platform)
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_daily_stats_date 
ON daily_stats(date DESC);

-- Table des statistiques par version
CREATE TABLE IF NOT EXISTS version_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    platform VARCHAR(20) NOT NULL,
    version_name VARCHAR(255) NOT NULL,
    version_number VARCHAR(255),
    downloads INTEGER NOT NULL,
    date_published TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, platform, version_name)
);

CREATE INDEX IF NOT EXISTS idx_version_stats_date 
ON version_stats(date DESC, platform);

-- Table des statistiques de modpacks
CREATE TABLE IF NOT EXISTS modpack_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    platform VARCHAR(20) NOT NULL,
    modpack_name VARCHAR(255) NOT NULL,
    modpack_slug VARCHAR(255),
    downloads INTEGER NOT NULL,
    followers INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, platform, modpack_slug)
);

CREATE INDEX IF NOT EXISTS idx_modpack_stats_date 
ON modpack_stats(date DESC, platform);

-- Permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO createnuclear;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO createnuclear;
```

### Initialisation Manuelle

Si vous devez réinitialiser la base de données:

```bash
# Arrêter les services
docker-compose down

# Supprimer le volume (ATTENTION: perte de données!)
docker volume rm create-nuke--data_pgdata

# Redémarrer
docker-compose up -d
```

---

## 🔧 Maintenance

### Commandes Utiles

#### Accéder à PostgreSQL

```bash
# Via Docker
docker-compose exec postgres psql -U createnuclear -d createnuclear_stats

# Depuis l'hôte (si PostgreSQL client installé)
psql -h localhost -U createnuclear -d createnuclear_stats
```

#### Vérifier l'État de la Base

```sql
-- Taille de la base de données
SELECT pg_size_pretty(pg_database_size('createnuclear_stats'));

-- Nombre d'enregistrements par table
SELECT 'daily_stats' as table_name, COUNT(*) FROM daily_stats
UNION ALL
SELECT 'version_stats', COUNT(*) FROM version_stats
UNION ALL
SELECT 'modpack_stats', COUNT(*) FROM modpack_stats;

-- Dernières entrées
SELECT date, platform, total_downloads 
FROM daily_stats 
ORDER BY date DESC 
LIMIT 10;
```

#### Nettoyer les Anciennes Données

```sql
-- Supprimer les données de plus de 90 jours
DELETE FROM daily_stats WHERE date < CURRENT_DATE - INTERVAL '90 days';
DELETE FROM version_stats WHERE date < CURRENT_DATE - INTERVAL '90 days';
DELETE FROM modpack_stats WHERE date < CURRENT_DATE - INTERVAL '90 days';

-- Vacuum pour récupérer l'espace
VACUUM FULL;
```

### Optimisation des Performances

```sql
-- Analyser les tables
ANALYZE daily_stats;
ANALYZE version_stats;
ANALYZE modpack_stats;

-- Réindexer
REINDEX TABLE daily_stats;
REINDEX TABLE version_stats;
REINDEX TABLE modpack_stats;

-- Vérifier les index manquants
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY abs(correlation) DESC;
```

---

## 💾 Sauvegarde et Restauration

### Sauvegarde Automatique

#### Script de Sauvegarde

Créer `scripts/backup.sh`:

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Créer le dossier de sauvegarde
mkdir -p $BACKUP_DIR

# Sauvegarde
docker-compose exec -T postgres pg_dump -U createnuclear createnuclear_stats > $BACKUP_FILE

# Compression
gzip $BACKUP_FILE

# Garder seulement les 7 dernières sauvegardes
ls -t $BACKUP_DIR/backup_*.sql.gz | tail -n +8 | xargs -r rm

echo "Backup créé: $BACKUP_FILE.gz"
```

#### Planification (Cron)

```bash
# Éditer crontab
crontab -e

# Ajouter (sauvegarde quotidienne à 2h du matin)
0 2 * * * /chemin/vers/scripts/backup.sh
```

### Sauvegarde Manuelle

```bash
# Sauvegarde complète
docker-compose exec postgres pg_dump -U createnuclear createnuclear_stats > backup.sql

# Sauvegarde avec compression
docker-compose exec postgres pg_dump -U createnuclear createnuclear_stats | gzip > backup.sql.gz

# Sauvegarde d'une table spécifique
docker-compose exec postgres pg_dump -U createnuclear -t daily_stats createnuclear_stats > daily_stats_backup.sql
```

### Restauration

```bash
# Restaurer depuis une sauvegarde
cat backup.sql | docker-compose exec -T postgres psql -U createnuclear createnuclear_stats

# Restaurer depuis une sauvegarde compressée
gunzip -c backup.sql.gz | docker-compose exec -T postgres psql -U createnuclear createnuclear_stats

# Restaurer avec suppression préalable
docker-compose exec postgres psql -U createnuclear -c "DROP DATABASE IF EXISTS createnuclear_stats;"
docker-compose exec postgres psql -U createnuclear -c "CREATE DATABASE createnuclear_stats;"
cat backup.sql | docker-compose exec -T postgres psql -U createnuclear createnuclear_stats
```

---

## 🔍 Troubleshooting

### Problème: Le conteneur PostgreSQL ne démarre pas

**Symptômes**: `docker-compose ps` montre le service comme "Exited"

**Solutions**:

```bash
# Vérifier les logs
docker-compose logs postgres

# Vérifier les permissions du volume
docker volume inspect create-nuke--data_pgdata

# Recréer le volume
docker-compose down -v
docker-compose up -d
```

### Problème: Erreur de connexion à la base de données

**Symptômes**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:

1. Vérifier que PostgreSQL est démarré:
```bash
docker-compose ps postgres
```

2. Vérifier la configuration réseau:
```bash
docker-compose exec streamlit-app ping postgres
```

3. Vérifier les variables d'environnement:
```bash
docker-compose exec streamlit-app env | grep DATABASE
```

### Problème: "current transaction is aborted"

**Symptômes**: Erreur lors de l'insertion de données

**Solutions**:

```python
# Dans le code Python, ajouter un rollback
try:
    # Opération base de données
    db.save_daily_stats(...)
except Exception as e:
    db.conn.rollback()  # Important!
    raise e
```

### Problème: Base de données pleine

**Symptômes**: `ERROR: could not extend file`

**Solutions**:

```bash
# Vérifier l'espace disque
docker system df

# Nettoyer les données anciennes (voir section Maintenance)

# Augmenter la taille du volume si nécessaire
```

### Problème: Performances lentes

**Solutions**:

```sql
-- Vérifier les requêtes lentes
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Vérifier les index
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0;

-- Analyser les tables
ANALYZE;
```

---

## 📊 Monitoring

### Healthcheck PostgreSQL

Le healthcheck est configuré dans `docker-compose.yml`:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U createnuclear"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Vérifier la Santé

```bash
# Status des conteneurs
docker-compose ps

# Logs en temps réel
docker-compose logs -f postgres

# Statistiques de ressources
docker stats createnuclear-postgres
```

### Métriques PostgreSQL

```sql
-- Connexions actives
SELECT count(*) FROM pg_stat_activity;

-- Taille des tables
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Cache hit ratio (devrait être > 99%)
SELECT 
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit) as heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;
```

---

## 🚀 Déploiement en Production

### Checklist de Sécurité

- [ ] Mot de passe PostgreSQL fort (min 16 caractères)
- [ ] Port 5432 non exposé publiquement
- [ ] SSL/TLS activé pour les connexions
- [ ] Sauvegardes automatiques configurées
- [ ] Monitoring actif
- [ ] Logs rotatifs configurés
- [ ] Firewall configuré

### Configuration Production

Créer `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    # NE PAS exposer le port en production
    # ports:
    #   - "5432:5432"
    command: 
      - "postgres"
      - "-c"
      - "ssl=on"
      - "-c"
      - "ssl_cert_file=/etc/ssl/certs/server.crt"
      - "-c"
      - "ssl_key_file=/etc/ssl/private/server.key"
    restart: always
```

Lancer en production:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 📚 Ressources Supplémentaires

- [Documentation PostgreSQL](https://www.postgresql.org/docs/15/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

## 🆘 Support

En cas de problème:

1. Vérifier les logs: `docker-compose logs`
2. Consulter cette documentation
3. Vérifier les issues GitHub du projet
4. Créer une nouvelle issue avec les détails du problème
