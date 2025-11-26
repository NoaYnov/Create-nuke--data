# Create Nuclear - Historisation des statistiques

## 📊 Système d'historisation PostgreSQL

Le système collecte automatiquement les statistiques chaque jour et les stocke dans PostgreSQL pour un suivi à long terme.

## 🗄️ Structure de la base de données

### Tables créées

1. **daily_stats** - Statistiques globales quotidiennes
   - date, platform, total_downloads, followers, versions_count

2. **version_stats** - Statistiques par version
   - date, platform, version_name, version_number, downloads

3. **modpack_stats** - Statistiques des modpacks
   - date, platform, modpack_name, downloads, followers

## 🚀 Installation

### 1. Installer PostgreSQL

**Windows:**
```powershell
# Télécharger depuis https://www.postgresql.org/download/windows/
# Ou avec Chocolatey:
choco install postgresql
```

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
```

**Docker (Recommandé):**
```bash
docker run --name createnuclear-postgres \
  -e POSTGRES_PASSWORD=votremdp \
  -e POSTGRES_DB=createnuclear_stats \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  -d postgres:15
```

### 2. Créer la base de données

```sql
CREATE DATABASE createnuclear_stats;
CREATE USER createnuclear WITH PASSWORD 'votremdp';
GRANT ALL PRIVILEGES ON DATABASE createnuclear_stats TO createnuclear;
```

### 3. Configurer la connexion

**Méthode 1: Variable d'environnement**
```bash
export DATABASE_URL="postgresql://createnuclear:votremdp@localhost:5432/createnuclear_stats"
```

**Méthode 2: Secrets Streamlit**
Ajouter dans `.streamlit/secrets.toml`:
```toml
DATABASE_URL = "postgresql://createnuclear:votremdp@localhost:5432/createnuclear_stats"
```

### 4. Initialiser les tables

Les tables sont créées automatiquement au premier lancement :
```bash
python collect_stats.py
```

## ⏰ Automatiser la collecte

### Linux (Cron)

```bash
# Éditer le crontab
crontab -e

# Ajouter cette ligne pour collecter à 2h du matin chaque jour
0 2 * * * cd /path/to/Create-nuke--data && /usr/bin/python3 collect_stats.py >> /var/log/createnuclear-stats.log 2>&1
```

### Windows (Tâche planifiée)

1. Créer `collect_daily.bat`:
```batch
@echo off
cd /d "C:\path\to\Create-nuke--data"
set DATABASE_URL=postgresql://createnuclear:votremdp@localhost:5432/createnuclear_stats
set CURSEFORGE_API_KEY=votre_clé_api
python collect_stats.py >> logs\collect.log 2>&1
```

2. Ouvrir "Planificateur de tâches"
3. Créer une tâche basique
4. Déclencheur : Quotidien à 2h00
5. Action : Lancer `collect_daily.bat`

### Docker Compose (Avec collecte automatique)

Modifier `docker-compose.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: createnuclear_stats
      POSTGRES_USER: createnuclear
      POSTGRES_PASSWORD: votremdp
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  streamlit-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DATABASE_URL=postgresql://createnuclear:votremdp@postgres:5432/createnuclear_stats
      - CURSEFORGE_API_KEY=${CURSEFORGE_API_KEY}
    depends_on:
      - postgres
    restart: unless-stopped

  stats-collector:
    build: .
    command: sh -c "while true; do python collect_stats.py && sleep 86400; done"
    environment:
      - DATABASE_URL=postgresql://createnuclear:votremdp@postgres:5432/createnuclear_stats
      - CURSEFORGE_API_KEY=${CURSEFORGE_API_KEY}
    depends_on:
      - postgres
    restart: unless-stopped

volumes:
  pgdata:
```

## 📈 Nouvelles fonctionnalités dans l'app

L'application Streamlit affiche maintenant :

1. **Historique à long terme** - Graphique des 90 derniers jours
2. **Croissance quotidienne** - Nouveaux téléchargements par jour
3. **Tendances** - Évolution dans le temps

## 🔍 Requêtes utiles

### Voir les stats des 30 derniers jours
```sql
SELECT date, platform, total_downloads, followers
FROM daily_stats
WHERE platform = 'modrinth'
ORDER BY date DESC
LIMIT 30;
```

### Croissance par semaine
```sql
SELECT 
  DATE_TRUNC('week', date) as week,
  platform,
  MAX(total_downloads) - MIN(total_downloads) as weekly_growth
FROM daily_stats
GROUP BY week, platform
ORDER BY week DESC;
```

### Top versions par période
```sql
SELECT 
  version_name,
  MAX(downloads) - MIN(downloads) as growth
FROM version_stats
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
  AND platform = 'modrinth'
GROUP BY version_name
ORDER BY growth DESC
LIMIT 10;
```

## 🔧 Maintenance

### Backup de la base de données
```bash
pg_dump createnuclear_stats > backup_$(date +%Y%m%d).sql
```

### Restaurer un backup
```bash
psql createnuclear_stats < backup_20250126.sql
```

### Nettoyer les anciennes données (> 1 an)
```sql
DELETE FROM daily_stats WHERE date < CURRENT_DATE - INTERVAL '1 year';
DELETE FROM version_stats WHERE date < CURRENT_DATE - INTERVAL '1 year';
DELETE FROM modpack_stats WHERE date < CURRENT_DATE - INTERVAL '1 year';
```

## 🌐 Hébergement PostgreSQL gratuit

Si vous ne voulez pas héberger PostgreSQL localement :

1. **Supabase** - https://supabase.com (500 MB gratuit)
2. **ElephantSQL** - https://www.elephantsql.com (20 MB gratuit)
3. **Neon** - https://neon.tech (3 GB gratuit)
4. **Render** - https://render.com (gratuit avec limitations)

Exemple avec Supabase:
```bash
DATABASE_URL="postgresql://postgres:votre_mdp@db.xxxxx.supabase.co:5432/postgres"
```

## ⚠️ Notes importantes

- La collecte quotidienne écrase les données du jour si déjà présentes
- Les graphiques historiques n'apparaissent que si la base est configurée
- Sans base de données, l'app fonctionne normalement avec les données en temps réel
