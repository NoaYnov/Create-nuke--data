"""
Create Nuclear Statistics Dashboard
Architecture modulaire avec design professionnel moderne
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from pathlib import Path
import time

# Import modules
from api_clients import ModrinthClient, CurseForgeClient
from modpack_manager import ModpackManager
from database import StatsDatabase
from config import DATABASE_URL, CACHE_TTL, LOGO_PATH, BANNER_PATH


# === PAGE CONFIG ===
st.set_page_config(
    page_title="Create Nuclear Statistics",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/NoaYnov/Create-nuke--data',
        'Report a bug': 'https://github.com/NoaYnov/Create-nuke--data/issues',
        'About': 'Create Nuclear Statistics Dashboard - Professional Analytics'
    }
)


# === CUSTOM CSS - DESIGN SYSTEM ===
def load_custom_css():
    """Charge le système de design personnalisé"""
    st.markdown("""
    <style>
        /* === FONTS === */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500;600&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        }
        
        /* === VARIABLES CSS === */
        :root {
            --bg-primary: #0a0e1a;
            --bg-secondary: #121825;
            --bg-tertiary: #1a2234;
            --accent-cyan: #00e5ff;
            --accent-purple: #b794f6;
            --accent-green: #48ff91;
            --text-primary: #f0f6fc;
            --text-secondary: #9ba4b5;
            --text-muted: #6b7280;
            --border-color: rgba(139, 148, 158, 0.2);
            --shadow-glow: rgba(0, 229, 255, 0.15);
        }
        
        /* === LAYOUT PRINCIPAL === */
        .stApp {
            background: linear-gradient(135deg, #0a0e1a 0%, #121825 50%, #0f1621 100%);
            background-attachment: fixed;
        }
        
        .main {
            background: transparent;
        }
        
        .block-container {
            padding: 2rem 3rem !important;
            max-width: 100% !important;
        }
        
        /* === SIDEBAR === */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
            border-right: 1px solid var(--border-color);
            box-shadow: 4px 0 20px rgba(0, 0, 0, 0.3);
        }
        
        [data-testid="stSidebar"] * {
            color: var(--text-secondary) !important;
        }
        
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: var(--text-primary) !important;
            font-weight: 700 !important;
        }
        
        [data-testid="stSidebar"] .stMarkdown {
            padding: 0.5rem 0;
        }
        
        /* === TYPOGRAPHY === */
        h1 {
            font-size: 3rem !important;
            font-weight: 800 !important;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple), var(--accent-green));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 2rem 0 1rem 0 !important;
            letter-spacing: -0.03em;
            line-height: 1.2;
        }
        
        h2 {
            color: var(--text-primary) !important;
            font-weight: 700 !important;
            font-size: 2rem !important;
            margin: 2rem 0 1.5rem 0 !important;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid var(--border-color);
            letter-spacing: -0.02em;
        }
        
        h3 {
            color: var(--text-primary) !important;
            font-weight: 600 !important;
            font-size: 1.5rem !important;
            margin: 1.5rem 0 1rem 0 !important;
            letter-spacing: -0.01em;
        }
        
        h4 {
            color: var(--text-secondary) !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            margin: 1rem 0 0.5rem 0 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        p, span, div, label {
            color: var(--text-secondary) !important;
            line-height: 1.6;
        }
        
        strong {
            color: var(--text-primary) !important;
            font-weight: 600 !important;
        }
        
        /* === TABS === */
        .stTabs {
            background: rgba(26, 34, 52, 0.6);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 2rem;
            border: 1px solid var(--border-color);
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: rgba(13, 17, 23, 0.9);
            padding: 0.5rem;
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border-radius: 10px;
            color: var(--text-muted) !important;
            font-weight: 600;
            padding: 12px 28px;
            border: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-size: 1rem;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(139, 148, 158, 0.1);
            color: var(--text-secondary) !important;
            transform: translateY(-1px);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple)) !important;
            color: #ffffff !important;
            font-weight: 700;
            box-shadow: 0 6px 20px var(--shadow-glow);
        }
        
        /* === METRICS === */
        [data-testid="stMetricValue"] {
            font-size: 2.75rem !important;
            font-weight: 800 !important;
            font-family: 'Fira Code', monospace !important;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-green));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.02em;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
            font-weight: 700 !important;
            color: var(--text-muted) !important;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin-bottom: 0.5rem !important;
        }
        
        [data-testid="stMetricDelta"] {
            font-size: 1rem !important;
            font-family: 'Fira Code', monospace !important;
            font-weight: 600 !important;
        }
        
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, rgba(26, 34, 52, 0.7), rgba(18, 24, 37, 0.7));
            backdrop-filter: blur(15px);
            padding: 1.75rem !important;
            border-radius: 16px;
            border: 1px solid var(--border-color);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        [data-testid="metric-container"]::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple), var(--accent-green));
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        [data-testid="metric-container"]:hover {
            transform: translateY(-6px);
            box-shadow: 0 16px 48px var(--shadow-glow);
            border-color: var(--accent-cyan);
        }
        
        [data-testid="metric-container"]:hover::before {
            opacity: 1;
        }
        
        /* === DATAFRAMES === */
        .stDataFrame {
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        }
        
        thead tr th {
            background: linear-gradient(135deg, #161b22, #1c2128) !important;
            color: var(--text-primary) !important;
            font-weight: 700 !important;
            padding: 16px 14px !important;
            text-transform: uppercase;
            font-size: 0.7rem !important;
            letter-spacing: 0.08em;
            border-bottom: 2px solid var(--accent-cyan) !important;
        }
        
        tbody tr {
            background: rgba(26, 34, 52, 0.5) !important;
            transition: all 0.2s ease;
        }
        
        tbody tr:nth-child(even) {
            background: rgba(18, 24, 37, 0.5) !important;
        }
        
        tbody tr:hover {
            background: rgba(0, 229, 255, 0.08) !important;
            box-shadow: 0 2px 12px var(--shadow-glow);
            transform: scale(1.002);
        }
        
        tbody td {
            padding: 14px !important;
            color: var(--text-secondary) !important;
            border-bottom: 1px solid rgba(139, 148, 158, 0.1) !important;
            font-family: 'Fira Code', monospace !important;
            font-size: 0.9rem;
        }
        
        /* === INPUTS === */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stMultiSelect > div > div {
            background: rgba(26, 34, 52, 0.8) !important;
            border-radius: 10px !important;
            border: 1px solid var(--border-color) !important;
            padding: 12px 16px !important;
            color: var(--text-primary) !important;
            transition: all 0.3s ease;
            font-size: 1rem;
        }
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div:focus-within,
        .stMultiSelect > div > div:focus-within {
            border-color: var(--accent-cyan) !important;
            box-shadow: 0 0 0 4px var(--shadow-glow) !important;
            background: rgba(26, 34, 52, 1) !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: var(--text-muted) !important;
        }
        
        /* === BUTTONS === */
        .stButton > button,
        .stDownloadButton > button {
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            color: #ffffff !important;
            border: none;
            border-radius: 10px;
            padding: 12px 32px;
            font-weight: 700;
            font-size: 1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 6px 20px var(--shadow-glow);
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        
        .stButton > button:hover,
        .stDownloadButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 32px var(--shadow-glow);
        }
        
        .stButton > button:active,
        .stDownloadButton > button:active {
            transform: translateY(-1px);
        }
        
        /* === ALERTS === */
        .stAlert {
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            border: 1px solid var(--border-color);
            backdrop-filter: blur(10px);
            font-weight: 500;
        }
        
        .stSuccess {
            background: rgba(72, 255, 145, 0.1) !important;
            border-color: var(--accent-green) !important;
            color: var(--accent-green) !important;
        }
        
        .stWarning {
            background: rgba(255, 184, 0, 0.1) !important;
            border-color: #ffb800 !important;
            color: #ffb800 !important;
        }
        
        .stError {
            background: rgba(255, 77, 77, 0.1) !important;
            border-color: #ff4d4d !important;
            color: #ff4d4d !important;
        }
        
        .stInfo {
            background: rgba(0, 229, 255, 0.1) !important;
            border-color: var(--accent-cyan) !important;
            color: var(--accent-cyan) !important;
        }
        
        /* === DIVIDER === */
        hr {
            margin: 2rem 0;
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        }
        
        /* === CAPTIONS === */
        .stCaption {
            color: var(--text-muted) !important;
            font-size: 0.85rem !important;
            font-weight: 400 !important;
        }
        
        /* === IMAGES === */
        img {
            border-radius: 16px;
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5);
        }
        
        /* === SCROLLBAR === */
        ::-webkit-scrollbar {
            width: 14px;
            height: 14px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(13, 17, 23, 0.6);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            border-radius: 10px;
            border: 3px solid rgba(13, 17, 23, 0.6);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-green));
        }
        
        /* === SPINNER === */
        .stSpinner > div {
            border-color: var(--accent-cyan) !important;
        }
        
        /* === PLOTLY CHARTS === */
        .js-plotly-plot {
            border-radius: 16px;
            border: 1px solid var(--border-color);
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
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
        
        [data-testid="stSidebar"] a {
            color: #58a6ff !important;
        }
        
        [data-testid="stSidebar"] a:hover {
            color: var(--accent-cyan) !important;
        }
        
        /* === EXPANDER === */
        .streamlit-expanderHeader {
            background: rgba(26, 34, 52, 0.6);
            border-radius: 10px;
            border: 1px solid var(--border-color);
            color: var(--text-primary) !important;
            font-weight: 600;
        }
        
        .streamlit-expanderHeader:hover {
            background: rgba(26, 34, 52, 0.8);
            border-color: var(--accent-cyan);
        }
        
        /* === ANIMATIONS === */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .main > div > div {
            animation: fadeIn 0.6s ease-out;
        }
        
        /* === CUSTOM CARD CLASS === */
        .custom-card {
            background: linear-gradient(135deg, rgba(26, 34, 52, 0.7), rgba(18, 24, 37, 0.7));
            backdrop-filter: blur(15px);
            border-radius: 16px;
            border: 1px solid var(--border-color);
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.4s ease;
        }
        
        .custom-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 48px var(--shadow-glow);
            border-color: var(--accent-cyan);
        }
    </style>
    """, unsafe_allow_html=True)


# === CACHE MANAGEMENT ===
@st.cache_resource
def get_modrinth_client():
    """Singleton Modrinth client"""
    return ModrinthClient()


@st.cache_resource
def get_curseforge_client():
    """Singleton CurseForge client"""
    return CurseForgeClient()


@st.cache_resource
def get_modpack_manager():
    """Singleton Modpack Manager"""
    return ModpackManager()


@st.cache_resource
def get_database():
    """Singleton Database connection"""
    try:
        return StatsDatabase(DATABASE_URL)
    except Exception as e:
        st.error(f"❌ Database connection error: {e}")
        return None


@st.cache_data(ttl=CACHE_TTL)
def load_modrinth_stats():
    """Charge les stats Modrinth avec cache"""
    try:
        client = get_modrinth_client()
        return client.get_stats()
    except Exception as e:
        st.error(f"❌ Modrinth API error: {e}")
        return None


@st.cache_data(ttl=CACHE_TTL)
def load_curseforge_stats():
    """Charge les stats CurseForge avec cache"""
    try:
        client = get_curseforge_client()
        if not client.is_available():
            return None
        return client.get_stats()
    except Exception as e:
        st.error(f"❌ CurseForge API error: {e}")
        return None


@st.cache_data(ttl=CACHE_TTL)
def load_modpacks():
    """Charge les modpacks avec cache"""
    try:
        manager = get_modpack_manager()
        modpacks = manager.load()
        stats = manager.get_stats()
        return modpacks, stats
    except Exception as e:
        st.error(f"❌ Modpacks loading error: {e}")
        return [], {}


# === COMPONENTS ===
def render_stat_card(icon: str, label: str, value: str, delta: str = None):
    """Carte de statistique personnalisée"""
    delta_html = ""
    if delta:
        delta_color = "var(--accent-green)" if "+" in delta else "#ff4d4d"
        delta_html = f'<div style="color: {delta_color}; font-size: 0.9rem; font-weight: 600; margin-top: 0.5rem;">{delta}</div>'
    
    st.markdown(f"""
    <div class="custom-card" style="text-align: center;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="color: var(--text-muted); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 0.75rem;">{label}</div>
        <div style="font-size: 2.5rem; font-weight: 800; font-family: 'Fira Code', monospace; background: linear-gradient(135deg, var(--accent-cyan), var(--accent-green)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Sidebar avec navigation et quick stats"""
    with st.sidebar:
        # Logo
        logo_path = Path(LOGO_PATH)
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        
        st.markdown("### ⚛️ Create Nuclear")
        st.caption("📊 Professional Statistics Dashboard")
        
        st.divider()
        
        # Quick Stats
        st.markdown("#### ⚡ Live Stats")
        
        with st.spinner("Loading..."):
            modrinth_stats = load_modrinth_stats()
            curseforge_stats = load_curseforge_stats()
            
            if modrinth_stats:
                st.metric(
                    "🟢 Modrinth Downloads",
                    f"{modrinth_stats['total_downloads']:,}",
                    f"+{modrinth_stats.get('daily_growth', 0):,}"
                )
            
            if curseforge_stats:
                st.metric(
                    "🔥 CurseForge Downloads",
                    f"{curseforge_stats['total_downloads']:,}",
                    f"+{curseforge_stats.get('daily_growth', 0):,}"
                )
        
        st.divider()
        
        # Navigation Links
        st.markdown("#### 🔗 External Links")
        st.markdown("🟢 [Modrinth Page](https://modrinth.com/mod/createnuclear)")
        st.markdown("🔥 [CurseForge Page](https://www.curseforge.com/minecraft/mc-mods/createnuclear)")
        st.markdown("💾 [GitHub Repository](https://github.com/NoaYnov/Create-nuke--data)")
        
        st.divider()
        
        # System Info
        st.markdown("#### ⚙️ System")
        st.caption(f"🕐 Last update: {datetime.now().strftime('%H:%M:%S')}")
        st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d')}")


def render_modrinth_overview(stats):
    """Vue d'ensemble Modrinth avec métriques"""
    st.markdown("## 📊 Modrinth Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        render_stat_card("📥", "Total Downloads", f"{stats['total_downloads']:,}")
    
    with col2:
        render_stat_card("👥", "Followers", f"{stats['followers']:,}")
    
    with col3:
        render_stat_card("📦", "Versions", str(stats['versions_count']))
    
    with col4:
        if stats['versions']:
            latest = stats['versions'][0]
            render_stat_card("🆕", "Latest Version", latest['name'])
    
    with col5:
        if stats['versions']:
            latest_downloads = stats['versions'][0]['downloads']
            render_stat_card("⭐", "Latest DL", f"{latest_downloads:,}")


def render_modrinth_charts(stats):
    """Graphiques Modrinth"""
    st.markdown("### 📈 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Top 10 Versions by Downloads")
        
        top_versions = sorted(stats['versions'], key=lambda x: x['downloads'], reverse=True)[:10]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=[v['downloads'] for v in top_versions],
            y=[v['name'] for v in top_versions],
            orientation='h',
            marker=dict(
                color=[v['downloads'] for v in top_versions],
                colorscale=[[0, '#00e5ff'], [1, '#48ff91']],
                showscale=False,
                line=dict(color='rgba(255,255,255,0.1)', width=1)
            ),
            text=[f"{v['downloads']:,}" for v in top_versions],
            textposition='auto',
            textfont=dict(size=11, family='Fira Code, monospace', color='white'),
            hovertemplate='<b>%{y}</b><br>Downloads: %{x:,}<extra></extra>'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(26, 34, 52, 0.0)',
            plot_bgcolor='rgba(26, 34, 52, 0.0)',
            font=dict(color='#9ba4b5', family='Inter, sans-serif'),
            height=450,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(
                title='Downloads',
                gridcolor='rgba(139, 148, 158, 0.1)',
                showgrid=True
            ),
            yaxis=dict(
                title='',
                gridcolor='rgba(139, 148, 158, 0.1)'
            ),
            hoverlabel=dict(
                bgcolor='rgba(26, 34, 52, 0.95)',
                font_size=12,
                font_family='Fira Code, monospace'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Game Versions Distribution")
        
        # Compter versions de jeu
        game_versions_count = {}
        for v in stats['versions']:
            for gv in v['game_versions']:
                game_versions_count[gv] = game_versions_count.get(gv, 0) + 1
        
        top_game_versions = sorted(game_versions_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            labels=[v[0] for v in top_game_versions],
            values=[v[1] for v in top_game_versions],
            hole=0.4,
            marker=dict(
                colors=px.colors.sequential.Teal,
                line=dict(color='rgba(255,255,255,0.1)', width=2)
            ),
            textfont=dict(size=12, family='Fira Code, monospace'),
            hovertemplate='<b>%{label}</b><br>Versions: %{value}<br>%{percent}<extra></extra>'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(26, 34, 52, 0.0)',
            plot_bgcolor='rgba(26, 34, 52, 0.0)',
            font=dict(color='#9ba4b5', family='Inter, sans-serif'),
            height=450,
            margin=dict(l=0, r=0, t=20, b=0),
            showlegend=True,
            legend=dict(
                orientation='v',
                yanchor='middle',
                y=0.5,
                xanchor='left',
                x=1.05
            ),
            hoverlabel=dict(
                bgcolor='rgba(26, 34, 52, 0.95)',
                font_size=12,
                font_family='Fira Code, monospace'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_modrinth_versions_table(stats):
    """Tableau des versions Modrinth"""
    st.markdown("### 📋 All Versions")
    
    versions_data = []
    for v in stats['versions']:
        versions_data.append({
            'Version': v['name'],
            'Downloads': v['downloads'],
            'Game Versions': ', '.join(v['game_versions'][:3]) + ('...' if len(v['game_versions']) > 3 else ''),
            'Release Date': date_parser.parse(v['date_published']).strftime('%Y-%m-%d'),
            'Time': date_parser.parse(v['date_published']).strftime('%H:%M')
        })
    
    df = pd.DataFrame(versions_data)
    
    # Format pour affichage
    display_df = df.copy()
    display_df['Downloads'] = display_df['Downloads'].apply(lambda x: f"{x:,}")
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=400,
        column_config={
            'Version': st.column_config.TextColumn('Version', width='medium'),
            'Downloads': st.column_config.TextColumn('Downloads', width='small'),
            'Game Versions': st.column_config.TextColumn('Game Versions', width='large'),
            'Release Date': st.column_config.TextColumn('Release Date', width='small'),
            'Time': st.column_config.TextColumn('Time', width='small')
        }
    )


def render_curseforge_overview(stats):
    """Vue d'ensemble CurseForge"""
    st.markdown("## 📊 CurseForge Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_stat_card("📥", "Total Downloads", f"{stats['total_downloads']:,}")
    
    with col2:
        render_stat_card("👍", "Thumbs Up", f"{stats['followers']:,}")
    
    with col3:
        render_stat_card("📄", "Files Count", str(stats['versions_count']))
    
    with col4:
        render_stat_card("📅", "Last Update", stats.get('last_updated', 'N/A'))


def render_modpacks_section():
    """Section modpacks avec filtres"""
    st.markdown("## 📦 Modpacks Ecosystem")
    st.caption("Modpacks featuring Create Nuclear")
    
    modpacks, modpack_stats = load_modpacks()
    
    if not modpacks:
        st.warning("⚠️ No modpacks data available")
        st.info("💡 Run `python collect_stats.py` to generate modpacks data")
        return
    
    # Stats overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_stat_card("📚", "Total Modpacks", f"{modpack_stats['total']:,}")
    
    with col2:
        render_stat_card("✅", "With Statistics", f"{modpack_stats['with_downloads']:,}")
    
    with col3:
        render_stat_card("📥", "Combined Downloads", f"{modpack_stats['total_downloads']:,}")
    
    with col4:
        coverage = (modpack_stats['with_ids'] / modpack_stats['total'] * 100) if modpack_stats['total'] > 0 else 0
        render_stat_card("🆔", "ID Coverage", f"{coverage:.1f}%")
    
    st.divider()
    
    # Filtres
    col1, col2, col3 = st.columns([4, 2, 2])
    
    with col1:
        search = st.text_input(
            "🔍 Search modpack",
            placeholder="Type modpack name...",
            key="modpack_search"
        )
    
    with col2:
        sort_options = {
            "Downloads (High to Low)": ("downloads", True),
            "Downloads (Low to High)": ("downloads", False),
            "Name (A-Z)": ("name", False),
            "Name (Z-A)": ("name", True)
        }
        sort_selection = st.selectbox("Sort by", list(sort_options.keys()), key="modpack_sort")
    
    with col3:
        show_stats_only = st.checkbox("📊 Only with stats", value=False, key="stats_filter")
    
    # Filtrage
    manager = get_modpack_manager()
    manager._modpacks = modpacks
    
    filtered = manager.filter_by_name(search) if search else modpacks
    
    if show_stats_only:
        filtered = [m for m in filtered if m.get('downloads', 0) > 0]
    
    # Tri
    sort_key, reverse = sort_options[sort_selection]
    if sort_key == "downloads":
        filtered = sorted(filtered, key=lambda x: x.get('downloads', 0), reverse=reverse)
    else:
        filtered = sorted(filtered, key=lambda x: x.get('name', '').lower(), reverse=reverse)
    
    st.success(f"✅ {len(filtered)} modpack(s) found")
    
    # Tableau
    if filtered:
        modpacks_data = []
        for m in filtered:
            modpacks_data.append({
                'Name': m['name'],
                'ID': m.get('id', 'N/A'),
                'Downloads': m.get('downloads', 0),
                'Link': m.get('link', 'N/A')
            })
        
        df = pd.DataFrame(modpacks_data)
        
        # Format
        display_df = df.copy()
        display_df['Downloads'] = display_df['Downloads'].apply(lambda x: f"{x:,}" if x > 0 else "N/A")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=500,
            column_config={
                'Name': st.column_config.TextColumn('Name', width='large'),
                'ID': st.column_config.TextColumn('ID', width='small'),
                'Downloads': st.column_config.TextColumn('Downloads', width='medium'),
                'Link': st.column_config.LinkColumn('Link', width='small', display_text="View →")
            }
        )
        
        # Export
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"modpacks_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


def render_database_analysis():
    """Analyse historique de la base de données"""
    st.markdown("## 💾 Historical Analytics")
    st.caption("Track download trends over time")
    
    db = get_database()
    
    if not db:
        st.error("❌ Database connection unavailable")
        return
    
    # Sélecteurs
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        platform = st.selectbox(
            "📊 Platform",
            ["modrinth", "curseforge"],
            key="db_platform"
        )
    
    with col2:
        period_options = {
            "Last 7 days": 7,
            "Last 30 days": 30,
            "Last 90 days": 90,
            "Last 180 days": 180,
            "All time": None
        }
        period_selection = st.selectbox(
            "📅 Period",
            list(period_options.keys()),
            key="db_period"
        )
        days = period_options[period_selection]
    
    with col3:
        st.write("")  # Spacing
        if st.button("🔄 Refresh Data", key="refresh_db"):
            st.cache_data.clear()
            st.rerun()
    
    # Charger données
    with st.spinner("Loading historical data..."):
        history = db.get_daily_stats_history(platform, days=days)
    
    if not history or len(history) == 0:
        st.warning("⚠️ No historical data available for this period")
        return
    
    # Préparer DataFrame
    df = pd.DataFrame(history)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Calculer métriques
    total_current = df['total_downloads'].iloc[-1] if len(df) > 0 else 0
    total_start = df['total_downloads'].iloc[0] if len(df) > 0 else 0
    growth = total_current - total_start
    avg_daily = growth / len(df) if len(df) > 1 else 0
    
    # Métriques summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_stat_card("📊", "Current Total", f"{total_current:,}")
    
    with col2:
        render_stat_card("📈", "Period Growth", f"+{growth:,}", f"+{(growth/total_start*100):.1f}%" if total_start > 0 else "")
    
    with col3:
        render_stat_card("📅", "Avg Daily", f"+{avg_daily:,.0f}")
    
    with col4:
        days_count = len(df)
        render_stat_card("🗓️", "Days Tracked", str(days_count))
    
    st.divider()
    
    # Graphique principal
    st.markdown("### 📈 Downloads Evolution")
    
    fig = go.Figure()
    
    # Ligne principale
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['total_downloads'],
        mode='lines+markers',
        name='Total Downloads',
        line=dict(color='#00e5ff', width=3, shape='spline'),
        marker=dict(size=8, color='#48ff91', line=dict(color='#00e5ff', width=2)),
        fill='tozeroy',
        fillcolor='rgba(0, 229, 255, 0.1)',
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Downloads: %{y:,}<extra></extra>'
    ))
    
    # Tendance
    if len(df) > 2:
        from scipy import stats
        x_numeric = (df['date'] - df['date'].min()).dt.days
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, df['total_downloads'])
        trend_line = slope * x_numeric + intercept
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=trend_line,
            mode='lines',
            name='Trend',
            line=dict(color='#b794f6', width=2, dash='dash'),
            hovertemplate='<b>Trend</b><br>%{y:,.0f}<extra></extra>'
        ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(26, 34, 52, 0.0)',
        plot_bgcolor='rgba(26, 34, 52, 0.0)',
        font=dict(color='#9ba4b5', family='Inter, sans-serif'),
        height=500,
        xaxis=dict(
            title='Date',
            gridcolor='rgba(139, 148, 158, 0.1)',
            showgrid=True
        ),
        yaxis=dict(
            title='Total Downloads',
            gridcolor='rgba(139, 148, 158, 0.1)',
            showgrid=True
        ),
        hovermode='x unified',
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        hoverlabel=dict(
            bgcolor='rgba(26, 34, 52, 0.95)',
            font_size=12,
            font_family='Fira Code, monospace'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Tableau détaillé
    st.markdown("### 📊 Detailed Data")
    
    display_df = df[['date', 'total_downloads', 'followers', 'versions_count']].copy()
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    
    # Calculer croissance quotidienne
    display_df['daily_growth'] = df['total_downloads'].diff().fillna(0).astype(int)
    
    display_df.columns = ['Date', 'Total Downloads', 'Followers', 'Versions', 'Daily Growth']
    
    # Format
    display_df['Total Downloads'] = display_df['Total Downloads'].apply(lambda x: f"{x:,}")
    display_df['Daily Growth'] = display_df['Daily Growth'].apply(lambda x: f"+{x:,}" if x > 0 else str(x))
    
    st.dataframe(
        display_df.iloc[::-1],  # Reverse pour avoir le plus récent en haut
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # Export
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Full History CSV",
        data=csv,
        file_name=f"{platform}_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def render_modrinth_tab():
    """Tab Modrinth complet"""
    stats = load_modrinth_stats()
    
    if not stats:
        st.error("❌ Failed to load Modrinth statistics")
        st.info("💡 Check your internet connection and API availability")
        return
    
    render_modrinth_overview(stats)
    st.divider()
    render_modrinth_charts(stats)
    st.divider()
    render_modrinth_versions_table(stats)


def render_curseforge_tab():
    """Tab CurseForge complet"""
    stats = load_curseforge_stats()
    
    if not stats:
        st.warning("⚠️ CurseForge API key not configured")
        st.info("💡 Set CURSEFORGE_API_KEY environment variable to enable CurseForge statistics")
        return
    
    render_curseforge_overview(stats)
    st.divider()
    render_modpacks_section()


def render_database_tab():
    """Tab Database complet"""
    render_database_analysis()


# === MAIN APP ===
def main():
    """Application principale"""
    
    # Charger CSS personnalisé
    load_custom_css()
    
    # Sidebar
    render_sidebar()
    
    # Header avec bannière
    banner_path = Path(BANNER_PATH)
    if banner_path.exists():
        st.image(str(banner_path), use_container_width=True)
    
    # Titre principal
    st.markdown("# ⚛️ Create Nuclear Statistics")
    st.caption(f"📊 Professional Analytics Dashboard • Real-time data • Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.divider()
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs([
        "📦 Modrinth",
        "🔥 CurseForge",
        "💾 Database"
    ])
    
    with tab1:
        render_modrinth_tab()
    
    with tab2:
        render_curseforge_tab()
    
    with tab3:
        render_database_tab()
    
    # Footer
    st.divider()
    st.caption("⚛️ Create Nuclear Statistics Dashboard v2.0 | Made with ❤️ using Streamlit")


if __name__ == "__main__":
    main()
