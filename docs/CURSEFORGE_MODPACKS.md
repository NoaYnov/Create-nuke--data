# 📦 Configuration des Modpacks CurseForge

## Pourquoi ce fichier ?

CurseForge Legacy bloque l'accès automatique à la page "Dependents" avec une erreur 403 Forbidden. Pour contourner ce problème, vous pouvez maintenir manuellement la liste des modpacks qui utilisent Create Nuclear.

## 📝 Format du fichier

Le fichier `curseforge_modpacks.json` contient une liste JSON de modpacks :

```json
[
  {
    "name": "Nom du Modpack",
    "slug": "nom-du-modpack",
    "link": "https://www.curseforge.com/minecraft/modpacks/nom-du-modpack"
  }
]
```

### Champs

- **name** *(obligatoire)* : Le nom affiché du modpack
- **slug** *(obligatoire)* : L'identifiant URL du modpack (dernière partie de l'URL)
- **link** *(obligatoire)* : L'URL complète vers le modpack sur CurseForge
- **downloads** *(optionnel)* : Nombre de téléchargements (si disponible)

## 🔍 Comment trouver les modpacks ?

### Méthode 1 : Page Dependents (manuelle)
1. Allez sur https://legacy.curseforge.com/minecraft/mc-mods/createnuclear/relations/dependents
2. Consultez la liste des modpacks affichés
3. Pour chaque modpack :
   - Copiez le nom
   - Extrayez le slug depuis l'URL
   - Copiez l'URL complète

### Méthode 2 : Recherche CurseForge
1. Allez sur https://www.curseforge.com/minecraft/modpacks
2. Utilisez la barre de recherche avec "Create Nuclear" ou "Create"
3. Parcourez les résultats et identifiez les modpacks pertinents

### Méthode 3 : API CurseForge (avancé)
Si vous avez une clé API CurseForge, vous pouvez interroger l'API pour récupérer automatiquement les dépendances.

## ✏️ Mise à jour du fichier

### Édition locale
Modifiez directement `curseforge_modpacks.json` avec votre éditeur de texte préféré.

### Exemple d'ajout

```json
[
  {
    "name": "Create: New Age",
    "slug": "create-new-age",
    "link": "https://www.curseforge.com/minecraft/modpacks/create-new-age"
  },
  {
    "name": "All the Mods 9",
    "slug": "all-the-mods-9",
    "link": "https://www.curseforge.com/minecraft/modpacks/all-the-mods-9",
    "downloads": 5000000
  },
  {
    "name": "FTB NeoTech",
    "slug": "ftb-neotech",
    "link": "https://www.curseforge.com/minecraft/modpacks/ftb-neotech"
  }
]
```

## 🔄 Rechargement

Après modification du fichier :

1. **Sans Docker** : Rechargez simplement la page Streamlit (le cache se réinitialise après 1h)
2. **Avec Docker** : Redémarrez le conteneur
   ```bash
   docker-compose restart streamlit-app
   ```

## 🚨 Validation JSON

Assurez-vous que votre JSON est valide :
- Utilisez un validateur en ligne : https://jsonlint.com/
- Vérifiez les virgules (pas de virgule après le dernier élément)
- Vérifiez les guillemets doubles `"` (pas simples `'`)
- Vérifiez les accolades et crochets

## 💡 Conseils

### Priorité des modpacks
Listez les modpacks les plus populaires en premier pour un meilleur affichage dans le dashboard.

### Téléchargements
Si vous connaissez le nombre de téléchargements, ajoutez-le pour obtenir un graphique plus informatif :
```json
{
  "name": "Popular Modpack",
  "slug": "popular-modpack",
  "link": "https://www.curseforge.com/minecraft/modpacks/popular-modpack",
  "downloads": 1250000
}
```

### Maintenance régulière
- ⏰ Mettez à jour la liste tous les mois
- 🔍 Recherchez les nouveaux modpacks populaires
- 🗑️ Retirez les modpacks obsolètes

## 🔧 Fallback

Si le fichier `curseforge_modpacks.json` n'existe pas ou est invalide, l'application utilisera une liste par défaut codée en dur avec quelques modpacks populaires.

## 📊 Affichage dans le dashboard

Les modpacks configurés apparaîtront dans l'onglet **🔥 CurseForge** sous la section **📦 Modpacks incluant Create Nuclear** avec :
- Un graphique des top modpacks (si downloads disponibles)
- Un tableau complet avec liens cliquables
- Une indication que les données proviennent de la configuration manuelle

---

**Note** : Cette solution est temporaire en attendant une alternative au scraping de CurseForge Legacy (ex: API officielle avec accès aux dépendances).
