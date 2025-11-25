# Create Nuclear - Statistiques

Application Streamlit interactive pour visualiser et analyser les statistiques de votre mod Create Nuclear sur **Modrinth** et **CurseForge**.

## 🎯 Fonctionnalités

### Deux plateformes en un
- **🟢 Onglet Modrinth** : statistiques complètes Modrinth
- **🔥 Onglet CurseForge** : statistiques complètes CurseForge

### Dashboard interactif
- 📊 Cartes de statistiques en temps réel
- 📈 Graphiques interactifs avec Plotly
- 🔄 Rafraîchissement des données
- 📥 Export JSON et CSV

### Statistiques disponibles
- Téléchargements totaux et par version
- Évolution temporelle des téléchargements
- Répartition par version Minecraft
- Analyse détaillée de chaque version
- Modpacks incluant le mod (Modrinth)

## 📦 Installation

1. Installez les dépendances :
```powershell
pip install -r requirements.txt
```

2. (Optionnel) Configurez la clé API CurseForge :
   - Obtenez une clé sur https://console.curseforge.com/
   - Éditez `.streamlit/secrets.toml` et ajoutez votre clé

## 🚀 Utilisation

### Application Streamlit (Recommandé)

Lancez l'application web interactive :
```powershell
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur avec :
- Bannière Create Nuclear
- Deux onglets (Modrinth et CurseForge)
- Graphiques interactifs
- Export de données

### Script Python (Alternative)

Pour un rapport en console (Modrinth uniquement) :
```powershell
python main.py
```

## 📊 Graphiques disponibles

1. **Évolution cumulée** : progression des téléchargements dans le temps
2. **Top versions** : les 10 versions les plus populaires
3. **Versions Minecraft** : répartition par version du jeu
4. **Top modpacks** : les modpacks incluant votre mod (Modrinth)

## 🔧 API Modrinth

Le script utilise l'API publique Modrinth v2 :
- Pas besoin de token d'authentification
- Limite : 300 requêtes/minute
- Documentation : https://docs.modrinth.com/api

## 📝 Notes

- La recherche de modpacks peut prendre quelques minutes
- Les données sont récupérées en temps réel
- Les graphiques sont sauvegardés en haute résolution (300 DPI)
