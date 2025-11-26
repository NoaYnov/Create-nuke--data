# Quick Start avec Docker Compose

## Lancement rapide

```bash
# Copier le fichier d'environnement
cp .env.example .env

# Modifier .env avec vos vraies valeurs si nécessaire

# Lancer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Accéder à l'app
# http://localhost:8501
```

## Services inclus

- **postgres** : Base de données PostgreSQL sur port 5432
- **streamlit-app** : Application web sur port 8501
- **stats-collector** : Collecte automatique quotidienne des stats

## Commandes utiles

```bash
# Arrêter
docker-compose down

# Arrêter et supprimer les données
docker-compose down -v

# Rebuild après modifications
docker-compose up -d --build

# Forcer la collecte maintenant
docker-compose exec stats-collector python collect_stats.py

# Voir la base de données
docker-compose exec postgres psql -U createnuclear -d createnuclear_stats
```
