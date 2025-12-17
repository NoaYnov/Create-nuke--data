"""
Configuration centralisée pour l'application Create Nuclear Stats
"""
import os

# API Configuration
MODRINTH_PROJECT_SLUG = "createnuclear"
MODRINTH_API_BASE = "https://api.modrinth.com/v2"
CURSEFORGE_API_BASE = "https://api.curseforge.com"
CURSEFORGE_MOD_ID = 989797
CURSEFORGE_API_KEY = os.getenv('CURSEFORGE_API_KEY', '')

# User Agent
USER_AGENT = "CreateNuclear-Stats/1.0"

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:changeme@localhost:5432/createnuclear_stats')

# File Paths
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
MODPACKS_CSV_PATH = os.path.join(DATA_DIR, 'data', 'curseforge_modpacks.csv')
MODPACKS_JSON_PATH = os.path.join(DATA_DIR, 'data', 'curseforge_modpacks.json')
LOGO_PATH = os.path.join(DATA_DIR, 'assets', 'logo.png')
BANNER_PATH = os.path.join(DATA_DIR, 'assets', 'banniere-nuclear.jpg')

# Cache Settings
CACHE_TTL = 3600  # 1 hour

# Scraping Settings
MAX_PAGES = 35
PAGE_DELAY = 2
CLOUDFLARE_DELAY = 10
API_DELAY = 1
BATCH_SIZE = 10
