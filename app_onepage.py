"""
Create Nuclear Statistics - One Page Dashboard
Interface minimaliste - Tout sur un écran - Filtres uniquement
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from dateutil import parser as date_parser

# Import modules
from api_clients import ModrinthClient, CurseForgeClient
from modpack_manager import ModpackManager
from database import StatsDatabase
from config import DATABASE_URL, CACHE_TTL


# === PAGE CONFIG ===
st.set_page_config(
    page_title="⚛️ Create Nuclear",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# === CUSTOM CSS - MINIMAL ONE PAGE ===
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800&family=Fira+Code:wght@500;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* === DÉSACTIVER SCROLL === */
    html, body, [data-testid="stAppViewContainer"], .main {
        overflow: hidden !important;
        height: 100vh !important;
        max-height: 100vh !important;
    }
    
    /* === LAYOUT SERRÉ === */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #111827 100%);
    }
    
    .block-container {
        padding: 0.5rem 1.5rem !important;
        max-width: 100% !important;
        max-height: 100vh !important;
        overflow: hidden !important;
    }
    
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* === TYPOGRAPHY MINIMAL === */
    h1 {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #0ef, #4ade80);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2;
        text-shadow: 0 0 30px rgba(14, 255, 255, 0.5);
        animation: glow 3s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.3); }
    }
    
    h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        margin: 0.3rem 0 !important;
        padding: 0 !important;
    }
    
    p, span, div, label {
        color: #e5e7eb !important;
        line-height: 1.3;
        font-size: 0.85rem !important;
    }
    
    .stMarkdown {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* === MÉTRIQUES MINIMALISTES - EFFET WOW === */
    [data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        font-family: 'Fira Code', monospace !important;
        background: linear-gradient(135deg, #0ef, #4ade80);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.6rem !important;
        font-weight: 700 !important;
        color: #d1d5db !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    [data-testid="metric-container"] {
        background: rgba(15, 23, 42, 0.9) !important;
        padding: 0.6rem !important;
        border-radius: 10px;
        border: 1px solid rgba(14, 255, 255, 0.3);
        box-shadow: 0 4px 20px rgba(14, 255, 255, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(14, 255, 255, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        border-color: rgba(14, 255, 255, 0.6);
    }
    
    /* === DATAFRAMES ULTRA COMPACT === */
    .stDataFrame {
        border-radius: 6px !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    thead tr th {
        background: #1f2937 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        padding: 4px 6px !important;
        font-size: 0.65rem !important;
        text-transform: uppercase;
    }
    
    tbody tr {
        background: rgba(31, 41, 55, 0.9) !important;
    }
    
    tbody tr:hover {
        background: rgba(14, 255, 255, 0.1) !important;
    }
    
    tbody td {
        padding: 3px 6px !important;
        color: #d1d5db !important;
        font-family: 'Fira Code', monospace !important;
        font-size: 0.7rem !important;
        border: none !important;
    }
    
    /* === INPUTS MINIMAL - EFFET GLOW === */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stRadio > div {
        background: rgba(31, 41, 55, 0.9) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(14, 255, 255, 0.3) !important;
        padding: 5px 8px !important;
        color: #ffffff !important;
        font-size: 0.8rem !important;
        box-shadow: 0 2px 10px rgba(14, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus-within {
        border-color: #0ef !important;
        box-shadow: 0 0 20px rgba(14, 255, 255, 0.4);
    }
    
    .stCheckbox {
        font-size: 0.8rem !important;
    }
    
    /* === BOUTONS MINIMAL === */
    .stButton > button {
        background: linear-gradient(135deg, #0ef, #4ade80) !important;
        color: #000000 !important;
        border: none;
        border-radius: 6px;
        padding: 5px 12px;
        font-weight: 700;
        font-size: 0.75rem;
    }
    
    .stButton > button:hover {
        opacity: 0.9;
    }
    
    /* === DIVIDER - EFFET GLOW === */
    hr {
        margin: 0.4rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(14, 255, 255, 0.5), transparent);
        box-shadow: 0 0 10px rgba(14, 255, 255, 0.3);
    }
    
    /* === CAPTIONS === */
    .stCaption {
        color: #9ca3af !important;
        font-size: 0.7rem !important;
    }
    
    /* === PLOTLY - EFFET WOW === */
    .js-plotly-plot {
        border-radius: 10px;
        border: 1px solid rgba(14, 255, 255, 0.3);
        box-shadow: 0 4px 20px rgba(14, 255, 255, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        background: rgba(15, 23, 42, 0.9);
    }
    
    /* Supprimer espaces inutiles */
    .element-container {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .row-widget {
        margin: 0 !important;
    }
</style>
""", unsafe_allow_html=True)


# === CACHE ===
@st.cache_resource
def get_clients():
    """Get clients"""
    return {
        'modrinth': ModrinthClient(),
        'curseforge': CurseForgeClient(),
        'modpack_manager': ModpackManager(),
        'database': StatsDatabase(DATABASE_URL) if DATABASE_URL else None
    }


@st.cache_data(ttl=CACHE_TTL)
def load_all_data():
    """Charge toutes les données"""
    clients = get_clients()
    
    data = {
        'modrinth': None,
        'curseforge': None,
        'modpacks': [],
        'modpack_stats': {},
        'database_modrinth': [],
        'database_curseforge': []
    }
    
    try:
        data['modrinth'] = clients['modrinth'].get_stats()
    except:
        pass
    
    try:
        if clients['curseforge'].is_available():
            data['curseforge'] = clients['curseforge'].get_stats()
    except:
        pass
    
    try:
        data['modpacks'] = clients['modpack_manager'].load()
        data['modpack_stats'] = clients['modpack_manager'].get_stats()
    except:
        pass
    
    # Charger historique database
    if clients['database']:
        try:
            data['database_modrinth'] = clients['database'].get_daily_stats_history('modrinth', days=90)
            data['database_curseforge'] = clients['database'].get_daily_stats_history('curseforge', days=90)
            data['initial_downloads'] = clients['database'].get_modpacks_initial_downloads('curseforge')
        except:
            pass
    
    return data


# === MAIN APP ===
def main():
    """Application ONE PAGE - Minimaliste"""
    
    # Charger données
    data = load_all_data()
    
    # === HEADER ULTRA COMPACT ===
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("# ⚛️ Create Nuclear")
    with col2:
        if st.button("🔄"):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # === ROW 1: MÉTRIQUES (5 colonnes) ===
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        if data['modrinth']:
            st.metric("🟢 Modrinth", f"{data['modrinth']['total_downloads']:,}")
    
    with c2:
        if data['modrinth']:
            st.metric("📦 Versions", str(data['modrinth']['versions_count']))
    
    with c3:
        if data['curseforge']:
            # Utiliser downloadCount du mod directement
            cf_downloads = data['curseforge']['mod'].get('downloadCount', 0)
            st.metric("🔥 CurseForge", f"{cf_downloads:,}")
        else:
            st.metric("🔥 CurseForge", "N/A")
    
    with c4:
        if data['modpack_stats']:
            st.metric("📚 Modpacks", f"{data['modpack_stats']['total']:,}")
    
    with c5:
        if data['modpack_stats']:
            st.metric("📥 MP DL", f"{data['modpack_stats']['total_downloads']:,}")
    
    st.markdown("---")
    
    # === ROW 2: GRAPHIQUE HISTORIQUE COMBINÉ ===
    c1, c2 = st.columns([5, 1])
    
    with c2:
        st.markdown("**⏱️ Période**")
        period = st.radio("", ["7j", "30j", "90j"], index=1, label_visibility="collapsed")
        
        period_map = {"7j": 7, "30j": 30, "90j": 90}
        days = period_map[period]
    
    with c1:
        st.markdown("**📈 Downloads Evolution (Modrinth + CurseForge)**")
        
        if data['database_modrinth'] or data['database_curseforge']:
            fig = go.Figure()
            
            # Modrinth
            if data['database_modrinth']:
                df_m = pd.DataFrame(data['database_modrinth'])
                df_m['date'] = pd.to_datetime(df_m['date'])
                df_m = df_m.sort_values('date').tail(days)
                
                fig.add_trace(go.Scatter(
                    x=df_m['date'],
                    y=df_m['total_downloads'],
                    name='Modrinth',
                    mode='lines',
                    line=dict(color='#0ef', width=3),
                    fill='tonexty' if not data['database_curseforge'] else 'tozeroy',
                    fillcolor='rgba(14, 255, 255, 0.2)',
                    hovertemplate='<b>Modrinth</b><br>%{x|%d/%m}<br>%{y:,}<extra></extra>'
                ))
            
            # CurseForge
            if data['database_curseforge']:
                df_c = pd.DataFrame(data['database_curseforge'])
                df_c['date'] = pd.to_datetime(df_c['date'])
                df_c = df_c.sort_values('date').tail(days)
                
                fig.add_trace(go.Scatter(
                    x=df_c['date'],
                    y=df_c['total_downloads'],
                    name='CurseForge',
                    mode='lines',
                    line=dict(color='#fb923c', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(251, 146, 60, 0.2)',
                    hovertemplate='<b>CurseForge</b><br>%{x|%d/%m}<br>%{y:,}<extra></extra>'
                ))
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff', size=10, family='Inter'),
                height=200,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.05)',
                    showticklabels=True,
                    tickfont=dict(size=9)
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.05)',
                    showticklabels=True,
                    tickfont=dict(size=9)
                ),
                legend=dict(
                    orientation='h',
                    yanchor='top',
                    y=1.15,
                    xanchor='center',
                    x=0.5,
                    bgcolor='rgba(0,0,0,0)',
                    font=dict(size=10, weight='bold')
                ),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⚠️ No historical data available")
    
    st.markdown("---")
    
    # === ROW 3: FILTRES + TABLE (2 colonnes) ===
    c1, c2 = st.columns([1, 4])
    
    with c1:
        st.markdown("**🔍 Filtres**")
        
        # Mode sélection
        mode = st.radio("", ["📦 Versions", "📚 Modpacks"], label_visibility="collapsed")
        
        if mode == "📦 Versions":
            # Filtres versions
            if data['modrinth']:
                all_game_versions = sorted(list(set([gv for v in data['modrinth']['versions'] for gv in v['game_versions']])), reverse=True)[:8]
                game_ver = st.selectbox("Game", ["All"] + all_game_versions, label_visibility="collapsed")
                sort_v = st.selectbox("Sort", ["DL↓", "Date↓"], label_visibility="collapsed")
        else:
            # Filtres modpacks
            search = st.text_input("", placeholder="Search...", label_visibility="collapsed")
            sort_m = st.selectbox("Sort", ["DL↓", "Name"], label_visibility="collapsed")
            with_stats = st.checkbox("With stats", value=False)
    
    with c2:
        st.markdown("**📊 Data**")
        
        if mode == "📦 Versions":
            # Afficher versions
            if data['modrinth']:
                versions = data['modrinth']['versions']
                
                if game_ver != "All":
                    versions = [v for v in versions if game_ver in v['game_versions']]
                
                if sort_v == "DL↓":
                    versions = sorted(versions, key=lambda x: x['downloads'], reverse=True)
                
                df = pd.DataFrame([{
                    'Version': v['name'][:18],
                    'Downloads': f"{v['downloads']:,}",
                    'Game': ', '.join(v['game_versions'][:2]),
                    'Date': date_parser.parse(v['date_published']).strftime('%m/%d')
                } for v in versions[:6]])
                
                st.dataframe(df, use_container_width=True, hide_index=True, height=150)
        
        else:
            # Afficher modpacks
            if data['modpacks']:
                filtered = data['modpacks']
                
                if search:
                    filtered = [m for m in filtered if search.lower() in m['name'].lower()]
                
                if with_stats:
                    filtered = [m for m in filtered if m.get('downloads', 0) > 0]
                
                if sort_m == "DL↓":
                    filtered = sorted(filtered, key=lambda x: x.get('downloads', 0), reverse=True)
                else:
                    filtered = sorted(filtered, key=lambda x: x.get('name', '').lower())
                
                modpacks_data = []
                initial_downloads = data.get('initial_downloads', {})
                
                for m in filtered[:6]:
                    current = m.get('downloads', 0)
                    slug = m.get('slug')
                    since_added = current
                    
                    if slug in initial_downloads:
                        since_added = max(0, current - initial_downloads[slug]['downloads'])
                        
                    modpacks_data.append({
                        'Modpack': m['name'][:25],
                        'Downloads': f"{current:,}" if current > 0 else 'N/A',
                        'Since Added': f"+{since_added:,}" if since_added > 0 else "0",
                        'ID': m.get('id', 'N/A')[:12]
                    })
                
                df = pd.DataFrame(modpacks_data)
                
                st.dataframe(df, use_container_width=True, hide_index=True, height=150)
                st.caption(f"{len(filtered)} résultats")
    
    # Footer
    st.markdown("---")
    st.caption(f"⚛️ Create Nuclear v2.0 | {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    main()
