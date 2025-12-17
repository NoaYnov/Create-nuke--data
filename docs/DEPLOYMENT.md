# 🚀 Déploiement - Guide Complet

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Installation Rapide](#installation-rapide)
3. [Configuration](#configuration)
4. [Démarrage](#démarrage)
5. [Vérification](#vérification)
6. [Production](#production)
7. [Maintenance](#maintenance)

---

## 🔧 Prérequis

### Logiciels Requis

```bash
# Vérifier les versions
docker --version          # >= 20.10
docker-compose --version  # >= 2.0
python --version          # >= 3.10
git --version
```

### Obtenir une Clé API CurseForge

1. Aller sur [CurseForge Console](https://console.curseforge.com/)
2. Créer un compte / Se connecter
3. Créer une nouvelle API Key
4. Copier la clé (vous en aurez besoin)

---

## ⚡ Installation Rapide

### 1. Cloner le Projet

```bash
git clone <votre-repo>
cd Create-nuke--data
```

### 2. Vérifier l'Environnement

```bash
python scripts/check_env.py
```

### 3. Configuration

```bash
# Copier le template
cp .env.example .env

# Éditer (Windows)
notepad .env

# Éditer (Linux/Mac)
nano .env
```

**Minimum requis dans `.env`:**

```env
POSTGRES_PASSWORD=VotreMotDePasseSecurise123!
CURSEFORGE_API_KEY=votre_cle_api_curseforge
```

### 4. Démarrer

```bash
# Construire et démarrer
docker-compose up -d

# Vérifier
docker-compose ps
```

### 5. Accéder

- **Application**: http://localhost:8501
- **Vue simplifiée**: http://localhost:8502

---

## ⚙️ Configuration

### Variables d'Environnement Essentielles

| Variable | Description | Exemple | Requis |
|----------|-------------|---------|--------|
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | `MySecurePass123!` | ✅ |
| `CURSEFORGE_API_KEY` | Clé API CurseForge | `$2a$10$...` | ✅ |
| `POSTGRES_USER` | Utilisateur PostgreSQL | `createnuclear` | ❌ |
| `POSTGRES_DB` | Nom de la base | `createnuclear_stats` | ❌ |
| `COLLECTION_INTERVAL` | Intervalle collecte (sec) | `21600` (6h) | ❌ |

### Configuration Avancée

```env
# Ports personnalisés
POSTGRES_PORT=5432
STREAMLIT_PORT=8501
STREAMLIT_ONEPAGE_PORT=8502

# Collecte
COLLECTION_INTERVAL=21600  # 6 heures

# Environnement
ENVIRONMENT=development
DEBUG=false
```

---

## 🚀 Démarrage

### Développement

```bash
# Démarrer avec logs
docker-compose up

# Démarrer en arrière-plan
docker-compose up -d

# Reconstruire après modification
docker-compose up -d --build
```

### Production

```bash
# Utiliser la configuration production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Vérifier
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

### Services Individuels

```bash
# Démarrer seulement PostgreSQL
docker-compose up -d postgres

# Démarrer app + postgres
docker-compose up -d postgres streamlit-app

# Redémarrer un service
docker-compose restart streamlit-app
```

---

## ✅ Vérification

### 1. État des Services

```bash
# Voir tous les services
docker-compose ps

# Devrait afficher:
# NAME                        STATUS
# createnuclear-postgres      Up (healthy)
# createnuclear-app           Up
# createnuclear-onepage       Up
# createnuclear-collector     Up
```

### 2. Logs

```bash
# Tous les logs
docker-compose logs

# Logs en temps réel
docker-compose logs -f

# Logs d'un service
docker-compose logs -f postgres
```

### 3. Base de Données

```bash
# Vérifier PostgreSQL
docker-compose exec postgres pg_isready -U createnuclear

# Accéder à la base
docker-compose exec postgres psql -U createnuclear -d createnuclear_stats

# Dans psql:
\dt                          # Lister les tables
SELECT COUNT(*) FROM daily_stats;
\q                           # Quitter
```

### 4. Applications

```bash
# Tester l'application principale
curl http://localhost:8501/_stcore/health

# Tester la vue simplifiée
curl http://localhost:8502/_stcore/health
```

### 5. Collecteur

```bash
# Voir les logs du collecteur
docker-compose logs stats-collector

# Collecter manuellement
docker-compose exec stats-collector python collect_stats.py
```

---

## 🏭 Production

### Checklist de Déploiement

- [ ] Mot de passe PostgreSQL fort (min 16 caractères)
- [ ] Clé API CurseForge valide
- [ ] `.env` configuré et sécurisé
- [ ] Port 5432 non exposé publiquement
- [ ] Sauvegardes automatiques configurées
- [ ] Monitoring actif
- [ ] Logs rotatifs configurés
- [ ] Firewall configuré
- [ ] SSL/TLS configuré (si applicable)

### Déploiement Production

```bash
# 1. Vérifier la configuration
python scripts/check_env.py

# 2. Démarrer en mode production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 3. Vérifier
docker-compose ps
docker-compose logs -f

# 4. Initialiser la base
python scripts/init_db.py

# 5. Première collecte
docker-compose exec stats-collector python collect_stats.py
```

### Sauvegardes Automatiques

```bash
# Configurer cron (Linux/Mac)
crontab -e

# Ajouter:
0 2 * * * cd /chemin/vers/projet && python scripts/backup.py >> /var/log/backup.log 2>&1

# Windows Task Scheduler
# Créer une tâche planifiée qui exécute:
python C:\chemin\vers\projet\scripts\backup.py
```

### Monitoring

```bash
# Statistiques en temps réel
docker stats

# Vérifier la santé
docker-compose ps
curl http://localhost:8501/_stcore/health

# Logs avec horodatage
docker-compose logs --timestamps
```

---

## 🔧 Maintenance

### Arrêt et Redémarrage

```bash
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes (⚠️ PERTE DE DONNÉES)
docker-compose down -v

# Redémarrer
docker-compose restart

# Redémarrer un service
docker-compose restart streamlit-app
```

### Mise à Jour

```bash
# 1. Sauvegarder
python scripts/backup.py

# 2. Arrêter
docker-compose down

# 3. Mettre à jour le code
git pull

# 4. Reconstruire
docker-compose build

# 5. Démarrer
docker-compose up -d

# 6. Vérifier
docker-compose ps
docker-compose logs -f
```

### Nettoyage

```bash
# Nettoyer les images inutilisées
docker system prune

# Nettoyer tout (attention!)
docker system prune -a

# Voir l'espace utilisé
docker system df
```

### Sauvegarde et Restauration

```bash
# Sauvegarder
python scripts/backup.py

# Restaurer (interactif)
python scripts/restore.py

# Restaurer un fichier spécifique
python scripts/restore.py backups/backup_20250127_120000.sql.gz
```

---

## 🐛 Dépannage

### PostgreSQL ne démarre pas

```bash
# Voir les logs
docker-compose logs postgres

# Recréer le volume
docker-compose down -v
docker-compose up -d
```

### Application ne charge pas

```bash
# Redémarrer
docker-compose restart streamlit-app

# Voir les logs
docker-compose logs streamlit-app

# Vérifier la connexion DB
docker-compose exec streamlit-app python -c "from database import StatsDatabase; db = StatsDatabase(); print('OK')"
```

### Erreur de connexion base de données

```bash
# Vérifier PostgreSQL
docker-compose exec postgres pg_isready -U createnuclear

# Vérifier les variables
docker-compose exec streamlit-app env | grep DATABASE

# Tester la connexion
docker-compose exec postgres psql -U createnuclear -d createnuclear_stats -c "SELECT 1"
```

### Collecteur ne fonctionne pas

```bash
# Voir les logs
docker-compose logs stats-collector

# Tester manuellement
docker-compose exec stats-collector python collect_stats.py

# Vérifier les variables
docker-compose exec stats-collector env | grep -E "(DATABASE|CURSEFORGE)"
```

---

## 📊 Commandes Utiles

### Docker Compose

```bash
# État
docker-compose ps
docker-compose top

# Logs
docker-compose logs -f
docker-compose logs --tail=100 postgres

# Ressources
docker stats

# Configuration
docker-compose config
```

### PostgreSQL

```bash
# Accès
docker-compose exec postgres psql -U createnuclear -d createnuclear_stats

# Commande directe
docker-compose exec postgres psql -U createnuclear -d createnuclear_stats -c "SELECT COUNT(*) FROM daily_stats"

# Dump
docker-compose exec postgres pg_dump -U createnuclear createnuclear_stats > backup.sql
```

### Scripts

```bash
# Vérification environnement
python scripts/check_env.py

# Initialisation DB
python scripts/init_db.py

# Sauvegarde
python scripts/backup.py

# Restauration
python scripts/restore.py

# Migrations
python scripts/migrate.py status
python scripts/migrate.py up
python scripts/migrate.py down
```

---

## 📚 Documentation

- **[Guide de démarrage rapide](QUICKSTART.md)** - Installation en 5 minutes
- **[Documentation PostgreSQL](DATABASE.md)** - Guide complet de la base de données
- **[Architecture](ARCHITECTURE.md)** - Architecture détaillée du projet
- **[Référence](REFERENCE.md)** - Référence rapide des commandes
- **[Changelog](../CHANGELOG.md)** - Historique des modifications

---

## 🆘 Support

### En cas de problème

1. **Vérifier les logs**: `docker-compose logs`
2. **Consulter la documentation**: `docs/`
3. **Vérifier l'environnement**: `python scripts/check_env.py`
4. **Sauvegarder**: `python scripts/backup.py`
5. **Créer une issue** avec les détails

### Ressources

- Documentation: `docs/`
- Issues GitHub: (votre repo)
- Logs: `docker-compose logs`

---

**Dernière mise à jour**: 2025-11-27
**Version**: 2.0.0
