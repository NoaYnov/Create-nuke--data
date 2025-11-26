# Create Nuclear Statistics Dashboard

Dashboard moderne et professionnel pour suivre les statistiques du mod Create Nuclear sur Modrinth et CurseForge.

## 🏗️ Architecture Refactorisée

### Structure Modulaire Professionnelle

```
├── config.py                # ⚙️ Configuration centralisée
├── api_clients.py           # 🔌 Clients API (classes ModrinthClient, CurseForgeClient)
├── modpack_manager.py       # 📦 Gestionnaire de modpacks (classe ModpackManager)
├── scraper.py               # 🕷️ Scraper CurseForge Legacy (classe CurseForgeScraper)
├── database.py              # 💾 ORM PostgreSQL
├── collect_stats.py         # 📊 Collecteur (classe StatsCollector)
├── streamlit_app.py         # 🎨 Interface utilisateur
└── curseforge_modpacks.csv  # 📄 Base CSV des modpacks (600+)
```

## 🚀 Démarrage Rapide

```bash
docker-compose up -d --build
# → http://localhost:8501
```

## 🎯 Fonctionnalités

✅ **600+ modpacks** chargés depuis CSV  
✅ **IDs CurseForge** pour chaque modpack  
✅ **Nombre de downloads** par modpack  
✅ **Mise à jour automatique** quotidienne  
✅ **Recherche et filtres** avancés  
✅ **Architecture modulaire** avec classes  
✅ **Code organisé** et maintenable  

## 📊 Dashboard

- **Modrinth:** Stats + versions
- **CurseForge:** Stats + 600 modpacks avec CSV
- **Database:** Historique PostgreSQL + graphiques

Voir [README complet](./DOCUMENTATION.md) pour plus de détails.
