# Gestion des Modpacks CurseForge

## Vue d'ensemble

Le système récupère automatiquement la liste complète des modpacks qui incluent Create Nuclear depuis CurseForge Legacy.

## Fichiers

### `curseforge_modpacks.json`
Fichier JSON contenant tous les modpacks qui dépendent de Create Nuclear.

Structure:
```json
[
  {
    "name": "Nom du modpack",
    "slug": "slug-du-modpack",
    "legacy_url": "https://legacy.curseforge.com/minecraft/modpacks/...",
    "id": 123456  // Optionnel, si disponible
  }
]
```

### `fetch_modpacks.py`
Script manuel pour récupérer et enrichir la liste des modpacks.

**Utilisation:**
```bash
python fetch_modpacks.py
```

**Fonctionnalités:**
- Scrape toutes les pages de CurseForge Legacy (30+ pages)
- Utilise cloudscraper pour contourner Cloudflare
- Peut enrichir avec l'API CurseForge si clé API disponible
- Sauvegarde dans `curseforge_modpacks.json`

### `collect_stats.py`
Script de collecte automatique quotidienne.

**Fonctionnalités:**
- Collecte les statistiques Modrinth
- Collecte les statistiques CurseForge
- **Met à jour automatiquement la liste des modpacks** (ajouté automatiquement)

**Exécution:**
- Dans Docker: automatique toutes les 24h
- Manuellement: `python collect_stats.py`

## Mise à jour automatique

La liste des modpacks est mise à jour automatiquement tous les jours lors de la collecte des statistiques.

### Dans Docker

Le conteneur `stats-collector` exécute `collect_stats.py` toutes les 24 heures, ce qui:
1. Collecte les stats Modrinth
2. Collecte les stats CurseForge  
3. **Met à jour la liste des modpacks** ✨

### Manuellement

Pour forcer une mise à jour immédiate:

```bash
# Avec enrichissement API (recommandé)
python fetch_modpacks.py

# Ou via la collecte normale
python collect_stats.py
```

## Dépendances

### Requises
- `requests` - Requêtes HTTP de base
- `beautifulsoup4` - Parsing HTML
- `lxml` - Parser HTML rapide
- `cloudscraper` - Contournement Cloudflare

### Optionnelles
- `CURSEFORGE_API_KEY` - Pour enrichir avec statistiques API

## Troubleshooting

### Aucun modpack trouvé
**Cause:** cloudscraper bloqué par Cloudflare

**Solutions:**
1. Attendre quelques heures et réessayer
2. Vérifier que cloudscraper est installé: `pip install cloudscraper`
3. Le fichier existant reste utilisable (pas de perte de données)

### Liste incomplète
**Cause:** Scraping interrompu

**Solution:** Relancer `python fetch_modpacks.py`

### Pas de statistiques de téléchargement
**Cause:** Pas de clé API CurseForge

**Solution:** Définir `CURSEFORGE_API_KEY` dans l'environnement

## Performance

- **Scraping:** ~2-3 minutes pour 600 modpacks (avec délais)
- **Chargement:** < 100ms (lecture JSON)
- **Cache Streamlit:** 1 heure (évite rechargement inutile)

## Architecture

```
collect_stats.py (quotidien)
    ↓
Scrape CurseForge Legacy
    ↓
curseforge_modpacks.json (600+ modpacks)
    ↓
app.py (Streamlit)
    ↓
Affichage instantané
```

## Avantages

✅ **Rapide:** Pas de scraping en temps réel  
✅ **Fiable:** Données pré-scrapées  
✅ **Complet:** 600+ modpacks au lieu de 3  
✅ **Automatique:** Mise à jour quotidienne  
✅ **Fallback:** Garde les anciennes données si échec  

## Notes

- Le scraping respecte les délais (2s entre pages)
- Les données sont dédupliquées par slug
- Le système survit aux pannes de Cloudflare
- Les statistiques peuvent être enrichies avec l'API CurseForge
