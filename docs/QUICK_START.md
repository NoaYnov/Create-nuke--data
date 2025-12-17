# 🚀 Guide de Démarrage Rapide

## Prérequis

- Docker Desktop installé et en cours d'exécution
- Git (optionnel)

## Installation et Configuration

### 1️⃣ Configuration Initiale

```bash
# Copier le fichier de configuration
cp .env.example .env
```

Éditez `.env` et ajoutez :
- Un **mot de passe sécurisé** pour `POSTGRES_PASSWORD`
- Votre **clé API CurseForge** dans `CURSEFORGE_API_KEY` (optionnel)

### 2️⃣ Démarrage des Services

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier que tout fonctionne
docker-compose ps
```

Vous devriez voir 4 conteneurs **"Up"** :
- ✅ `createnuclear-postgres`
- ✅ `createnuclear-app`
- ✅ `createnuclear-onepage`
- ✅ `createnuclear-collector`

### 3️⃣ Accéder au Dashboard

Ouvrez votre navigateur :
- **Dashboard Principal** : http://localhost:8501
- **Vue Simplifiée** : http://localhost:8502

## 📊 Première Collecte de Données

### Option A : Via le Dashboard (Recommandé)

1. Ouvrez http://localhost:8501
2. Dans la sidebar, cliquez sur **"🔄 Run Data Collection"**
3. Attendez la fin de la collecte (quelques minutes)

### Option B : Via la Ligne de Commande

```bash
docker-compose exec streamlit-app python src/collectors/collect_stats.py
```

## ⏰ Collecte Automatique

**C'est déjà configuré !** Le service `stats-collector` collecte automatiquement les données **toutes les 24 heures**.

Pour vérifier :
```bash
# Voir les logs du collecteur
docker-compose logs -f stats-collector
```

## 📈 Importer des Données Existantes (Optionnel)

Si vous avez des données CSV/JSON à importer :

```powershell
# Windows PowerShell
.\scripts\import_data.ps1
```

```bash
# Linux/Mac
./scripts/import_data.sh
```

## 🔍 Vérification

### Vérifier la Base de Données

```bash
docker-compose exec streamlit-app python scripts/init_db.py
```

### Voir les Logs

```bash
# Tous les services
docker-compose logs

# Service spécifique
docker-compose logs streamlit-app
docker-compose logs stats-collector
```

## 🛑 Arrêt des Services

```bash
# Arrêter sans supprimer les données
docker-compose stop

# Arrêter et supprimer les conteneurs (garde les données)
docker-compose down

# Supprimer TOUT (conteneurs + données)
docker-compose down -v
```

## 📚 Documentation Complète

- **[AUTO_COLLECTION.md](AUTO_COLLECTION.md)** - Configuration de la collecte automatique
- **[POSTGRES_DATA.md](POSTGRES_DATA.md)** - Gestion des données PostgreSQL
- **[README.md](../README.md)** - Documentation générale du projet

## ⚙️ Configuration Avancée

### Modifier l'Intervalle de Collecte

Éditez `.env` :
```bash
# 86400 = 24 heures (défaut)
# 43200 = 12 heures
# 3600 = 1 heure (test)
COLLECTION_INTERVAL=86400
```

Puis redémarrer :
```bash
docker-compose restart stats-collector
```

### Changer les Ports

Éditez `.env` :
```bash
STREAMLIT_PORT=8501
STREAMLIT_ONEPAGE_PORT=8502
POSTGRES_PORT=5433
```

## 🐛 Problèmes Courants

### "Module not found"
```bash
# Reconstruire les conteneurs
docker-compose up -d --build
```

### "Connection refused" (PostgreSQL)
```bash
# Attendre que PostgreSQL soit prêt
docker-compose logs postgres

# Vérifier la santé
docker-compose ps postgres
```

### Les données n'apparaissent pas
```bash
# Forcer une collecte
docker-compose exec streamlit-app python src/collectors/collect_stats.py

# Vérifier la base de données
docker-compose exec streamlit-app python scripts/init_db.py
```

## 🎯 Commandes Utiles

```bash
# Redémarrer tout
docker-compose restart

# Reconstruire et redémarrer
docker-compose up -d --build

# Voir les ressources utilisées
docker stats

# Nettoyer les logs
docker-compose logs --tail=0 > /dev/null

# Backup de la base de données
docker-compose exec postgres pg_dump -U createnuclear createnuclear_stats > backup.sql
```

## ✅ Checklist de Démarrage

- [ ] Docker Desktop installé et démarré
- [ ] Fichier `.env` créé et configuré
- [ ] Services démarrés avec `docker-compose up -d`
- [ ] Tous les conteneurs affichent "Up"
- [ ] Dashboard accessible sur http://localhost:8501
- [ ] Première collecte lancée (via bouton ou script)
- [ ] Données visibles dans le dashboard

## 🎉 Vous êtes Prêt !

Le système collecte maintenant automatiquement les données toutes les 24 heures et les stocke dans PostgreSQL !

Pour toute question, consultez la documentation ou vérifiez les logs.
