# Create Nuclear Statistics - Dashboards

Ce projet dispose maintenant de **deux dashboards** qui tournent en parallèle :

## 🚀 Dashboards Disponibles

### 1️⃣ Dashboard Principal (Multi-Tabs)
**URL:** http://localhost:8501

**Fichier:** `streamlit_app.py`

**Caractéristiques:**
- Architecture modulaire avec 3 tabs
- Tab Modrinth: Analytics détaillés avec graphiques interactifs
- Tab CurseForge: Stats et modpacks ecosystem complet
- Tab Database: Analyse historique avec tendances
- Design professionnel avec glassmorphism
- Sidebar avec quick stats et navigation

**Idéal pour:**
- Exploration détaillée des données
- Analyse approfondie par plateforme
- Navigation organisée par sections

---

### 2️⃣ Dashboard One-Page
**URL:** http://localhost:8502

**Fichier:** `app_onepage.py`

**Caractéristiques:**
- **Tout sur une seule page** - pas de tabs
- Vue d'ensemble globale immédiate
- **Contraste amélioré** pour meilleure visibilité:
  - Textes plus blancs (#ffffff, #d1d5db)
  - Backgrounds plus foncés et opaques
  - Bordures plus visibles
  - Métriques avec text-shadow pour effet glow
  - Boutons avec texte noir pour contraste maximal
- Sections organisées avec headers visuels
- Graphiques compacts et optimisés
- Chargement unique de toutes les données
- Design épuré et performant

**Sections:**
1. 📊 Global Overview (6 métriques clés)
2. 🟢 Modrinth Analytics (Top 8 versions + distribution + tableau)
3. 📈 Historical Trends (30 jours Modrinth + CurseForge)
4. 📦 Modpacks Ecosystem (Top 10 chart + tableau complet)

**Idéal pour:**
- Vue d'ensemble rapide
- Présentation/démo
- Monitoring en temps réel
- Affichage sur écran externe

---

## 🎨 Améliorations de Contraste (One-Page)

### Changements visuels pour meilleure lisibilité:

1. **Textes:**
   - Primary: `#ffffff` (blanc pur)
   - Secondary: `#d1d5db` (gris très clair)
   - Muted: `#9ca3af` (gris moyen)

2. **Backgrounds:**
   - Plus opaques: `rgba(31, 41, 55, 0.95)` au lieu de 0.6-0.7
   - Gradient plus foncé: `#0d1117 → #161b22 → #1f2937`

3. **Bordures:**
   - Plus visibles: `rgba(255, 255, 255, 0.1)` au lieu de 0.05
   - Accent cyan plus lumineux: `#0ef` au lieu de `#00e5ff`

4. **Effets:**
   - Text-shadow sur les titres pour effet glow
   - Box-shadow plus prononcées
   - Hover states plus contrastés

5. **Boutons:**
   - Texte noir (`#000000`) sur gradient cyan/purple
   - Meilleure lisibilité garantie

6. **Tableaux:**
   - Headers avec background plus foncé (`#1f2937, #374151`)
   - Séparation plus claire entre lignes
   - Hover avec glow cyan

---

## 🐳 Docker

Les deux applications tournent **simultanément** dans des containers séparés:

```yaml
services:
  streamlit-app:        # Port 8501 - Dashboard principal
  streamlit-onepage:    # Port 8502 - Dashboard one-page
  stats-collector:      # Collecteur de stats
  postgres:            # Base de données
```

**Commandes:**
```bash
# Démarrer tout
docker-compose up -d

# Rebuild et démarrer
docker-compose up -d --build

# Arrêter tout
docker-compose down

# Voir les logs
docker logs createnuclear-app        # Dashboard principal
docker logs createnuclear-onepage   # Dashboard one-page
```

---

## 📊 Choix du Dashboard

**Utilisez le Dashboard Principal si:**
- Vous voulez explorer en détail chaque plateforme
- Vous avez besoin de tous les tableaux de données
- Vous préférez une navigation organisée par tabs
- Vous faites une analyse approfondie

**Utilisez le Dashboard One-Page si:**
- Vous voulez une vue d'ensemble rapide
- Vous faites une présentation/démo
- Vous avez besoin de voir toutes les infos d'un coup d'œil
- Vous préférez le scrolling aux tabs
- Vous voulez un contraste maximal pour la lisibilité

---

## 🔄 Mise à jour

Les deux dashboards partagent les mêmes:
- Modules backend (`api_clients.py`, `database.py`, etc.)
- Configuration (`config.py`)
- Cache Streamlit (TTL configurable)
- Base de données PostgreSQL

**Aucune duplication de code backend** - seule l'interface diffère !

---

## 🎯 Prochaines Étapes

1. ✅ Dashboard principal opérationnel
2. ✅ Dashboard one-page créé avec meilleur contraste
3. ✅ Les deux tournent en parallèle
4. 🔄 Testez les deux et choisissez votre préféré !

**Bon monitoring !** 📊⚛️
