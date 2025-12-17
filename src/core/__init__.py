# src/core/__init__.py
"""
Core modules for Create Nuclear Stats
Contains database, API clients, scrapers, and modpack management
"""

from .database import StatsDatabase
from .api_clients import ModrinthClient, CurseForgeClient
from .scraper import CurseForgeScraper
from .modpack_manager import ModpackManager

__all__ = [
    'StatsDatabase',
    'ModrinthClient',
    'CurseForgeClient',
    'CurseForgeScraper',
    'ModpackManager',
]
