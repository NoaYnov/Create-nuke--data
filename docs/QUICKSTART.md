# 🚀 Guide de Démarrage Rapide

## Prérequis

- Docker et Docker Compose installés
- Git (pour cloner le projet)

## Installation en 5 Minutes

### 1. Cloner le Projet

```bash
git clone <votre-repo>
cd Create-nuke--data
```

### 2. Configuration

Copier et éditer le fichier de configuration :

```bash
# Windows PowerShell
copy .env.example .env
notepad .env

# Linux/Mac
cp .env.example .env
nano .env
```

**Minimum requis dans `.env`:**

```env
POSTGRES_PASSWORD=VotreMotDePasseSecurise123!
CURSEFORGE_API_KEY=votre_cle_api
```

### 3. Démarrer les Services

```bash
# Construire et démarrer tous les services
docker-compose up -d

# Vérifier que tout fonctionne
docker-compose ps
```

Vous devriez voir tous les services "Up" :

```
NAME                        STATUS
createnuclear-postgres      Up (healthy)
createnuclear-app           Up
createnuclear-onepage       Up
createnuclear-collector     Up
```

### 4. Accéder aux Applications

- **Application principale**: http://localhost:8501
- **Vue simplifiée**: http://localhost:8502

### 5. Vérifier la Base de Données

```bash
# Accéder à PostgreSQL
docker-compose exec postgres psql -U createnuclear -d createnuclear_stats

# Dans psql, vérifier les tables
\dt

# Quitter
\q
```

## Commandes Utiles

### Gestion des Services

```bash
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Redémarrer
docker-compose restart

# Voir les logs
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f postgres
docker-compose logs -f streamlit-app
```

### Base de Données

```bash
# Accéder à PostgreSQL
docker-compose exec postgres psql -U createnuclear -d createnuclear_stats

# Sauvegarder
python scripts/backup.py

# Initialiser/Vérifier
python scripts/init_db.py
```

### Collecte de Données

```bash
# Collecter manuellement
docker-compose exec stats-collector python collect_stats.py

# Voir les logs du collecteur
docker-compose logs -f stats-collector
```

## Troubleshooting

### Le service PostgreSQL ne démarre pas

```bash
# Vérifier les logs
docker-compose logs postgres

# Recréer le volume
docker-compose down -v
docker-compose up -d
```

### Erreur de connexion à la base de données

```bash
# Vérifier que PostgreSQL est prêt
docker-compose exec postgres pg_isready -U createnuclear

# Vérifier les variables d'environnement
docker-compose exec streamlit-app env | grep DATABASE
```

### L'application Streamlit ne charge pas

```bash
# Redémarrer l'application
docker-compose restart streamlit-app

# Vérifier les logs
docker-compose logs streamlit-app
```

## Prochaines Étapes

1. Consulter la [documentation complète](docs/DATABASE.md)
2. Configurer les sauvegardes automatiques
3. Personnaliser les intervalles de collecte
4. Explorer l'architecture dans [ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Support

Pour plus d'aide, consultez :
- [Documentation de déploiement](docs/DATABASE.md)
- [Architecture du projet](docs/ARCHITECTURE.md)
- Les logs : `docker-compose logs`
