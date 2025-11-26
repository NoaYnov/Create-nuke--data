"""
Create Nuclear Statistics - True One Page Dashboard
Tout visible sur un seul écran sans scroll - Design ultra-compact
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
from dateutil import parser as date_parser
from pathlib import Path

# Import modules
from api_clients import ModrinthClient, CurseForgeClient
from modpack_manager import ModpackManager
from database import StatsDatabase
from config import DATABASE_URL, CACHE_TTL, LOGO_PATH, BANNER_PATH


# === PAGE CONFIG ===
st.set_page_config(
    page_title="Create Nuclear - One Page",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# === CUSTOM CSS - ONE PAGE OPTIMIZED ===
st.markdown("""
<style>
    /* === FONTS === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fira+Code:wght@400;500;600&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* === VARIABLES - MEILLEUR CONTRASTE === */
    :root {
        --bg-primary: #0d1117;
        --bg-secondary: #161b22;
        --bg-tertiary: #1f2937;
        --accent-cyan: #0ef;
        --accent-purple: #c084fc;
        --accent-green: #4ade80;
        --accent-orange: #fb923c;
        --text-primary: #ffffff;
        --text-secondary: #d1d5db;
        --text-muted: #9ca3af;
        --border-color: rgba(255, 255, 255, 0.1);
        --shadow-glow: rgba(14, 255, 255, 0.25);
    }
    
    /* === LAYOUT === */
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #1f2937 100%);
        background-attachment: fixed;
    }
    
    .main {
        background: transparent;
    }
    
    .block-container {
        padding: 0.5rem 1rem !important;
        max-width: 100% !important;
    }
    
    /* Désactiver scroll */
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
        height: 100vh !important;
    }
    
    /* === TYPOGRAPHY - CONTRASTE AMÉLIORÉ === */
    h1 {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple), var(--accent-green));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0.25rem 0 0.25rem 0 !important;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }
    
    h2 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        margin: 0.25rem 0 0.25rem 0 !important;
        padding-bottom: 0.25rem;
        border-bottom: 1px solid var(--border-color);
        letter-spacing: -0.02em;
    }
    
    h3 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        margin: 0.25rem 0 0.25rem 0 !important;
    }
    
    h4 {
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        margin: 0.25rem 0 0.25rem 0 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    p, span, div, label {
        color: var(--text-secondary) !important;
        line-height: 1.5;
    }
    
    strong {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }
    
    /* === MÉTRIQUES - ULTRA COMPACT === */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        font-family: 'Fira Code', monospace !important;
        color: var(--text-primary) !important;
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-green));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.6rem !important;
        font-weight: 700 !important;
        color: var(--text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.15rem !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.75rem !important;
        font-family: 'Fira Code', monospace !important;
        font-weight: 600 !important;
    }
    
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(31, 41, 55, 0.95), rgba(22, 27, 34, 0.95)) !important;
        backdrop-filter: blur(20px);
        padding: 0.5rem 0.75rem !important;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px var(--shadow-glow), 0 0 0 1px var(--accent-cyan);
        border-color: var(--accent-cyan);
    }
    
    /* === DATAFRAMES - COMPACT === */
    .stDataFrame {
        border-radius: 6px !important;
        overflow: hidden !important;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    }
    
    thead tr th {
        background: linear-gradient(135deg, #1f2937, #374151) !important;
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        padding: 6px 8px !important;
        text-transform: uppercase;
        font-size: 0.65rem !important;
        letter-spacing: 0.05em;
        border-bottom: 1px solid var(--accent-cyan) !important;
    }
    
    tbody tr {
        background: rgba(31, 41, 55, 0.7) !important;
        transition: all 0.2s ease;
    }
    
    tbody tr:nth-child(even) {
        background: rgba(22, 27, 34, 0.7) !important;
    }
    
    tbody tr:hover {
        background: rgba(14, 255, 255, 0.1) !important;
    }
    
    tbody td {
        padding: 4px 8px !important;
        color: var(--text-secondary) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        font-family: 'Fira Code', monospace !important;
        font-size: 0.7rem;
    }
    
    /* === INPUTS - COMPACT === */
    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        background: rgba(31, 41, 55, 0.95) !important;
        border-radius: 6px !important;
        border: 1px solid var(--border-color) !important;
        padding: 6px 10px !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease;
        font-weight: 500;
        font-size: 0.85rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus-within {
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 0 3px var(--shadow-glow) !important;
        background: rgba(31, 41, 55, 1) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-muted) !important;
    }
    
    /* === BOUTONS - COMPACT === */
    .stButton > button,
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple)) !important;
        color: #000000 !important;
        border: none;
        border-radius: 6px;
        padding: 6px 16px;
        font-weight: 700;
        font-size: 0.75rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px var(--shadow-glow);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px var(--shadow-glow);
        background: linear-gradient(135deg, var(--accent-purple), var(--accent-green)) !important;
    }
    
    /* === ALERTES - CONTRASTE ÉLEVÉ === */
    .stAlert {
        border-radius: 10px;
        padding: 1rem 1.25rem;
        border: 1px solid;
        backdrop-filter: blur(10px);
        font-weight: 600;
    }
    
    .stSuccess {
        background: rgba(74, 222, 128, 0.15) !important;
        border-color: var(--accent-green) !important;
        color: var(--accent-green) !important;
    }
    
    .stWarning {
        background: rgba(251, 146, 60, 0.15) !important;
        border-color: var(--accent-orange) !important;
        color: var(--accent-orange) !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.15) !important;
        border-color: #ef4444 !important;
        color: #ef4444 !important;
    }
    
    .stInfo {
        background: rgba(14, 255, 255, 0.15) !important;
        border-color: var(--accent-cyan) !important;
        color: var(--accent-cyan) !important;
    }
    
    /* === DIVIDER - COMPACT === */
    hr {
        margin: 0.5rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
    }
    
    /* === CAPTIONS === */
    .stCaption {
        color: var(--text-muted) !important;
        font-size: 0.85rem !important;
    }
    
    /* === IMAGES === */
    img {
        border-radius: 12px;
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.6);
    }
    
    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(13, 17, 23, 0.8);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
        border-radius: 10px;
        border: 2px solid rgba(13, 17, 23, 0.8);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--accent-purple), var(--accent-green));
    }
    
    /* === PLOTLY CHARTS === */
    .js-plotly-plot {
        border-radius: 12px;
        border: 1px solid var(--border-color);
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    
    /* === LINKS === */
    a {
        color: var(--accent-cyan) !important;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    a:hover {
        color: var(--accent-purple) !important;
        text-decoration: underline;
    }
    
    /* === SPINNER === */
    .stSpinner > div {
        border-color: var(--accent-cyan) !important;
    }
    
    /* === EXPANDER === */
    .streamlit-expanderHeader {
        background: rgba(31, 41, 55, 0.9);
        border-radius: 8px;
        border: 1px solid var(--border-color);
        color: var(--text-primary) !important;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(31, 41, 55, 1);
        border-color: var(--accent-cyan);
    }
    
    /* === CUSTOM SECTION - COMPACT === */
    .section-header {
        background: linear-gradient(135deg, rgba(31, 41, 55, 0.95), rgba(22, 27, 34, 0.95));
        backdrop-filter: blur(20px);
        padding: 0.4rem 0.75rem;
        border-radius: 6px;
        border: 1px solid var(--border-color);
        margin: 0.25rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    /* === ANIMATIONS === */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .main > div > div {
        animation: fadeIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)


# === CACHE ===
@st.cache_resource
def get_clients():
    """Get all clients as singleton"""
    return {
        'modrinth': ModrinthClient(),
        'curseforge': CurseForgeClient(),
        'modpack_manager': ModpackManager(),
        'database': StatsDatabase(DATABASE_URL) if DATABASE_URL else None
    }


@st.cache_data(ttl=CACHE_TTL)
def load_all_data():
    """Charge toutes les données en une fois"""
    clients = get_clients()
    
    data = {
        'modrinth': None,
        'curseforge': None,
        'modpacks': [],
        'modpack_stats': {},
        'database_modrinth': [],
        'database_curseforge': []
    }
    
    # Modrinth
    try:
        data['modrinth'] = clients['modrinth'].get_stats()
    except:
        pass
    
    # CurseForge
    try:
        if clients['curseforge'].is_available():
            data['curseforge'] = clients['curseforge'].get_stats()
    except:
        pass
    
    # Modpacks
    try:
        data['modpacks'] = clients['modpack_manager'].load()
        data['modpack_stats'] = clients['modpack_manager'].get_stats()
    except:
        pass
    
    # Database
    if clients['database']:
        try:
            data['database_modrinth'] = clients['database'].get_daily_stats_history('modrinth', days=30)
            data['database_curseforge'] = clients['database'].get_daily_stats_history('curseforge', days=30)
        except:
            pass
    
    return data


def create_compact_metric(label, value, icon):
    """Métrique ultra-compacte pour one-page"""
    st.markdown(f"""
    <div style="text-align: center; padding: 0.4rem 0.5rem; background: linear-gradient(135deg, rgba(31, 41, 55, 0.95), rgba(22, 27, 34, 0.95)); border-radius: 6px; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);">
        <div style="font-size: 1rem; margin-bottom: 0.15rem;">{icon}</div>
        <div style="color: #9ca3af; font-size: 0.55rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.2rem;">{label}</div>
        <div style="font-size: 1.1rem; font-weight: 800; font-family: 'Fira Code', monospace; background: linear-gradient(135deg, #0ef, #4ade80); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1;">{value}</div>
    </div>
    """, unsafe_allow_html=True)


# === MAIN APP ===
def main():
    """Application one-page - SANS SCROLL"""
    
    # Charger toutes les données
    data = load_all_data()
    
    # Header ultra-compact
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown("# ⚛️ Create Nuclear - One Page")
    with col2:
        if st.button("🔄", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # === ROW 1: MÉTRIQUES GLOBALES (6 colonnes) ===
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        if data['modrinth']:
            create_compact_metric("Modrinth", f"{data['modrinth']['total_downloads']:,}", "🟢")
    
    with col2:
        if data['modrinth']:
            create_compact_metric("Followers", f"{data['modrinth']['followers']:,}", "👥")
    
    with col3:
        if data['modrinth']:
            create_compact_metric("Versions", str(data['modrinth']['versions_count']), "📦")
    
    with col4:
        if data['curseforge']:
            create_compact_metric("CurseForge", f"{data['curseforge']['total_downloads']:,}", "🔥")
        else:
            create_compact_metric("CurseForge", "N/A", "🔥")
    
    with col5:
        if data['modpack_stats']:
            create_compact_metric("Modpacks", f"{data['modpack_stats']['total']:,}", "📚")
    
    with col6:
        if data['modpack_stats']:
            create_compact_metric("Total MP DL", f"{data['modpack_stats']['total_downloads']:,}", "📥")
    
    st.markdown("---")
    
    # === ROW 2: GRAPHIQUES (3 colonnes) ===
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🟢 Top Versions**")
        if data['modrinth']:
            top_versions = sorted(data['modrinth']['versions'], key=lambda x: x['downloads'], reverse=True)[:6]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[v['downloads'] for v in top_versions],
                y=[v['name'][:15] for v in top_versions],
                orientation='h',
                marker=dict(
                    color=[v['downloads'] for v in top_versions],
                    colorscale=[[0, '#0ef'], [1, '#4ade80']],
                    showscale=False
                ),
                text=[f"{v['downloads']:,}" for v in top_versions],
                textposition='auto',
                textfont=dict(size=8, family='Fira Code', color='white'),
                hovertemplate='%{y}<br>%{x:,}<extra></extra>'
            ))
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#d1d5db', family='Inter', size=9),
                height=220,
                margin=dict(l=0, r=0, t=5, b=0),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)', showgrid=True),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**📈 Modrinth Trend (30d)**")
        if data['database_modrinth']:
            df_modrinth = pd.DataFrame(data['database_modrinth'])
            df_modrinth['date'] = pd.to_datetime(df_modrinth['date'])
            df_modrinth = df_modrinth.sort_values('date')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_modrinth['date'],
                y=df_modrinth['total_downloads'],
                mode='lines',
                line=dict(color='#0ef', width=2),
                fill='tozeroy',
                fillcolor='rgba(14, 255, 255, 0.1)',
                hovertemplate='%{x|%m-%d}<br>%{y:,}<extra></extra>'
            ))
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#d1d5db', family='Inter', size=9),
                height=220,
                margin=dict(l=0, r=0, t=5, b=0),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)', showgrid=True, showticklabels=False),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)', showgrid=True),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**📦 Top Modpacks**")
        if data['modpacks']:
            top_modpacks = [m for m in data['modpacks'] if m.get('downloads', 0) > 0][:6]
            
            if top_modpacks:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=[m.get('downloads', 0) for m in top_modpacks],
                    y=[m['name'][:15] for m in top_modpacks],
                    orientation='h',
                    marker=dict(
                        color=[m.get('downloads', 0) for m in top_modpacks],
                        colorscale=[[0, '#c084fc'], [1, '#4ade80']],
                        showscale=False
                    ),
                    text=[f"{m.get('downloads', 0):,}" for m in top_modpacks],
                    textposition='auto',
                    textfont=dict(size=8, family='Fira Code', color='white'),
                    hovertemplate='%{y}<br>%{x:,}<extra></extra>'
                ))
                
                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#d1d5db', family='Inter', size=9),
                    height=220,
                    margin=dict(l=0, r=0, t=5, b=0),
                    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', showgrid=True),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # === ROW 3: FILTRES + DONNÉES (2 colonnes) ===
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("**🔍 Filters**")
        
        # Sélecteur de vue
        view_mode = st.radio("View", ["📦 Versions", "📚 Modpacks"], label_visibility="collapsed")
        
        if view_mode == "📦 Versions":
            # Filtres versions
            if data['modrinth']:
                game_version_filter = st.selectbox(
                    "Game Version",
                    ["All"] + sorted(list(set([gv for v in data['modrinth']['versions'] for gv in v['game_versions']])), reverse=True)[:10],
                    key="gv_filter"
                )
                
                sort_versions = st.selectbox("Sort", ["Downloads ↓", "Date ↓"], key="sort_v")
        else:
            # Filtres modpacks
            search = st.text_input("Search", placeholder="Name...", key="search")
            sort_modpacks = st.selectbox("Sort", ["Downloads ↓", "Name A→Z"], key="sort_m")
            show_stats = st.checkbox("Only with stats", key="stats_only")
    
    with col2:
        st.markdown("**📊 Data**")
        
        if view_mode == "📦 Versions":
            if data['modrinth']:
                # Filtrer versions
                versions = data['modrinth']['versions']
                
                if game_version_filter != "All":
                    versions = [v for v in versions if game_version_filter in v['game_versions']]
                
                if sort_versions == "Downloads ↓":
                    versions = sorted(versions, key=lambda x: x['downloads'], reverse=True)
                
                # Tableau versions (Top 8)
                versions_df = pd.DataFrame([{
                    'Ver': v['name'][:20],
                    'DL': f"{v['downloads']:,}",
                    'Game': ', '.join(v['game_versions'][:2]),
                    'Date': date_parser.parse(v['date_published']).strftime('%m-%d')
                } for v in versions[:8]])
                
                st.dataframe(versions_df, use_container_width=True, hide_index=True, height=190)
        
        else:
            # Afficher modpacks
            if data['modpacks']:
                filtered = data['modpacks']
                
                if search:
                    filtered = [m for m in filtered if search.lower() in m['name'].lower()]
                
                if show_stats:
                    filtered = [m for m in filtered if m.get('downloads', 0) > 0]
                
                if "Downloads" in sort_modpacks:
                    filtered = sorted(filtered, key=lambda x: x.get('downloads', 0), reverse=True)
                else:
                    filtered = sorted(filtered, key=lambda x: x.get('name', '').lower())
                
                # Tableau modpacks (Top 8)
                modpacks_df = pd.DataFrame([{
                    'Name': m['name'][:30],
                    'DL': f"{m.get('downloads', 0):,}" if m.get('downloads', 0) > 0 else 'N/A',
                    'ID': m.get('id', 'N/A')[:15]
                } for m in filtered[:8]])
                
                st.dataframe(modpacks_df, use_container_width=True, hide_index=True, height=190)
                st.caption(f"Found: {len(filtered)} modpacks")
    
    # Footer compact
    st.markdown("---")
    st.caption(f"⚛️ Create Nuclear v2.0 | {datetime.now().strftime('%H:%M:%S')} | [Modrinth](https://modrinth.com/mod/createnuclear) • [CurseForge](https://www.curseforge.com/minecraft/mc-mods/createnuclear) • [GitHub](https://github.com/NoaYnov/Create-nuke--data)")


if __name__ == "__main__":
    main()
