# 🗄️ Guide pgAdmin - Visualisation de la Base de Données

## 📋 Vue d'ensemble

pgAdmin est une interface graphique pour gérer et visualiser PostgreSQL. Elle vous permet de voir toutes les tables, exécuter des requêtes SQL, et explorer les données facilement.

## 🚀 Démarrage de pgAdmin

### 1. Démarrer le Service

```bash
# Démarrer tous les services (y compris pgAdmin)
docker-compose up -d

# Ou démarrer uniquement pgAdmin
docker-compose up -d pgadmin
```

### 2. Accéder à pgAdmin

Ouvrez votre navigateur et allez sur :

👉 **http://localhost:5050**

### 3. Connexion Initiale

**Identifiants par défaut :**
- **Email** : `admin@createnuclear.local`
- **Mot de passe** : `admin`

> ⚠️ Ces identifiants peuvent être changés dans le fichier `.env`

## 🔌 Connexion à PostgreSQL

### Première Configuration (une seule fois)

1. **Clic droit sur "Servers"** dans le menu de gauche
2. Sélectionnez **"Register" → "Server"**

3. **Onglet "General"**
   - **Name** : `Create Nuclear Stats`
   - **Description** : `Create Nuclear Statistics Database` (optionnel)

4. **Onglet "Connection"**
   - **Host name/address** : `postgres` (nom du service Docker)
   - **Port** : `5432` (port interne Docker)
   - **Maintenance database** : `createnuclear_stats`
   - **Username** : `createnuclear` (ou votre valeur dans `.env`)
   - **Password** : Votre mot de passe PostgreSQL (voir `.env`)
   - ✅ Cochez **"Save password"**

5. Cliquez sur **"Save"**

## 📊 Voir les Tables

### Navigation

```
Servers
  └─ Create Nuclear Stats
      └─ Databases (1)
          └─ createnuclear_stats
              └─ Schemas (1)
                  └─ public
                      └─ Tables (3)
                          ├─ daily_stats
                          ├─ version_stats
                          └─ modpack_stats
```

### Voir le Contenu d'une Table

1. **Expand** : `Servers → Create Nuclear Stats → Databases → createnuclear_stats → Schemas → public → Tables`
2. **Clic droit** sur une table (ex: `daily_stats`)
3. Sélectionnez **"View/Edit Data" → "All Rows"**

## 📈 Tables Disponibles

### 1. `daily_stats` - Statistiques Quotidiennes Globales

| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL | ID unique |
| date | DATE | Date de la collecte |
| platform | VARCHAR(20) | Plateforme (modrinth/curseforge) |
| total_downloads | INTEGER | Téléchargements totaux |
| followers | INTEGER | Nombre de followers |
| versions_count | INTEGER | Nombre de versions |
| created_at | TIMESTAMP | Date de création de l'entrée |

### 2. `version_stats` - Statistiques par Version

| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL | ID unique |
| date | DATE | Date de la collecte |
| platform | VARCHAR(20) | Plateforme |
| version_name | VARCHAR(255) | Nom de la version |
| version_number | VARCHAR(255) | Numéro de version |
| downloads | INTEGER | Téléchargements de cette version |
| date_published | TIMESTAMP | Date de publication |
| created_at | TIMESTAMP | Date de création de l'entrée |

### 3. `modpack_stats` - Statistiques des Modpacks

| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL | ID unique |
| date | DATE | Date de la collecte |
| platform | VARCHAR(20) | Plateforme |
| modpack_name | VARCHAR(255) | Nom du modpack |
| modpack_slug | VARCHAR(255) | Slug du modpack |
| downloads | INTEGER | Téléchargements |
| followers | INTEGER | Followers |
| created_at | TIMESTAMP | Date de création de l'entrée |

## 🔍 Requêtes SQL Utiles

### Ouvrir l'Éditeur SQL

1. Clic droit sur **`createnuclear_stats`** (database)
2. Sélectionnez **"Query Tool"**

### Exemples de Requêtes

#### 📊 Voir les dernières statistiques

```sql
-- Dernières stats globales
SELECT * FROM daily_stats 
ORDER BY date DESC 
LIMIT 10;
```

#### 📈 Téléchargements totaux par plateforme

```sql
SELECT 
    platform,
    MAX(total_downloads) as total_downloads,
    MAX(followers) as followers
FROM daily_stats
GROUP BY platform;
```

#### 🔝 Top 10 versions les plus téléchargées

```sql
SELECT 
    version_name,
    SUM(downloads) as total_downloads
FROM version_stats
WHERE platform = 'modrinth'
GROUP BY version_name
ORDER BY total_downloads DESC
LIMIT 10;
```

#### 📦 Top 10 modpacks

```sql
SELECT 
    modpack_name,
    MAX(downloads) as downloads
FROM modpack_stats
WHERE platform = 'curseforge'
GROUP BY modpack_name
ORDER BY downloads DESC
LIMIT 10;
```

#### 📅 Évolution des téléchargements (7 derniers jours)

```sql
SELECT 
    date,
    platform,
    total_downloads
FROM daily_stats
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date DESC, platform;
```

#### 🚀 Croissance quotidienne

```sql
WITH daily_growth AS (
    SELECT 
        date,
        platform,
        total_downloads,
        LAG(total_downloads) OVER (PARTITION BY platform ORDER BY date) as prev_downloads
    FROM daily_stats
)
SELECT 
    date,
    platform,
    total_downloads,
    total_downloads - COALESCE(prev_downloads, 0) as growth
FROM daily_growth
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date DESC;
```

## 🛠️ Fonctionnalités Utiles

### Exporter des Données

1. Exécutez une requête
2. Dans les résultats, cliquez sur **"Download as CSV"** (icône disquette)

### Voir le Diagramme ER

1. Clic droit sur **`createnuclear_stats`**
2. **"Generate ERD"** (Entity Relationship Diagram)
3. Visualisation graphique des relations entre tables

### Voir les Index

1. Expand **`Tables → [nom_table] → Indexes`**
2. Voir les index créés pour optimiser les performances

### Historique des Requêtes

1. **Tools → Query History**
2. Voir toutes vos requêtes précédentes

## ⚙️ Configuration Avancée

### Changer le Port pgAdmin

Éditez `.env` :
```bash
PGADMIN_PORT=5050  # Changez si le port est déjà utilisé
```

Puis redémarrez :
```bash
docker-compose restart pgadmin
```

### Changer les Identifiants

Éditez `.env` :
```bash
PGADMIN_EMAIL=votre.email@example.com
PGADMIN_PASSWORD=votre_mot_de_passe_secure
```

Puis recréez le conteneur :
```bash
docker-compose up -d --force-recreate pgadmin
```

## 🐛 Dépannage

### Impossible de se connecter à pgAdmin

```bash
# Vérifier que le service tourne
docker-compose ps pgadmin

# Voir les logs
docker-compose logs pgadmin

# Redémarrer
docker-compose restart pgadmin
```

### "Could not connect to server"

Vérifiez les paramètres de connexion :
- **Host** : Doit être `postgres` (pas `localhost`)
- **Port** : Doit être `5432` (port interne Docker)
- **Username/Password** : Vérifiez dans votre `.env`

### Les tables n'apparaissent pas

```bash
# Vérifier que les tables existent
docker-compose exec postgres psql -U createnuclear -d createnuclear_stats -c "\dt"

# Initialiser la base si nécessaire
docker-compose exec streamlit-app python scripts/init_db.py
```

## 🎯 Workflow Recommandé

### Exploration Quotidienne

1. **Ouvrir pgAdmin** → http://localhost:5050
2. **Aller dans Query Tool**
3. **Vérifier les dernières données** :
   ```sql
   SELECT * FROM daily_stats ORDER BY date DESC LIMIT 5;
   ```

### Analyse Approfondie

1. **Utiliser les requêtes SQL** pour des analyses personnalisées
2. **Exporter en CSV** pour Excel/Google Sheets
3. **Créer des vues** pour des requêtes récurrentes

### Maintenance

1. **Vérifier la taille de la base** :
   ```sql
   SELECT pg_size_pretty(pg_database_size('createnuclear_stats'));
   ```

2. **Voir l'espace par table** :
   ```sql
   SELECT 
       relname AS table_name,
       pg_size_pretty(pg_total_relation_size(relid)) AS total_size
   FROM pg_catalog.pg_statio_user_tables
   ORDER BY pg_total_relation_size(relid) DESC;
   ```

## 💡 Conseils

1. **Sauvegardez vos requêtes fréquentes** dans des fichiers `.sql`
2. **Utilisez les favoris** pour accéder rapidement aux tables
3. **Activez l'auto-complétion** dans les paramètres
4. **Créez des vues SQL** pour les requêtes complexes répétitives

## 🔒 Sécurité

- ✅ pgAdmin n'est accessible que localement (localhost:5050)
- ✅ Changez le mot de passe par défaut en production
- ✅ Les données sont isolées dans le réseau Docker
- ⚠️ Ne pas exposer le port 5050 publiquement

## 📚 Ressources

- **Documentation pgAdmin** : https://www.pgadmin.org/docs/
- **Documentation PostgreSQL** : https://www.postgresql.org/docs/
- **Tutoriels SQL** : https://www.postgresql.org/docs/current/tutorial.html

---

**Accès Rapide** : 🌐 http://localhost:5050
