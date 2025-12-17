# Configuration PostgreSQL avec Mot de Passe Complexe

## ✅ Configuration Actuelle

### Identifiants PostgreSQL
- **Database** : `createnuclear_stats`
- **User** : `admin`
- **Password** : `VnzEEC4*k0G*3t4&j3%hk*GjWvFCqG`
- **Port** : `5432` (interne Docker) / `5433` (exposé)

### Mot de Passe Encodé pour URL
Le mot de passe contient des caractères spéciaux qui doivent être encodés dans les URLs PostgreSQL :
- **Original** : `VnzEEC4*k0G*3t4&j3%hk*GjWvFCqG`
- **Encodé** : `VnzEEC4%2Ak0G%2A3t4%26j3%25hk%2AGjWvFCqG`

## 🔧 Fichiers Modifiés

### 1. `.env`
```bash
POSTGRES_USER=admin
POSTGRES_PASSWORD=VnzEEC4*k0G*3t4&j3%hk*GjWvFCqG
POSTGRES_PASSWORD_ENCODED=VnzEEC4%2Ak0G%2A3t4%26j3%25hk%2AGjWvFCqG
```

### 2. `docker-compose.yml`
Tous les services utilisent maintenant :
- `${POSTGRES_USER:-admin}` au lieu de `${POSTGRES_USER:-createnuclear}`
- `${POSTGRES_PASSWORD_ENCODED}` dans les DATABASE_URL

## 🌐 Connexion pgAdmin

### Sur pgadmin.createnuclear.net

**Paramètres de Connexion :**
- **Host** : `postgres` (ou l'IP du serveur Docker)
- **Port** : `5432`
- **Database** : `createnuclear_stats`
- **Username** : `admin`
- **Password** : `VnzEEC4*k0G*3t4&j3%hk*GjWvFCqG`

## 🚀 Déploiement sur Serveur

### Étape 1 : Upload des Fichiers
Uploadez les fichiers modifiés sur votre serveur :
- `.env`
- `docker-compose.yml`

### Étape 2 : Redémarrage
```bash
# Arrêter les conteneurs
docker-compose down

# IMPORTANT : Supprimer l'ancien volume si vous changez user/password
docker volume rm createnuclear_pgdata

# Redémarrer avec la nouvelle config
docker-compose up -d

# Vérifier que tout fonctionne
docker-compose ps
docker-compose logs postgres
```

### Étape 3 : Initialiser la Base
```bash
# Créer les tables
docker-compose exec streamlit-app python scripts/init_db.py

# Collecter les données
docker-compose exec streamlit-app python src/collectors/collect_stats.py
```

## 📊 Vérification

### 1. Tester la Connexion Locale
```bash
docker-compose exec postgres psql -U admin -d createnuclear_stats -c "SELECT version();"
```

### 2. Vérifier les Tables
```bash
docker-compose exec postgres psql -U admin -d createnuclear_stats -c "\dt"
```

### 3. Voir les Données
```bash
docker-compose exec postgres psql -U admin -d createnuclear_stats -c "SELECT * FROM daily_stats LIMIT 5;"
```

## 🔐 Sécurité

- ✅ Le mot de passe complexe est maintenu
- ✅ L'encodage URL évite les erreurs de parsing
- ✅ Les credentials sont dans `.env` (gitignored)
- ⚠️ N'exposez pas le port 5432/5433 publiquement

## 🐛 Dépannage

### Erreur "invalid percent-encoded token"
- ✅ **Résolu** : Utilisation de `POSTGRES_PASSWORD_ENCODED` dans `DATABASE_URL`

### Erreur "role admin does not exist"
- Supprimez le volume : `docker volume rm createnuclear_pgdata`
- Redémarrez : `docker-compose up -d`

### pgAdmin ne se connecte pas
Vérifiez :
1. Le service `postgres` est bien démarré (`docker-compose ps`)
2. Le host est `postgres` (pas `localhost`)
3. Le port est `5432` (port interne)
4. Le username est `admin`
5. Le mot de passe est correct (copier-coller depuis `.env`)

## 📝 Notes

- Le user `admin` est maintenant utilisé partout au lieu de `createnuclear`
- Le mot de passe encodé est utilisé dans les URLs de connexion
- Le mot de passe original (non encodé) est utilisé pour les variables d'environnement PostgreSQL
