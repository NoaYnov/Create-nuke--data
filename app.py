import streamlit as st
import requests
import json
from datetime import datetime, timezone
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict
import pandas as pd

# Configuration de la page
st.set_page_config(
    page_title="Create Nuclear - Statistiques",
    page_icon="☢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration Modrinth
MODRINTH_PROJECT_SLUG = "createnuclear"
MODRINTH_API_BASE = "https://api.modrinth.com/v2"
USER_AGENT = "CreateNuclear-Stats/1.0"

# Configuration CurseForge
CURSEFORGE_API_BASE = "https://api.curseforge.com"
CURSEFORGE_MOD_ID = 989797  # ID de Create Nuclear sur CurseForge
try:
    CURSEFORGE_API_KEY = st.secrets.get("CURSEFORGE_API_KEY", "")
except (FileNotFoundError, KeyError):
    CURSEFORGE_API_KEY = ""

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1bd96a;
        margin-bottom: 2rem;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1bd96a;
    }
    .stat-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .curseforge-stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #f16436;
    }
</style>
""", unsafe_allow_html=True)

# ==================== MODRINTH FUNCTIONS ====================

@st.cache_data(ttl=3600)
def get_modrinth_project_info():
    """Récupère les informations générales du projet Modrinth"""
    url = f"{MODRINTH_API_BASE}/project/{MODRINTH_PROJECT_SLUG}"
    headers = {"User-Agent": USER_AGENT}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=3600)
def get_modrinth_project_versions():
    """Récupère toutes les versions du projet Modrinth"""
    url = f"{MODRINTH_API_BASE}/project/{MODRINTH_PROJECT_SLUG}/version"
    headers = {"User-Agent": USER_AGENT}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=3600)
def search_modrinth_modpacks_with_dependency():
    """Recherche les modpacks Modrinth qui incluent ce mod"""
    url = f"{MODRINTH_API_BASE}/search"
    headers = {"User-Agent": USER_AGENT}
    params = {
        "facets": f'[["project_type:modpack"]]',
        "limit": 100
    }
    
    modpacks_with_mod = []
    project_info = get_modrinth_project_info()
    project_id = project_info['id']
    
    offset = 0
    max_checks = 200
    
    while offset < max_checks:
        params['offset'] = offset
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data['hits']:
                break
                
            for modpack in data['hits']:
                try:
                    versions_url = f"{MODRINTH_API_BASE}/project/{modpack['project_id']}/version"
                    versions_response = requests.get(versions_url, headers=headers)
                    if versions_response.status_code == 200:
                        versions = versions_response.json()
                        for version in versions:
                            if 'dependencies' in version:
                                for dep in version['dependencies']:
                                    if dep.get('project_id') == project_id:
                                        modpacks_with_mod.append({
                                            'title': modpack['title'],
                                            'slug': modpack['slug'],
                                            'downloads': modpack['downloads'],
                                            'follows': modpack['follows']
                                        })
                                        break
                except:
                    pass
            
            offset += len(data['hits'])
            if offset >= data['total_hits']:
                break
        except:
            break
    
    unique_modpacks = {mp['slug']: mp for mp in modpacks_with_mod}.values()
    return list(unique_modpacks)

# ==================== CURSEFORGE FUNCTIONS ====================

@st.cache_data(ttl=3600)
def get_curseforge_mod_info():
    """Récupère les informations du mod CurseForge"""
    if not CURSEFORGE_API_KEY:
        return None
    
    url = f"{CURSEFORGE_API_BASE}/v1/mods/{CURSEFORGE_MOD_ID}"
    headers = {"x-api-key": CURSEFORGE_API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['data']
    except Exception as e:
        st.error(f"Erreur CurseForge API: {e}")
        return None

@st.cache_data(ttl=3600)
def get_curseforge_mod_files():
    """Récupère les fichiers/versions du mod CurseForge"""
    if not CURSEFORGE_API_KEY:
        return None
    
    url = f"{CURSEFORGE_API_BASE}/v1/mods/{CURSEFORGE_MOD_ID}/files"
    headers = {"x-api-key": CURSEFORGE_API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['data']
    except Exception as e:
        st.error(f"Erreur CurseForge API: {e}")
        return None

@st.cache_data(ttl=3600)
def search_curseforge_modpacks():
    """Recherche les modpacks CurseForge qui incluent ce mod"""
    if not CURSEFORGE_API_KEY:
        return []
    
    # Récupérer les modpacks qui dépendent de notre mod
    url = f"{CURSEFORGE_API_BASE}/v1/mods/search"
    headers = {"x-api-key": CURSEFORGE_API_KEY}
    params = {
        "gameId": 432,  # Minecraft
        "classId": 4471,  # Modpacks
        "pageSize": 50
    }
    
    modpacks_with_mod = []
    
    try:
        # Rechercher les modpacks populaires
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        modpacks = response.json()['data']
        
        # Vérifier chaque modpack pour voir s'il contient notre mod
        for modpack in modpacks:
            try:
                # Récupérer les fichiers du modpack
                files_url = f"{CURSEFORGE_API_BASE}/v1/mods/{modpack['id']}/files"
                files_response = requests.get(files_url, headers=headers, params={"pageSize": 1})
                
                if files_response.status_code == 200:
                    files = files_response.json()['data']
                    if files:
                        # Vérifier les dépendances du fichier le plus récent
                        latest_file = files[0]
                        if 'dependencies' in latest_file:
                            for dep in latest_file['dependencies']:
                                if dep.get('modId') == CURSEFORGE_MOD_ID:
                                    modpacks_with_mod.append({
                                        'name': modpack['name'],
                                        'slug': modpack['slug'],
                                        'downloads': modpack['downloadCount'],
                                        'id': modpack['id']
                                    })
                                    break
            except:
                pass
        
        return modpacks_with_mod
    except Exception as e:
        st.error(f"Erreur recherche modpacks CurseForge: {e}")
        return []

# ==================== UTILITY FUNCTIONS ====================

def analyze_downloads_by_version(versions, platform="modrinth"):
    """Analyse les téléchargements par version"""
    version_stats = []
    
    for version in versions:
        if platform == "modrinth":
            version_stats.append({
                'name': version['name'],
                'version_number': version['version_number'],
                'downloads': version['downloads'],
                'date_published': version['date_published'],
                'game_versions': version['game_versions']
            })
        else:  # curseforge
            version_stats.append({
                'name': version['displayName'],
                'version_number': version['fileName'],
                'downloads': version['downloadCount'],
                'date_published': version['fileDate'],
                'game_versions': version.get('gameVersions', [])
            })
    
    version_stats.sort(key=lambda x: x['date_published'])
    return version_stats

def create_timeline_chart(version_stats, color='#1bd96a'):
    """Crée un graphique d'évolution temporelle"""
    dates = [datetime.fromisoformat(v['date_published'].replace('Z', '+00:00')) for v in version_stats]
    downloads = [v['downloads'] for v in version_stats]
    cumulative_downloads = []
    total = 0
    for d in downloads:
        total += d
        cumulative_downloads.append(total)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=cumulative_downloads,
        mode='lines+markers',
        name='Téléchargements cumulés',
        line=dict(color=color, width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Total: %{y:,}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Évolution cumulée des téléchargements",
        xaxis_title="Date de publication",
        yaxis_title="Téléchargements cumulés",
        hovermode='x unified',
        height=500,
        template="plotly_white"
    )
    
    return fig

def create_top_versions_chart(version_stats, color='#1bd96a'):
    """Crée un graphique des top versions"""
    top_versions = sorted(version_stats, key=lambda x: x['downloads'], reverse=True)[:10]
    
    fig = go.Figure(go.Bar(
        x=[v['downloads'] for v in top_versions],
        y=[f"{v['name']}" for v in top_versions],
        orientation='h',
        marker=dict(color=color),
        hovertemplate='<b>%{y}</b><br>%{x:,} téléchargements<extra></extra>'
    ))
    
    fig.update_layout(
        title="Top 10 versions",
        xaxis_title="Téléchargements",
        yaxis_title="",
        height=400,
        template="plotly_white"
    )
    
    return fig

def create_mc_versions_chart(version_stats):
    """Crée un graphique par version Minecraft"""
    mc_version_downloads = defaultdict(int)
    for version in version_stats:
        for mc_version in version['game_versions']:
            mc_version_downloads[mc_version] += version['downloads']
    
    sorted_mc_versions = sorted(mc_version_downloads.items(), key=lambda x: x[1], reverse=True)[:10]
    
    fig = go.Figure(go.Bar(
        x=[v[1] for v in sorted_mc_versions],
        y=[v[0] for v in sorted_mc_versions],
        orientation='h',
        marker=dict(color='#ff6b6b'),
        hovertemplate='<b>%{y}</b><br>%{x:,} téléchargements<extra></extra>'
    ))
    
    fig.update_layout(
        title="Top 10 versions Minecraft",
        xaxis_title="Téléchargements",
        yaxis_title="",
        height=400,
        template="plotly_white"
    )
    
    return fig

# ==================== PAGE RENDERING ====================

def render_modrinth_tab():
    """Affiche l'onglet Modrinth"""
    with st.spinner("📡 Chargement des données Modrinth..."):
        try:
            project_info = get_modrinth_project_info()
            versions = get_modrinth_project_versions()
            version_stats = analyze_downloads_by_version(versions, "modrinth")
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement des données Modrinth: {e}")
            return
    
    # Statistiques principales
    st.markdown("## 📊 Vue d'ensemble")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{project_info['downloads']:,}</div>
            <div class="stat-label">📥 Téléchargements</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{project_info['followers']:,}</div>
            <div class="stat-label">⭐ Followers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(versions)}</div>
            <div class="stat-label">📦 Versions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        days_since_creation = (datetime.now(timezone.utc) - datetime.fromisoformat(project_info['published'].replace('Z', '+00:00'))).days
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{days_since_creation}</div>
            <div class="stat-label">📅 Jours depuis création</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Description
    with st.expander("📝 Description du projet", expanded=False):
        st.markdown(project_info['description'])
        st.caption(f"**Créé le:** {project_info['published'][:10]} | **Dernière mise à jour:** {project_info['updated'][:10]}")
    
    st.markdown("---")
    
    # Graphiques
    st.markdown("## 📈 Évolution des téléchargements")
    st.plotly_chart(create_timeline_chart(version_stats, '#1bd96a'), use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📦 Téléchargements par version")
        st.plotly_chart(create_top_versions_chart(version_stats, '#1bd96a'), use_container_width=True)
    
    with col2:
        st.markdown("### 🎮 Téléchargements par version Minecraft")
        st.plotly_chart(create_mc_versions_chart(version_stats), use_container_width=True)
    
    st.markdown("---")
    
    # Tableau des versions
    st.markdown("## 📋 Détails des versions")
    df_versions = pd.DataFrame([
        {
            'Version': v['name'],
            'Numéro': v['version_number'],
            'Téléchargements': v['downloads'],
            'Date': datetime.fromisoformat(v['date_published'].replace('Z', '+00:00')).strftime('%d/%m/%Y'),
            'Versions MC': ', '.join(v['game_versions'][:3]) + ('...' if len(v['game_versions']) > 3 else '')
        }
        for v in reversed(version_stats)
    ])
    
    total_dl = df_versions['Téléchargements'].sum()
    df_versions['%'] = (df_versions['Téléchargements'] / total_dl * 100).round(1)
    
    st.dataframe(df_versions, use_container_width=True, height=400, hide_index=True)
    
    st.markdown("---")
    
    # Modpacks
    st.markdown("## 📦 Modpacks incluant Create Nuclear")
    with st.spinner("🔍 Recherche des modpacks..."):
        try:
            modpacks = search_modrinth_modpacks_with_dependency()
            
            if modpacks:
                st.success(f"✅ {len(modpacks)} modpack(s) trouvé(s)")
                modpacks_sorted = sorted(modpacks, key=lambda x: x['downloads'], reverse=True)
                
                if len(modpacks_sorted) > 0:
                    top_modpacks = modpacks_sorted[:10]
                    
                    fig = go.Figure(go.Bar(
                        x=[mp['downloads'] for mp in top_modpacks],
                        y=[mp['title'] for mp in top_modpacks],
                        orientation='h',
                        marker=dict(color='#4ecdc4'),
                        hovertemplate='<b>%{y}</b><br>%{x:,} téléchargements<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        title="Top 10 modpacks par téléchargements",
                        xaxis_title="Téléchargements du modpack",
                        yaxis_title="",
                        height=400,
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                df_modpacks = pd.DataFrame([
                    {
                        'Nom': mp['title'],
                        'Téléchargements': mp['downloads'],
                        'Followers': mp['follows'],
                        'Lien': f"https://modrinth.com/modpack/{mp['slug']}"
                    }
                    for mp in modpacks_sorted
                ])
                
                st.dataframe(
                    df_modpacks,
                    use_container_width=True,
                    height=400,
                    hide_index=True,
                    column_config={
                        "Lien": st.column_config.LinkColumn("Lien", display_text="Voir sur Modrinth")
                    }
                )
            else:
                st.info("ℹ️ Aucun modpack trouvé ou recherche limitée.")
        except Exception as e:
            st.error(f"❌ Erreur lors de la recherche: {e}")

def render_curseforge_tab():
    """Affiche l'onglet CurseForge"""
    
    if not CURSEFORGE_API_KEY:
        st.warning("⚠️ Clé API CurseForge non configurée")
        st.info("""
        Pour utiliser l'API CurseForge, vous devez:
        1. Obtenir une clé API sur https://console.curseforge.com/
        2. Ajouter la clé dans un fichier `.streamlit/secrets.toml`:
        ```toml
        CURSEFORGE_API_KEY = "votre_clé_ici"
        ```
        """)
        return
    
    with st.spinner("📡 Chargement des données CurseForge..."):
        mod_info = get_curseforge_mod_info()
        mod_files = get_curseforge_mod_files()
        
        if not mod_info:
            st.error("❌ Impossible de charger les données CurseForge")
            return
        
        version_stats = analyze_downloads_by_version(mod_files, "curseforge") if mod_files else []
    
    # Statistiques principales
    st.markdown("## 📊 Vue d'ensemble")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="curseforge-stat-number">{mod_info['downloadCount']:,}</div>
            <div class="stat-label">📥 Téléchargements</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="curseforge-stat-number">{mod_info.get('thumbsUpCount', 0):,}</div>
            <div class="stat-label">👍 Likes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="curseforge-stat-number">{len(mod_files) if mod_files else 0}</div>
            <div class="stat-label">📦 Fichiers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        days_since_creation = (datetime.now(timezone.utc) - datetime.fromisoformat(mod_info['dateCreated'].replace('Z', '+00:00'))).days
        st.markdown(f"""
        <div class="stat-card">
            <div class="curseforge-stat-number">{days_since_creation}</div>
            <div class="stat-label">📅 Jours depuis création</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Description
    with st.expander("📝 Description du projet", expanded=False):
        st.markdown(mod_info['summary'])
        st.caption(f"**Créé le:** {mod_info['dateCreated'][:10]} | **Dernière mise à jour:** {mod_info['dateModified'][:10]}")
    
    st.markdown("---")
    
    if version_stats:
        # Graphiques
        st.markdown("## 📈 Évolution des téléchargements")
        st.plotly_chart(create_timeline_chart(version_stats, '#f16436'), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📦 Téléchargements par version")
            st.plotly_chart(create_top_versions_chart(version_stats, '#f16436'), use_container_width=True)
        
        with col2:
            st.markdown("### 🎮 Téléchargements par version Minecraft")
            st.plotly_chart(create_mc_versions_chart(version_stats), use_container_width=True)
        
        st.markdown("---")
        
        # Tableau des versions
        st.markdown("## 📋 Détails des fichiers")
        df_versions = pd.DataFrame([
            {
                'Nom': v['name'],
                'Fichier': v['version_number'],
                'Téléchargements': v['downloads'],
                'Date': datetime.fromisoformat(v['date_published'].replace('Z', '+00:00')).strftime('%d/%m/%Y'),
                'Versions MC': ', '.join([str(gv) for gv in v['game_versions'][:3]]) + ('...' if len(v['game_versions']) > 3 else '')
            }
            for v in reversed(version_stats)
        ])
        
        total_dl = df_versions['Téléchargements'].sum()
        if total_dl > 0:
            df_versions['%'] = (df_versions['Téléchargements'] / total_dl * 100).round(1)
        
        st.dataframe(df_versions, use_container_width=True, height=400, hide_index=True)
    
    st.markdown("---")
    
    # Modpacks
    st.markdown("## 📦 Modpacks incluant Create Nuclear")
    with st.spinner("🔍 Recherche des modpacks CurseForge..."):
        try:
            modpacks = search_curseforge_modpacks()
            
            if modpacks:
                st.success(f"✅ {len(modpacks)} modpack(s) trouvé(s)")
                modpacks_sorted = sorted(modpacks, key=lambda x: x['downloads'], reverse=True)
                
                if len(modpacks_sorted) > 0:
                    top_modpacks = modpacks_sorted[:10]
                    
                    fig = go.Figure(go.Bar(
                        x=[mp['downloads'] for mp in top_modpacks],
                        y=[mp['name'] for mp in top_modpacks],
                        orientation='h',
                        marker=dict(color='#f16436'),
                        hovertemplate='<b>%{y}</b><br>%{x:,} téléchargements<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        title="Top 10 modpacks par téléchargements",
                        xaxis_title="Téléchargements du modpack",
                        yaxis_title="",
                        height=400,
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                df_modpacks = pd.DataFrame([
                    {
                        'Nom': mp['name'],
                        'Téléchargements': mp['downloads'],
                        'Lien': f"https://www.curseforge.com/minecraft/modpacks/{mp['slug']}"
                    }
                    for mp in modpacks_sorted
                ])
                
                st.dataframe(
                    df_modpacks,
                    use_container_width=True,
                    height=400,
                    hide_index=True,
                    column_config={
                        "Lien": st.column_config.LinkColumn("Lien", display_text="Voir sur CurseForge")
                    }
                )
            else:
                st.info("ℹ️ Aucun modpack trouvé ou recherche limitée.")
        except Exception as e:
            st.error(f"❌ Erreur lors de la recherche: {e}")

def main():
    # Bannière
    st.image("banniere-nuclear.jpg", use_column_width=True)
    
    # En-tête
    st.markdown('<h1 class="main-header">☢️ Create Nuclear - Statistiques</h1>', unsafe_allow_html=True)
    
    # Barre latérale
    with st.sidebar:
        st.image("logo.png", width=150)
        st.markdown("---")
        st.markdown("### 🔗 Liens")
        st.markdown(f"[📦 Modrinth](https://modrinth.com/mod/{MODRINTH_PROJECT_SLUG})")
        st.markdown(f"[🔥 CurseForge](https://www.curseforge.com/minecraft/mc-mods/createnuclear)")
        st.markdown("---")
        
        if st.button("🔄 Rafraîchir les données", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.caption("📊 Données mises à jour toutes les heures")
    
    # Onglets
    tab1, tab2 = st.tabs(["🟢 Modrinth", "🔥 CurseForge"])
    
    with tab1:
        render_modrinth_tab()
    
    with tab2:
        render_curseforge_tab()
    
    # Export des données
    st.markdown("---")
    st.markdown("## 💾 Export des données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            project_info = get_modrinth_project_info()
            versions = get_modrinth_project_versions()
            version_stats = analyze_downloads_by_version(versions, "modrinth")
            
            export_data = {
                'generated_at': datetime.now().isoformat(),
                'modrinth': {
                    'project': {
                        'title': project_info['title'],
                        'slug': project_info['slug'],
                        'total_downloads': project_info['downloads'],
                        'followers': project_info['followers'],
                        'published': project_info['published'],
                        'updated': project_info['updated']
                    },
                    'versions': version_stats
                }
            }
            
            st.download_button(
                label="📥 Télécharger JSON (Modrinth)",
                data=json.dumps(export_data, indent=2, ensure_ascii=False),
                file_name=f"createnuclear_modrinth_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
        except:
            pass
    
    with col2:
        if CURSEFORGE_API_KEY:
            try:
                mod_info = get_curseforge_mod_info()
                if mod_info:
                    export_data = {
                        'generated_at': datetime.now().isoformat(),
                        'curseforge': {
                            'id': mod_info['id'],
                            'name': mod_info['name'],
                            'downloads': mod_info['downloadCount'],
                            'created': mod_info['dateCreated'],
                            'modified': mod_info['dateModified']
                        }
                    }
                    
                    st.download_button(
                        label="📥 Télécharger JSON (CurseForge)",
                        data=json.dumps(export_data, indent=2, ensure_ascii=False),
                        file_name=f"createnuclear_curseforge_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            except:
                pass

if __name__ == "__main__":
    main()
