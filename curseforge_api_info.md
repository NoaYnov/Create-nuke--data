# Guide API CurseForge pour "Create Nuclear"

## 1. URL de base de l'API
```
https://api.curseforge.com
```

## 2. Comment obtenir une clé API

### Processus de demande :
1. Remplir le formulaire de demande : https://forms.monday.com/forms/dce5ccb7afda9a1c21dab1a1aa1d84eb?r=use1
2. Accepter les conditions d'utilisation : https://support.curseforge.com/en/support/solutions/articles/9000207405
3. Attendre l'approbation de l'équipe Overwolf
4. La clé sera envoyée par email

### Critères d'évaluation :
- Impact sur les revenus des auteurs
- Impact sur les serveurs et CDN de CurseForge
- Consentement des auteurs pour la distribution tierce

### Documentation :
- Lien support : https://support.curseforge.com/en/support/solutions/articles/9000208346

## 3. Authentification

### Header requis :
```
x-api-key: VOTRE_CLE_API
```

### Exemple de requête :
```bash
curl -X GET https://api.curseforge.com/v1/mods/{modId} \
  -H 'Accept: application/json' \
  -H 'x-api-key: VOTRE_CLE_API'
```

## 4. Trouver l'ID du mod "Create Nuclear"

### Méthode 1 : Recherche par slug
```bash
GET https://api.curseforge.com/v1/mods/search?gameId=432&slug=createnuclear&classId=6
```

**Paramètres :**
- `gameId=432` : Minecraft
- `slug=createnuclear` : Slug du mod (visible dans l'URL)
- `classId=6` : Classe "Mods" pour Minecraft

### Méthode 2 : Recherche par nom
```bash
GET https://api.curseforge.com/v1/mods/search?gameId=432&searchFilter=Create%20Nuclear
```

### Méthode 3 : Extraire depuis l'URL
L'URL du mod est : `https://www.curseforge.com/minecraft/mc-mods/createnuclear`

**Note :** L'ID du mod n'est pas visible dans l'URL publique. Il faut utiliser l'API de recherche ou inspecter les requêtes réseau du site.

## 5. Endpoints principaux

### A. Obtenir les informations d'un mod
```bash
GET /v1/mods/{modId}
```

**Réponse inclut :**
- `id` : ID du mod
- `name` : Nom du mod
- `slug` : Slug (createnuclear)
- `summary` : Description courte
- `downloadCount` : Nombre total de téléchargements
- `dateCreated` : Date de création
- `dateModified` : Date de dernière modification
- `dateReleased` : Date de sortie
- `authors` : Liste des auteurs
- `categories` : Catégories
- `logo` : Logo du mod
- `screenshots` : Captures d'écran
- `latestFiles` : Derniers fichiers publiés
- `gamePopularityRank` : Rang de popularité

### B. Obtenir les fichiers d'un mod
```bash
GET /v1/mods/{modId}/files
```

**Paramètres optionnels :**
- `gameVersion` : Filtrer par version (ex: "1.20.1")
- `modLoaderType` : Filtrer par mod loader (0=Any, 1=Forge, 4=Fabric, etc.)
- `pageSize` : Nombre de résultats (max 50)
- `index` : Pagination

**Réponse inclut pour chaque fichier :**
- `id` : ID du fichier
- `displayName` : Nom d'affichage
- `fileName` : Nom du fichier
- `fileDate` : Date de publication
- `downloadCount` : Nombre de téléchargements
- `downloadUrl` : URL de téléchargement
- `fileLength` : Taille du fichier
- `releaseType` : Type (1=Release, 2=Beta, 3=Alpha)
- `gameVersions` : Versions de jeu supportées
- `dependencies` : Dépendances

### C. Obtenir la description d'un mod
```bash
GET /v1/mods/{modId}/description
```

Retourne la description complète en HTML.

### D. Recherche de mods
```bash
GET /v1/mods/search
```

**Paramètres importants :**
- `gameId` : 432 pour Minecraft
- `classId` : 6 pour les mods
- `searchFilter` : Texte de recherche
- `slug` : Slug du mod
- `sortField` : 1=Featured, 2=Popularity, 6=TotalDownloads, etc.
- `sortOrder` : "asc" ou "desc"
- `pageSize` : Max 50
- `index` : Pagination (max index + pageSize <= 10000)

## 6. Données statistiques disponibles

### Pour le mod :
- ✅ Nombre total de téléchargements (`downloadCount`)
- ✅ Date de création (`dateCreated`)
- ✅ Date de dernière modification (`dateModified`)
- ✅ Rang de popularité (`gamePopularityRank`)
- ✅ Nombre de "thumbs up" (`thumbsUpCount`)
- ✅ Note/Rating (`rating`)
- ✅ Statut (approuvé, actif, etc.)

### Pour chaque version/fichier :
- ✅ Nombre de téléchargements par fichier
- ✅ Date de publication
- ✅ Taille du fichier
- ✅ Versions Minecraft compatibles
- ✅ Type de release (stable/beta/alpha)
- ✅ Mod loader (Forge/Fabric/etc.)

### Informations supplémentaires :
- ✅ Liste des auteurs
- ✅ Catégories associées
- ✅ Dépendances entre mods
- ✅ Historique des versions

## 7. Limites importantes

### Pagination :
- Maximum 50 résultats par page
- Limite totale : `index + pageSize <= 10000`

### Rate limiting :
Non spécifié dans la documentation, mais à respecter selon les termes d'utilisation.

## 8. Exemple de workflow complet

### Étape 1 : Trouver l'ID du mod
```python
import requests

headers = {
    'Accept': 'application/json',
    'x-api-key': 'VOTRE_CLE_API'
}

# Recherche par slug
response = requests.get(
    'https://api.curseforge.com/v1/mods/search',
    headers=headers,
    params={
        'gameId': 432,
        'slug': 'createnuclear',
        'classId': 6
    }
)

data = response.json()
mod_id = data['data'][0]['id']
print(f"Mod ID: {mod_id}")
```

### Étape 2 : Récupérer les statistiques
```python
# Infos du mod
response = requests.get(
    f'https://api.curseforge.com/v1/mods/{mod_id}',
    headers=headers
)

mod_data = response.json()['data']
print(f"Téléchargements totaux: {mod_data['downloadCount']}")
print(f"Rang de popularité: {mod_data['gamePopularityRank']}")
```

### Étape 3 : Récupérer les fichiers
```python
# Liste des fichiers
response = requests.get(
    f'https://api.curseforge.com/v1/mods/{mod_id}/files',
    headers=headers,
    params={'pageSize': 50}
)

files = response.json()['data']
for file in files:
    print(f"{file['displayName']}: {file['downloadCount']} téléchargements")
```

## 9. Notes importantes

1. **Respect des auteurs** : L'API est conçue pour respecter les revenus et droits des créateurs de mods
2. **Termes d'utilisation** : Lire attentivement https://support.curseforge.com/en/support/solutions/articles/9000207405
3. **Distribution** : La redistribution de contenu téléchargé via l'API peut être soumise à restrictions
4. **Cache** : Considérer la mise en cache des données pour limiter les appels API
5. **Attribution** : Toujours créditer les auteurs lors de l'utilisation des données

## 10. Ressources utiles

- **Documentation complète** : https://docs.curseforge.com/rest-api/
- **Demande de clé API** : https://forms.monday.com/forms/dce5ccb7afda9a1c21dab1a1aa1d84eb?r=use1
- **Support** : https://support.curseforge.com/
- **Termes & Conditions** : https://support.curseforge.com/en/support/solutions/articles/9000207405
- **Page du mod** : https://www.curseforge.com/minecraft/mc-mods/createnuclear

## 11. ID des jeux et classes communs

### Game IDs :
- Minecraft : `432`
- World of Warcraft : `1`
- The Sims 4 : `4475`

### Class IDs pour Minecraft :
- Mods : `6`
- Modpacks : `4471`
- Resource Packs : `12`
- Worlds : `17`

### Mod Loader Types :
- Any : `0`
- Forge : `1`
- Cauldron : `2`
- LiteLoader : `3`
- Fabric : `4`
- Quilt : `5`
- NeoForge : `6`
