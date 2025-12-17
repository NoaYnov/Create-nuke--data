# Collecte Automatique de Données

## 📋 Vue d'ensemble

Le système collecte automatiquement les données **toutes les 24 heures** via un service dédié qui tourne en continu dans Docker.

## ⚙️ Configuration

### Intervalle de Collecte

L'intervalle est défini dans le fichier `.env` :

```bash
# 86400 secondes = 24 heures
COLLECTION_INTERVAL=86400
```

### Valeurs Communes

| Intervalle | Secondes | Description |
|-----------|----------|-------------|
| 1 heure | 3600 | Pour tests/développement |
| 6 heures | 21600 | Collecte fréquente |
| 12 heures | 43200 | Deux fois par jour |
| **24 heures** | **86400** | **Recommandé (défaut)** |

## 🚀 Services Automatiques

### 1. Stats Collector (`stats-collector`)

Service Docker qui :
- ✅ Démarre automatiquement avec `docker-compose up`
- ✅ Collecte les données toutes les 24h
- ✅ Sauvegarde dans PostgreSQL
- ✅ Redémarre automatiquement en cas d'erreur
- ✅ Attend 30 secondes au démarrage (pour PostgreSQL)

### 2. Ce qui est Collecté

À chaque cycle, le système collecte :

1. **Modrinth**
   - Statistiques globales (téléchargements, followers, versions)
   - Statistiques par version

2. **CurseForge** (si API key configurée)
   - Statistiques globales
   - Statistiques par version
   - Liste des modpacks utilisant le mod

3. **Sauvegarde**
   - Toutes les données → PostgreSQL
   - Modpacks → CSV backup

## 📊 Vérifier la Collecte Automatique

### Voir les Logs du Collecteur

```bash
# Logs en temps réel
docker-compose logs -f stats-collector

# Dernières 50 lignes
docker-compose logs --tail=50 stats-collector
```

### Vérifier le Statut

```bash
# Voir si le service tourne
docker-compose ps stats-collector

# Devrait afficher "Up"
```

### Vérifier les Données dans PostgreSQL

```bash
# Voir les dernières collectes
docker-compose exec postgres psql -U createnuclear -d createnuclear_stats -c "
SELECT 
    date, 
    platform, 
    total_downloads, 
    followers, 
    versions_count 
FROM daily_stats 
ORDER BY date DESC 
LIMIT 10;
"
```

## 🔄 Modifier l'Intervalle de Collecte

### Option 1 : Via le fichier .env (Recommandé)

1. Créer/éditer le fichier `.env` :
```bash
# Copier le template
cp .env.example .env

# Éditer avec votre intervalle préféré
COLLECTION_INTERVAL=86400  # 24 heures
```

2. Redémarrer le service :
```bash
docker-compose restart stats-collector
```

### Option 2 : Directement dans docker-compose.yml

Éditer la ligne dans `docker-compose.yml` :
```yaml
- COLLECTION_INTERVAL=${COLLECTION_INTERVAL:-86400}
```

## 🎯 Forcer une Collecte Immédiate

Plusieurs options :

### Option 1 : Via le Dashboard Streamlit
1. Ouvrir http://localhost:8501
2. Cliquer sur le bouton **"🔄 Run Data Collection"** dans la sidebar

### Option 2 : Via Docker (Manuel)
```bash
docker-compose exec stats-collector python src/collectors/collect_stats.py
```

### Option 3 : Redémarrer le Collecteur
```bash
# Le collecteur lance une collecte immédiate au démarrage
# (après 30s d'attente)
docker-compose restart stats-collector
```

## 📅 Planification

### Heure de Collecte

Le collecteur utilise le fuseau horaire **UTC**. La première collecte démarre :
- 30 secondes après le démarrage du conteneur
- Puis répète toutes les 24h (ou selon votre intervalle)

### Exemple de Planning

Si vous démarrez les conteneurs à **10:00 UTC** :
- Première collecte : **10:00:30 UTC**
- Deuxième collecte : **10:00:30 UTC** (lendemain)
- Troisième collecte : **10:00:30 UTC** (surlendemain)

## 🔧 Dépannage

### Le collecteur ne démarre pas

```bash
# Vérifier les logs d'erreur
docker-compose logs stats-collector

# Vérifier que PostgreSQL est prêt
docker-compose ps postgres
```

### Les données ne sont pas collectées

```bash
# Vérifier si le service tourne
docker-compose ps stats-collector

# Vérifier les logs
docker-compose logs --tail=100 stats-collector

# Vérifier la connexion à PostgreSQL
docker-compose exec streamlit-app python scripts/init_db.py
```

### Changer l'intervalle ne fonctionne pas

```bash
# Reconstruire et redémarrer
docker-compose up -d --build stats-collector

# Vérifier la variable d'environnement
docker-compose exec stats-collector env | grep COLLECTION_INTERVAL
```

## 📈 Monitoring

### Voir les Statistiques de Collecte

```bash
# Nombre de collectes par plateforme
docker-compose exec postgres psql -U createnuclear -d createnuclear_stats -c "
SELECT 
    platform,
    COUNT(*) as collectes,
    MIN(date) as premiere_collecte,
    MAX(date) as derniere_collecte
FROM daily_stats
GROUP BY platform;
"
```

### Graphique de Croissance

Les données historiques sont visibles dans le dashboard Streamlit :
- http://localhost:8501 → Onglet "Modrinth" ou "CurseForge"
- Graphiques de téléchargements au fil du temps

## 🎉 Avantages

✅ **Automatique** - Aucune intervention manuelle
✅ **Fiable** - Redémarrage automatique en cas d'erreur
✅ **Historique** - Toutes les données dans PostgreSQL
✅ **Flexible** - Intervalle personnalisable
✅ **Monitoring** - Logs détaillés disponibles

## 💡 Conseils

1. **Intervalle recommandé** : 24h est optimal pour éviter de surcharger les API
2. **Backup** : Les données PostgreSQL sont dans un volume Docker persistant
3. **API Limits** : Respectez les limites des API (Modrinth, CurseForge)
4. **Surveillance** : Vérifiez les logs régulièrement au début

## 🔐 Sécurité

- Les clés API sont dans le fichier `.env` (non versionné)
- PostgreSQL utilise l'authentification par mot de passe
- Les services communiquent via un réseau Docker privé
