# 📘 Guide de Référence Rapide

## 🚀 Commandes Essentielles

### Démarrage et Arrêt

```bash
# Démarrer tous les services
docker-compose up -d

# Démarrer en mode développement (avec logs)
docker-compose up

# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes (⚠️ PERTE DE DONNÉES)
docker-compose down -v

# Redémarrer tous les services
docker-compose restart

# Redémarrer un service spécifique
docker-compose restart streamlit-app
docker-compose restart postgres
docker-compose restart stats-collector
```

### Logs et Monitoring

```bash
# Voir tous les logs
docker-compose logs

# Logs en temps réel
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f postgres
docker-compose logs -f streamlit-app
docker-compose logs -f stats-collector

# Dernières 100 lignes
docker-compose logs --tail=100

# Statistiques de ressources
docker stats
```

### État des Services

```bash
# Voir l'état de tous les services
docker-compose ps

# Voir les processus en cours
docker-compose top

# Vérifier la santé de PostgreSQL
docker-compose exec postgres pg_isready -U createnuclear
```

---

## 🗄️ Base de Données

### Accès PostgreSQL

```bash
# Accéder au shell PostgreSQL
docker-compose exec postgres psql -U createnuclear -d createnuclear_stats

# Exécuter une commande SQL
docker-compose exec postgres psql -U createnuclear -d createnuclear_stats -c "SELECT COUNT(*) FROM daily_stats;"

# Lister les bases de données
docker-compose exec postgres psql -U createnuclear -l

# Lister les tables
docker-compose exec postgres psql -U createnuclear -d createnuclear_stats -c "\dt"
```

### Commandes SQL Utiles

```sql
-- Dans psql (après docker-compose exec postgres psql ...)

-- Lister les tables
\dt

-- Décrire une table
\d daily_stats

-- Voir les index
\di

-- Taille de la base de données
SELECT pg_size_pretty(pg_database_size('createnuclear_stats'));

-- Nombre d'enregistrements par table
SELECT 'daily_stats' as table, COUNT(*) FROM daily_stats
UNION ALL
SELECT 'version_stats', COUNT(*) FROM version_stats
UNION ALL
SELECT 'modpack_stats', COUNT(*) FROM modpack_stats;

-- Dernières statistiques
SELECT date, platform, total_downloads, followers 
FROM daily_stats 
ORDER BY date DESC 
LIMIT 10;

-- Statistiques par plateforme
SELECT platform, COUNT(*) as days, MAX(total_downloads) as max_downloads
FROM daily_stats
GROUP BY platform;

-- Quitter psql
\q
```

### Sauvegarde et Restauration

```bash
# Sauvegarder (avec script Python)
python scripts/backup.py

# Sauvegarder (manuel)
docker-compose exec postgres pg_dump -U createnuclear createnuclear_stats > backup.sql

# Sauvegarder avec compression
docker-compose exec postgres pg_dump -U createnuclear createnuclear_stats | gzip > backup.sql.gz

# Restaurer (avec script Python)
python scripts/restore.py

# Restaurer (manuel)
cat backup.sql | docker-compose exec -T postgres psql -U createnuclear createnuclear_stats

# Restaurer depuis fichier compressé
gunzip -c backup.sql.gz | docker-compose exec -T postgres psql -U createnuclear createnuclear_stats
```

### Migrations

```bash
# Voir l'état des migrations
python scripts/migrate.py status

# Appliquer les migrations
python scripts/migrate.py up

# Annuler la dernière migration
python scripts/migrate.py down

# Initialiser/vérifier la base
python scripts/init_db.py
```

---

## 📊 Collecte de Données

### Collecte Manuelle

```bash
# Collecter immédiatement
docker-compose exec stats-collector python collect_stats.py

# Voir les logs du collecteur
docker-compose logs -f stats-collector

# Redémarrer le collecteur
docker-compose restart stats-collector
```

### Configuration de la Collecte

Modifier dans `.env`:

```env
# Intervalle en secondes
COLLECTION_INTERVAL=21600  # 6 heures (défaut)
COLLECTION_INTERVAL=43200  # 12 heures
COLLECTION_INTERVAL=86400  # 24 heures
```

Puis redémarrer:

```bash
docker-compose restart stats-collector
```

---

## 🔧 Maintenance

### Nettoyage

```bash
# Nettoyer les images inutilisées
docker system prune

# Nettoyer tout (⚠️ attention)
docker system prune -a

# Nettoyer les volumes non utilisés
docker volume prune

# Voir l'espace utilisé
docker system df
```

### Optimisation PostgreSQL

```sql
-- Dans psql

-- Analyser les tables
ANALYZE daily_stats;
ANALYZE version_stats;
ANALYZE modpack_stats;

-- Vacuum (récupérer l'espace)
VACUUM;

-- Vacuum complet (plus lent mais plus efficace)
VACUUM FULL;

-- Réindexer
REINDEX TABLE daily_stats;
REINDEX TABLE version_stats;
REINDEX TABLE modpack_stats;

-- Statistiques de cache
SELECT 
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit) as heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;
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

## 🐛 Dépannage

### PostgreSQL ne démarre pas

```bash
# Voir les logs
docker-compose logs postgres

# Vérifier le volume
docker volume inspect createnuclear_pgdata

# Recréer le volume (⚠️ PERTE DE DONNÉES)
docker-compose down -v
docker-compose up -d
```

### Erreur de connexion

```bash
# Vérifier que PostgreSQL est prêt
docker-compose exec postgres pg_isready -U createnuclear

# Vérifier les variables d'environnement
docker-compose exec streamlit-app env | grep DATABASE

# Tester la connexion
docker-compose exec streamlit-app python -c "from database import StatsDatabase; db = StatsDatabase(); print('OK')"
```

### Application Streamlit ne charge pas

```bash
# Redémarrer l'application
docker-compose restart streamlit-app

# Voir les logs
docker-compose logs streamlit-app

# Vérifier le healthcheck
docker-compose exec streamlit-app curl -f http://localhost:8501/_stcore/health
```

### Collecteur ne fonctionne pas

```bash
# Voir les logs
docker-compose logs stats-collector

# Tester manuellement
docker-compose exec stats-collector python collect_stats.py

# Vérifier les variables d'environnement
docker-compose exec stats-collector env | grep -E "(DATABASE|CURSEFORGE)"
```

### Espace disque plein

```bash
# Voir l'utilisation
docker system df

# Nettoyer les images
docker image prune -a

# Nettoyer les conteneurs arrêtés
docker container prune

# Nettoyer tout
docker system prune -a --volumes
```

---

## 🔐 Sécurité

### Changer le mot de passe PostgreSQL

1. Modifier `.env`:
```env
POSTGRES_PASSWORD=NouveauMotDePasse123!
```

2. Recréer les services:
```bash
docker-compose down
docker-compose up -d
```

### Vérifier les permissions

```sql
-- Dans psql

-- Voir les utilisateurs
\du

-- Voir les permissions sur une table
\dp daily_stats

-- Voir les bases de données et propriétaires
\l
```

---

## 📈 Production

### Déployer en production

```bash
# Utiliser le fichier de production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Vérifier
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

# Logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
```

### Sauvegardes automatiques (Cron)

```bash
# Éditer crontab
crontab -e

# Ajouter (sauvegarde quotidienne à 2h)
0 2 * * * cd /chemin/vers/projet && python scripts/backup.py >> /var/log/backup.log 2>&1

# Vérifier les tâches cron
crontab -l
```

### Monitoring

```bash
# Statistiques en temps réel
docker stats

# Logs avec rotation
docker-compose logs --tail=1000 > logs/app-$(date +%Y%m%d).log

# Vérifier la santé
docker-compose ps
curl http://localhost:8501/_stcore/health
```

---

## 📚 Ressources

### URLs Importantes

- **Application principale**: http://localhost:8501
- **Vue simplifiée**: http://localhost:8502
- **PostgreSQL**: localhost:5432

### Documentation

- [Guide de démarrage rapide](QUICKSTART.md)
- [Documentation PostgreSQL](DATABASE.md)
- [Architecture du projet](ARCHITECTURE.md)
- [README principal](../README.md)

### Fichiers de Configuration

- `.env` - Variables d'environnement
- `docker-compose.yml` - Configuration Docker
- `docker-compose.prod.yml` - Configuration production
- `config.py` - Configuration application

---

## 💡 Astuces

### Alias Utiles

Ajouter dans votre `.bashrc` ou `.zshrc`:

```bash
# Alias pour docker-compose
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dcp='docker-compose ps'

# Alias pour PostgreSQL
alias pgcli='docker-compose exec postgres psql -U createnuclear -d createnuclear_stats'

# Alias pour les scripts
alias db-backup='python scripts/backup.py'
alias db-restore='python scripts/restore.py'
alias db-init='python scripts/init_db.py'
alias db-migrate='python scripts/migrate.py'
```

### Variables d'Environnement Utiles

```bash
# Afficher toutes les variables
docker-compose config

# Vérifier une variable spécifique
docker-compose exec streamlit-app printenv DATABASE_URL
```

### Performance

```bash
# Limiter les ressources d'un service
docker-compose up -d --scale stats-collector=0  # Désactiver le collecteur

# Voir l'utilisation des ressources
docker stats --no-stream

# Redémarrer sans downtime
docker-compose up -d --no-deps --build streamlit-app
```

---

## 🆘 Support d'Urgence

### Problème Critique

1. **Sauvegarder immédiatement**:
   ```bash
   python scripts/backup.py
   ```

2. **Capturer les logs**:
   ```bash
   docker-compose logs > emergency-logs.txt
   ```

3. **Vérifier l'état**:
   ```bash
   docker-compose ps
   docker system df
   ```

4. **Redémarrage propre**:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Contacts et Ressources

- Documentation: `docs/`
- Issues GitHub: (votre repo)
- Logs: `docker-compose logs`

---

**Dernière mise à jour**: 2025-11-27
